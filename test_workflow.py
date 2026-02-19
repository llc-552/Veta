#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""简单的工作流测试脚本"""

import asyncio
import sys
from main.teaching_workflow import TeachingWorkflow

async def main():
    print("=" * 60)
    print("🎓 Veta 智能教案与PPT生成系统 - 工作流测试")
    print("=" * 60)
    print()

    try:
        print("正在初始化 TeachingWorkflow...")
        workflow = TeachingWorkflow(
            rag_folder='./rag_data',
            templates_folder='./templates/ppt_templates',
            output_folder='./generated_lessons'
        )
        print("✅ TeachingWorkflow 初始化成功")
        print()

        # 简单的教学输入
        user_input = """
教学主题：人体循环系统
学生年级：初中
学科领域：生物
课程时长：45分钟
学习目标：学生应该理解血液循环系统的基本结构和功能
教学方法：讲授法
PPT风格：formal
        """.strip()

        print("运行教学工作流...")
        print("-" * 60)

        result = await workflow.run(user_input)

        print()
        print("=" * 60)
        print("📊 工作流执行结果")
        print("=" * 60)
        print(f"状态 (Status): {result.get('status', 'unknown')}")
        print(f"处理步骤 (Processing Step): {result.get('processing_step', 'N/A')}")

        if result.get('error'):
            print(f"❌ 错误信息: {result.get('error')}")
        else:
            print("✅ 无错误")

        if result.get('export_result'):
            print()
            print("导出结果:")
            for key, value in result['export_result'].items():
                print(f"  - {key}: {value}")

        print()
        print("=" * 60)

        if result.get('status') == 'completed':
            print("✅ 工作流执行成功！")
            sys.exit(0)
        else:
            print("⚠️  工作流未成功完成")
            sys.exit(1)

    except Exception as e:
        import traceback
        print()
        print("=" * 60)
        print(f"❌ 错误: {str(e)}")
        print("=" * 60)
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())

