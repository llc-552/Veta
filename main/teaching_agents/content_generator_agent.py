"""Content Generator Agent - Generates lesson plan content and PPT key points"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from main.config import get_openai_config
from typing import Dict, Any, List, Optional
import json

class ContentGeneratorAgent:
    """Agent for generating educational content including lesson plans and PPT key points"""

    def __init__(self):
        """Initialize the Content Generator Agent"""
        openai_config = get_openai_config()
        self.model = ChatOpenAI(
            openai_api_base=openai_config['api_base'],
            openai_api_key=openai_config['api_key'],
            model=openai_config['model'],
            temperature=0.7,
        )

        self.system_prompt = """You are an expert curriculum developer and educational content writer.
Your task is to generate comprehensive lesson plan content and PPT key points based on:
- Teaching intent and objectives
- Retrieved educational materials (text and images)
- Target audience characteristics
- Teaching approach preferences

Generate content following pedagogical best practices:
1. Start with clear learning objectives (measurable, specific)
2. Include introduction/hook to engage students
3. Structure content logically with main sections
4. Highlight key concepts and important facts
5. Include examples and real-world applications
6. Add discussion questions or thinking prompts
7. Plan interactive activities
8. Include assessment/practice exercises
9. Provide closure and summary

Output should be in valid JSON format with the following structure:
{
    "lesson_plan": {
        "title": "string",
        "learning_objectives": ["string", ...],
        "duration_minutes": number,
        "materials_needed": ["string", ...],
        "introduction": "string (2-3 paragraphs)",
        "main_content": [
            {
                "section_title": "string",
                "content": "string (detailed explanation)",
                "key_points": ["string", ...],
                "notes": "string (optional teacher notes)"
            },
            ...
        ],
        "activities": [
            {
                "activity_name": "string",
                "description": "string",
                "duration_minutes": number,
                "instructions": ["string", ...]
            },
            ...
        ],
        "assessment": "string (formative and summative assessment strategies)",
        "closure": "string (lesson wrap-up and connection to future learning)"
    },
    "ppt_outline": {
        "total_slides": number,
        "slides": [
            {
                "slide_number": number,
                "slide_type": "cover|section|content|activity|summary",
                "title": "string",
                "bullet_points": ["string", ...],
                "speaker_notes": "string",
                "suggested_images": ["image description for retrieval", ...]
            },
            ...
        ]
    },
    "discussion_questions": ["string", ...],
    "homework": "string (optional homework assignment)"
}"""

    async def generate_content(
        self,
        intent_data: Dict[str, Any],
        retrieved_materials: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate lesson plan content and PPT outline

        Args:
            intent_data: Parsed teaching intent from IntentParserAgent
            retrieved_materials: List of retrieved educational materials

        Returns:
            Dictionary containing lesson plan and PPT outline
        """
        try:
            # Prepare the prompt
            materials_text = ""
            if retrieved_materials:
                materials_text = f"\n\nRetrieved Educational Materials:\n" + "\n---\n".join(retrieved_materials)

            prompt_content = f"""Based on the following teaching requirements, generate comprehensive lesson plan content and PPT outline:

Teaching Theme: {intent_data.get('theme', 'Unknown')}
Learning Objectives: {', '.join(intent_data.get('objectives', []))}
Audience Level: {intent_data.get('audience_level', 'General')}
Subject Area: {intent_data.get('subject_area', 'General')}
Duration: {intent_data.get('duration_minutes', 45)} minutes
Key Concepts: {', '.join(intent_data.get('key_concepts', []))}
Teaching Approach: {intent_data.get('teaching_approach', 'Interactive')}
Prerequisites: {', '.join(intent_data.get('prerequisites', []))}
{materials_text}

Please generate detailed, pedagogically sound content that:
1. Aligns with stated learning objectives
2. Uses retrieved materials effectively
3. Is age-appropriate for the audience
4. Follows the preferred teaching approach
5. Includes interactive elements and assessments
6. Provides clear speaker notes for the instructor
"""

            response = await self.model.ainvoke([
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt_content)
            ])

            # Parse the JSON response
            response_text = response.content

            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                content_data = json.loads(json_match.group())
            else:
                content_data = json.loads(response_text)

            return content_data

        except json.JSONDecodeError as e:
            return {
                "lesson_plan": {
                    "title": intent_data.get('theme', 'Lesson Plan'),
                    "learning_objectives": intent_data.get('objectives', []),
                    "duration_minutes": intent_data.get('duration_minutes', 45),
                    "materials_needed": [],
                    "introduction": "Error generating introduction",
                    "main_content": [],
                    "activities": [],
                    "assessment": "Error generating assessment",
                    "closure": "Error generating closure"
                },
                "ppt_outline": {
                    "total_slides": 0,
                    "slides": []
                },
                "discussion_questions": [],
                "error": f"JSON parsing error: {str(e)}"
            }
        except Exception as e:
            return {
                "lesson_plan": {
                    "title": intent_data.get('theme', 'Lesson Plan'),
                    "learning_objectives": intent_data.get('objectives', []),
                    "duration_minutes": intent_data.get('duration_minutes', 45),
                    "materials_needed": [],
                    "introduction": f"Error: {str(e)}",
                    "main_content": [],
                    "activities": [],
                    "assessment": "",
                    "closure": ""
                },
                "ppt_outline": {
                    "total_slides": 0,
                    "slides": []
                },
                "discussion_questions": [],
                "error": f"Content generation error: {str(e)}"
            }

    async def refine_content(
        self,
        original_content: Dict[str, Any],
        refinement_request: str
    ) -> Dict[str, Any]:
        """
        Refine generated content based on user feedback

        Args:
            original_content: Previously generated content
            refinement_request: User's refinement request

        Returns:
            Refined content dictionary
        """
        try:
            refinement_prompt = f"""The following lesson plan and PPT outline was generated:

{json.dumps(original_content, indent=2, ensure_ascii=False)}

Please refine it based on this user request:
{refinement_request}

Return the refined content in the same JSON format, maintaining the overall structure but incorporating the requested changes."""

            response = await self.model.ainvoke([
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=refinement_prompt)
            ])

            response_text = response.content

            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                refined_data = json.loads(json_match.group())
            else:
                refined_data = json.loads(response_text)

            return refined_data

        except Exception as e:
            return {
                "lesson_plan": original_content.get('lesson_plan', {}),
                "ppt_outline": original_content.get('ppt_outline', {}),
                "error": f"Refinement error: {str(e)}"
            }


# Example usage for testing
async def test_content_generator():
    """Test the Content Generator Agent"""
    agent = ContentGeneratorAgent()

    intent_data = {
        "theme": "The Human Circulatory System",
        "objectives": [
            "Understand the structure and function of the heart",
            "Explain how blood circulates through the body",
            "Differentiate between arteries, veins, and capillaries"
        ],
        "audience_level": "10th Grade",
        "subject_area": "Biology",
        "duration_minutes": 50,
        "key_concepts": ["Heart", "Blood", "Arteries", "Veins", "Circulation"],
        "teaching_approach": "Interactive"
    }

    content = await agent.generate_content(intent_data)
    print("Generated Content:")
    print(json.dumps(content, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_content_generator())
