# 智能教案与PPT生成系统 - 快速启动指南

## 🚀 快速开始 (5分钟)

### 环境要求

- Python 3.9+
- Conda 或 pip
- 4GB+ RAM
- 网络连接（用于LLM服务）

### 步骤1: 启动服务

```bash
# 方式一: 使用启动脚本（推荐）
cd /home/lilinchen/code/Veta
./local.sh

# 方式二: 手动启动
conda activate veta
uvicorn main.app:app --reload --host 0.0.0.0 --port 3367
```

启动成功后，你会看到：
```
INFO:     Uvicorn running on http://0.0.0.0:3367 (Press CTRL+C to quit)
```

### 步骤2: 打开Web界面

在浏览器中访问:
```
http://localhost:3367/teaching
```

### 步骤3: 生成你的第一个教案

1. **填写课程信息**
   ```
   主题: 光合作用
   级别: 初中二年级
   目标: 掌握光反应和暗反应的过程
   ```

2. **点击"生成教案"**
   - 系统会自动分析你的需求
   - 从知识库中检索相关内容
   - 生成完整的教案和PPT大纲

3. **预览和编辑**
   - 实时查看生成进度
   - 在Web界面编辑内容
   - 替换或添加图片

4. **导出文档**
   - 下载Word格式教案
   - 下载PowerPoint演示文件
   - 导出为JSON或Markdown

---

## 📋 详细使用说明

### 方案1: Web界面生成（最简单）

#### 访问教学界面
```
URL: http://localhost:3367/teaching
```

#### 界面说明
```
┌─────────────────────────────────────────┐
│   智能教案与PPT生成系统                 │
├─────────────────────────────────────────┤
│                                         │
│  课程信息输入区                         │
│  ┌─────────────────────────────────┐  │
│  │ 教学主题: [________]             │  │
│  │ 学生级别: [选择]                │  │
│  │ 教学目标: [________]             │  │
│  │ 特殊需求: [________]             │  │
│  └─────────────────────────────────┘  │
│                                         │
│  [模板选择] [生成教案] [清空]          │
│                                         │
│  ─────────────────────────────────     │
│                                         │
│  生成结果预览:                         │
│  ┌─────────────────────────────────┐  │
│  │ 教案内容...                     │  │
│  │ PPT大纲...                      │  │
│  │                                 │  │
│  │ [下载Word] [下载PPT]            │  │
│  └─────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

### 方案2: Python代码调用

#### 创建完整的教案

```python
import asyncio
from main.teaching_workflow import TeachingWorkflow

async def generate_lesson():
    # 初始化工作流
    workflow = TeachingWorkflow(
        rag_folder="./rag_data",
        templates_folder="./templates/ppt_templates",
        output_folder="./generated_lessons"
    )
    
    # 准备用户输入
    user_input = "请为初中二年级学生讲解光合作用的基本原理"
    
    # 运行工作流
    result = await workflow.run(user_input)
    
    # 查看结果
    print(f"教案: {result['generated_content']['lesson_plan']}")
    print(f"PPT大纲: {result['generated_content']['ppt_outline']}")
    print(f"输出文件: {result['export_paths']}")

# 运行
asyncio.run(generate_lesson())
```

### 方案3: API调用

#### 通过HTTP API生成教案

```bash
curl -X POST http://localhost:3367/send_message \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "请为初中二年级学生讲解光合作用",
    "mode": "teaching",
    "user_id": "teacher_001",
    "task_id": "lesson_001",
    "rag": true
  }'
```

#### Python请求示例

```python
import requests
import json

url = "http://localhost:3367/send_message"
payload = {
    "user_input": "请为初中二年级学生讲解光合作用",
    "mode": "teaching",
    "user_id": "teacher_001",
    "task_id": "lesson_001",
    "rag": True
}

response = requests.post(url, json=payload)
result = response.json()

