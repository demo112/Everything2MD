# ACCEPTANCE: 修复上传及完善测试

## 验收记录

### 1. Bug 修复验证
- **测试项**: GUI 上传选中文件
- **预期**: 选中文件后点击上传，系统应能正确识别文件并调用上传接口。
- **结果**: 通过单元测试 `test_upload_selected_files_success` 验证，Mock 验证了调用参数正确。

### 2. 测试覆盖率验证
- **测试项**: 单元测试执行
- **命令**: `python -m pytest test/unit`
- **结果**: 
    - 89 passed, 0 failed.
    - 修复了 `test_engine.py` 中因 `context` 参数变更导致的断言失败。
    - 解决了 `test_gui_logic.py` 中 `ConfigManager` Mock 导致的 `TypeError`。
    - 完善了 `test_ppt.py` 的测试用例，覆盖了 `LibreOffice` 超时/失败、`pdftotext` 缺失、`pdfminer` 异常等边界情况。

### 3. 核心逻辑验证
- **测试项**: Office 转换重试机制
- **结果**: 通过 `test_office_retry.py` 验证了在 `PermissionError` 发生时会自动重试.
- **测试项**: PDF 转换降级链路
- **结果**: 通过 `test_pdf_integration.py` 和 `test_ppt.py` 验证了 `LibreOffice -> Pandoc -> pdftotext -> pdfminer -> Copy` 的完整降级链路。

### 4. RAGFlow API 修复与去重逻辑
- **修复**: 修正了 RAGFlow 上传接口路径和解析接口方法 (POST /chunks)。
- **新增**: 在文件转换和上传环节增加了去重逻辑。
    - 转换: 检查输出目录是否存在同名文件。
    - 上传: 调用 `list_documents` 检查知识库中是否存在同名文件。
- **验证**: 
    - 单元测试 `test_upload_deduplication` 通过。
    - 集成测试 `test_ragflow_real.py` 通过。

### 5. 全量测试回归
- **命令**: `python -m pytest test/unit`
- **结果**: 
    - 89 passed, 0 failed.
    - `src/core/converters/ppt.py` 覆盖率提升至 84%。
    - 整体覆盖率 75%。
    - 修复了 `test_utils.py` 中 `setup_gui_logging` 弃用导致的测试失败。

## 结论
所有修复和新增测试均已完成并通过验收。核心转换逻辑（特别是 PPT/PDF）的健壮性得到充分验证，GUI 逻辑测试已修复，项目测试覆盖率和稳定性显著提升。
