# 增加文档目标格式：PDF - Consensus Document

## 1. 需求描述
用户希望在 Everything2MD 工具中增加 PDF 作为输出格式选项。这意味着用户可以将 Office 文档和 PPT 文档转换为 PDF 文件，而不仅仅是 Markdown。

## 2. 验收标准
1.  **GUI 选项**: 在配置界面的“输出格式”下拉菜单中可以看到并选择 "pdf"。
2.  **配置保存**: 选择 "pdf" 后，配置可以正常保存并持久化。
3.  **功能实现**:
    - Word (.doc, .docx) -> PDF: 转换成功，内容一致。
    - Excel (.xls, .xlsx) -> PDF: 转换成功。
    - PPT (.ppt, .pptx) -> PDF: 转换成功。
    - PDF -> PDF: 直接复制，内容不变。
4.  **错误处理**: 如果输入是不支持转 PDF 的格式（如纯文本且无 Pandoc PDF 引擎支持），应给出提示或跳过。

## 3. 技术实现方案
### 3.1 GUI 修改
- 修改 `src/gui/fixed_main_v2.py`:
  - `validate_config`: 在 `valid_formats` 列表中添加 `"pdf"`。
  - `create_general_tab`: 在 `output_format_combo` 的 values 中添加 `"pdf"`。

### 3.2 核心逻辑修改
- 修改 `src/core/converters/office.py`:
  - 在 `convert` 方法中，检查 `output_path.suffix`。
  - 如果后缀是 `.pdf`，设置 LibreOffice 参数 `--convert-to pdf`。
  - 确保复制/重命名逻辑适配 PDF。
- 修改 `src/core/converters/ppt.py`:
  - 在 `convert` 方法中，如果 `output_path.suffix == '.pdf'`:
    - 跳过 `pptx2md` 逻辑。
    - 使用 LibreOffice 进行转换（类似 OfficeConverter 的逻辑）。
- 修改 `src/core/engine.py` (如有必要):
  - 确保在生成 `output_path` 时，如果配置了 PDF 格式，生成 `.pdf` 后缀的路径。
  - *注*: `engine.py` 的 `convert_file` 接收的是 `output_path`，所以生成路径的逻辑可能在调用方（如 `batch_processor` 或 GUI 的调用逻辑中）。需要检查是谁调用了 `engine.convert_file`。

### 3.3 调用逻辑检查
- 需要检查 `src/gui/fixed_main_v2.py` 或其他地方是如何调用 `engine` 的，确保传入的 `output_path` 扩展名正确。
- 如果 GUI 只是保存配置，实际运行是靠脚本或另外的 Python 代码，需要检查那个执行者。

## 4. 任务边界
- 本次任务不包含 Text -> PDF 的实现（依赖复杂）。
- 本次任务不包含复杂的 PDF 样式定制。

## 5. 遗留问题/待确认
- 确认是谁在调用 `ConversionEngine.convert_file` 并构造 `output_path`。
  - 搜索代码库中 `convert_file` 的调用。
