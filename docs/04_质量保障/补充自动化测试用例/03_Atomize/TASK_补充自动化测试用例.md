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

### 3.4 (新增) GUI 模块测试
- **任务目标**: 验证 `src/gui/main.py` 的核心交互逻辑。
- **输入**: Mock 的 Tkinter 上下文。
- **输出**: `tests/test_gui_main.py`。
- **测试点**:
    - `test_init`: 验证 GUI 初始化及配置加载。
    - `test_browse_input`: 验证文件选择对话框逻辑。
    - `test_start_conversion`: 验证“开始转换”按钮正确调用 Engine。
    - `test_connect_rag`: 验证 RAGFlow 连接逻辑及下拉框更新。
    - `test_log_queue`: 验证日志队列处理逻辑。

## 4. 任务依赖图
