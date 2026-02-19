# 智能教案与PPT生成系统 - 实现指南

## 📋 系统概述

本项目是一个基于多智能体与多模态检索增强生成（Multimodal RAG）的**智能教案与教学PPT生成系统**。该系统能够根据教师输入的教学主题、教学目标与相关素材，自动生成结构化教案与对应教学PPT。

### 核心特性

✅ **多智能体协作** - 5 个专业智能体（意图解析、知识检索、内容生成、模板匹配、导出管理）
✅ **多模态RAG** - 融合文本与图像的语义检索和关联
✅ **自动化生成** - 从主题到成品文档的完整自动流程
✅ **模板定制** - 4+ 种内置PPT模板，支持自定义样式
✅ **交互式编辑** - Web界面支持实时修改和预览
✅ **多格式导出** - 支持Word、PowerPoint、JSON、Markdown等格式

---

## 🏗️ 系统架构

### 整体流程图

```
教师输入 (主题、目标、素材)
         ↓
┌─────────────────────────────────────────────────┐
│           多智能体工作流 (LangGraph)             │
├─────────────────────────────────────────────────┤
│  1. 教学意图解析智能体                         │
│     ↓ 理解主题、目标、受众等信息                │
│  2. 多模态检索智能体                           │
│     ↓ 从RAG数据库检索相关文本和图像             │
│  3. 内容生成智能体                             │
│     ↓ 生成教案文本和PPT大纲                    │
│  4. 模板匹配智能体                             │
│     ↓ 自动选择或推荐合适的PPT模板              │
│  5. 导出管理智能体                             │
│     ↓ 生成最终文档（Word、PPT、JSON等）       │
└─────────────────────────────────────────────────┘
         ↓
    生成完整成品 (教案+PPT)
         ↓
    用户交互修改 → 重新导出
```

### 模块组成

```
main/
├── teaching_workflow.py          [核心工作流管理]
├── multimodal_rag.py            [多模态检索增强生成]
├── app.py                        [FastAPI服务]
└── teaching_agents/
    ├── intent_parser_agent.py    [教学意图解析]
    ├── multimodal_retriever_agent.py [多模态检索]
    ├── content_generator_agent.py    [内容生成]
    ├── template_matcher_agent.py     [模板匹配]
    └── export_manager_agent.py       [导出管理]
```

---

## 🤖 各智能体详细说明

### 1. 教学意图解析智能体 (IntentParserAgent)

**职责**: 理解和解析教师的教学意图

**功能**:
- 自动识别教学主题和学科领域
- 提取教学目标（知识目标、技能目标、态度目标）
- 判断学生受众等级（小学、中学、大学等）
- 识别教学重点和难点
- 给出信心度评分

**输入示例**:
```
"我需要为初中二年级学生讲解光合作用，重点是讲清楚光反应和暗反应的过程"
```

**输出示例**:
```python
{
    "topic": "光合作用",
    "subject": "生物",
    "level": "初中二年级",
    "learning_objectives": {
        "knowledge": ["光合作用的定义", "光反应和暗反应"],
        "skills": ["实验分析能力"],
        "attitude": ["科学探究精神"]
    },
    "key_points": ["光反应", "暗反应"],
    "difficult_points": ["电子传递链"],
    "confidence_score": 0.92
}
```

### 2. 多模态检索智能体 (MultimodalRetrieverAgent)

**职责**: 从知识库中检索相关的文本和图像素材

**功能**:
- 混合检索（BM25 + FAISS）
- 自动文本分块和索引
- 图像检索和关联
- 结果重排序（使用交叉编码器）
- 自动索引更新

**检索流程**:
```
用户查询
  ↓
文本归一化
  ↓
┌──────────────────────────────┐
│  BM25检索 + FAISS向量检索    │
└──────────────────────────────┘
  ↓
交叉编码器重排序
  ↓
返回Top-K结果 + 关联图像
```

