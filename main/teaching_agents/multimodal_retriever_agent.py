"""Multimodal Retriever Agent - Retrieves images, diagrams, and related educational materials"""

from main.multimodal_rag import MultimodalRetriever
from main.config import get_openai_config
from typing import Dict, Any, List, Optional
import json
import logging
import os
import base64

logger = logging.getLogger(__name__)

class MultimodalRetrieverAgent:
    """Agent for retrieving multimodal educational materials (text and images)"""

    def __init__(self, rag_folder: str = "./rag_data", device: str = "cpu"):
        self.rag_folder = rag_folder
        self.device = device
        self.retriever = None
        self.retriever_initialized = False
        self._llm = None
        self._init_retriever()

    def _get_llm(self):
        """Lazily initialise the LLM for image captioning."""
        if self._llm is None:
            try:
                from langchain_openai import ChatOpenAI
                openai_config = get_openai_config()
                self._llm = ChatOpenAI(
                    openai_api_base=openai_config['api_base'],
                    openai_api_key=openai_config['api_key'],
                    model=openai_config['model'],
                    temperature=0.3,
                )
            except Exception as e:
                logger.warning(f"Could not initialise LLM for image captioning: {e}")
        return self._llm

    async def generate_image_description(self, image_path: str) -> str:
        """
        Generate a textual description for an image file.
        Tries vision-capable API first; falls back to filename-based description.
        """
        filename = os.path.basename(image_path)
        stem = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")
        desc_file = image_path + ".desc"

        # Return cached description if available
        if os.path.exists(desc_file):
            try:
                with open(desc_file, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except Exception:
                pass

        # Try to use vision LLM
        try:
            from langchain_core.messages import HumanMessage
            llm = self._get_llm()
            if llm is None:
                return stem

            image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
            if os.path.splitext(filename)[1].lower() not in image_extensions:
                return stem

            with open(image_path, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode("utf-8")

            ext = os.path.splitext(filename)[1].lower().lstrip(".")
            mime_map = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png",
                        "gif": "gif", "bmp": "bmp", "webp": "webp"}
            mime_type = f"image/{mime_map.get(ext, 'jpeg')}"

            msg = HumanMessage(content=[
                {"type": "text",
                 "text": "请用中文简洁描述这张图片的内容，重点说明图片中的教学相关信息，不超过100字。"},
                {"type": "image_url",
                 "image_url": {"url": f"data:{mime_type};base64,{img_data}"}}
            ])
            response = await llm.ainvoke([msg])
            description = response.content.strip()

            # Cache the description
            try:
                with open(desc_file, "w", encoding="utf-8") as f:
                    f.write(description)
            except Exception:
                pass

            logger.info(f"Generated description for {filename}: {description[:60]}...")
            return description

        except Exception as e:
            logger.warning(f"Vision LLM description failed for {filename}: {e}")
            return stem

    async def build_image_index_from_uploads(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Build a semantic index of uploaded images by generating text descriptions.
        Returns a list of {path, filename, description} dicts.
        """
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
        indexed_images = []
        for path in image_paths:
            ext = os.path.splitext(path)[1].lower()
            if ext not in image_extensions:
                continue
            description = await self.generate_image_description(path)
            indexed_images.append({
                "path": path,
                "filename": os.path.basename(path),
                "description": description
            })
            logger.info(f"Indexed image: {os.path.basename(path)} -> {description[:60]}")
        return indexed_images

    def _init_retriever(self):
        """Initialize the retriever with error handling"""
        try:
            self.retriever = MultimodalRetriever(
                folder_path=self.rag_folder,
                device=self.device
            )
            self.retriever_initialized = True
            logger.info("MultimodalRetriever initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize MultimodalRetriever: {str(e)}")
            logger.warning("System will operate with degraded RAG capabilities")
            self.retriever_initialized = False

    def refresh_retriever(self, rag_folder: Optional[str] = None) -> None:
        """Rebuild the retriever to include newly uploaded materials."""
        if rag_folder:
            self.rag_folder = rag_folder
        logger.info("Refreshing MultimodalRetriever with folder: %s", self.rag_folder)
        self._init_retriever()

    async def retrieve_materials(
        self,
        intent_data: Dict[str, Any],
        query_count: int = 5
    ) -> Dict[str, Any]:
        """
        Retrieve relevant educational materials based on teaching intent

        Args:
            intent_data: Parsed teaching intent
            query_count: Number of materials to retrieve for each query

        Returns:
            Dictionary containing retrieved materials organized by type
        """
        retrieved_materials = {
            "text_materials": [],
            "image_materials": [],
            "combined_materials": [],
            "key_concept_materials": {}
        }

        # If retriever is not initialized, return empty materials
        if not self.retriever_initialized:
            logger.warning("Retriever not available, returning empty materials")
            return retrieved_materials

        try:
            # Generate retrieval queries from intent data
            queries = self._generate_retrieval_queries(intent_data)

            # Retrieve text materials
            for query in queries:
                try:
                    text_results = self.retriever.retrieve_text(query, top_k=query_count)
                    retrieved_materials["text_materials"].extend(text_results)
                except Exception as e:
                    logger.warning(f"Error retrieving text for query '{query}': {str(e)}")

            # Retrieve image materials
            for concept in intent_data.get('key_concepts', []):
                try:
                    image_results = self.retriever.retrieve_images(concept, top_k=query_count)
                    retrieved_materials["image_materials"].extend(image_results)
                    retrieved_materials["key_concept_materials"][concept] = image_results
                except Exception as e:
                    logger.warning(f"Error retrieving images for concept '{concept}': {str(e)}")

            # Retrieve combined multimodal materials
            for query in queries:
                try:
                    multimodal_results = self.retriever.retrieve_multimodal(query, top_k=query_count)
                    retrieved_materials["combined_materials"].extend(multimodal_results)
                except Exception as e:
                    logger.warning(f"Error retrieving multimodal for query '{query}': {str(e)}")

            return retrieved_materials

        except Exception as e:
            logger.error(f"Critical error in retrieve_materials: {str(e)}")
            return retrieved_materials

    def _generate_retrieval_queries(self, intent_data: Dict[str, Any]) -> List[str]:
        """Generate search queries from intent data"""
        queries = []

        if intent_data.get('theme'):
            queries.append(intent_data['theme'])

        queries.extend(intent_data.get('key_concepts', []))

        for obj in intent_data.get('objectives', []):
            queries.append(' '.join(obj.split()[:5]))

        seen = set()
        unique_queries = []
        for q in queries:
            if q.lower() not in seen:
                seen.add(q.lower())
                unique_queries.append(q)

        return unique_queries[:10]

    async def retrieve_by_concept(
        self,
        concept: str,
        material_type: str = "all"
    ) -> Dict[str, Any]:
        """Retrieve materials for a specific concept"""
        results = {
            "concept": concept,
            "text_materials": [],
            "image_materials": []
        }

        if not self.retriever_initialized:
            logger.warning("Retriever not available for concept retrieval")
            return results

        try:
            if material_type in ["text", "all"]:
                results["text_materials"] = self.retriever.retrieve_text(concept, top_k=5)

            if material_type in ["image", "all"]:
                results["image_materials"] = self.retriever.retrieve_images(concept, top_k=5)

            return results

        except Exception as e:
            logger.error(f"Error retrieving concept materials: {str(e)}")
            return results

    def get_retriever_stats(self) -> Dict[str, Any]:
        """Get statistics about the retriever"""
        if not self.retriever_initialized:
            return {
                "index_status": "not_initialized",
                "warning": "Retriever not available"
            }

        try:
            return {
                "total_documents": self.retriever.get_document_count(),
                "total_images": self.retriever.get_image_count(),
                "embedding_model": self.retriever.embedding_model_name,
                "vector_dimension": self.retriever.vector_dimension,
                "index_status": "ready"
            }
        except Exception as e:
            logger.error(f"Stats retrieval error: {str(e)}")
            return {
                "index_status": "error",
                "error": f"Stats retrieval error: {str(e)}"
            }


# Example usage for testing
async def test_multimodal_retriever():
    """Test the Multimodal Retriever Agent"""
    agent = MultimodalRetrieverAgent(rag_folder="./rag_data")

    intent_data = {
        "theme": "The Human Circulatory System",
        "objectives": [
            "Understand the structure and function of the heart",
            "Explain how blood circulates through the body"
        ],
        "audience_level": "10th Grade",
        "subject_area": "Biology",
        "duration_minutes": 50,
        "key_concepts": ["Heart", "Blood Circulation", "Arteries", "Veins"],
        "teaching_approach": "Interactive"
    }

    materials = await agent.retrieve_materials(intent_data)
    print("Retrieved Materials:")
    print(json.dumps(materials, indent=2, ensure_ascii=False, default=str))

    stats = agent.get_retriever_stats()
    print("\nRetriever Stats:")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_multimodal_retriever())
