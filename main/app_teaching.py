from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import uuid
import json
from typing import Optional, Dict
from main.teaching_workflow import TeachingWorkflow  # 智能教案与PPT生成系统
from main.config import get_redis_config

# -------------------------------
# 初始化 FastAPI
# -------------------------------
app = FastAPI()

# 使用相对路径或从项目根目录开始的路径
import os
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(base_dir, "main", "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(base_dir, "main", "static")), name="static")

state_lock = asyncio.Lock()

# -------------------------------
# 全局状态管理
# -------------------------------
teaching_workflow_instances: Dict[str, TeachingWorkflow] = {}  # 存储教学工作流实例

# -------------------------------
# 启动事件
# -------------------------------
@app.on_event("startup")
async def startup_event():
    print("✅ 智能教案与PPT生成系统已准备就绪")

# -------------------------------
# 辅助函数
# -------------------------------
def get_or_create_teaching_workflow(user_id: Optional[str] = None, task_id: Optional[str] = None) -> TeachingWorkflow:
    """获取或创建 TeachingWorkflow 实例"""
    # 用户ID由用户输入，如果没有则使用默认值
    actual_user_id = user_id or "anonymous_user"

    # 任务ID随机生成（如果task_id存在则使用，否则生成新的）
    if task_id:
        actual_task_id = task_id
    else:
        actual_task_id = f"lesson_{uuid.uuid4().hex[:8]}"

    # 使用 user_id + task_id 作为实例的唯一键
    instance_key = f"{actual_user_id}:{actual_task_id}"

    # 实例化TeachingWorkflow
    if instance_key not in teaching_workflow_instances:
        teaching_workflow_instances[instance_key] = TeachingWorkflow(
            rag_folder="./rag_data",
            templates_folder="./templates/ppt_templates",
            output_folder="./generated_lessons"
        )
        print(f"✅ 创建新的 TeachingWorkflow 实例: user_id={actual_user_id}, task_id={actual_task_id}")

    return teaching_workflow_instances[instance_key]

# -------------------------------
# 请求模型
# -------------------------------
class MessageRequest(BaseModel):
    message: str
    mode: Optional[str] = "teaching"  # 教学模式
    user_id: Optional[str] = None  # 用户ID
    task_id: Optional[str] = None  # 任务ID
    rag_enabled: Optional[bool] = False  # RAG知识库开关

# -------------------------------
# 页面路由
# -------------------------------
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# -------------------------------
# 消息接口
# -------------------------------
@app.post("/send_message")
async def send_message(req: MessageRequest):
    """同步消息接口"""
    user_input = req.message
    user_id = req.user_id
    task_id = req.task_id

    async with state_lock:
        try:
            # 获取或创建 TeachingWorkflow 实例
            teaching_workflow = get_or_create_teaching_workflow(user_id, task_id)

            # 运行教学工作流
            result = await teaching_workflow.run(user_input)

            # 返回结果
            return {
                "response": f"教学材料已生成！状态: {result.get('status', 'unknown')}",
                "status": result.get("status"),
                "processing_step": result.get("processing_step"),
                "export_result": result.get("export_result", {}),
                "error": result.get("error"),
                "awaiting_input": False,
                "ended": result.get("status") == "completed"
            }
        except Exception as e:
            return JSONResponse(content={"error": f"Teaching workflow error: {str(e)}"}, status_code=500)

# -------------------------------
# 流式消息接口（SSE）
# -------------------------------
@app.post("/send_message_stream")
async def send_message_stream(req: MessageRequest):
    """使用 Server-Sent Events 进行流式输出"""
    user_input = req.message
    user_id = req.user_id
    task_id = req.task_id

    async def event_generator():
        """生成 SSE 事件流"""
        try:
            # 获取或创建 TeachingWorkflow 实例
            teaching_workflow = get_or_create_teaching_workflow(user_id, task_id)

            # 运行教学工作流
            result = await teaching_workflow.run(user_input)

            # 构造响应
            ai_response = f"""
## 教学材料生成完成

**处理状态**: {result.get('status', 'unknown')}

**处理步骤**: {result.get('processing_step', '无')}

**错误信息**: {result.get('error', '无')}

### 导出结果
"""

            export_result = result.get('export_result', {})
            if export_result:
                for key, value in export_result.items():
                    ai_response += f"\n- **{key}**: {value}"
            else:
                ai_response += "\n- 暂无导出结果"

            # 逐个字符发送响应
            for char in ai_response:
                yield f"data: {json.dumps({'type': 'token', 'content': char})}\n\n"
                await asyncio.sleep(0.001)  # 模拟流式延迟

            # 发送完成信号
            yield f"data: {json.dumps({'type': 'done', 'response': ai_response, 'awaiting_input': False, 'ended': True})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# -------------------------------
# 会话重置接口
# -------------------------------
@app.post("/reset")
async def reset(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        task_id = data.get("task_id")
    except Exception:
        user_id = None
        task_id = None

    async with state_lock:
        # 清除指定用户的 TeachingWorkflow 实例
        if user_id and task_id:
            instance_key = f"{user_id}:{task_id}"
            if instance_key in teaching_workflow_instances:
                del teaching_workflow_instances[instance_key]
                print(f"✅ TeachingWorkflow 会话已重置: {instance_key}")
        else:
            # 如果没有指定用户，清除所有实例
            teaching_workflow_instances.clear()
            print("✅ 所有 TeachingWorkflow 会话已重置")

    print(f"[系统]: 会话已重置")
    return {"status": "ok"}