**示例**:
```python
# 输入
query = "光合作用中的光反应过程"

# 输出
{
    "text_materials": [
        {
            "id": "doc_001",
            "content": "光反应是指发生在叶绿体类囊体薄膜上的...",
            "score": 0.95,
            "source": "高中生物教材"
        },
        ...
    ],
    "image_materials": [
        {
            "url": "/images/photosynthesis_light_reaction.png",
            "caption": "光反应过程示意图",
            "relevance_score": 0.88
        },
        ...
    ]
}
```

### 3. 内容生成智能体 (ContentGeneratorAgent)

**职责**: 根据意图和检索结果生成教案和PPT大纲

**功能**:
- 生成结构化教案
  - 教学目标
  - 教学重点和难点
  - 教学过程设计
  - 课堂作业和评估
- 生成PPT大纲
  - 幻灯片结构
  - 各页面的标题和内容
  - 图片位置建议

**生成结果示例**:
```python
{
    "lesson_plan": {
        "title": "光合作用",
        "objectives": ["掌握光合作用的定义", ...],
        "key_points": ["光反应", "暗反应"],
        "teaching_process": [
            {
                "phase": "导入",
                "duration": "5分钟",
                "content": "通过提问引出光合作用..."
            },
            ...
        ],
        "homework": ["完成练习题1-5", ...]
    },
    "ppt_outline": {
        "slides": [
            {
                "slide_num": 1,
                "type": "title_slide",
                "title": "光合作用",
                "subtitle": "理解植物的能量转换过程"
            },
            {
                "slide_num": 2,
                "type": "content_slide",
                "title": "光合作用的定义",
                "content": ["植物利用光能...", "产生有机物..."],
                "image_suggestions": ["光合作用基本图"]
            },
            ...
        ]
    }
}
```

### 4. 模板匹配智能体 (TemplateMatcherAgent)

**职责**: 根据课程特性推荐和匹配合适的PPT模板

**功能**:
- 自动分析课程特点
- 推荐最适合的模板
- 生成模板定制建议
- 支持用户手动选择

**内置模板**:
- 📚 **学术风格** - 适合科学、研究相关课程
- 💼 **商业风格** - 适合管理、商业相关课程
- 🎨 **创意风格** - 适合艺术、设计相关课程
- ⚪ **极简风格** - 通用，强调内容清晰

**推荐逻辑**:
```
根据科目领域 → 识别课程特征 → 匹配模板 → 返回推荐
```

### 5. 导出管理智能体 (ExportManagerAgent)

**职责**: 将生成的内容导出为多种格式

**功能**:
- Word文档导出
  - 自动生成目录
  - 格式化标题和正文
  - 插入表格和图片
  - 设置页眉页脚
- PowerPoint导出
  - 创建各类幻灯片
  - 应用模板和主题
  - 插入文字和图片
  - 设置动画和过渡
- JSON数据导出
- Markdown导出

**导出示例**:
```python
# 输出文件
generated_lessons/
├── docx/
│   └── 光合作用_lesson_20240206_xxx.docx
├── pptx/
│   └── 光合作用_teaching_20240206_xxx.pptx
├── json/
│   └── 光合作用_data_20240206_xxx.json
└── markdown/
    └── 光合作用_lesson_20240206_xxx.md
```

---

## 🔍 多模态RAG系统

### 架构设计

```
原始文档
  ↓
文本分块 (分块大小: 500字符, 重叠: 50字符)
  ↓
┌─────────────────────────────────────────┐
│ Embedding 向量化                        │
│ 模型: Qwen/Qwen3-Embedding-0.6B        │
└─────────────────────────────────────────┘
  ↓
┌──────────────┐  ┌──────────────┐
│  FAISS索引   │  │  BM25索引    │
└──────────────┘  └──────────────┘
  ↓
查询处理
  ↓
┌──────────────────────────────────┐
│ 混合检索                         │
│ - FAISS: 向量相似度              │
│ - BM25: 关键词匹配               │
└──────────────────────────────────┘
  ↓
交叉编码器重排序 (BAAI/bge-reranker-base)
  ↓
返回Top-K结果
```

