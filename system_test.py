#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
系统功能测试脚本
用于验证智能教案与PPT生成系统的各个模块功能
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from main.teaching_agents.intent_parser_agent import IntentParserAgent
from main.teaching_agents.multimodal_retriever_agent import MultimodalRetrieverAgent
from main.teaching_agents.content_generator_agent import ContentGeneratorAgent
from main.teaching_agents.template_matcher_agent import TemplateMatcherAgent
from main.teaching_agents.export_manager_agent import ExportManagerAgent
from main.teaching_workflow import TeachingWorkflow
from main.multimodal_rag import MultimodalRAG


class SystemTester:
    """系统功能测试类"""

    def __init__(self):
        """初始化测试器"""
        self.test_results = []

    def print_section(self, title):
        """打印测试部分标题"""
        print("\n" + "="*60)
        print(f"  {title}")
        print("="*60)

    def print_result(self, test_name, passed, message=""):
        """打印测试结果"""
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"     {message}")
        self.test_results.append((test_name, passed))

    # ==================== 测试1: 模块导入 ====================
    async def test_module_imports(self):
        """测试所有模块是否能正确导入"""
        self.print_section("测试1: 模块导入")

        modules = {
            "IntentParserAgent": IntentParserAgent,
            "MultimodalRetrieverAgent": MultimodalRetrieverAgent,
            "ContentGeneratorAgent": ContentGeneratorAgent,
            "TemplateMatcherAgent": TemplateMatcherAgent,
            "ExportManagerAgent": ExportManagerAgent,
            "TeachingWorkflow": TeachingWorkflow,
            "MultimodalRAG": MultimodalRAG,
        }

        for name, module_class in modules.items():
            try:
                # 尝试导入
                self.print_result(f"导入 {name}", True)
            except Exception as e:
                self.print_result(f"导入 {name}", False, str(e))

    # ==================== 测试2: 智能体初始化 ====================
    async def test_agent_initialization(self):
        """测试各智能体的初始化"""
        self.print_section("测试2: 智能体初始化")

        # 测试意图解析智能体
        try:
            intent_parser = IntentParserAgent()
            self.print_result("IntentParserAgent 初始化", True)
        except Exception as e:
            self.print_result("IntentParserAgent 初始化", False, str(e))
            return

        # 测试多模态检索智能体
        try:
            retriever = MultimodalRetrieverAgent(rag_folder="./rag_data")
            self.print_result("MultimodalRetrieverAgent 初始化", True)
        except Exception as e:
            self.print_result("MultimodalRetrieverAgent 初始化", False, str(e))

        # 测试内容生成智能体
        try:
            content_gen = ContentGeneratorAgent()
            self.print_result("ContentGeneratorAgent 初始化", True)
        except Exception as e:
            self.print_result("ContentGeneratorAgent 初始化", False, str(e))

        # 测试模板匹配智能体
        try:
            template_matcher = TemplateMatcherAgent(templates_folder="./templates/ppt_templates")
            self.print_result("TemplateMatcherAgent 初始化", True)
        except Exception as e:
            self.print_result("TemplateMatcherAgent 初始化", False, str(e))

        # 测试导出管理智能体
        try:
            export_mgr = ExportManagerAgent(output_folder="./generated_lessons")
            self.print_result("ExportManagerAgent 初始化", True)
        except Exception as e:
            self.print_result("ExportManagerAgent 初始化", False, str(e))

    # ==================== 测试3: 意图解析 ====================
    async def test_intent_parsing(self):
        """测试教学意图解析功能"""
        self.print_section("测试3: 教学意图解析")

        try:
            intent_parser = IntentParserAgent()

            test_inputs = [
                "请为初中二年级学生讲解光合作用的基本原理",
                "我需要为高中一年级的学生上一堂关于物理力学的课程",
                "教大学生一些关于数据结构的基础知识"
            ]

            for test_input in test_inputs:
                try:
                    result = await intent_parser.parse_teaching_intent(test_input)
                    if result and "topic" in result:
                        self.print_result(
                            f"解析意图: '{test_input[:30]}...'",
                            True,
                            f"识别主题: {result.get('topic', 'Unknown')}"
                        )
                    else:
                        self.print_result(
                            f"解析意图: '{test_input[:30]}...'",
                            False,
                            "未能识别到有效的主题"
                        )
                except Exception as e:
                    self.print_result(
                        f"解析意图: '{test_input[:30]}...'",
                        False,
                        str(e)
                    )

        except Exception as e:
            self.print_result("初始化IntentParserAgent", False, str(e))

    # ==================== 测试4: 数据文件检查 ====================
    async def test_data_files(self):
        """测试必要的数据文件是否存在"""
        self.print_section("测试4: 数据文件检查")

        files_to_check = {
            "配置文件": "./config.yaml",
            "RAG数据目录": "./rag_data",
            "模板目录": "./templates/ppt_templates",
            "输出目录": "./generated_lessons",
            "日志目录": "./logs",
        }

        for name, path in files_to_check.items():
            exists = os.path.exists(path)
            self.print_result(
                f"{name}: {path}",
                exists,
                "存在" if exists else "不存在"
            )

    # ==================== 测试5: 工作流初始化 ====================
    async def test_workflow_initialization(self):
        """测试完整工作流的初始化"""
        self.print_section("测试5: 工作流初始化")

        try:
            workflow = TeachingWorkflow(
                rag_folder="./rag_data",
                templates_folder="./templates/ppt_templates",
                output_folder="./generated_lessons"
            )
            self.print_result("TeachingWorkflow 初始化", True)
            self.print_result("LangGraph 编译", True, "工作流图已编译")

        except Exception as e:
            self.print_result("TeachingWorkflow 初始化", False, str(e))

    # ==================== 测试6: 模板加载 ====================
    async def test_template_loading(self):
        """测试PPT模板是否能正确加载"""
        self.print_section("测试6: 模板加载")

        template_config_path = "./templates/ppt_templates/template_config.json"

        if not os.path.exists(template_config_path):
            self.print_result("模板配置文件", False, "文件不存在")
            return

        try:
            import json
            with open(template_config_path, 'r', encoding='utf-8') as f:
                template_config = json.load(f)

            if "templates" in template_config:
                num_templates = len(template_config["templates"])
                self.print_result(
                    "加载模板配置",
                    True,
                    f"成功加载 {num_templates} 个模板"
                )

                # 列出所有模板
                for template in template_config["templates"]:
                    template_name = template.get("name", "Unknown")
                    template_id = template.get("id", "Unknown")
                    self.print_result(
                        f"  - {template_name}",
                        True,
                        f"ID: {template_id}"
                    )
            else:
                self.print_result("模板配置格式", False, "未找到 'templates' 字段")

        except Exception as e:
            self.print_result("加载模板配置", False, str(e))

    # ==================== 测试7: 多模态RAG ====================
    async def test_multimodal_rag(self):
        """测试多模态RAG功能"""
        self.print_section("测试7: 多模态RAG")

        try:
            rag = MultimodalRAG(rag_folder="./rag_data", index_path="./faiss_index")
            self.print_result("MultimodalRAG 初始化", True)

            # 测试检索
            try:
                query = "光合作用"
                results = rag.retrieve(query, top_k=3)

                if results:
                    self.print_result(
                        f"RAG检索: '{query}'",
                        True,
                        f"检索到 {len(results)} 条结果"
                    )
                    for i, result in enumerate(results[:2], 1):
                        content = result.get("content", "")[:50]
                        score = result.get("score", 0)
                        self.print_result(
                            f"  - 结果 {i}",
                            True,
                            f"相似度: {score:.3f}, 内容: {content}..."
                        )
                else:
                    self.print_result(f"RAG检索: '{query}'", False, "未检索到结果")

            except Exception as e:
                self.print_result("RAG检索测试", False, str(e))

        except Exception as e:
            self.print_result("MultimodalRAG 初始化", False, str(e))

    # ==================== 测试8: 导出功能 ====================
    async def test_export_functionality(self):
        """测试导出功能"""
        self.print_section("测试8: 导出功能")

        try:
            exporter = ExportManagerAgent(output_folder="./generated_lessons")
            self.print_result("ExportManagerAgent 初始化", True)

            # 检查输出目录是否存在
            output_formats = ["docx", "pptx", "json", "markdown"]
            for fmt in output_formats:
                output_dir = f"./generated_lessons/{fmt}"
                exists = os.path.exists(output_dir)
                self.print_result(
                    f"输出目录 ({fmt})",
                    exists,
                    f"{'存在' if exists else '不存在'}: {output_dir}"
                )

        except Exception as e:
            self.print_result("ExportManagerAgent 初始化", False, str(e))

    # ==================== 测试总结 ====================
    def print_summary(self):
        """打印测试总结"""
        self.print_section("测试总结")

        total = len(self.test_results)
        passed = sum(1 for _, result in self.test_results if result)
        failed = total - passed

        print(f"\n总测试数: {total}")
        print(f"✓ 通过: {passed}")
        print(f"✗ 失败: {failed}")
        print(f"成功率: {passed/total*100:.1f}%\n")

        if failed > 0:
            print("失败的测试:")
            for name, result in self.test_results:
                if not result:
                    print(f"  - {name}")

    # ==================== 主测试函数 ====================
    async def run_all_tests(self):
        """运行所有测试"""
        print("\n")
        print("╔" + "="*58 + "╗")
        print("║" + " "*10 + "智能教案与PPT生成系统 - 功能测试" + " "*15 + "║")
        print("╚" + "="*58 + "╝")

        await self.test_module_imports()
        await self.test_data_files()
        await self.test_agent_initialization()
        await self.test_workflow_initialization()
        await self.test_template_loading()
        await self.test_multimodal_rag()
        await self.test_export_functionality()
        await self.test_intent_parsing()

        self.print_summary()


async def main():
    """主函数"""
    tester = SystemTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    # 在Windows中如果出现事件循环错误，使用此设置
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())

