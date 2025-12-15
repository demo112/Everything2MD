# ACCEPTANCE: 完善测试体系

## 1. 验收概览
| 验收项 | 状态 | 说明 |
| :--- | :--- | :--- |
| OfficeConverter 测试 | ✅ 已完成 | 覆盖了 LibreOffice 正常/异常/重试，Pandoc 降级等场景 |
| PptConverter 测试 | ✅ 已完成 | 覆盖了 pptx2md, LibreOffice 降级场景 |
| Web API 测试 | ✅ 已完成 | 覆盖了 config 读写，文件列表，WebSocket 连接 |
| RAGFlowClient 测试 | ✅ 已完成 | 增加了 API 错误和文件缺失测试 |
| 覆盖率提升 | ✅ 已完成 | 核心逻辑覆盖率提升至 60% (Office: 73%, PPT: 87%) |
| 去重逻辑测试 | ✅ 已完成 | 覆盖了上传去重和转换去重逻辑 |

## 2. 详细验收记录

### Task 1: Converters 测试
- [x] `test_office.py`: 成功 Mock 了 `subprocess.run` 和路径检查，验证了重试逻辑。
- [x] `test_ppt.py`: 成功 Mock 了 `pptx2md` 模块导入和降级逻辑。

### Task 2: Web API 测试
- [x] `test_web_api.py`: 修复了 Mock 逻辑，增加了 `fs_list` 和 `websocket` 测试。

### Task 3: 整体质量
- 所有 29 个测试用例全部通过。
- 修复了 `test_fs_list_api` 中的类型错误。
- 修复了 `test_office.py` 和 `test_ppt.py` 中的缩进和 Mock 副作用路径问题。

### Task 4: 新增功能测试 (Deduplication & RAGFlow)
- [x] `test_rag_upload.py`: 增加了 `test_upload_deduplication` 测试用例，验证了重复文件跳过逻辑。
- [x] `test_ragflow_real.py`: 集成测试通过。
- [x] `test_office.py`: 修复了 Mock 路径索引问题 (Index 5 -> 6)，解决了 `test_convert_docx_success` 失败问题。

### Task 5: 最新测试状态 (2025-12-15)
- **全量测试**: `python -m pytest`
- **结果**: 38 passed, 0 failed.
- **覆盖率**: 保持在较高水平，关键路径覆盖完整。

## 3. 遗留问题与改进
- **GUI 覆盖率**: `src/gui/main.py` 覆盖率仍为 50%。由于 Tkinter 测试较难完全模拟（涉及事件循环），当前主要覆盖了 ViewModel 逻辑。后续可引入 `pytest-tk` 进行更深度的测试。
- **Utils 覆盖率**: `src/core/utils.py` (40%) 包含一些特定平台的路径检测逻辑，在单一测试环境下难以全覆盖。
