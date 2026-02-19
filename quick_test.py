#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""快速测试脚本 - 测试整个系统的各个部分"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_imports():
    """Test if all modules can be imported"""
    print("=" * 70)
    print("🔍 Testing Imports...")
    print("=" * 70)
    
    try:
        print("1. Importing teaching_workflow...")
        from main.teaching_workflow import TeachingWorkflow
        print("   ✅ teaching_workflow imported successfully")
    except Exception as e:
        print(f"   ❌ Failed to import teaching_workflow: {e}")
        return False
    
    try:
        print("2. Importing app...")
        from main.app import app, send_message
        print("   ✅ app imported successfully")
    except Exception as e:
        print(f"   ❌ Failed to import app: {e}")
        return False
    
    try:
        print("3. Importing all teaching agents...")
        from main.teaching_agents.intent_parser_agent import IntentParserAgent
        from main.teaching_agents.multimodal_retriever_agent import MultimodalRetrieverAgent
        from main.teaching_agents.content_generator_agent import ContentGeneratorAgent
        from main.teaching_agents.template_matcher_agent import TemplateMatcherAgent
        from main.teaching_agents.export_manager_agent import ExportManagerAgent
        print("   ✅ all teaching agents imported successfully")
    except Exception as e:
        print(f"   ❌ Failed to import teaching agents: {e}")
        return False
    
    print("\n✅ All imports successful!\n")
    return True

async def test_workflow():
    """Test the teaching workflow"""
    print("=" * 70)
    print("🚀 Testing Teaching Workflow...")
    print("=" * 70)
    
    try:
        from main.teaching_workflow import TeachingWorkflow
        
        workflow = TeachingWorkflow()
        print("✅ TeachingWorkflow initialized")
        
        user_input = """
教学主题：细胞的结构与功能
学生年级：高中
学科领域：生物
课程时长：45分钟
学习目标：学生应该理解细胞的基本结构和各部分的功能
教学方法：讲授法
PPT风格：formal
        """.strip()
        
        print("\n🔄 Running workflow...")
        result = await workflow.run(user_input)
        
        print(f"\n📊 Results:")
        print(f"  Status: {result.get('status')}")
        print(f"  Error: {result.get('error')}")
        print(f"  Processing Step: {result.get('processing_step')}")
        
        if result.get('export_result'):
            print(f"\n✅ Export Results:")
            exports = result['export_result'].get('exports', {})
            
            if exports.get('lesson_plan'):
                lp = exports['lesson_plan']
                files = lp.get('files', {})
                print(f"  Lesson Plan:")
                if files.get('docx'):
                    print(f"    - DOCX: {files['docx'].get('path')}")
                if files.get('json'):
                    print(f"    - JSON: {files['json'].get('path')}")
            
            if exports.get('ppt'):
                ppt = exports['ppt']
                if ppt.get('error'):
                    print(f"  PPT Error: {ppt['error']}")
                else:
                    print(f"  PPT: {ppt.get('file', {}).get('path')}")
        
        return result.get('status') == 'completed'
    
    except Exception as e:
        import traceback
        print(f"\n❌ Workflow error: {e}")
        print(traceback.format_exc())
        return False

async def main():
    """Main test function"""
    # Test imports
    if not await test_imports():
        return 1
    
    # Test workflow
    if await test_workflow():
        print("\n" + "=" * 70)
        print("✅ All tests passed!")
        print("=" * 70)
        return 0
    else:
        print("\n" + "=" * 70)
        print("❌ Some tests failed")
        print("=" * 70)
        return 1

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

