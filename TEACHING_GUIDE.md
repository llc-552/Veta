# 智能教案与PPT生成系统 - 使用指南

## 项目概述

融合LLM、多模态RAG与多智能体协作的智能教学文档生成系统。

## 核心功能

### 1. 多智能体系统
- 教学意图解析智能体
- 多模态检索智能体  
- 内容生成智能体
- 模板匹配智能体
- 导出管理智能体

### 2. 多模态RAG
- 文本与图像混合检索
- 语义关联搜索
- 智能排序重排

### 3. 自动生成
- Word格式教案
- PowerPoint演示
- JSON数据导出

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置config.yaml
```yaml
openai:
  api_key: "your_key"
  model: "gpt-4-turbo"

rag:
  embedding_model: "Qwen/Qwen3-Embedding-0.6B"
  chunk_size: 500
```

### 启动服务
```bash
python -m uvicorn main.app:app --reload
```

访问 http://localhost:8000

## 使用流程

1. 选择"教学助手"模式
2. 填写课程信息：主题、年级、学科、目标
3. 选择PPT风格
4. 点击"生成教案与PPT"
5. 下载生成的Word教案和PPT文件

## 项目结构

```
main/
├── teaching_agents/          # 教学智能体
├── multimodal_rag.py        # 多模态RAG
├── teaching_workflow.py     # 工作流
├── app.py                   # FastAPI应用
└── templates/teaching.html  # 前端界面
```

## PPT模板

- formal: 正式学术风格
- colorful: 彩色趣味风格  
- minimalist: 极简现代风格
- creative: 创意艺术风格

## 接口

### 生成教案与PPT
```
POST /send_message
{
    "message": "课程描述...",
    "mode": "teaching",
    "user_id": "teacher_id",
    "task_id": "lesson_id"
}
```

### 重置会话
```
POST /reset
{
    "mode": "teaching",
    "user_id": "user_id",
    "task_id": "task_id"
}
```

## 文件格式

### 输入：RAG数据
- 文本：.txt, .md
- 文档：.pdf, .docx
- 图像：.png, .jpg

### 输出：生成文件
- generated_lessons/
  - docx/: Word教案
  - pptx/: PPT演示
  - json/: 数据备份

## 配置参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| chunk_size | 文本块大小 | 500 |
| chunk_overlap | 重叠度 | 50 |
| bm25_k | BM25结果数 | 5 |
| faiss_k | FAISS结果数 | 5 |
| top_n | 最终返回数 | 3 |

## 扩展指南

### 添加新模板
编辑 `template_matcher_agent.py` 中的 `_load_templates()` 方法

### 优化检索
增加RAG数据质量，调整参数在 `multimodal_rag.py`

### 自定义智能体
在 `teaching_agents/` 中创建新文件继承相应类

## 许可证

MIT License
