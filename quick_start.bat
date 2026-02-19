@echo off
REM Quick start script for Teaching Workflow System (Windows)
REM 智能教案与PPT生成系统 - 快速启动脚本 (Windows)

echo.
echo 🎓 智能教案与PPT生成系统
echo ==================================
echo.

REM Check Python version
echo 检查Python环境...
python --version

REM Create virtual environment if not exists
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM Activate virtual environment
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM Install dependencies
echo 安装依赖...
pip install -r requirements.txt

REM Create necessary directories
echo 创建必要的文件夹...
if not exist "rag_data" mkdir rag_data
if not exist "generated_lessons\pptx" mkdir generated_lessons\pptx
if not exist "generated_lessons\docx" mkdir generated_lessons\docx
if not exist "generated_lessons\json" mkdir generated_lessons\json
if not exist "templates\ppt_templates" mkdir templates\ppt_templates

REM Check config file
if not exist "config.yaml" (
    echo ❌ config.yaml 不存在！
    echo 请复制 config.example.yaml 为 config.yaml 并填写API密钥
    pause
    exit /b 1
)

REM Start the application
echo.
echo ✅ 环境设置完成！
echo.
echo 正在启动应用...
echo 访问地址: http://localhost:8000
echo.

python -m uvicorn main.app:app --reload --host 0.0.0.0 --port 8000

pause
