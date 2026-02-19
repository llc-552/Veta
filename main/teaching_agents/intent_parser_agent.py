"""Teaching Intent Parser Agent - Parses teaching theme, objectives, and audience level"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from main.config import get_openai_config
from typing import Dict, Any, Optional
import json

class IntentParserAgent:
    """Agent for parsing and understanding teaching intent from user input"""

    def __init__(self):
        """Initialize the Intent Parser Agent"""
        openai_config = get_openai_config()
        self.model = ChatOpenAI(
            openai_api_base=openai_config['api_base'],
            openai_api_key=openai_config['api_key'],
            model=openai_config['model'],
            temperature=0.5,
        )

        self.system_prompt = """You are an experienced educational curriculum designer and teaching expert.
Your task is to analyze the user's teaching requirements and extract the following structured information:

1. **Teaching Theme**: The main topic or subject to teach
2. **Teaching Objectives**: What students should be able to do/know after the lesson (3-5 learning outcomes)
3. **Audience Level**: Grade level or age group (e.g., Elementary/Middle/High School, Age 10-12)
4. **Subject Area**: Academic discipline (e.g., Math, Science, History, Literature, etc.)
5. **Duration**: Estimated teaching duration (e.g., 45 minutes, 2 hours)
6. **Key Concepts**: Main concepts to cover (3-5 core ideas)
7. **Teaching Approach**: Preferred methodology (e.g., Lecture, Discussion, Hands-on, Interactive)
8. **Prerequisites**: What students should already know
9. **Additional Context**: Any special requirements or constraints

When analyzing, be thorough and extract as much detail as possible from the user input.
If information is missing, make reasonable assumptions based on the context and ask clarifying questions if needed.

Always respond with valid JSON format with these exact keys:
{
    "theme": "string",
    "objectives": ["string", ...],
    "audience_level": "string",
    "subject_area": "string",
    "duration_minutes": number,
    "key_concepts": ["string", ...],
    "teaching_approach": "string",
    "prerequisites": ["string", ...],
    "special_requirements": "string",
    "confidence_score": number (0.0-1.0)
}"""

    async def parse_teaching_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Parse user input to extract teaching intent and requirements

        Args:
            user_input: User's teaching requirements description

        Returns:
            Dictionary containing parsed teaching intent
        """
        try:
            response = await self.model.ainvoke([
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Please analyze the following teaching requirement and extract structured information:\n\n{user_input}")
            ])

            # Parse the JSON response
            response_text = response.content

            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                intent_data = json.loads(json_match.group())
            else:
                intent_data = json.loads(response_text)

            return intent_data

        except json.JSONDecodeError as e:
            # If JSON parsing fails, return structured error response
            return {
                "theme": user_input[:50] if user_input else "Unknown",
                "objectives": ["Unable to parse objectives from input"],
                "audience_level": "Unspecified",
                "subject_area": "General",
                "duration_minutes": 45,
                "key_concepts": [],
                "teaching_approach": "Interactive",
                "prerequisites": [],
                "special_requirements": f"JSON parsing error: {str(e)}",
                "confidence_score": 0.3
            }
        except Exception as e:
            return {
                "theme": user_input[:50] if user_input else "Unknown",
                "objectives": [],
                "audience_level": "Unspecified",
                "subject_area": "General",
                "duration_minutes": 45,
                "key_concepts": [],
                "teaching_approach": "Interactive",
                "prerequisites": [],
                "special_requirements": f"Error during parsing: {str(e)}",
                "confidence_score": 0.0
            }

    def validate_intent(self, intent_data: Dict[str, Any]) -> bool:
        """
        Validate if parsed intent data has minimum required fields

        Args:
            intent_data: Parsed intent dictionary

        Returns:
            Boolean indicating if intent is valid
        """
        required_fields = ['theme', 'objectives', 'audience_level', 'subject_area']
        return all(field in intent_data and intent_data[field] for field in required_fields)


# Example usage function for testing
async def test_intent_parser():
    """Test the Intent Parser Agent"""
    agent = IntentParserAgent()

    test_input = """
    I need to teach 10th grade biology students about the human circulatory system.
    The class is 50 minutes long. Students should understand how blood flows through the body,
    the function of the heart, and the difference between arteries and veins.
    This is a first introduction to the topic, so I need it to be engaging and visual.
    """

    intent = await agent.parse_teaching_intent(test_input)
    print("Parsed Intent:")
    print(json.dumps(intent, indent=2, ensure_ascii=False))

    is_valid = agent.validate_intent(intent)
    print(f"\nIntent Valid: {is_valid}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_intent_parser())
