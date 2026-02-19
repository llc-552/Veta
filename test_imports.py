#!/usr/bin/env python3
"""
测试脚本：验证所有必要的导入是否可用
Test script: Verify all necessary imports are available
"""

import sys
import traceback

def test_import(module_name, description=""):
    """测试单个模块的导入"""
    try:
        __import__(module_name)
        print(f"✅ {module_name} - {description}")
        return True
    except Exception as e:
        print(f"❌ {module_name} - {description}")
        print(f"   错误: {str(e)}")
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("🔍 测试项目依赖导入")
    print("=" * 60)
    print()

    # 标准库测试
    print("📦 标准库测试:")
    test_import("asyncio", "异步编程")
    test_import("json", "JSON处理")
    test_import("os", "操作系统接口")
    print()

    # FastAPI 相关
    print("🌐 FastAPI 相关:")
    test_import("fastapi", "FastAPI 框架")
    test_import("uvicorn", "Uvicorn 服务器")
    test_import("pydantic", "Pydantic 数据验证")
    print()

    # LangChain 相关
    print("🤖 LangChain 相关:")
    test_import("langchain", "LangChain 框架")
    test_import("langgraph", "LangGraph 工作流")
    test_import("langchain_openai", "OpenAI 集成")
    print()

    # RAG 相关
    print("🔎 RAG 相关:")
    test_import("sentence_transformers", "句子转换器")
    test_import("faiss", "FAISS 向量搜索")
    test_import("rank_bm25", "BM25 排序")
    print()

    # 文档处理
    print("📄 文档处理:")
    test_import("pptx", "python-pptx PPT处理")
    test_import("docx", "python-docx Word处理")
    test_import("pypdf", "PyPDF PDF处理")
    print()

    # 项目模块
    print("🎓 项目模块:")
    try:
        from main.config import get_openai_config
        print(f"✅ main.config - 配置模块")
    except Exception as e:
        print(f"❌ main.config - 配置模块")
        print(f"   错误: {str(e)}")

    try:
        from main.teaching_workflow import TeachingWorkflow
        print(f"✅ main.teaching_workflow - 教学工作流")
    except Exception as e:
        print(f"❌ main.teaching_workflow - 教学工作流")
        print(f"   错误: {str(e)}")

    try:
        from main.teaching_agents import (
            IntentParserAgent,
            MultimodalRetrieverAgent,
            ContentGeneratorAgent,
            TemplateMatcherAgent,
            ExportManagerAgent
        )
        print(f"✅ main.teaching_agents - 所有教学智能体")
    except Exception as e:
        print(f"❌ main.teaching_agents - 教学智能体")
        print(f"   错误: {str(e)}")

    print()
    print("=" * 60)
    print("✨ 导入测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()

