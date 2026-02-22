from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import UploadFile, File, Form
from pydantic import BaseModel
import asyncio
import uuid
import json
from typing import Optional, Dict, List
from main.teaching_workflow import TeachingWorkflow  # 智能教案与PPT生成系统

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
    print("=" * 50)
    print("🎓 智能教案与PPT生成系统 - 后端服务启动")
    print("=" * 50)
    print("✅ TeachingWorkflow 服务已准备就绪")
    print("📝 系统模式: 智能教案与PPT生成")
    print("🔗 API 地址: http://0.0.0.0:3367")
    print("=" * 50)

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
    return templates.TemplateResponse("teaching.html", {"request": request})

# -------------------------------
# 消息接口（同步）
# -------------------------------
@app.post("/send_message")
async def send_message(req: MessageRequest):
    """同步消息接口 - 返回完整的生成结果"""
    user_input = req.message
    user_id = req.user_id
    task_id = req.task_id

    print("")
    print("=" * 70)
    print("📨 New Message Received")
    print("=" * 70)
    print(f"User ID: {user_id}")
    print(f"Task ID: {task_id}")
    print(f"Mode: {req.mode}")
    print(f"Message preview: {user_input[:100]}...")
    print("=" * 70)

    try:
        # 获取或创建 TeachingWorkflow 实例
        print("📌 Step 1: Getting or creating TeachingWorkflow instance...")
        teaching_workflow = get_or_create_teaching_workflow(user_id, task_id)
        print("✅ TeachingWorkflow instance ready")

        # 运行教学工作流
        print("📌 Step 2: Running teaching workflow...")
        result = await teaching_workflow.run(user_input)
        print("✅ Workflow completed")
        print(f"Result status: {result.get('status')}")
        print(f"Result error: {result.get('error')}")

        print("📌 Step 3: Building response...")
        print("✅ Response built successfully")

        print("=" * 70)
        print("✅ Request processing completed")
        print("=" * 70)
        print("")

        return _build_response(result)
    except Exception as e:
        import traceback
        print(f"❌ Error in send_message: {str(e)}")
        print(traceback.format_exc())
        print("=" * 70)
        return JSONResponse(
            content={
                "error": f"Teaching workflow error: {str(e)}",
                "response": "❌ 发生错误",
                "status": "error",
                "processing_step": "工作流执行失败",
                "awaiting_input": False,
                "ended": False
            },
            status_code=500
        )

# -------------------------------
# 消息接口（流式）
# -------------------------------
@app.post("/send_message_stream")
async def send_message_stream(req: MessageRequest):
    """使用 Server-Sent Events 进行流式输出"""
    user_input = req.message
    user_id = req.user_id
    task_id = req.task_id

    # 先在async上下文中获取结果，然后在generator中使用
    teaching_workflow = get_or_create_teaching_workflow(user_id, task_id)

    try:
        # 在async上下文中运行工作流
        result = await teaching_workflow.run(user_input)
    except Exception as e:
        import traceback
        print(f"Error running workflow: {str(e)}")
        print(traceback.format_exc())
        result = {
            "status": "error",
            "error": str(e),
            "processing_step": "Workflow execution failed"
        }

    def event_generator():
        """生成 SSE 事件流"""
        try:

            ai_response = ""
            awaiting_input = False
            ended = False

            # 获取生成的内容
            if result.get("status") == "completed":
                ai_response = f"""✅ 教学材料已成功生成！

**生成状态:** {result.get('status', 'unknown')}

**处理步骤:** {result.get('processing_step', 'N/A')}

**导出结果:**
{json.dumps(result.get('export_result', {}), ensure_ascii=False, indent=2)}

感谢使用智能教案与PPT生成系统！"""
                ended = True
            else:
                ai_response = f"""❌ 教学材料生成出现问题

**状态:** {result.get('status', 'unknown')}

**错误信息:** {result.get('error', 'Unknown error')}

请检查输入并重试。"""
                awaiting_input = False
                ended = False

            # 分段发送响应内容（模拟流式）
            chunk_size = 50
            for i in range(0, len(ai_response), chunk_size):
                chunk = ai_response[i:i+chunk_size]
                yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
                import time
                time.sleep(0.01)  # 模拟流延迟

            # 发送完成信号
            yield f"data: {json.dumps({'type': 'done', 'response': ai_response, 'awaiting_input': awaiting_input, 'ended': ended})}\n\n"

        except Exception as e:
            import traceback
            print(f"Error in event_generator: {str(e)}")
            print(traceback.format_exc())
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
    """重置教学工作流会话"""
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

    print(f"[系统]: TeachingWorkflow 会话已重置")
    return {"status": "ok", "mode": "teaching"}

def _build_response(result: Dict) -> JSONResponse:
    response_msg = "✅ 教学材料已成功生成！" if result.get('status') == 'completed' else "❌ 教学材料生成出现问题"
    response_data = {
        "response": response_msg,
        "status": result.get("status", "unknown"),
        "processing_step": result.get("processing_step", ""),
        "export_result": result.get("export_result", {}),
        "error": result.get("error"),
        "awaiting_input": False,
        "ended": result.get("status") == "completed"
    }
    return JSONResponse(content=response_data)


def _save_uploaded_files(files: List[UploadFile], task_id: str) -> list:
    rag_folder = os.path.join(base_dir, "rag_data")
    os.makedirs(rag_folder, exist_ok=True)

    allowed_exts = {".pdf", ".txt", ".md", ".docx", ".png", ".jpg", ".jpeg", ".gif", ".bmp"}
    saved_paths = []
    for file in files:
        filename = file.filename or ""
        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        if ext not in allowed_exts:
            print(f"⚠️  Skipping unsupported upload: {filename}")
            continue

        safe_name = f"{task_id}_{uuid.uuid4().hex}{ext}"
        save_path = os.path.join(rag_folder, safe_name)
        with open(save_path, "wb") as f:
            f.write(file.file.read())
        saved_paths.append(save_path)

    return saved_paths

@app.post("/send_message_with_files")
async def send_message_with_files(
    message: str = Form(...),
    mode: str = Form("teaching"),
    user_id: Optional[str] = Form(None),
    task_id: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[])
):
    user_input = message
    actual_task_id = task_id or f"lesson_{uuid.uuid4().hex[:8]}"

    print("")
    print("=" * 70)
    print("📨 New Message Received (with files)")
    print("=" * 70)
    print(f"User ID: {user_id}")
    print(f"Task ID: {actual_task_id}")
    print(f"Mode: {mode}")
    print(f"Message preview: {user_input[:100]}...")
    print(f"Uploaded files: {len(files)}")
    print("=" * 70)

    try:
        saved_files = _save_uploaded_files(files, actual_task_id)
        teaching_workflow = get_or_create_teaching_workflow(user_id, actual_task_id)
        result = await teaching_workflow.run(user_input, uploaded_files=saved_files)
        return _build_response(result)
    except Exception as e:
        import traceback
        print(f"❌ Error in send_message_with_files: {str(e)}")
        print(traceback.format_exc())
        print("=" * 70)
        return JSONResponse(
            content={
                "error": f"Teaching workflow error: {str(e)}",
                "response": "❌ 发生错误",
                "status": "error",
                "processing_step": "工作流执行失败",
                "awaiting_input": False,
                "ended": False
            },
            status_code=500
        )
