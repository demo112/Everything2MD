# TASK: 补充自动化测试用例

## 任务清单

### Task 1: 实现 RAGFlowClient 测试
- **文件**: `tests/test_ragflow_client.py`
- **依赖**: `src/core/ragflow_client.py`
- **输入**: Mock 数据
- **输出**: 通过的测试用例
- **验收标准**:
  - `pytest tests/test_ragflow_client.py` 通过。
  - 覆盖 `list_datasets`, `create_dataset`, `upload_document` 的正常和异常路径。

### Task 2: 实现 PptConverter 测试
- **文件**: `tests/test_ppt_converter.py`
- **依赖**: `src/core/converters/ppt.py`
- **输入**: Mock 对象
- **输出**: 通过的测试用例
- **验收标准**:
  - `pytest tests/test_ppt_converter.py` 通过。
  - 覆盖 PPTX (pptx2md) 和 PPT (LibreOffice) 路径。
  - 验证降级逻辑。

### Task 3: 实现 OfficeConverter 测试
- **文件**: `tests/test_office_converter.py`
- **依赖**: `src/core/converters/office.py`
- **输入**: Mock 对象
- **输出**: 通过的测试用例
- **验收标准**:
  - `pytest tests/test_office_converter.py` 通过。
  - 覆盖 LibreOffice 和 Pandoc 路径。
  - 验证文件复制重试逻辑。

### Task 4: 整体回归测试
- **动作**: 运行 `pytest`
- **验收标准**: 所有新旧测试用例全部通过。
