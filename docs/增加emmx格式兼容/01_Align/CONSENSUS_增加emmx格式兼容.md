# CONSENSUS: 增加 emmx 格式兼容

## 1. 需求描述
实现对 MindMaster/EdrawMind `.emmx` 文件的解析，并将其转换为 Markdown 格式。

## 2. 验收标准
1.  **功能**: 用户可以选择 `.emmx` 文件并成功转换为 `.md` 文件。
2.  **内容**: 转换后的 Markdown 文件应准确反映思维导图的层级结构（使用缩进列表）。
3.  **鲁棒性**: 处理非标准或损坏的 emmx 文件时应报错并记录日志，而不是崩溃。
4.  **界面**: GUI 文件选择器应支持 `.emmx` 扩展名。

## 3. 技术实现方案
### 3.1 核心逻辑 (`src/core/converters/emmx.py`)
- 类名: `EmmxConverter` 继承自 `BaseConverter`。
- 方法: `convert(source_path, output_path)`。
- 实现细节:
  1. 使用 `zipfile` 打开 `.emmx` 文件。
  2. 寻找 `doc/document.json` 或 `mindmap.json`（通常是 `doc/document.json`，其中 `models` 字段包含 `map` 数据）。
  3. 解析 JSON，定位到 `topic` (根节点)。
  4. 递归遍历 `children` 或 `topics` 字段。
  5. 生成 Markdown 文本行。
  6. 写入输出文件。

### 3.2 架构集成
- 在 `src/core/converters/__init__.py` 中导出 `EmmxConverter`。
- 在 `src/core/engine.py` 的转换器映射中添加 `.emmx`: `EmmxConverter`。

### 3.3 依赖
- 标准库 `zipfile`, `json`。无需新增第三方依赖。

## 4. 边界限制
- 仅支持文本内容的提取。
- 仅支持标准的 `.emmx` 格式（基于 JSON 的版本）。
- 图片、附件、样式信息将被忽略。
- 复杂的布局（如鱼骨图、时间轴）统一转换为列表结构。

## 5. 风险评估
- **未知的文件结构**: 不同版本的 MindMaster 可能使用不同的 JSON 结构。
  - **对策**: 编写灵活的解析器，先打印 JSON 结构进行调试，或者尝试多种可能的键名 (`text`, `title`, `content`)。
