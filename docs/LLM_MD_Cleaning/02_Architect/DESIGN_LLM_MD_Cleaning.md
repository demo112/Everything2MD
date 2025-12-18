# DESIGN: LLM Markdown Cleaning (解析增强 - 结构化清洗)

## 1. 架构设计

本模块将作为 `ConversionEngine` 管道的最后一步（或图片识别之后的一步）。核心逻辑封装在 `src/core/structure_cleaner.py` 中。

```mermaid
graph TD
    A[ConversionEngine] -->|MD File| B{Cleaning Enabled?}
    B -->|No| C[End]
    B -->|Yes| D[StructureCleaner.clean_markdown]
    D --> E[Read Original MD]
    E --> F[Call LLM (Streaming/Blocking)]
    F --> G[Get Cleaned Content]
    G --> H{Integrity Check}
    H -->|Pass| I[Overwrite MD File]
    H -->|Fail| J[Log Warning & Discard]
    I --> C
    J --> C
```

## 2. 模块设计

### 2.1 `src/core/structure_cleaner.py`
- **类**: `StructureCleaner`
- **依赖**: `ConfigManager`, `httpx`
- **方法**:
    - `__init__(self, config_manager)`: 加载配置。
    - `async clean_markdown(self, file_path: Path) -> bool`: 主入口。
    - `_call_llm(self, content: str) -> str`: 执行 API 调用。
    - `_verify_integrity(self, original: str, cleaned: str) -> bool`: 核心校验逻辑。
    - `_strip_markdown(self, content: str) -> str`: 辅助方法，去除 MD 标记提取纯文本。

### 2.2 `src/core/config.py`
- 扩展 `get_default_config` 和 `ConfigManager` 以支持新字段：
    - `structure_cleaning.enabled`
    - `structure_cleaning.api_base`
    - `structure_cleaning.api_key`
    - `structure_cleaning.model`

### 2.3 `src/gui/main.py`
- 修改 `init_parsing_tab`:
    - 将现有 "图片识别" 放入一个 `LabelFrame`。
    - 新增 "结构化清洗" `LabelFrame`。
    - 绑定相关变量。

## 3. 校验算法 (`_strip_markdown`) 细节
为了确保 "一个字符都不变"，直接对比纯文本可能过于严格（例如 LLM 可能会调整空行、空白字符）。
**修正策略**:
1.  **Normalization**: 
    - 去除所有 Markdown 符号 (`#`, `*`, `-`, `>`, `[]`, `()`, `` ` ``)。
    - 将连续空白字符 (空格, Tab, 换行) 替换为单个空格。
    - 去除首尾空白。
2.  **Comparison**: 
    - 对比规范化后的字符串。
    - 这样允许 LLM 调整段落间距、列表缩进，但一旦修改了文字内容（汉字、单词、标点），校验将失败。

## 4. Prompt 设计
```text
You are a Markdown formatting expert.
Task: Reformat the provided Markdown content to strictly follow best practices (CommonMark/GFM).
Rules:
1. Fix heading levels (ensure hierarchy is logical).
2. Fix list indentation and markers.
3. Fix table formatting.
4. Ensure code blocks are properly fenced.
5. CRITICAL: DO NOT CHANGE, ADD, OR REMOVE ANY TEXT CONTENT. DO NOT CHANGE PUNCTUATION.
6. CRITICAL: KEEP ALL IMAGES AND LINKS EXACTLY AS IS.
Input follows:
```

## 5. 接口定义
无需新增对外接口，仅作为内部工具类被 `ConversionEngine` 调用。
