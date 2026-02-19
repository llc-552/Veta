#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试API调用的脚本"""

import asyncio
import json
from httpx import AsyncClient
from main.app import app

async def test_api():
    """Test the API endpoint"""
    print("=" * 70)
    print("🧪 Testing /send_message API Endpoint")
    print("=" * 70)

    # Create an async test client
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Prepare request data
        request_data = {
            "message": """
教学主题：人体循环系统
学生年级：初中
学科领域：生物
课程时长：45分钟
学习目标：学生应该理解血液循环的基本原理
教学方法：讲授法
PPT风格：formal
            """,
            "mode": "teaching",
            "user_id": "test_user_123",
            "task_id": "test_task_123"
        }

        print("\n📤 Sending POST request to /send_message...")
        print(f"Request data: {json.dumps({'mode': request_data['mode'], 'user_id': request_data['user_id']}, ensure_ascii=False)}")

        try:
            response = await client.post("/send_message", json=request_data)

            print(f"\n📥 Response Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print("\n✅ API Response:")
                print(f"  Status: {data.get('status')}")
                print(f"  Response Message: {data.get('response', '')[:100]}...")
                print(f"  Processing Step: {data.get('processing_step')}")
                print(f"  Error: {data.get('error')}")

                if data.get('export_result'):
                    print("\n📊 Export Result Available:")
                    print(f"  {json.dumps(data['export_result'], ensure_ascii=False, indent=2)[:500]}...")

                return data.get('status') == 'completed'
            else:
                print(f"❌ Error: {response.text}")
                return False

        except Exception as e:
            import traceback
            print(f"\n❌ Request error: {e}")
            print(traceback.format_exc())
            return False

async def main():
    """Main function"""
    success = await test_api()

    print("\n" + "=" * 70)
    if success:
        print("✅ API test passed!")
    else:
        print("❌ API test failed")
    print("=" * 70)

    return 0 if success else 1

if __name__ == '__main__':
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

