# ALIGNMENT: 完善测试体系

## 1. 项目上下文分析
当前项目覆盖率仅 48%。主要缺失在于对外部工具（LibreOffice, Pandoc, pptx2md）调用的模拟，以及 Web API 的全面测试。

## 2. 原始需求与理解
用户要求“完善整个项目的测试”。
这意味着不仅要覆盖核心逻辑，还要尽可能覆盖边界条件、异常处理和外部依赖交互。

**核心目标**:
1.  **OfficeConverter 测试**: 模拟 LibreOffice 和 Pandoc 的调用。
2.  **PptConverter 测试**: 模拟 `pptx2md` 和 LibreOffice 的调用。
3.  **Web API 测试**: 覆盖所有 API 端点（GET/POST config, WebSocket, FS list）。
4.  **RAGFlowClient**: 增加异常场景测试。
5.  **提升覆盖率**: 目标 > 70%。

## 3. 智能决策与策略

### 3.1 外部依赖 Mock 策略
*   **subprocess.run**: 使用 `unittest.mock.patch` 拦截。
    *   正常场景：模拟 `returncode=0`。
    *   异常场景：模拟 `CalledProcessError`。
*   **文件系统操作**: 继续利用 `tmp_path` fixture。
*   **工具路径检测**: Mock `get_soffice_path` 和 `get_pandoc_path`。

### 3.2 任务拆解
1.  `test/unit/core/converters/test_office.py`: 测试 DOCX/DOC 转换。
2.  `test/unit/core/converters/test_ppt.py`: 测试 PPTX/PPT 转换。
3.  `test/integration/test_web_api.py`: 完善 API 测试。
4.  `test/unit/core/test_ragflow_client.py`: 增加异常测试。

## 4. 验收标准
1.  所有新测试通过。
2.  覆盖率显著提升（目标 70%+）。
3.  无遗留的明显逻辑未测试区域。
