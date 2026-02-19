# 🎓 智能教案与PPT生成系统 - 启动指南

## 系统简介

本项目是一个融合大语言模型（LLM）、多模态检索增强生成（Multimodal RAG）与多智能体协作机制的教学文档智能生成系统。

系统能够根据教师输入的教学主题、教学目标与相关素材，自动生成结构化教案与对应教学PPT。

## 快速启动

### 前置条件

1. **Python 环境**: Python 3.10+
2. **Conda 环境**: 已安装 conda，并创建了名为 `veta` 的虚拟环境
3. **依赖安装**: 已安装 requirements.txt 中的所有依赖

### 启动步骤

#### 方法 1：使用启动脚本（推荐）

```bash
# Linux/macOS
chmod +x local.sh
./local.sh

# Windows
# 等待 Windows 版本脚本
```

#### 方法 2：手动启动

```bash
# 1. 激活 conda 环境
conda activate veta

# 2. 安装依赖（如果未安装）
pip install -r requirements.txt

# 3. 启动后端服务
uvicorn main.app:app --reload --host 0.0.0.0 --port 3367
```

#### 方法 3：验证依赖

```bash
# 运行导入测试脚本
python test_imports.py
```

### 访问应用

启动成功后，在浏览器中打开：

```
http://localhost:3367
```

## 系统架构

### 前端技术栈

- **HTML5/CSS3**: 现代化界面
- **JavaScript**: 交互逻辑，支持 SSE 流式响应
- **Markdown 渲染**: markdown-it + DOMPurify
- **LocalStorage**: 本地任务管理

### 后端技术栈

- **FastAPI**: 高性能 Web 框架
- **Uvicorn**: ASGI 服务器
- **LangChain**: LLM 框架
- **LangGraph**: 工作流编排
- **python-pptx**: PPT 生成
- **python-docx**: Word 文档生成

### 多智能体架构

系统由 5 个主要智能体组成：

1. **IntentParserAgent**: 解析教学意图
2. **MultimodalRetrieverAgent**: 多模态素材检索
3. **ContentGeneratorAgent**: 内容生成
4. **TemplateMatcherAgent**: 模板匹配与排版
5. **ExportManagerAgent**: 多格式导出

## 功能特性

### ✅ 已实现功能

- ✅ 智能教案生成系统
- ✅ 多智能体协作工作流
- ✅ 教学意图智能解析
- ✅ 多模态检索增强生成（RAG）
- ✅ PPT 智能生成与排版
- ✅ Word 教案文档导出
- ✅ 任务历史管理与持久化
- ✅ 用户系统与登录管理
- ✅ SSE 流式响应支持

### 🚀 计划中的功能

- 🔄 实时预览编辑
- 🔄 图片与文本的语义对齐
- 🔄 PPT 主题色自定义
- 🔄 多语言支持

## 项目文件结构

```
Veta/
├── main/
│   ├── app.py                    # FastAPI 主应用
│   ├── config.py                 # 配置管理
│   ├── teaching_workflow.py       # 教学工作流
│   ├── teaching_agents/           # 智能体系统
│   │   ├── intent_parser_agent.py
│   │   ├── multimodal_retriever_agent.py
│   │   ├── content_generator_agent.py
│   │   ├── template_matcher_agent.py
│   │   └── export_manager_agent.py
│   ├── static/                    # 前端资源
│   │   ├── veta_teaching.js       # 教学系统脚本
│   │   ├── veta.css               # 样式表
│   │   ├── user-storage.js        # 本地存储
│   │   └── 1.png                  # 示例图片
│   └── templates/                 # HTML 模板
│       └── index.html             # 主页
├── rag_data/                      # RAG 数据库
├── generated_lessons/             # 生成的课程
│   ├── pptx/                      # PPT 文件
│   ├── docx/                      # Word 文件
│   ├── json/                      # JSON 数据
│   └── markdown/                  # Markdown 文件
├── templates/ppt_templates/       # PPT 模板
├── config.yaml                    # 配置文件
├── requirements.txt               # Python 依赖
├── local.sh                       # Linux 启动脚本
└── README.md                      # 项目说明

```

## 配置文件

### config.yaml

```yaml
# OpenAI API 配置
openai:
  api_key: "your-api-key-here"
  model: "gpt-4-turbo"  # 或其他模型
  temperature: 0.7
  max_tokens: 4096

# Redis 配置（可选）
redis:
  host: "localhost"
  port: 6379
  db: 0

# 应用配置
app:
  debug: true
  port: 3367
  host: "0.0.0.0"
```

## 常见问题

### Q: 无法导入 python_pptx

**A:** 确保使用 conda 虚拟环境：
```bash
conda activate veta
pip install python-pptx==1.0.2
```

### Q: OpenAI API 报错

**A:** 检查配置文件中的 API 密钥是否正确设置

### Q: RAG 数据库未加载

**A:** 确保 `rag_data/` 目录下有文档文件，可以参考 `document.md` 和 `pet_medicine.md`

### Q: 前端无法加载

**A:** 检查浏览器开发工具中的网络错误，确保后端服务正常运行

## 开发指南

### 添加新的教学智能体

1. 在 `main/teaching_agents/` 下创建新的代理文件
2. 继承基础代理类
3. 在 `teaching_workflow.py` 中集成新代理
4. 更新工作流图

### 修改 PPT 模板

1. 编辑 `templates/ppt_templates/` 下的模板配置
2. 在 `template_matcher_agent.py` 中更新模板匹配逻辑
3. 重新启动应用

### 自定义 RAG 数据

1. 在 `rag_data/` 目录下添加文档
2. 重启应用自动重新索引
3. 查询时会使用新数据

## 性能优化

- 使用 FAISS 进行快速向量搜索
- 启用 uvicorn 的 worker 多进程
- 缓存常用的模板和检索结果
- 使用 SSE 流式响应减少首字节延迟

## 许可证

MIT License

## 联系支持

如有问题，请提交 issue 或联系项目维护者。

---

**最后更新**: 2026 年 2 月 6 日  
**版本**: 1.0.0

