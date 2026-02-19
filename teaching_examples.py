"""
Example usage and testing script for the Teaching Workflow system
演示和测试教学工作流系统的脚本
"""

import asyncio
import json
from main.teaching_workflow import TeachingWorkflow
from main.teaching_agents.intent_parser_agent import IntentParserAgent
from main.teaching_agents.multimodal_retriever_agent import MultimodalRetrieverAgent
from main.teaching_agents.content_generator_agent import ContentGeneratorAgent
from main.teaching_agents.template_matcher_agent import TemplateMatcherAgent
from main.teaching_agents.export_manager_agent import ExportManagerAgent


async def example_1_full_workflow():
    """Example 1: Run complete teaching workflow"""
    print("\n" + "="*60)
    print("示例1: 运行完整教学工作流")
    print("="*60)

    workflow = TeachingWorkflow()

    user_input = """
    我需要为高中生物班（高一）设计一节关于人体循环系统的课程。
    课程时长为50分钟。学生应该能够：
    1. 理解心脏的基本结构和功能
    2. 掌握血液循环的主要过程
    3. 区分动脉、静脉和毛细血管
    
    我希望课程采用互动式教学方法，包含一些图表和视觉元素。
    """

    print(f"\n输入内容:\n{user_input}")
    print("\n正在处理...")

    result = await workflow.run(user_input)

    print(f"\n✅ 工作流状态: {result['status']}")
    print(f"处理步骤: {result['processing_step']}")

    if result.get('export_result'):
        print("\n📁 生成的文件:")
        files = result['export_result'].get('files', {})
        if 'docx' in files:
            print(f"  - Word教案: {files['docx']['path']}")
        if 'ppt' in files:
            print(f"  - PPT演示: {files['ppt']['path']}")

    if result.get('error'):
        print(f"\n❌ 错误: {result['error']}")


async def example_2_intent_parsing():
    """Example 2: Test intent parsing"""
    print("\n" + "="*60)
    print("示例2: 教学意图解析")
    print("="*60)

    agent = IntentParserAgent()

    test_inputs = [
        "我要教初中化学学生关于酸碱中和反应的知识，需要40分钟。",
        "高二数学：概率论基础，45分钟，需要教学目标明确且有练习题。"
    ]

    for test_input in test_inputs:
        print(f"\n输入: {test_input}")
        intent = await agent.parse_teaching_intent(test_input)
        print("解析结果:")
        print(json.dumps(intent, indent=2, ensure_ascii=False))
        print("-" * 40)


async def example_3_content_generation():
    """Example 3: Test content generation"""
    print("\n" + "="*60)
    print("示例3: 内容生成")
    print("="*60)

    agent = ContentGeneratorAgent()

    intent_data = {
        "theme": "光合作用的基本过程",
        "objectives": [
            "理解光合作用的定义",
            "掌握光反应和暗反应",
            "学会光合作用方程式"
        ],
        "audience_level": "高中一年级",
        "subject_area": "生物",
        "duration_minutes": 45,
        "key_concepts": ["光反应", "暗反应", "叶绿体", "ATP"],
        "teaching_approach": "讲授与实验相结合"
    }

    print(f"教学主题: {intent_data['theme']}")
    print(f"学习目标: {', '.join(intent_data['objectives'])}")

    print("\n正在生成内容...")
    content = await agent.generate_content(intent_data)

    if 'lesson_plan' in content:
        print("\n✅ 生成的教案:")
        print(f"  标题: {content['lesson_plan'].get('title')}")
        print(f"  学习目标: {len(content['lesson_plan'].get('learning_objectives', []))}个")
        print(f"  主要内容章节: {len(content['lesson_plan'].get('main_content', []))}个")
        print(f"  活动数: {len(content['lesson_plan'].get('activities', []))}个")

    if 'ppt_outline' in content:
        slides = content['ppt_outline'].get('slides', [])
        print(f"\n✅ PPT大纲: {len(slides)}张幻灯片")
        for i, slide in enumerate(slides[:3], 1):
            print(f"  幻灯片{i}: {slide.get('title')} ({slide.get('slide_type')})")


