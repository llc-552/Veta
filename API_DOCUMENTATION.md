# API 文档 - 智能教案与PPT生成系统

## 基础信息

- **基础URL**: `http://localhost:8000`
- **协议**: HTTP REST + WebSocket (SSE)
- **内容类型**: application/json
- **字符编码**: UTF-8

---

## 1. 发送消息接口

### 1.1 同步请求 (Synchronous)

```http
POST /send_message
Content-Type: application/json

{
    "message": "string",
    "mode": "teaching|vet|animal",
    "user_id": "string (optional)",
    "task_id": "string (optional)",
    "rag_enabled": "boolean (optional, default: false)"
}
```

#### 请求参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| message | string | ✓ | 用户输入的课程描述或问题 |
| mode | string | ✓ | 工作模式：teaching（教学助手）、vet（兽医问诊）、animal（动物医院） |
| user_id | string | ✗ | 用户ID，用于会话管理，默认为anonymous_user |
| task_id | string | ✗ | 任务ID，用于特定任务追踪，默认自动生成 |
| rag_enabled | boolean | ✗ | RAG知识库开关（vet模式有效），默认false |

#### 教学模式示例请求

```json
{
    "message": "我需要为高二学生设计一节关于光合作用的生物课，时长50分钟。学生需要理解光反应和暗反应的区别，并能掌握光合作用的方程式。我希望用互动式教学方法。",
    "mode": "teaching",
    "user_id": "teacher_001",
    "task_id": "biology_lesson_001"
}
```

#### 教学模式成功响应 (200 OK)

```json
{
    "response": "教学材料已生成！状态: completed",
    "status": "completed",
    "processing_step": "Export completed",
    "export_result": {
        "lesson_title": "光合作用",
        "export_id": "550e8400-e29b-41d4-a716-446655440000",
        "export_timestamp": "2024-02-04T10:30:45.123456",
        "exports": {
            "lesson_plan": {
                "files": {
                    "docx": {
                        "path": "./generated_lessons/docx/光合作用_20240204_103045.docx",
                        "format": "Word Document (.docx)",
                        "size_mb": 2.5
                    },
                    "json": {
                        "path": "./generated_lessons/json/光合作用_20240204_103045.json",
                        "format": "JSON (.json)",
                        "size_mb": 1.2
                    }
                }
            },
            "ppt": {
                "file": {
                    "path": "./generated_lessons/pptx/光合作用_20240204_103045.pptx",
                    "format": "PowerPoint (.pptx)",
                    "size_mb": 4.8
                }
            }
        }
    },
    "error": null,
    "awaiting_input": false,
    "ended": true
}
```

#### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| response | string | 用户友好的响应消息 |
| status | string | 处理状态：initializing、processing_input、parsing_intent、retrieving_materials、generating_content、matching_template、layouting_slides、exporting、completed、failed |
| processing_step | string | 当前处理步骤的详细描述 |
| export_result | object | 导出结果，包含生成的文件路径 |
| error | string/null | 错误消息（如有） |
| awaiting_input | boolean | 是否等待用户输入 |
| ended | boolean | 处理是否已完成 |

#### 错误响应 (400/500)

```json
{
    "error": "Error message describing what went wrong"
}
```

---

### 1.2 流式请求 (Streaming with SSE)

```http
POST /send_message_stream
Content-Type: application/json

{
    "message": "string",
    "mode": "teaching|vet|animal",
    "user_id": "string (optional)",
    "task_id": "string (optional)"
}
```

#### 响应流格式

使用Server-Sent Events (SSE) 格式进行流式传输：

```
data: {"type": "token", "content": "生成"}\n\n
data: {"type": "token", "content": "的"}\n\n
data: {"type": "token", "content": "文本"}\n\n
data: {"type": "node", "node": "content_generation"}\n\n
data: {"type": "done", "response": "生成的文本", "awaiting_input": false, "ended": true}\n\n
```

#### SSE 事件类型

| 类型 | 数据 | 说明 |
|------|------|------|
| token | {content: string} | 单个token的流式输出 |
| node | {node: string} | 节点处理完成事件 |
| clear | {node: string} | 清除前一个输出 |
| done | {response, awaiting_input, ended} | 处理完成 |
| error | {message: string} | 处理出错 |

---

## 2. 重置会话接口

### 请求

```http
POST /reset
Content-Type: application/json

{
    "mode": "teaching|vet|animal",
    "user_id": "string (optional)",
    "task_id": "string (optional)"
}
```

### 请求参数

| 参数 | 说明 |
|------|------|
| mode | 要重置的模式 |
| user_id | 用户ID（如指定则只清除该用户的会话） |
| task_id | 任务ID（如指定则只清除该任务的会话） |

