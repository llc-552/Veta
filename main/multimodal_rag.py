"""Multimodal RAG Module - Extended RAG system with text and image retrieval capabilities"""

import os
import json
import hashlib
from tqdm import tqdm
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.docstore.document import Document
from main.config import get_rag_config

class MultimodalRetriever:
    """Extended retriever supporting both text and image retrieval"""

    def __init__(
        self,
        folder_path: str,
        embedding_model: str = "Qwen/Qwen3-Embedding-0.6B",
        rerank_model: str = "BAAI/bge-reranker-base",
        index_path: str = "./faiss_index",
        image_index_path: str = "./faiss_image_index",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        bm25_k: int = 5,
        faiss_k: int = 5,
        top_n: int = 3,
        device: str = "cpu"
    ):
        """
        Initialize Multimodal Retriever

        Args:
            folder_path: Path to folder containing educational materials
            embedding_model: Name of embedding model
            rerank_model: Name of reranking model
            index_path: Path to FAISS text index
            image_index_path: Path to FAISS image index
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            bm25_k: Number of results from BM25
            faiss_k: Number of results from FAISS
            top_n: Final number of results after reranking
            device: Device to use ('cpu' or 'cuda')
        """
        self.folder_path = folder_path
        self.index_path = index_path
        self.image_index_path = image_index_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.bm25_k = bm25_k
        self.faiss_k = faiss_k
        self.top_n = top_n
        self.device = device

        # Initialize embeddings with offline mode and error handling
        print("Initializing embeddings...")
        try:
            import os as os_module
            # Try to use offline mode first
            old_offline = os_module.environ.get('HF_HUB_OFFLINE')
            os_module.environ['HF_HUB_OFFLINE'] = '1'

            self.embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model,
                encode_kwargs={"normalize_embeddings": True},
                model_kwargs={"device": device}
            )
            self.embedding_model_name = embedding_model
            self.vector_dimension = 768
            print("✅ Embeddings initialized successfully")

            # Restore previous offline mode setting
            if old_offline is not None:
                os_module.environ['HF_HUB_OFFLINE'] = old_offline
            else:
                os_module.environ.pop('HF_HUB_OFFLINE', None)
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize embeddings: {str(e)}")
            print("System will operate with degraded RAG capabilities (BM25 only)")
            self.embeddings = None
            self.embedding_model_name = embedding_model
            self.vector_dimension = 768

        # Initialize retriever attributes with defaults
        self.bm25_retriever = None
        self.faiss_retriever = None
        self.image_faiss_retriever = None
        self.ensemble_retriever = None
        self.compression_retriever = None
        self.rerank_model = None
        self.compressor = None
        self.docs = []
        self.image_docs = []

        # Check if index rebuild is needed
        need_rebuild = self._need_rebuild_index()

        if need_rebuild:
            print("Building/rebuilding multimodal indices...")
            try:
                self._build_indices()
                print("Indices built successfully!")
            except Exception as e:
                print(f"Warning: Could not build indices: {str(e)}")
        else:
            print("Using existing indices...")

        # Load documents for BM25
        try:
            self._load_documents_for_bm25()
        except Exception as e:
            print(f"Warning: Could not load documents for BM25: {str(e)}")

        # Load or create FAISS indices
        try:
            self._setup_faiss_retrievers()
        except Exception as e:
            print(f"Warning: Could not setup FAISS retrievers: {str(e)}")

        # Setup reranking
        try:
            self.rerank_model = HuggingFaceCrossEncoder(model_name=rerank_model)
            self.compressor = CrossEncoderReranker(model=self.rerank_model, top_n=top_n)
        except Exception as e:
            print(f"Warning: Could not setup reranking: {str(e)}")
            self.rerank_model = None
            self.compressor = None

        # Create ensemble retriever
        try:
            if hasattr(self, 'bm25_retriever') and hasattr(self, 'faiss_retriever'):
                self.ensemble_retriever = EnsembleRetriever(
                    retrievers=[self.bm25_retriever, self.faiss_retriever],
                    weights=[0.5, 0.5]
                )
            else:
                self.ensemble_retriever = None
        except Exception as e:
            print(f"Warning: Could not create ensemble retriever: {str(e)}")
            self.ensemble_retriever = None

        # Create compression retriever
        try:
            if self.compressor and self.ensemble_retriever:
                self.compression_retriever = ContextualCompressionRetriever(
                    base_compressor=self.compressor,
                    base_retriever=self.ensemble_retriever
                )
            else:
                self.compression_retriever = None
        except Exception as e:
            print(f"Warning: Could not create compression retriever: {str(e)}")
            self.compression_retriever = None

    def _need_rebuild_index(self) -> bool:
        """Check if indices need to be rebuilt"""
        # Check if both indices exist
        if not os.path.exists(self.index_path) or not os.path.exists(self.image_index_path):
            return True

        # Check if source files have changed
        hash_file = os.path.join(self.index_path, ".hash")
        if not os.path.exists(hash_file):
            return True

        current_hash = self._calculate_folder_hash(self.folder_path)
        with open(hash_file, 'r') as f:
            stored_hash = f.read().strip()

        return current_hash != stored_hash

    def _calculate_folder_hash(self, folder_path: str) -> str:
        """Calculate hash of all files in folder"""
        file_hashes = []

        if not os.path.exists(folder_path):
            return ""

        for file in sorted(os.listdir(folder_path)):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                    file_hashes.append(file_hash)

        combined = ''.join(file_hashes)
        return hashlib.md5(combined.encode()).hexdigest()

    def _build_indices(self) -> None:
        """Build both text and image indices"""
        # Load documents
        self.docs = self._load_documents(self.folder_path)

        if not self.docs:
            print("Warning: No documents loaded")
            return

        # Check if embeddings are available
        if self.embeddings is None:
            print("Warning: Embeddings not available, skipping FAISS index creation")
            os.makedirs(self.index_path, exist_ok=True)
            os.makedirs(self.image_index_path, exist_ok=True)
            # Save hash anyway to mark index as processed
            current_hash = self._calculate_folder_hash(self.folder_path)
            hash_file = os.path.join(self.index_path, ".hash")
            with open(hash_file, 'w') as f:
                f.write(current_hash)
            return

        # Split text
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        split_docs = splitter.split_documents(self.docs)

        # Create FAISS index for text
        try:
            os.makedirs(self.index_path, exist_ok=True)
            faiss_vectorstore = FAISS.from_documents(split_docs, self.embeddings)
            faiss_vectorstore.save_local(self.index_path)
        except Exception as e:
            print(f"Warning: Could not create FAISS index: {e}")

        # Save hash to prevent unnecessary rebuilds
        current_hash = self._calculate_folder_hash(self.folder_path)
        hash_file = os.path.join(self.index_path, ".hash")
        with open(hash_file, 'w') as f:
            f.write(current_hash)

        # Create image index (placeholder - would need image loading implementation)
        os.makedirs(self.image_index_path, exist_ok=True)

        # For now, create empty image index - could be extended with PIL/vision models
        try:
            self.image_docs = self._load_images(self.folder_path)
            if self.image_docs:
                image_vectorstore = FAISS.from_documents(self.image_docs, self.embeddings)
                image_vectorstore.save_local(self.image_index_path)
        except Exception as e:
            print(f"Warning: Could not create image index: {e}")

    def _load_documents(self, folder_path: str) -> List[Document]:
        """Load documents from folder"""
        docs = []

        if not os.path.exists(folder_path):
            return docs

        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)

            if file.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
                docs.extend(loader.load())
            elif file.endswith('.txt'):
                loader = TextLoader(file_path)
                docs.extend(loader.load())
            elif file.endswith('.md'):
                loader = TextLoader(file_path)
                docs.extend(loader.load())
            elif file.endswith('.docx'):
                try:
                    loader = UnstructuredWordDocumentLoader(file_path)
                    docs.extend(loader.load())
                except Exception as e:
                    print(f"Error loading {file}: {e}")

        return docs

    def _load_images(self, folder_path: str) -> List[Document]:
        """Load images from folder (stub - would need vision model)"""
        image_docs = []

        # Image file extensions to look for
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}

        if not os.path.exists(folder_path):
            return image_docs

        for file in os.listdir(folder_path):
            if Path(file).suffix.lower() in image_extensions:
                file_path = os.path.join(folder_path, file)
                # Create document with image metadata
                image_doc = Document(
                    page_content=f"Image: {file}",
                    metadata={
                        "source": file_path,
                        "type": "image",
                        "filename": file
                    }
                )
                image_docs.append(image_doc)

        return image_docs

    def _load_documents_for_bm25(self) -> None:
        """Load documents for BM25 retriever"""
        self.docs = self._load_documents(self.folder_path)

    def _setup_faiss_retrievers(self) -> None:
        """Setup FAISS retrievers"""
        try:
            # Check if embeddings are available
            if self.embeddings is None:
                print("Embeddings not available, skipping FAISS setup")
                self.faiss_retriever = None
                self.bm25_retriever = None
                self.image_faiss_retriever = None
                return

            # Load text FAISS
            if os.path.exists(self.index_path):
                try:
                    self.faiss_vectorstore = FAISS.load_local(
                        self.index_path,
                        self.embeddings,
                        allow_dangerous_deserialization=True
                    )
                    self.faiss_retriever = self.faiss_vectorstore.as_retriever(
                        search_kwargs={"k": self.faiss_k}
                    )
                except Exception as e:
                    print(f"Could not load FAISS index: {e}")
                    self.faiss_retriever = None
            else:
                self.faiss_retriever = None

            # Setup BM25
            if hasattr(self, 'docs') and self.docs:
                texts = [doc.page_content for doc in self.docs]
                metadatas = [doc.metadata for doc in self.docs]
                self.bm25_retriever = BM25Retriever.from_texts(texts, metadatas=metadatas)
                self.bm25_retriever.k = self.bm25_k
            else:
                self.bm25_retriever = None

            # Try to load image FAISS if it exists
            if os.path.exists(self.image_index_path):
                try:
                    self.image_faiss_vectorstore = FAISS.load_local(
                        self.image_index_path,
                        self.embeddings,
                        allow_dangerous_deserialization=True
                    )
                    self.image_faiss_retriever = self.image_faiss_vectorstore.as_retriever(
                        search_kwargs={"k": self.faiss_k}
                    )
                except Exception as e:
                    print(f"Could not load image index: {e}")
                    self.image_faiss_retriever = None
            else:
                self.image_faiss_retriever = None
        except Exception as e:
            print(f"Critical error in _setup_faiss_retrievers: {e}")
            self.faiss_retriever = None
            self.bm25_retriever = None
            self.image_faiss_retriever = None

    def retrieve_text(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve text documents

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of retrieved documents
        """
        try:
            # Try compression retriever first
            if self.compression_retriever:
                results = self.compression_retriever.invoke(query)
            # Fallback to ensemble retriever
            elif self.ensemble_retriever:
                results = self.ensemble_retriever.invoke(query)
            # Fallback to BM25 only
            elif hasattr(self, 'bm25_retriever') and self.bm25_retriever:
                results = self.bm25_retriever.invoke(query)
            else:
                return []

            return [
                {
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                    "score": getattr(doc, "score", 0.0)
                }
                for doc in results[:top_k]
            ]
        except Exception as e:
            print(f"Text retrieval error: {e}")
            return []

    def retrieve_images(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve image documents

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of retrieved image documents
        """
        try:
            if self.image_faiss_retriever is None:
                return []

            results = self.image_faiss_retriever.invoke(query)

            return [
                {
                    "filename": doc.metadata.get("filename", "unknown"),
                    "source": doc.metadata.get("source", "unknown"),
                    "type": "image",
                    "score": getattr(doc, "score", 0.0)
                }
                for doc in results[:top_k]
            ]
        except Exception as e:
            print(f"Image retrieval error: {e}")
            return []

    def retrieve_multimodal(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve both text and images for a query

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of multimodal results
        """
        results = []

        # Get text results
        text_results = self.retrieve_text(query, top_k=top_k)
        results.extend([{**r, "type": "text"} for r in text_results])

        # Get image results
        image_results = self.retrieve_images(query, top_k=top_k)
        results.extend([{**r, "type": "image"} for r in image_results])

        return results[:top_k]

    def get_document_count(self) -> int:
        """Get number of documents in index"""
        return len(self.docs) if hasattr(self, 'docs') else 0

    def get_image_count(self) -> int:
        """Get number of images in index"""
        return len(self.image_docs) if hasattr(self, 'image_docs') else 0


# Backward compatibility with original Retriever class
class Retriever(MultimodalRetriever):
    """Backward compatible Retriever class"""
    pass


# Example usage for testing
def test_multimodal_retriever():
    """Test the multimodal retriever"""
    retriever = MultimodalRetriever(
        folder_path="./rag_data",
        device="cpu"
    )

    # Test text retrieval
    text_results = retriever.retrieve_text("teaching methods", top_k=3)
    print("Text Results:")
    for result in text_results:
        print(f"  - {result['source']}")

    # Test image retrieval
    image_results = retriever.retrieve_images("diagram", top_k=3)
    print("\nImage Results:")
    for result in image_results:
        print(f"  - {result['filename']}")

    # Test multimodal retrieval
    multimodal_results = retriever.retrieve_multimodal("biology", top_k=5)
    print("\nMultimodal Results:")
    for result in multimodal_results:
        print(f"  - [{result['type']}] {result.get('filename', result.get('source'))}")


if __name__ == "__main__":
    test_multimodal_retriever()
