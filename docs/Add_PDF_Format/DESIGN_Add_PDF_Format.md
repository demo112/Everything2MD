# 增加文档目标格式：PDF - Design Document

## 1. 架构概览
本次修改主要涉及 `src/core/engine.py` 中的任务生成逻辑，以及 `src/core/converters` 中的具体转换逻辑。GUI 层 `src/gui/fixed_main_v2.py` 也需要适配以提供选项。

```mermaid
graph TD
    GUI[GUI (FixedEverything2MDGUI)] -->|Load/Save Config| Config[Config Manager]
    GUI -->|Start Conversion| Engine[ConversionEngine]
    Engine -->|Read Config| Config
    Engine -->|Dispatch Task| OfficeConverter
    Engine -->|Dispatch Task| PptConverter
    OfficeConverter -->|LibreOffice| PDF[PDF File]
    PptConverter -->|LibreOffice| PDF
```

## 2. 详细设计

### 2.1 Engine 层设计 (`src/core/engine.py`)
- **修改点**: `_run_task` 调度前的任务生成逻辑 (在 `run` 或类似方法中，具体是 `convert_directory` 或 `run` 方法)。
- **逻辑**:
  - 读取配置 `self.config.get("output_format", "markdown")`。
  - 根据格式决定后缀：
    - `markdown` -> `.md`
    - `html` -> `.html`
    - `txt` -> `.txt`
    - `pdf` -> `.pdf`
  - 将此后缀用于构造 `out_file`。

### 2.2 Converter 层设计

#### 2.2.1 `OfficeConverter` (`src/core/converters/office.py`)
- **修改点**: `convert` 方法。
- **逻辑**:
  - 获取 `output_path.suffix`。
  - 如果后缀是 `.pdf`:
    - 构造 LibreOffice 命令时，使用 `--convert-to pdf`。
    - 输出目录仍为临时目录，生成后移动到 `output_path`。
    - 跳过后续的 Pandoc (HTML -> MD) 步骤。

#### 2.2.2 `PptConverter` (`src/core/converters/ppt.py`)
- **修改点**: `convert` 方法。
- **逻辑**:
  - 获取 `output_path.suffix`。
  - 如果后缀是 `.pdf`:
    - 如果输入是 `.pptx`，跳过 `pptx2md`，直接使用 LibreOffice 转 PDF（调用 `_convert_ppt` 逻辑或抽取公共逻辑）。
    - 如果输入是 `.ppt`，使用 LibreOffice 转 PDF。
    - 如果输入是 `.pdf`，直接复制输入文件到输出文件。

### 2.3 GUI 层设计 (`src/gui/fixed_main_v2.py`)
- **修改点**: 
  - `validate_config`: 允许 `pdf` 格式。
  - `create_general_tab`: 下拉框增加 `pdf` 选项。

## 3. 接口契约
- `ConversionEngine` 不需要改变公开方法的签名，但行为会根据 Config 改变。
- `BaseConverter.convert(input_path, output_path, **kwargs)`: 契约不变，通过 `output_path` 传递意图。

## 4. 异常处理
- 如果用户选择 PDF 但没有安装 LibreOffice，抛出明确错误。
- 如果用户选择 PDF 但输入是 Text (且不支持转换)，记录警告并跳过或复制原文件。

## 5. 数据流向
1. User Selects "pdf" in GUI -> Config Saved.
2. Engine Starts -> Reads Config -> format="pdf".
3. Engine scans files -> Generates output paths with `.pdf` suffix.
4. Engine calls Converter with `output_path=".../doc.pdf"`.
5. Converter sees `.pdf` suffix -> Executes PDF conversion logic.