def example_4_template_matching():
    """Example 4: Test template matching"""
    print("\n" + "="*60)
    print("示例4: PPT模板匹配")
    print("="*60)

    agent = TemplateMatcherAgent()

    test_cases = [
        {
            "theme": "小学数学：分数概念",
            "audience_level": "小学五年级",
            "subject_area": "数学",
            "teaching_approach": "互动游戏"
        },
        {
            "theme": "大学物理：量子力学基础",
            "audience_level": "大学二年级",
            "subject_area": "物理",
            "teaching_approach": "讲授"
        },
        {
            "theme": "高中语文：古诗词鉴赏",
            "audience_level": "高中",
            "subject_area": "语文",
            "teaching_approach": "讨论"
        }
    ]

    for intent_data in test_cases:
        print(f"\n课程: {intent_data['theme']}")
        print(f"年级: {intent_data['audience_level']}")

        matched = agent.match_template(intent_data)
        recommended = matched.get('recommended_template', {})

        print(f"✅ 推荐模板: {recommended.get('name')} (匹配度: {recommended.get('match_score', 0):.1%})")
        print(f"   风格: {recommended.get('style')}")

        alternatives = matched.get('alternative_templates', [])
        if alternatives:
            print(f"   其他选项:")
            for alt in alternatives[:2]:
                print(f"     - {alt.get('name')} ({alt.get('match_score', 0):.1%})")


async def example_5_export():
    """Example 5: Test export functionality"""
    print("\n" + "="*60)
    print("示例5: 文件导出")
    print("="*60)

    agent = ExportManagerAgent()

    # Sample data
    lesson_data = {
        "lesson_plan": {
            "title": "细胞的结构与功能",
            "learning_objectives": [
                "了解细胞的基本结构",
                "掌握各细胞器的功能",
                "理解细胞膜的作用"
            ],
            "duration_minutes": 45,
            "materials_needed": ["细胞模型", "显微镜", "视频"],
            "introduction": "细胞是生命的基本单位...",
            "main_content": [
                {
                    "section_title": "细胞膜",
                    "content": "细胞膜的结构...",
                    "key_points": ["选择透过性", "流动镶嵌模型"]
                }
            ],
            "activities": [
                {
                    "activity_name": "观察细胞",
                    "description": "使用显微镜观察细胞",
                    "duration_minutes": 15
                }
            ],
            "assessment": "课堂小测和讨论",
            "closure": "总结本课内容并预告下节课"
        },
        "discussion_questions": [
            "为什么细胞被称为生命的基本单位？",
            "不同的细胞器如何分工合作？"
        ],
        "homework": "完成课本第三章的练习题"
    }

    ppt_data = {
        "ppt_outline": {
            "title": "细胞的结构与功能",
            "slides": [
                {
                    "slide_number": 1,
                    "slide_type": "cover",
                    "title": "细胞的结构与功能"
                },
                {
                    "slide_number": 2,
                    "slide_type": "content",
                    "title": "细胞膜",
                    "bullet_points": ["选择透过性", "流动镶嵌模型"]
                }
            ]
        }
    }

    print("\n正在导出...")
    result = await agent.export_full_lesson(lesson_data, ppt_data, "formal", "细胞结构")

    print("\n✅ 导出完成:")
    print(f"  导出ID: {result.get('export_id')}")
    print(f"  时间: {result.get('export_timestamp')}")

    if 'exports' in result:
        exports = result['exports']
        if 'lesson_plan' in exports:
            print("\n  教案:")
            for fmt, info in exports['lesson_plan'].get('files', {}).items():
                print(f"    - {fmt.upper()}: {info.get('path')}")

        if 'ppt' in exports:
            print("\n  PPT:")
            ppt_info = exports['ppt'].get('file', {})
            print(f"    - {ppt_info.get('path')}")


async def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("🎓 智能教案与PPT生成系统 - 示例演示")
    print("="*60)

    print("\n选择要运行的示例:")
    print("1. 完整工作流演示")
    print("2. 教学意图解析示例")
    print("3. 内容生成示例")
    print("4. 模板匹配示例")
    print("5. 文件导出示例")
    print("6. 运行所有示例")

    try:
        choice = input("\n请输入选择 (1-6): ").strip()

        if choice == "1":
            await example_1_full_workflow()
        elif choice == "2":
            await example_2_intent_parsing()
        elif choice == "3":
            await example_3_content_generation()
        elif choice == "4":
            example_4_template_matching()
        elif choice == "5":
            await example_5_export()
        elif choice == "6":
            await example_2_intent_parsing()
            await example_3_content_generation()
            example_4_template_matching()
            await example_5_export()
            await example_1_full_workflow()
        else:
            print("无效选择")
    except KeyboardInterrupt:
        print("\n\n已取消")


if __name__ == "__main__":
    asyncio.run(main())
