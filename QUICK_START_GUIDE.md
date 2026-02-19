# 🎓 快速启动指南

## 系统状态 ✅

所有功能已验证并正常运行：
- ✅ 前端功能简化（仅保留教案生成系统）
- ✅ 后端日志系统完整（可追踪每个处理步骤）
- ✅ PPT导出修复（成功生成Word和PowerPoint文件）
- ✅ API调用正常（前后端通信完整）

## 快速启动 (3步)

### 步骤 1: 启动服务器
```bash
cd /home/lilinchen/code/Veta
./run.sh
```

或者使用原始脚本：
```bash
./local.sh
```

你会看到：
```
================================
🎓 Veta 智能教案与PPT生成系统
================================

✓ 检测到 Conda 环境已配置，开始启动服务...
✓ 服务地址: http://localhost:3367

按 Ctrl+C 停止服务
```

### 步骤 2: 打开浏览器
访问：`http://localhost:3367`

你会看到教案生成系统的界面。

### 步骤 3: 填写课程信息

在左侧表单填写：
- **教学主题** ⭐ 必填（例如：人体循环系统）
- **学生年级** ⭐ 必填（小学/初中/高中/大学）
- **学科领域** ⭐ 必填（数学/语文/英语/物理/化学/生物/历史/地理）
- 课程时长（默认45分钟）
- 学习目标（可选）
- 教学方法（讲授法/讨论法/实践法/互动式）
- PPT风格（正式/彩色/极简/创意）

然后点击 **"生成教案与PPT"** 按钮。

## 监控生成过程

### 方式1：终端日志
服务器运行时，终端会显示详细的处理日志：

```
======================================================================
📨 New Message Received
======================================================================
User ID: teacher_1707212345678
Task ID: lesson_1707212345678
Mode: teaching
Message preview: 教学主题：人体循环系统...
======================================================================
📌 Step 1: Getting or creating TeachingWorkflow instance...
✅ TeachingWorkflow instance ready

📌 Step 2: Running teaching workflow...
============================================================
📝 Step 1: Parsing Teaching Intent
...
✅ Intent parsed: 人体循环系统
...
🎨 Step 4: Matching PPT Template
✅ Template matched: Professional Academic
...
💾 Step 6: Exporting Output
✅ Export completed successfully
============================================================
✅ Teaching Workflow Completed Successfully!
```

### 方式2：浏览器控制台
按 `F12` 打开浏览器开发者工具，查看Console标签页：

```
Sending request to /send_message with input: ...
Response received: 200
Response data: {status: "completed", response: "✅ 教学材料已成功生成！", ...}
```

## 查看生成的文件

所有生成的教案和PPT保存在：
```
generated_lessons/
├── docx/           # 教案Word文档 (.docx)
│   └── 人体循环系统_20260206_180041.docx
├── pptx/           # 教学PPT演示 (.pptx)
│   └── 人体循环系统_20260206_180041.pptx
├── json/           # 课程数据 (.json)
│   └── 人体循环系统_20260206_180041.json
└── markdown/       # Markdown版本 (.md)
```

你可以直接下载使用这些文件，或在浏览器中下载。

## 完整工作流示例

### 示例输入
```
教学主题���人体循环系统
学生年级：初中
学科领域：生物
课程时长：45分钟
学习目标：理解心脏结构，了解血液循环的基本路径，认识血管的功能
教学方法：讲授法
PPT风格：formal
```

### 预期输出
1. **Word文档** - 包含：
   - 教案标题和元数据
   - 学习目标（明确列举）
   - 教学材料清单
   - 详细的主要内容章节
   - 教学活动设计
   - 评估策略
   - 课程总结

2. **PowerPoint演示** - 包含：
   - 封面页（标题+副标题）
   - 各章节导航页
   - 内容页（含关键要点）
   - 活动页（教学活动说明）
   - 总结页（知识回顾）

3. **JSON数据** - 包含：
   - 完整的课程结构
   - 所有生成的内容
   - 幻灯片信息
   - 元数据

## 测试脚本

如果要离线测试系统而不启动Web服务器：

```bash
# 测试工作流执行
python test_workflow.py

# 测试API端点
python test_api.py

# 快速功能测试
python quick_test.py

# 完整系统验证
python final_check.py
```

## 故障排除

### 问题1: 服务器启动失败
**症状**: `ModuleNotFoundError: No module named 'python_pptx'`

**解决方案**:
```bash
conda activate veta
pip install python-pptx python-docx
```

### 问题2: 前端没有响应
**症状**: 点击"生成"后没有任何反应

**排查步骤**:
1. 检查服务器是否运行：访问 `http://localhost:3367`
2. 打开浏览器控制台（F12）查看错误信息
3. 检查终端是否显示日志
4. 确保所有必填项都已填写

### 问题3: PPT导出失败
**症状**: 生成了Word文件，但没有PPT

**解决方案**: 已自动修复，系统会自动创建textbox当placeholder不可用时

### 问题4: 生成速度很慢
**原因**: 系统需要调用LLM API和进行多模态检索

**预期时间**: 
- 简单课题：30-60秒
- 复杂课题：1-2分钟
- 包含RAG检索：2-3分钟

## 系统架构简介

```
浏览器前端 (HTML/CSS/JS)
    ↓
HTTP POST /send_message
    ↓
FastAPI 后端 (main/app.py)
    ↓
教学工作流 (TeachingWorkflow)
    ├─ Intent Parser Agent      (解析教学意图)
    ├─ Multimodal Retriever     (检索教学材料)
    ├─ Content Generator Agent  (生成课程内容)
    ├─ Template Matcher Agent   (匹配PPT模板)
    ├─ Slide Layout             (排版幻灯片)
    └─ Export Manager Agent     (导出DOCX/PPTX)
    ↓
生成的文件 (generated_lessons/)
    ├─ .docx (Word文档)
    ├─ .pptx (PowerPoint)
    ├─ .json (数据)
    └─ .md (Markdown)
```

## 关键改进总结

| 改进项 | 状态 | 说明 |
|------|------|------|
| 前端功能简化 | ✅ 完成 | 仅保留教案生成系统，移除兽医/动物医院模块 |
| 后端日志系统 | ✅ 完成 | 每个步骤都有详细的进度日志输出 |
| PPT导出修复 | ✅ 完成 | 修复placeholder问题，添加容错机制 |
| API调用改进 | ✅ 完成 | 完整的请求/响应日志和错误处理 |
| 前端console日志 | ✅ 完成 | 浏览器console显示完整的调试信息 |

## 需要帮助？

如果遇到问题，查看以下文件获取更多信息：

- `IMPROVEMENTS_SUMMARY.md` - 详细改进说明
- `README.md` - 项目总体说明
- `logs/` - 系统日志文件
- 终端输出 - 查看实时处理日志

---

**准备好了吗？运行 `./run.sh` 开始使用！** 🚀