print(f"状态: {result['response']['status']}")
print(f"教案: {result['response']['lesson_plan']}")
print(f"文件位置: {result['response']['export_paths']}")
```

---

## 📚 功能演示

### 示例1: 生成生物学教案

**输入**:
```
我需要为高中一年级的学生讲解DNA复制的原理和过程。
学生已经学过DNA的基本结构。
我希望使用学术风格的PPT模板。
```

**系统自动完成**:
1. ✓ 解析出主题: DNA复制
2. ✓ 识别受众: 高中一年级
3. ✓ 提取前置知识: DNA结构
4. ✓ 从知识库检索相关内容
5. ✓ 生成教案（包含教学目标、重点难点、教学过程等）
6. ✓ 生成PPT大纲（包含适当的幻灯片结构）
7. ✓ 匹配学术风格模板
8. ✓ 导出Word和PPT文件

**输出文件**:
- `generated_lessons/docx/DNA复制_lesson_xxx.docx`
- `generated_lessons/pptx/DNA复制_teaching_xxx.pptx`

### 示例2: 生成历史教案

**输入**:
```
帮我制作一个关于中国古代丝绸之路的教案，
针对初中三年级的学生。
我想了解丝绸之路的历史背景、主要路线、
商业交易和文化交流。
```

**系统生成结果**:
- 教学目标：理解丝绸之路的重要性
- 教学重点：贸易路线和文化交流
- 生成包含10-12页PPT
- 包含地图、历史图片、时间线

### 示例3: 数学教案与交互式PPT

**输入**:
```
我需要为初二学生讲解勾股定理的证明方法。
学生应该能够理解定理的含义和在实际中的应用。
```

**自动生成**:
- 教案包含5个教学活动
- PPT包含3个交互式演示
- 课堂作业和评估方案
- 参考资源和扩展阅读

---

## 🔧 常用命令

### 启动/停止服务

```bash
# 启动服务
./local.sh

# 停止服务
Ctrl+C

# 查看日志
tail -f logs/app.log
```

### 数据管理

```bash
# 重建RAG索引
python -c "from main.multimodal_rag import MultimodalRAG; m = MultimodalRAG(); m.rebuild_index()"

# 清除缓存
rm -rf faiss_index/*
rm -rf .cache/*

# 查看生成的文件
ls -la generated_lessons/
```

### 系统测试

```bash
# 运行完整的系统测试
python system_test.py

# 运行示例代码
python teaching_examples.py
```

---

## 🎓 教学场景示例

### 场景1: 快速准备课堂（5分钟）

1. 打开Web界面
2. 输入: "初中二年级，光合作用，45分钟"
3. 点击生成
4. 立即下载PPT进教室讲课

### 场景2: 深度教学设计（30分钟）

1. 详细填写所有课程信息
2. 上传自己的教学资料
3. 选择喜欢的模板风格
4. 生成后进行编辑优化
5. 最终调整样式和内容

### 场景3: 教材复用与改进（15分钟）

1. 上传去年的教案文本
2. 系统自动重新组织
3. 匹配现代化PPT模板
4. 添加最新的教学资源
5. 导出改进后的版本

---

## 💡 提示与技巧

### 获得最佳结果的建议

1. **明确的输入**
   - 明确指定学生级别
   - 清楚地表述教学目标
   - 说明时间限制

2. **使用模板选择**
   - 学术内容 → 学术风格
   - 商业课程 → 商业风格
   - 创意课程 → 创意风格

3. **上传参考资料**
   - 上传相关的教材章节
   - 提供具体的图片素材
   - 标注重要的概念

4. **迭代优化**
   - 先生成基础版本
   - 进行Web界面编辑
   - 调整和完善细节
   - 最终导出

### 常见问题

**Q: 生成太慢了怎么办？**
- 减少输入的复杂度
- 检查网络连接
- 尝试使用更小的模型配置

**Q: 生成的内容不满意怎么办？**
- 在Web界面直接编辑
- 修改题目重新生成
- 上传更多参考资料

**Q: 如何自定义模板？**
- 编辑 `templates/ppt_templates/template_config.json`
- 修改颜色、字体、布局
- 重启服务应用更改

---

## 📖 相关文档

| 文档 | 内容 | 适合人群 |
|------|------|--------|
| [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) | 系统架构和详细实现 | 开发者 |
| [TEACHING_GUIDE.md](./TEACHING_GUIDE.md) | 使用指南和示例 | 教师用户 |
| [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) | 实现完成情况总结 | 项目评审 |
| [system_test.py](./system_test.py) | 系统功能测试脚本 | QA和开发者 |

---

## 🐛 故障排除

### 服务启动失败

```bash
# 检查Python环境
python --version

# 检查依赖
pip list | grep -i fastapi

# 重新安装依赖
pip install -r requirements.txt
```

### 生成失败

```bash
# 检查API配置
cat config.yaml | grep openai

# 检查RAG数据
ls -la rag_data/

# 查看错误日志
tail -f logs/app.log
```

### 文件导出问题

```bash
# 检查输出目录权限
ls -la generated_lessons/

# 创建必要的目录
mkdir -p generated_lessons/{docx,pptx,json,markdown}
```

---

## 📞 获取帮助

1. **查看日志**: `logs/app.log`
2. **运行测试**: `python system_test.py`
3. **查阅文档**: 项目 `README.md` 和各项指南
4. **检查示例**: `teaching_examples.py`

---

## 🎉 准备好开始了吗？

```bash
# 一键启动
./local.sh

# 打开浏览器
# http://localhost:3367/teaching

# 开始创建你的第一个教案！
```

---

**版本**: 1.0  
**最后更新**: 2024年2月6日

