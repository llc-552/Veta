"""Teaching Workflow - LangGraph-based workflow for lesson plan and PPT generation"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from langgraph.graph import StateGraph, START, END
from main.teaching_agents.intent_parser_agent import IntentParserAgent
from main.teaching_agents.multimodal_retriever_agent import MultimodalRetrieverAgent
from main.teaching_agents.content_generator_agent import ContentGeneratorAgent
from main.teaching_agents.template_matcher_agent import TemplateMatcherAgent
from main.teaching_agents.export_manager_agent import ExportManagerAgent

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TeachingWorkflow:
    """LangGraph-based workflow for intelligent lesson plan and PPT generation"""

    def __init__(
        self,
        rag_folder: str = "./rag_data",
        templates_folder: str = "./templates/ppt_templates",
        output_folder: str = "./generated_lessons"
    ):
        """
        Initialize Teaching Workflow

        Args:
            rag_folder: Path to RAG data folder
            templates_folder: Path to templates folder
            output_folder: Path to output folder
        """
        # Initialize agents
        self.intent_parser = IntentParserAgent()
        self.retriever = MultimodalRetrieverAgent(rag_folder=rag_folder)
        self.content_generator = ContentGeneratorAgent()
        self.template_matcher = TemplateMatcherAgent(templates_folder)
        self.export_manager = ExportManagerAgent(output_folder)

        # Build the workflow graph
        self.graph = self._build_workflow_graph()
        self.compiled_graph = self.graph.compile()

    def _build_workflow_graph(self) -> StateGraph:
        """Build the LangGraph workflow graph"""

        # Define the state schema
        state_schema = dict

        # Create the graph
        graph = StateGraph(state_schema)

        # Add nodes for each stage
        graph.add_node("input_processing", self.process_input)
        graph.add_node("intent_parsing", self.parse_intent)
        graph.add_node("material_retrieval", self.retrieve_materials)
        graph.add_node("content_generation", self.generate_content)
        graph.add_node("template_matching", self.match_template)
        graph.add_node("slide_layout", self.layout_slides)
        graph.add_node("export", self.export_output)

        # Define edges
        graph.add_edge(START, "input_processing")
        graph.add_edge("input_processing", "intent_parsing")
        graph.add_edge("intent_parsing", "material_retrieval")
        graph.add_edge("material_retrieval", "content_generation")
        graph.add_edge("content_generation", "template_matching")
        graph.add_edge("template_matching", "slide_layout")
        graph.add_edge("slide_layout", "export")
        graph.add_edge("export", END)

        return graph

    def process_input(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate user input"""
        logger.info("=" * 60)
        logger.info("🎓 Starting Teaching Workflow - Input Processing")
        logger.info("=" * 60)

        state["status"] = "processing_input"
        state["error"] = None

        # Validate required input
        if not state.get("user_input"):
            state["error"] = "User input is required"
            logger.error("❌ User input is required but was not provided")
            return state

        logger.info("✅ User input received:")
        logger.info(state.get("user_input"))

        state["processing_step"] = "Input processed successfully"
        logger.info("✅ Input validation passed")
        return state

    async def parse_intent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Parse teaching intent from user input"""
        state["status"] = "parsing_intent"
        logger.info("")
        logger.info("📝 Step 1: Parsing Teaching Intent")
        logger.info("-" * 60)

        try:
            user_input = state.get("user_input", "")
            logger.info("Calling IntentParserAgent.parse_teaching_intent()...")

            intent_data = await self.intent_parser.parse_teaching_intent(user_input)
            logger.info(f"Intent data received: {json.dumps(intent_data, ensure_ascii=False, default=str)}")

            if not self.intent_parser.validate_intent(intent_data):
                state["error"] = "Failed to parse sufficient teaching intent"
                logger.error("❌ Intent validation failed")
            else:
                state["intent_data"] = intent_data
                state["processing_step"] = "Intent parsed successfully"
                logger.info(f"✅ Intent parsed: {intent_data.get('theme', 'Unknown')}")

        except Exception as e:
            state["error"] = f"Intent parsing error: {str(e)}"
            logger.error(f"❌ Intent parsing error: {str(e)}", exc_info=True)

        return state

    async def retrieve_materials(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant educational materials"""
        state["status"] = "retrieving_materials"
        logger.info("")
        logger.info("📚 Step 2: Retrieving Educational Materials")
        logger.info("-" * 60)

        try:
            intent_data = state.get("intent_data", {})
            uploaded_files = state.get("uploaded_files", [])
            if uploaded_files:
                logger.info("Uploaded materials detected (%d). Refreshing retriever.", len(uploaded_files))
                self.retriever.refresh_retriever()

            logger.info(f"Calling MultimodalRetrieverAgent with intent: {intent_data.get('theme', 'Unknown')}")

            materials = await self.retriever.retrieve_materials(intent_data)
            logger.info(f"Materials retrieved: {len(materials.get('text_materials', []))} text materials, {len(materials.get('image_materials', []))} image materials")

            state["retrieved_materials"] = materials
            state["processing_step"] = f"Retrieved materials for {len(materials.get('text_materials', []))} concepts"
            logger.info(f"✅ Materials retrieved successfully")

        except Exception as e:
            state["error"] = f"Material retrieval error: {str(e)}"
            logger.error(f"❌ Material retrieval error: {str(e)}", exc_info=True)

        return state

    async def generate_content(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate lesson plan content and PPT outline"""
        state["status"] = "generating_content"
        logger.info("")
        logger.info("✍️  Step 3: Generating Content")
        logger.info("-" * 60)

        try:
            intent_data = state.get("intent_data", {})
            materials = state.get("retrieved_materials", {})
            logger.info(f"Calling ContentGeneratorAgent for: {intent_data.get('theme', 'Unknown')}")

            # Extract text materials for content generation
            text_materials = [m["content"] for m in materials.get("text_materials", [])]

            content = await self.content_generator.generate_content(
                intent_data,
                retrieved_materials=text_materials
            )

            num_slides = len(content.get('ppt_outline', {}).get('slides', []))
            state["generated_content"] = content
            state["processing_step"] = f"Generated {num_slides} slides"
            logger.info(f"✅ Content generated: {num_slides} slides")

        except Exception as e:
            state["error"] = f"Content generation error: {str(e)}"
            logger.error(f"❌ Content generation error: {str(e)}", exc_info=True)

        return state

    def match_template(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Match PPT template based on intent"""
        state["status"] = "matching_template"
        logger.info("")
        logger.info("🎨 Step 4: Matching PPT Template")
        logger.info("-" * 60)

        try:
            intent_data = state.get("intent_data", {})
            logger.info(f"Calling TemplateMatcherAgent for: {intent_data.get('theme', 'Unknown')}")

            template_match = self.template_matcher.match_template(intent_data)
            template_name = template_match.get('recommended_template', {}).get('name', 'Unknown')

            state["template_selection"] = template_match
            state["processing_step"] = f"Matched template: {template_name}"
            logger.info(f"✅ Template matched: {template_name}")

        except Exception as e:
            state["error"] = f"Template matching error: {str(e)}"
            logger.error(f"❌ Template matching error: {str(e)}", exc_info=True)

        return state

    def layout_slides(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Layout slides with selected template"""
        state["status"] = "layouting_slides"
        logger.info("")
        logger.info("📐 Step 5: Laying Out Slides")
        logger.info("-" * 60)

        try:
            content = state.get("generated_content", {})
            template_selection = state.get("template_selection", {})

            template_id = template_selection.get("recommended_template", {}).get("id", "default_formal")
            slides = content.get("ppt_outline", {}).get("slides", [])
            logger.info(f"Laying out {len(slides)} slides with template: {template_id}")

            # Layout each slide with template
            for i, slide in enumerate(slides):
                try:
                    slide_template = self.template_matcher.generate_slide_template(
                        template_id,
                        slide.get("slide_type", "content"),
                        slide
                    )
                    slide["layout"] = slide_template.get("layout")
                    slide["style"] = slide_template.get("style")
                    logger.debug(f"Slide {i+1}: Laid out successfully")
                except Exception as e:
                    logger.warning(f"Slide {i+1}: Failed to layout - {str(e)}")

            state["layouted_slides"] = slides
            state["processing_step"] = f"Laid out {len(slides)} slides"
            logger.info(f"✅ All {len(slides)} slides laid out successfully")

        except Exception as e:
            state["error"] = f"Slide layout error: {str(e)}"
            logger.error(f"❌ Slide layout error: {str(e)}", exc_info=True)

        return state

    async def export_output(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Export lesson plan and PPT"""
        state["status"] = "exporting"
        logger.info("")
        logger.info("💾 Step 6: Exporting Output")
        logger.info("-" * 60)

        try:
            lesson_data = state.get("generated_content", {})
            ppt_data = state.get("generated_content", {})
            template_selection = state.get("template_selection", {})
            template_id = template_selection.get("recommended_template", {}).get("id", "default_formal")

            intent_data = state.get("intent_data", {})
            lesson_title = intent_data.get("theme", "Lesson Plan")

            logger.info(f"Calling ExportManagerAgent for: {lesson_title}")

            # Export full lesson
            export_result = await self.export_manager.export_full_lesson(
                lesson_data,
                ppt_data,
                template_id,
                lesson_title
            )

            state["export_result"] = export_result
            state["processing_step"] = "Export completed"
            state["status"] = "completed"
            logger.info("✅ Export completed successfully")
            logger.info("")
            logger.info("=" * 60)
            logger.info("✅ Teaching Workflow Completed Successfully!")
            logger.info("=" * 60)

        except Exception as e:
            state["error"] = f"Export error: {str(e)}"
            logger.error(f"❌ Export error: {str(e)}", exc_info=True)

        return state

    async def run(self, user_input: str, uploaded_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the complete teaching workflow

        Args:
            user_input: User's teaching requirement
            uploaded_files: Optional list of uploaded file paths

        Returns:
            Final state with all generated outputs
        """
        initial_state = {
            "user_input": user_input,
            "status": "initializing",
            "error": None,
            "processing_step": "",
            "intent_data": {},
            "retrieved_materials": {},
            "generated_content": {},
            "template_selection": {},
            "layouted_slides": [],
            "export_result": {},
            "uploaded_files": uploaded_files or []
        }

        try:
            logger.info("")
            logger.info("🚀 Starting Teaching Workflow...")

            # Run through workflow nodes
            state = self.process_input(initial_state)
            if state.get("error"):
                logger.error(f"Workflow stopped at input_processing: {state.get('error')}")
                return state

            state = await self.parse_intent(state)
            if state.get("error"):
                logger.error(f"Workflow stopped at parse_intent: {state.get('error')}")
                return state

            state = await self.retrieve_materials(state)
            if state.get("error"):
                logger.error(f"Workflow stopped at retrieve_materials: {state.get('error')}")
                return state

            state = await self.generate_content(state)
            if state.get("error"):
                logger.error(f"Workflow stopped at generate_content: {state.get('error')}")
                return state

            state = self.match_template(state)
            if state.get("error"):
                logger.error(f"Workflow stopped at match_template: {state.get('error')}")
                return state

            state = self.layout_slides(state)
            if state.get("error"):
                logger.error(f"Workflow stopped at layout_slides: {state.get('error')}")
                return state

            state = await self.export_output(state)
            if state.get("error"):
                logger.error(f"Workflow stopped at export_output: {state.get('error')}")
                return state

            return state

        except Exception as e:
            import traceback
            logger.error(f"🔥 Critical error in workflow: {str(e)}")
            logger.error(traceback.format_exc())
            initial_state["error"] = f"Workflow execution error: {str(e)}"
            initial_state["status"] = "failed"
            return initial_state


# Example usage for testing
async def test_teaching_workflow():
    """Test the teaching workflow"""
    workflow = TeachingWorkflow()

    user_input = """
    I need to create a 50-minute lesson about the human circulatory system 
    for 10th grade biology students. The students should understand how blood 
    circulates through the body, learn about different types of blood vessels,
    and understand the function of the heart. I want an engaging, interactive
    lesson with some visual elements.
    """

    result = await workflow.run(user_input)

    print("Workflow Execution Result:")
    print(f"Status: {result['status']}")
    print(f"Error: {result['error']}")
    print(f"Processing Step: {result['processing_step']}")

    if result.get("export_result"):
        print("\nExport Results:")
        print(json.dumps(result["export_result"], indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    asyncio.run(test_teaching_workflow())
