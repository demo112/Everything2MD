# DESIGN: 带上下文的图片解析

## 1. 模块设计

### 1.1 配置模块 (`src/core/config.py`)

增加配置项：
- Key: `img_rec_context_length`
- Type: `int`
- Default: `500`
- Description: 图片识别时提取的上下文文本长度（前后各 N 字符）。

### 1.2 图片识别模块 (`src/core/image_recognition.py`)

#### `_process_markdown_async` 方法更新

**逻辑变更**:
在遍历 `matches` 时，利用 `match.start()` 和 `match.end()` 计算切片范围。

```python
# 伪代码
context_len = self.config.get("img_rec_context_length", 500)
start, end = match.span()

# 提取前文
prev_start = max(0, start - context_len)
prev_text = content[prev_start:start]

# 提取后文
next_end = min(len(content), end + context_len)
next_text = content[end:next_end]

context = f"Previous text:\n{prev_text}\n\nNext text:\n{next_text}"
```

#### `_process_single_image` 方法更新

**签名变更**:
```python
async def _process_single_image(
    self,
    image_path: Path,
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    index: int,
    total: int,
    context: str = ""  # 新增参数
) -> str:
```

**Payload 变更**:
在 `messages` 的 `content` 中，追加 Context 信息。

```python
prompt_text = """...Existing Prompt...

Context from document:
\"\"\"
{context}
\"\"\"
"""
```

## 2. 数据流

1.  `_process_markdown_async` 读取 MD 内容。
2.  正则匹配找到图片。
3.  切片获取上下文。
4.  调用 `_process_single_image(..., context=...)`。
5.  构造包含上下文的 Prompt。
6.  LLM 返回结果。
7.  结果回填 MD。

## 3. 兼容性

-   旧的配置文件如果没有 `img_rec_context_length`，代码应使用默认值 500。
-   如果上下文为空（例如只有一张图片的文档），Prompt 应适配处理或直接留空。