### 配置参数

```yaml
rag:
  folder_path: "./rag_data"              # RAG数据目录
  index_path: "./faiss_index"            # FAISS索引目录
  embedding_model: "Qwen/Qwen3-Embedding-0.6B"
  rerank_model: "BAAI/bge-reranker-base"
  bm25_k: 5                              # BM25检索数量
  faiss_k: 5                             # FAISS检索数量
  top_n: 1                               # 最终保留数量
  chunk_size: 500                        # 分块大小
  chunk_overlap: 50                      # 分块重叠
  device: "cpu"                          # 计算设备
```

---

## 💻 API 接口

### 主要端点

#### 1. 发送教学请求

```http
POST /send_message HTTP/1.1
Content-Type: application/json

{
    "user_input": "请为初中二年级学生生成关于光合作用的教案和PPT",
    "user_id": "teacher_001",
    "task_id": "lesson_20240206_001",
    "mode": "teaching",
    "rag": true
}
```

**响应**:
```json
{
    "response": {
        "status": "success",
        "lesson_plan": {...},
        "ppt_outline": {...},
        "export_paths": {
            "docx": "generated_lessons/docx/lesson_xxx.docx",
            "pptx": "generated_lessons/pptx/lesson_xxx.pptx"
        }
    }
}
```

#### 2. 重置会话

```http
POST /reset HTTP/1.1
Content-Type: application/json

{
    "user_id": "teacher_001",
    "task_id": "lesson_20240206_001",
    "mode": "teaching"
}
```

#### 3. 流式响应

```python
# 支持实时流式返回生成过程
async def stream_response():
    async for chunk in teaching_workflow.stream():
        yield chunk
```

---

## 🎯 使用流程

### 第一步：启动系统

```bash
# 激活虚拟环境
conda activate veta

# 启动服务（自动进行设置）
./local.sh

# 或手动启动
uvicorn main.app:app --reload --host 0.0.0.0 --port 3367
```

### 第二步：访问Web界面

打开浏览器访问:
```
http://localhost:3367/teaching
```

### 第三步：创建教案

1. **填写课程信息**
   - 教学主题（必填）
   - 学生级别
   - 教学目标
   - 特殊需求

2. **选择模板**
   - 预览4种内置模板
   - 选择最适合的风格

3. **上传补充材料**（可选）
   - 文本资料
   - 图片素材
   - 参考资源

4. **生成并预览**
   - 点击"生成教案"
   - 实时查看生成进度
   - 预览生成结果

5. **编辑和调整**
   - 修改文本内容
   - 替换图片
   - 调整样式

6. **导出文档**
   - 下载Word教案
   - 下载PowerPoint演示
   - 导出JSON数据

---

## 📚 数据准备

### RAG数据格式

在 `rag_data/` 目录下放置教学资料：

```
rag_data/
├── document.md           # 通用教学文档
├── pet_medicine.md       # 领域特定资料
├── science/
│   ├── biology.md
│   ├── chemistry.md
│   └── physics.md
├── humanities/
│   ├── history.md
│   ├── literature.md
│   └── geography.md
└── images/
    ├── photosynthesis.png
    ├── cell_structure.png
    └── ...
```

### 图片和文本的语义关联

系统会自动：
1. 为每张图片生成描述文本
2. 计算文本和图片的相似度
3. 在生成PPT时，根据内容自动插入相关图片

```python
# 自动关联过程
文本内容: "光反应发生在类囊体薄膜上..."
        ↓
    向量化
        ↓
    在图像数据库中检索
        ↓
    返回最匹配的图片: photosynthesis_light_reaction.png
```

---

## 🔧 配置和自定义

### 配置文件

编辑 `config.yaml`:

```yaml
openai:
  api_base: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  api_key: "your-api-key"
  model: "qwen-plus"
  temperature: 0.9

rag:
  folder_path: "./rag_data"
  chunk_size: 500
  chunk_overlap: 50

redis:
  host: "127.0.0.1"
  port: 6378
  password: "your-password"
```

