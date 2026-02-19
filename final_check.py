#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终验证脚本 - 确保系统完全正常运行
"""

import sys
import os
import asyncio
from pathlib import Path

def print_section(title):
    print("\n" + "=" * 70)
    print(f"✅ {title}")
    print("=" * 70)

def check_files():
    """检查关键文件是否存在"""
    print_section("检查关键文件")
    
    required_files = [
        "main/app.py",
        "main/teaching_workflow.py",
        "main/templates/teaching.html",
        "main/teaching_agents/intent_parser_agent.py",
        "main/teaching_agents/multimodal_retriever_agent.py",
        "main/teaching_agents/content_generator_agent.py",
        "main/teaching_agents/template_matcher_agent.py",
        "main/teaching_agents/export_manager_agent.py",
        "config.yaml",
        "requirements.txt"
    ]
    
    missing = []
    for f in required_files:
        if not os.path.exists(f):
            missing.append(f)
            print(f"  ❌ {f}")
        else:
            print(f"  ✅ {f}")
    
    return len(missing) == 0

def check_imports():
    """检查模块导入"""
    print_section("检查模块导入")
    
    modules = [
        ("FastAPI", "fastapi"),
        ("Uvicorn", "uvicorn"),
        ("LangGraph", "langgraph"),
        ("LangChain", "langchain"),
        ("python-pptx", "pptx"),
        ("python-docx", "docx"),
        ("Pydantic", "pydantic"),
    ]
    
    failed = []
    for name, module in modules:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            failed.append(name)
    
    return len(failed) == 0

async def check_workflow():
    """检查工作流执行"""
    print_section("检查工作流执行")
    
    try:
        from main.teaching_workflow import TeachingWorkflow
        
        print("  🔄 正在初始化工作流...")
        workflow = TeachingWorkflow()
        print("  ✅ 工作流初始化成功")
        
        user_input = """
教学主题：光合作用
学生年级：高中
学科领域：生物
课程时长：45分钟
学习目标：学生应该理解光合作用的基本过程和意义
教学方法：讲授法
PPT风格：formal
        """.strip()
        
        print("  🔄 运行工作流...")
        result = await workflow.run(user_input)
        
        if result.get('status') == 'completed':
            print(f"  ✅ 工作流执行成功")
            print(f"     - 生成了 {len(result.get('export_result', {}).get('exports', {}).get('lesson_plan', {}).get('files', {}))} 个文件")
            return True
        else:
            print(f"  ❌ 工作流执行失败: {result.get('error')}")
            return False
    
    except Exception as e:
        print(f"  ❌ 工作流测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_output_files():
    """检查生成的输出文件"""
    print_section("检查生成的输出文件")
    
    output_dirs = [
        ("generated_lessons/docx", "Word文档"),
        ("generated_lessons/pptx", "PowerPoint演示"),
        ("generated_lessons/json", "JSON数据"),
        ("generated_lessons/markdown", "Markdown文档"),
    ]
    
    all_good = True
    for dir_path, desc in output_dirs:
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            print(f"  ✅ {desc} ({len(files)} 个文件)")
            if files and len(files) <= 3:
                for f in files[:3]:
                    print(f"     - {f}")
        else:
            print(f"  ⚠️  {desc} (目录不存在)")
            all_good = False
    
    return all_good

def check_frontend():
    """检查前端配置"""
    print_section("检查前端配置")
    
    try:
        with open("main/templates/teaching.html", "r", encoding="utf-8") as f:
            content = f.read()
        
        checks = [
            ("教学系统标题", "智能教案与PPT生成系统" in content),
            ("生成按钮", "generateLesson()" in content),
            ("表单输入", "teaching-theme" in content),
            ("API调用", "/send_message" in content),
            ("兽医模块移除", "兽医问诊" not in content),
            ("动物医院移除", "动物医院" not in content),
        ]
        
        all_good = True
        for name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {name}")
            if not passed:
                all_good = False
        
        return all_good
    
    except Exception as e:
        print(f"  ❌ 前端检查失败: {e}")
        return False

def check_api():
    """检查API端点"""
    print_section("检查API端���")
    
    try:
        with open("main/app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        checks = [
            ("send_message端点", "@app.post(\"/send_message\")" in content),
            ("详细日志", "print(\"📨 New Message Received\")" in content),
            ("错误处理", "except Exception as e:" in content),
            ("JSON响应", "JSONResponse" in content),
        ]
        
        all_good = True
        for name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {name}")
            if not passed:
                all_good = False
        
        return all_good
    
    except Exception as e:
        print(f"  ❌ API检查失败: {e}")
        return False

async def main():
    """主要验证函数"""
    print("\n" + "=" * 70)
    print("🔍 Veta 智能教案与PPT生成系统 - 最终验证")
    print("=" * 70)
    
    results = {
        "文件检查": check_files(),
        "模块导入": check_imports(),
        "前端配置": check_frontend(),
        "API检查": check_api(),
        "输出文件": check_output_files(),
        "工作流测试": await check_workflow(),
    }
    
    # 总结结果
    print("\n" + "=" * 70)
    print("📊 最终验证结果")
    print("=" * 70)
    
    all_passed = True
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status}: {name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ 所有检查通过！系统已准备好运行")
        print("\n快速开始:")
        print("  1. 运行: ./run.sh")
        print("  2. 打开: http://localhost:3367")
        print("  3. 输入教学信息并点击'生成教案与PPT'")
        print("=" * 70)
        return 0
    else:
        print("❌ 有些检查失败，请检查上面的错误信息")
        print("=" * 70)
        return 1

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