### 成功响应 (200 OK)

```json
{
    "status": "ok",
    "mode": "teaching"
}
```

---

## 3. 页面路由

### 主页面

```http
GET /
```

返回 HTML 页面，包含所有三种模式的界面。

### 管理页面

```http
GET /admin
```

返回管理员界面。

---

## 使用示例

### Python 示例

```python
import requests
import json

# 教学模式请求
url = "http://localhost:8000/send_message"
payload = {
    "message": "我需要教初中化学的酸碱中和反应，30分钟，学生需要理解反应原理和能量变化。",
    "mode": "teaching",
    "user_id": "teacher_002",
    "task_id": "chemistry_lesson_001"
}

response = requests.post(url, json=payload)
data = response.json()

print(f"状态: {data['status']}")
print(f"处理步骤: {data['processing_step']}")

if data['export_result'] and data['export_result'].get('exports'):
    exports = data['export_result']['exports']
    if 'lesson_plan' in exports:
        docx_file = exports['lesson_plan']['files'].get('docx')
        if docx_file:
            print(f"教案已保存: {docx_file['path']}")
    if 'ppt' in exports:
        ppt_file = exports['ppt']['file']
        print(f"PPT已保存: {ppt_file['path']}")
```

### JavaScript 示例

```javascript
async function generateLesson(theme, grade, subject) {
    const response = await fetch('http://localhost:8000/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: `教学主题：${theme}\n学生年级：${grade}\n学科领域：${subject}`,
            mode: 'teaching',
            user_id: `teacher_${Date.now()}`,
            task_id: `lesson_${Date.now()}`
        })
    });

    const data = await response.json();
    
    if (data.error) {
        console.error('生成失败:', data.error);
    } else {
        console.log('生成成功:', data.export_result);
        // 显示下载链接
        if (data.export_result.files) {
            console.log('教案:', data.export_result.files.docx?.path);
            console.log('PPT:', data.export_result.files.ppt?.path);
        }
    }
}

// 使用流式请求
async function generateLessonStream(theme) {
    const response = await fetch('http://localhost:8000/send_message_stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: theme,
            mode: 'teaching'
        })
    });

    const reader = response.body.getReader();
    
    while (true) {
        const {done, value} = await reader.read();
        if (done) break;
        
        const text = new TextDecoder().decode(value);
        const lines = text.split('\n\n');
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const event = JSON.parse(line.substring(6));
                console.log('事件:', event);
            }
        }
    }
}
```

### cURL 示例

```bash
# 同步请求
curl -X POST http://localhost:8000/send_message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "我需要一节关于分数的小学数学课，30分钟",
    "mode": "teaching",
    "user_id": "teacher_001",
    "task_id": "math_lesson_001"
  }'

# 流式请求
curl -X POST http://localhost:8000/send_message_stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "教学主题：光合作用",
    "mode": "teaching"
  }'

# 重置会话
curl -X POST http://localhost:8000/reset \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "teaching",
    "user_id": "teacher_001",
    "task_id": "math_lesson_001"
  }'
```

---

## 错误处理

### 常见错误代码

| 状态码 | 说明 | 可能原因 |
|--------|------|--------|
| 200 | 成功 | 请求成功处理 |
| 400 | 请求错误 | 参数缺失或格式不正确 |
| 500 | 服务器错误 | API密钥错误、网络问题等 |

### 错误响应示例

```json
{
    "error": "Teaching workflow error: OpenAI API connection failed"
}
```

---

## 速率限制

- 暂无速率限制（生产环境建议添加）
- 建议并发请求数 ≤ 5

---

## 数据大小限制

- 消息最大长度：10000 字符
- 生成文件最大：20 MB
- 上传RAG数据单个文件：100 MB

---

## 身份验证

当前实现无身份验证。生产环境建议添加：
- Bearer Token 验证
- API Key 验证
- OAuth 2.0

---

## 版本信息

- **API版本**: v1.0
- **最后更新**: 2024年2月
- **兼容版本**: Python 3.8+

---

## 常见问题

### Q: 如何获取生成的文件？

A: 文件保存在本地 `generated_lessons/` 文件夹下，可通过响应中的路径访问。

### Q: 如何自定义PPT模板？

A: 在教学请求中选择不同的模板风格（formal/colorful/minimalist/creative）。

### Q: 流式响应何时完成？

A: 当收到 type 为 "done" 的事件时，说明处理完成。

### Q: 如何持续使用同一会话？

A: 保持相同的 user_id 和 task_id，系统将复用已有的工作流实例。

---

**更多信息请参考完整文档**: `TEACHING_GUIDE.md` 和 `IMPLEMENTATION_SUMMARY.md`
