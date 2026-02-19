"""Multimodal Retriever Agent - Retrieves images, diagrams, and related educational materials"""

from main.multimodal_rag import MultimodalRetriever
from typing import Dict, Any, List, Optional
import json
import logging

logger = logging.getLogger(__name__)

class MultimodalRetrieverAgent:
    """Agent for retrieving multimodal educational materials (text and images)"""

    def __init__(self, rag_folder: str = "./rag_data", device: str = "cpu"):
        """
        Initialize the Multimodal Retriever Agent

        Args:
            rag_folder: Path to folder containing educational materials
            device: Device to use for embeddings ('cpu' or 'cuda')
        """
        self.rag_folder = rag_folder
        self.device = device
        self.retriever = None
        self.retriever_initialized = False
        self._init_retriever()

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
        """
        Generate search queries from intent data

        Args:
            intent_data: Parsed teaching intent

        Returns:
            List of search queries
        """
        queries = []

        # Add theme as primary query
        if intent_data.get('theme'):
            queries.append(intent_data['theme'])

        # Add key concepts
        queries.extend(intent_data.get('key_concepts', []))

        # Add objectives (simplified)
        for obj in intent_data.get('objectives', []):
            # Take first 20 words of objective as query
            queries.append(' '.join(obj.split()[:5]))

        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for q in queries:
            if q.lower() not in seen:
                seen.add(q.lower())
                unique_queries.append(q)

        return unique_queries[:10]  # Limit to 10 queries

    async def retrieve_by_concept(
        self,
        concept: str,
        material_type: str = "all"
    ) -> Dict[str, Any]:
        """
        Retrieve materials for a specific concept

        Args:
            concept: The concept to retrieve materials for
            material_type: Type of materials ('text', 'image', or 'all')

        Returns:
            Dictionary containing retrieved materials
        """
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
        """
        Get statistics about the retriever

        Returns:
            Dictionary containing retriever statistics
        """
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
