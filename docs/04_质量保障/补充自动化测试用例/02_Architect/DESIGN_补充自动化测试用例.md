# DESIGN: 补充自动化测试用例

## 1. 整体架构
- **测试框架**: `pytest`
- **Mock 工具**: `unittest.mock` (Python 标准库)
- **目标目录**: `tests/`
- **新增文件**:
  - `tests/test_ragflow_client.py`
  - `tests/test_ppt_converter.py`
  - `tests/test_office_converter.py`

## 2. 详细设计

### 2.1 RAGFlowClient 测试设计 (`tests/test_ragflow_client.py`)
- **Setup**: `pytest.fixture` 创建 `RAGFlowClient` 实例。
- **Test Cases**:
  - `test_list_datasets_success`: 
    - Mock `httpx.Client.get` 返回 `{"code": 0, "data": [...]}`。
    - 验证 `list_datasets` 返回正确列表。
  - `test_list_datasets_api_error`:
    - Mock 返回 `{"code": 1, "message": "error"}`。
    - 验证抛出 `Exception`。
  - `test_create_dataset_success`:
    - Mock `httpx.Client.post` 返回成功。
  - `test_upload_document_success`:
    - Mock `open` (使用 `mock_open`) 和 `httpx.Client.post`。
    - 验证 `files` 参数构建正确。
  - `test_upload_document_file_not_found`:
    - 验证文件不存在时抛出 `FileNotFoundError`。

### 2.2 PptConverter 测试设计 (`tests/test_ppt_converter.py`)
- **Setup**: `pytest.fixture` 创建 `PptConverter` 实例。
- **Test Cases**:
  - `test_convert_pptx_with_pptx2md`:
    - Mock `pptx2md.entry.convert` 和 `pptx2md.types.ConversionConfig`。
    - 验证 `_convert_pptx` 被调用且未触发异常。
  - `test_convert_ppt_libreoffice`:
    - Mock `input_path.suffix` 为 `.ppt`。
    - Mock `subprocess.run` 模拟 LibreOffice 调用成功。
    - 验证命令参数包含 `--headless` 和正确的输出路径。
  - `test_convert_pptx_fallback`:
    - 模拟 `pptx2md` 导入失败或执行失败。
    - 验证是否降级调用 LibreOffice 逻辑。

### 2.3 OfficeConverter 测试设计 (`tests/test_office_converter.py`)
- **Setup**: `pytest.fixture` 创建 `OfficeConverter` 实例。
- **Test Cases**:
  - `test_convert_docx_libreoffice`:
    - Mock `get_soffice_path` 返回有效路径。
    - Mock `subprocess.run` 成功。
    - 验证命令参数。
  - `test_convert_docx_pandoc_fallback`:
    - Mock `get_soffice_path` 返回 None。
    - Mock `get_pandoc_path` 返回有效路径。
    - Mock `subprocess.run` 验证 Pandoc 调用。
  - `test_convert_no_converter`:
    - Mock 两者都不可用，验证抛出 `RuntimeError`。
  - `test_file_copy_retry`:
    - Mock `shutil.copy` 抛出 `PermissionError` 几次后成功。
    - 验证重试逻辑（这部分逻辑在 `convert` 方法开头）。

## 3. 接口规范
- 测试函数命名：`test_<function_name>_<scenario>`
- 所有的外部 IO 操作（文件读写、网络请求、子进程）必须被 Mock，确保测试在无环境依赖下运行。

## 4. 依赖关系
- `src.core.ragflow_client`
- `src.core.converters.ppt`
- `src.core.converters.office`
- `src.core.utils` (可能需要 Mock `log_info`, `log_error` 以避免控制台噪音)
