# 🎓 智能教案与PPT生成系统

> 基于多智能体和多模态检索增强生成（RAG）技术的智能教学文档生成平台

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green)
![LangGraph](https://img.shields.io/badge/LangGraph-0.6+-orange)
![License](https://img.shields.io/badge/License-MIT-red)

## 📋 目录

- [项目特色](#项目特色)
- [核心功能](#核心功能)
- [快速开始](#快速开始)
- [使用指南](#使用指南)
- [系统架构](#系统架构)
- [API文档](#api文档)
- [扩展指南](#扩展指南)

## ✨ 项目特色

### 🤖 多智能体协作
系统由5个专科化智能体组成，各司其职：
- **意图解析智能体** - 理解教学需求
- **多模态检索智能体** - 查找相关教学素材
- **内容生成智能体** - 创作教案和PPT
- **模板匹配智能体** - 选择合适的设计风格
- **导出管理智能体** - 生成最终文档

### 🔍 多模态RAG检索
融合最新的信息检索技术：
- 混合检索（BM25 + FAISS向量搜索）
- 交叉编码器智能重排
- 文本和图像的语义关联
- 自动索引增量更新

### 🎨 智能排版和设计
4种精心设计的PPT模板：
- **正式风格** - 学术专业型
- **彩色风格** - 生动趣味型
- **极简风格** - 现代清爽型
- **创意风格** - 艺术视觉型

### 📄 多格式输出
一键生成完整的教学文档：
- **Word教案** - 包含完整章节和目录
- **PPT演示** - 精美的幻灯片序列
- **JSON数据** - 便于二次处理和备份

## 🚀 核心功能

### 1. 智能化教案生成

```
输入: 教学主题 + 年级 + 学科 + 目标
        ↓
    [意图解析] → 结构化教学需求
        ↓
    [多模态检索] → 相关教学素材
        ↓
    [内容生成] → 完整教案大纲
        ↓
输出: 结构化教案 + PPT大纲
```

### 2. 自动PPT设计

系统自动为不同的课程选择最合适的设计风格，并自动排版幻灯片内容。

### 3. 交互式编辑

在生成过程中和生成后，教师可以：
- 调整教学目标
- 修改内容结构
- 更换设计风格
- 自定义图文元素

### 4. 会话管理

支持多用户并发，每个教师有独立的会话空间，可以创建多个课程任务。

## 📦 快速开始

### 系统需求

- Python 3.8+
- OpenAI API密钥（或兼容的LLM API）
- Redis（可选，用于会话存储）
- 4GB+ RAM（RAG索引建议）

### 1️⃣ 安装依赖

```bash
# 克隆仓库
git clone <repo-url>
cd Veta

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2️⃣ 配置设置

复制配置文件并修改：

```bash
cp config.example.yaml config.yaml
```

编辑 `config.yaml`，填写你的API信息：

```yaml
openai:
  api_base: "https://api.openai.com/v1"
  api_key: "sk-your-api-key"
  model: "gpt-4-turbo"
  temperature: 0.7

rag:
  embedding_model: "Qwen/Qwen3-Embedding-0.6B"
  rerank_model: "BAAI/bge-reranker-base"
  chunk_size: 500
  chunk_overlap: 50

redis:
  host: "localhost"
  port: 6379
```

### 3️⃣ 启动服务

**快速启动（推荐）：**

```bash
# Linux/Mac
bash quick_start.sh

# Windows
quick_start.bat
```

**或手动启动：**

```bash
python -m uvicorn main.app:app --reload --host 0.0.0.0 --port 8000
```

### 4️⃣ 访问应用

打开浏览器访问：

```
http://localhost:8000
```

你会看到一个美观的Web界面，默认打开教学助手模式。

## 📖 使用指南

### 生成一节课程

1. **选择教学助手模式** 📚
   - 在页面顶部选择"教学助手"

2. **填写课程信息**
   - 教学主题（必填）：如"人体循环系统"
   - 学生年级（必填）：小学、初中、高中、大学
   - 学科领域（必填）：数学、英语、生物等
   - 课程时长：默认45分钟
   - 学习目标：学生应该学会什么

3. **选择教学方法**
   - 讲授法、讨论法、实践法、互动式

4. **选择PPT风格**
   - 正式风格 📊
   - 彩色风格 🌈
   - 极简风格 ⚪
   - 创意风格 🎨

5. **点击生成按钮** 🎯
   - 系统自动处理
   - 显示处理进度

6. **下载生成的文件**
   - Word教案：包含完整内容和格式
   - PowerPoint：精美的幻灯片
   - JSON：数据备份

### 高级用法

#### 自定义RAG数据

将你的教学素材放在 `rag_data/` 文件夹：

```
rag_data/
├── biology/
│   ├── circulatory.md
│   └── diagram.png
├── physics/
│   └── mechanics.pdf
└── ...
```

支持的格式：`.md`, `.txt`, `.pdf`, `.docx`, `.png`, `.jpg`

#### 集成到你的应用

```python
from main.teaching_workflow import TeachingWorkflow

workflow = TeachingWorkflow()
result = await workflow.run("教学主题和要求...")

# 访问生成的文件
files = result['export_result']['files']
docx_path = files['docx']['path']
ppt_path = files['ppt']['path']
```

## 🏗️ 系统架构

### 高层流程图

```
┌──────────────────────────────────┐
│   用户Web界面                     │
├──────────────────────────────────┤
│   FastAPI 服务层                  │
├──────────────────────────────────┤
│   LangGraph 工作流引擎             │
├──────────────────────────────────┤
│   多智能体系统                    │
│   ├─ 意图解析Agent               │
│   ├─ 检索Agent                   │
│   ├─ 生成Agent                   │
│   ├─ 模板Agent                   │
│   └─ 导出Agent                   │
├──────────────────────────────────┤
│   外部服务                        │
│   ├─ OpenAI/LLM                  │
│   ├─ RAG (FAISS)                 │
│   └─ Redis (会话)                 │
└──────────────────────────────────┘
```

### 核心模块

| 模块 | 功能 | 位置 |
|------|------|------|
| IntentParserAgent | 解析教学意图 | `main/teaching_agents/` |
| MultimodalRetrieverAgent | 检索教学素材 | `main/teaching_agents/` |
| ContentGeneratorAgent | 生成教案内容 | `main/teaching_agents/` |
| TemplateMatcherAgent | 匹配PPT模板 | `main/teaching_agents/` |
| ExportManagerAgent | 导出文档 | `main/teaching_agents/` |
| MultimodalRetriever | RAG检索系统 | `main/multimodal_rag.py` |
| TeachingWorkflow | 工作流编排 | `main/teaching_workflow.py` |

## 🔌 API文档

### 生成教案与PPT

```bash
curl -X POST http://localhost:8000/send_message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "我需要一节高中生物课关于细胞膜的结构和功能，45分钟",
    "mode": "teaching",
    "user_id": "teacher_001"
  }'
```

**响应：**

```json
{
    "response": "教学材料已生成！状态: completed",
    "status": "completed",
    "processing_step": "Export completed",
    "export_result": {
        "files": {
            "docx": {"path": "..."},
            "ppt": {"path": "..."}
        }
    },
    "ended": true
}
```

更多详情见 [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## 🎓 示例使用场景

### 场景1：小学数学
```
主题：分数的基本概念
年级：小学五年级
学科：数学
时长：40分钟
模板：彩色风格
```

**生成结果：**
- 趣味生动的教案
- 8张彩色PPT
- 实践活动建议

### 场景2：高中生物
```
主题：光合作用
年级：高中
学科：生物
时长：50分钟
模板：正式风格
```

**生成结果：**
- 专业的教案文档
- 6张学术PPT
- 形成性评估

### 场景3：大学物理
```
主题：量子力学基础
年级：大学二年级
学科：物理
时长：90分钟
模板：极简风格
```

**生成结果：**
- 详细的讲义
- 10张清爽PPT
- 推导过程和公式

## 🛠️ 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | HTML5 + CSS3 + JavaScript |
| 后端 | FastAPI + Uvicorn |
| AI框架 | LangChain + LangGraph |
| LLM | OpenAI API (或兼容) |
| 检索 | FAISS + Sentence Transformers |
| 文档 | python-pptx + python-docx |
| 缓存 | Redis |
| 部署 | Docker (可选) |

## 📊 性能指标

- **响应时间** 30-60秒（取决于LLM API）
- **并发用户** 支持多用户独立会话
- **文件大小** 教案2-5MB，PPT3-10MB
- **RAG索引** 初次5-30秒，增量更新<5秒

## 🔒 安全性

- API密钥通过环境变量和config.yaml管理
- 用户会话隔离
- 文件输出目录隔离
- 完整的错误处理和日志

## 📚 文档

- [快速入门指南](TEACHING_GUIDE.md)
- [API完整文档](API_DOCUMENTATION.md)
- [实现总结](IMPLEMENTATION_SUMMARY.md)
- [代码示例](teaching_examples.py)

## 🚀 扩展和改进

### 计划中的功能

- [ ] 图像自动生成集成
- [ ] 多语言支持
- [ ] 实时协作编辑
- [ ] 用户自定义模板
- [ ] 本地化嵌入模型

### 贡献指南

欢迎提交Issue和Pull Request！

```bash
# Fork项目
# 创建特性分支
git checkout -b feature/YourFeature
# 提交更改
git commit -am 'Add YourFeature'
# 推送到分支
git push origin feature/YourFeature
# 创建Pull Request
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 🙏 致谢

感谢以下开源项目和服务：
- [LangChain](https://langchain.com)
- [FastAPI](https://fastapi.tiangolo.com)
- [FAISS](https://github.com/facebookresearch/faiss)
- [python-pptx](https://python-pptx.readthedocs.io)
- [OpenAI API](https://openai.com/api)

## 📞 联系方式

- 提交问题：GitHub Issues
- 项目讨论：GitHub Discussions
- 邮箱：support@example.com

## 🎯 项目状态

✅ **生产就绪** - 核心功能完整，可直接部署

**版本**: 1.0.0
**最后更新**: 2024年2月4日

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个Star！**

![Visitors](https://visitor-badge.glitch.me/badge?page_id=your.repo.id)

</div>