### 自定义模板

编辑 `templates/ppt_templates/template_config.json`:

```json
{
  "templates": [
    {
      "id": "my_template",
      "name": "我的自定义模板",
      "colors": {
        "primary": "#FF6B6B",
        "secondary": "#4ECDC4"
      },
      "layout": {
        "title_slide": {...},
        "content_slide": {...}
      }
    }
  ]
}
```

---

## 🚀 性能优化

### 缓存机制

- LLM响应缓存（减少API调用）
- 向量索引缓存（加快检索）
- 会话状态缓存（使用Redis）

### 并发处理

- FastAPI异步处理
- LangGraph并行执行支持
- 多进程向量计算

### 资源管理

- 自动索引定期重建
- 过期缓存自动清理
- 内存占用监控

---

## 📊 示例输出

### 生成的Word教案

```
┌─────────────────────────────────┐
│      光合作用 - 教学设计         │
├─────────────────────────────────┤
│  教学目标                       │
│  • 理解光合作用的基本原理        │
│  • 掌握光反应和暗反应的过程      │
│  • 能够设计简单的实验验证        │
├─────────────────────────────────┤
│  教学重点和难点                 │
│  重点：光反应 → 暗反应的能量转换  │
│  难点：电子传递链的理解           │
├─────────────────────────────────┤
│  教学过程                       │
│  [详细的教学步骤和时间分配]       │
├─────────────────────────────────┤
│  课堂作业                       │
│  [练习题和拓展任务]              │
└─────────────────────────────────┘
```

### 生成的PPT大纲

```
第1页: 封面
  - 标题: 光合作用
  - 副标题: 理解植物的能量转换过程

第2页: 什么是光合作用？
  - 定义文字
  - 关键公式图

第3页: 光反应过程
  - 过程说明
  - 流程图
  - 相关图片

第4页: 暗反应过程
  - 过程说明
  - 循环图

第5页: 总结
  - 要点列表
  - 复习问题
```

---

## ✅ 功能检查清单

### 核心功能
- [x] 教学意图解析
- [x] 多模态知识检索
- [x] 自动内容生成
- [x] 模板智能匹配
- [x] 多格式导出

### 高级功能
- [x] Web交互界面
- [x] 实时流式生成
- [x] 会话管理
- [x] 缓存机制

### 优化功能
- [x] 并发处理
- [x] 错误恢复
- [x] 日志记录
- [x] 性能监控

---

## 🐛 故障排除

### 常见问题

**Q: 提示 `ModuleNotFoundError: No module named 'python_pptx'`**
```bash
# 在正确的conda环境中安装依赖
conda activate veta
conda run -n veta pip install -r requirements.txt
```

**Q: 向量索引加载失败**
```bash
# 重建索引
rm -rf faiss_index/
python -c "from main.multimodal_rag import MultimodalRAG; m = MultimodalRAG(); m.rebuild_index()"
```

**Q: API超时**
- 增加timeout参数
- 减少chunk_size
- 使用更小的模型

---

## 📖 相关文档

- [快速开始指南](./TEACHING_GUIDE.md)
- [系统详细文档](./TEACHING_SYSTEM_GUIDE.md)
- [实现总结](./IMPLEMENTATION_SUMMARY.md)
- [测试示例](./teaching_examples.py)

---

## 📝 注意事项

1. **API密钥**: 请确保在 `config.yaml` 中设置有效的API密钥
2. **网络连接**: 系统需要网络连接以调用LLM服务
3. **存储空间**: 生成的文档会存储在 `generated_lessons/` 目录
4. **内存占用**: 大规模数据集可能需要较多内存，建议至少8GB

---

## 📧 联系与反馈

对于问题、建议或反馈，请：
- 查看日志文件: `logs/`
- 提交问题报告
- 提供复现步骤

---

**系统版本**: 1.0
**最后更新**: 2024年2月6日
**许可证**: MIT

