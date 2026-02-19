"""Template Matcher Agent - Matches PPT templates by course type and generates slide layouts"""

from typing import Dict, Any, List, Optional
import json
import os

class TemplateMatcherAgent:
    """Agent for matching and managing PPT templates based on course characteristics"""

    def __init__(self, templates_folder: str = "./templates/ppt_templates"):
        """
        Initialize the Template Matcher Agent

        Args:
            templates_folder: Path to folder containing PPT templates
        """
        self.templates_folder = templates_folder
        self.templates = self._load_templates()

        # Define template categories and their characteristics
        self.template_categories = {
            "formal": {
                "description": "Professional and formal style suitable for academic institutions",
                "colors": ["dark_blue", "gray", "white"],
                "fonts": ["Times New Roman", "Calibri"],
                "suitable_for": ["University", "Research", "Technical", "Science"],
                "keywords": ["professional", "academic", "formal", "research"]
            },
            "colorful": {
                "description": "Vibrant and engaging style for elementary and middle school",
                "colors": ["bright_colors", "gradient", "rainbow"],
                "fonts": ["Comic Sans", "Arial", "Verdana"],
                "suitable_for": ["Elementary", "Middle School", "Language", "Arts"],
                "keywords": ["colorful", "engaging", "fun", "interactive", "young"]
            },
            "minimalist": {
                "description": "Clean and simple design with focus on content",
                "colors": ["white", "black", "single_accent"],
                "fonts": ["Helvetica", "Arial", "Sans-serif"],
                "suitable_for": ["High School", "Business", "Science", "Math"],
                "keywords": ["simple", "clean", "modern", "minimalist"]
            },
            "creative": {
                "description": "Creative and artistic style for humanities and arts",
                "colors": ["warm_colors", "pastel", "artistic"],
                "fonts": ["Creative fonts", "Handwriting"],
                "suitable_for": ["Literature", "History", "Art", "Music"],
                "keywords": ["creative", "artistic", "visual", "humanities"]
            }
        }

    def _load_templates(self) -> Dict[str, Any]:
        """
        Load available PPT templates from folder

        Returns:
            Dictionary of available templates
        """
        templates = {
            "default_formal": {
                "name": "Professional Academic",
                "style": "formal",
                "description": "Clean professional template for academic content",
                "color_scheme": "dark_blue_gray",
                "slide_types": ["cover", "section", "content", "activity", "summary"],
                "template_file": None  # Will be loaded from file if exists
            },
            "bright_elementary": {
                "name": "Colorful Learning",
                "style": "colorful",
                "description": "Bright and engaging template for young learners",
                "color_scheme": "rainbow",
                "slide_types": ["cover", "section", "content", "activity", "summary"]
            },
            "minimal_modern": {
                "name": "Minimal Modern",
                "style": "minimalist",
                "description": "Modern minimalist design focusing on content",
                "color_scheme": "black_white",
                "slide_types": ["cover", "section", "content", "activity", "summary"]
            },
            "artistic_creative": {
                "name": "Creative Canvas",
                "style": "creative",
                "description": "Artistic template for creative subjects",
                "color_scheme": "warm_colors",
                "slide_types": ["cover", "section", "content", "activity", "summary"]
            }
        }

        return templates

    def match_template(self, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match the best PPT template based on teaching intent

        Args:
            intent_data: Parsed teaching intent

        Returns:
            Dictionary containing matched template and configuration
        """
        try:
            # Score each template based on intent
            scores = {}

            for template_id, template in self.templates.items():
                score = self._score_template(template, intent_data)
                scores[template_id] = score

            # Get top 3 templates
            sorted_templates = sorted(scores.items(), key=lambda x: x[1], reverse=True)

            recommended_template_id = sorted_templates[0][0]
            recommended_template = self.templates[recommended_template_id]

            return {
                "recommended_template": {
                    "id": recommended_template_id,
                    **recommended_template,
                    "match_score": sorted_templates[0][1]
                },
                "alternative_templates": [
                    {
                        "id": tid,
                        **self.templates[tid],
                        "match_score": score
                    }
                    for tid, score in sorted_templates[1:3]
                ],
                "customization_suggestions": self._get_customization_suggestions(
                    recommended_template,
                    intent_data
                )
            }

        except Exception as e:
            # Return default template on error
            return {
                "recommended_template": self.templates["default_formal"],
                "alternative_templates": list(self.templates.values())[1:3],
                "error": f"Template matching error: {str(e)}"
            }

    def _score_template(self, template: Dict[str, Any], intent_data: Dict[str, Any]) -> float:
        """
        Score how well a template matches the intent

        Args:
            template: Template to score
            intent_data: Teaching intent data

        Returns:
            Float score between 0 and 1
        """
        score = 0.0

        # Score based on subject area
        subject_area = intent_data.get('subject_area', '').lower()
        audience_level = intent_data.get('audience_level', '').lower()

        template_style = template.get('style', 'formal')
        category = self.template_categories.get(template_style, {})
        suitable_subjects = category.get('suitable_for', [])

        for subject in suitable_subjects:
            if subject.lower() in subject_area:
                score += 0.3
                break
        else:
            score += 0.1  # Base score if not explicitly suitable

        # Score based on audience level
        if 'Elementary' in [s for s in suitable_subjects]:
            if 'elementary' in audience_level or 'primary' in audience_level:
                score += 0.3
        elif 'Middle School' in suitable_subjects:
            if 'middle' in audience_level or 'junior' in audience_level:
                score += 0.3
        elif 'High School' in suitable_subjects or 'University' in suitable_subjects:
            if 'high' in audience_level or 'secondary' in audience_level or 'university' in audience_level:
                score += 0.3

        # Score based on teaching approach
        teaching_approach = intent_data.get('teaching_approach', '').lower()
        if 'interactive' in teaching_approach or 'hands-on' in teaching_approach:
            if template_style in ['colorful', 'creative']:
                score += 0.2
        elif 'lecture' in teaching_approach:
            if template_style in ['formal', 'minimalist']:
                score += 0.2

        # Score based on theme keywords
        theme = intent_data.get('theme', '').lower()
        for keyword in category.get('keywords', []):
            if keyword in theme:
                score += 0.1

        return min(score, 1.0)  # Cap at 1.0

    def _get_customization_suggestions(
        self,
        template: Dict[str, Any],
        intent_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate customization suggestions for the template

        Args:
            template: Selected template
            intent_data: Teaching intent

        Returns:
            Dictionary of customization suggestions
        """
        suggestions = {
            "title_style": "large_bold",
            "color_accents": [],
            "font_recommendations": [],
            "layout_suggestions": [],
            "visual_elements": []
        }

        # Suggest colors based on subject
        subject_area = intent_data.get('subject_area', '').lower()

        color_suggestions = {
            "math": ["blue", "purple"],
            "science": ["green", "blue"],
            "history": ["brown", "gold"],
            "language": ["blue", "red"],
            "art": ["colorful", "pastel"],
            "music": ["purple", "pink"],
            "literature": ["brown", "burgundy"]
        }

        for subject, colors in color_suggestions.items():
            if subject in subject_area:
                suggestions["color_accents"] = colors
                break

        # Suggest fonts based on audience
        audience_level = intent_data.get('audience_level', '').lower()
        if 'elementary' in audience_level:
            suggestions["font_recommendations"] = ["Arial", "Comic Sans", "Verdana"]
        elif 'high' in audience_level or 'university' in audience_level:
            suggestions["font_recommendations"] = ["Times New Roman", "Calibri", "Helvetica"]
        else:
            suggestions["font_recommendations"] = ["Arial", "Calibri"]

        # Suggest visual elements
        suggestions["visual_elements"] = [
            "add_relevant_diagrams",
            "include_charts_for_data",
            "use_icons_for_concepts",
            "add_images_between_sections"
        ]

        # Layout suggestions
        suggestions["layout_suggestions"] = [
            "use_clear_hierarchy",
            "max_5_bullet_points_per_slide",
            "include_speaker_notes",
            "add_interactive_elements"
        ]

        return suggestions

    def generate_slide_template(
        self,
        template_id: str,
        slide_type: str,
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a specific slide template with content

        Args:
            template_id: ID of the selected template
            slide_type: Type of slide (cover, section, content, activity, summary)
            content: Content to populate the slide

        Returns:
            Dictionary containing slide template
        """
        try:
            template = self.templates.get(template_id, self.templates["default_formal"])

            slide_template = {
                "slide_type": slide_type,
                "template_id": template_id,
                "title": content.get("title", ""),
                "subtitle": content.get("subtitle", ""),
                "body_text": content.get("body_text", ""),
                "bullet_points": content.get("bullet_points", []),
                "speaker_notes": content.get("speaker_notes", ""),
                "image_placeholders": content.get("image_placeholders", []),
                "layout": self._get_slide_layout(template_id, slide_type),
                "style": self._get_slide_style(template_id)
            }

            return slide_template

        except Exception as e:
            return {
                "error": f"Slide template generation error: {str(e)}"
            }

    def _get_slide_layout(self, template_id: str, slide_type: str) -> Dict[str, Any]:
        """Get the layout configuration for a specific slide type"""
        layouts = {
            "cover": {
                "title_position": "center",
                "title_size": "large",
                "subtitle_position": "lower",
                "image_position": "background"
            },
            "section": {
                "title_position": "center",
                "title_size": "very_large",
                "image_position": "right"
            },
            "content": {
                "title_position": "top_left",
                "title_size": "medium",
                "content_position": "main",
                "image_position": "right"
            },
            "activity": {
                "title_position": "top",
                "title_size": "medium",
                "content_position": "main",
                "image_position": "left"
            },
            "summary": {
                "title_position": "top",
                "title_size": "large",
                "content_position": "main",
                "image_position": "background_light"
            }
        }

        return layouts.get(slide_type, layouts["content"])

    def _get_slide_style(self, template_id: str) -> Dict[str, Any]:
        """Get the style configuration for a template"""
        template = self.templates.get(template_id, {})

        style_config = {
            "color_scheme": template.get("color_scheme", "default"),
            "font_family": "Arial, sans-serif",
            "background_color": "#ffffff",
            "text_color": "#000000",
            "accent_color": "#0066cc"
        }

        return style_config


# Example usage for testing
def test_template_matcher():
    """Test the Template Matcher Agent"""
    agent = TemplateMatcherAgent()

    intent_data = {
        "theme": "The Human Circulatory System",
        "objectives": ["Understand the heart structure"],
        "audience_level": "10th Grade High School",
        "subject_area": "Biology Science",
        "duration_minutes": 50,
        "key_concepts": ["Heart", "Blood", "Circulation"],
        "teaching_approach": "Interactive Discussion"
    }

    matched = agent.match_template(intent_data)
    print("Matched Template:")
    print(json.dumps(matched, indent=2, ensure_ascii=False))

    # Test slide template generation
    slide = agent.generate_slide_template(
        matched["recommended_template"]["id"],
        "content",
        {
            "title": "Heart Structure",
            "body_text": "The heart is a muscular organ...",
            "bullet_points": ["Left and right chambers", "Pumps blood throughout body"],
            "speaker_notes": "Explain the chambers of the heart..."
        }
    )
    print("\nGenerated Slide Template:")
    print(json.dumps(slide, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_template_matcher()
