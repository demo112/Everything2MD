# TASK: 自动启动解析

## 任务分解

- [x] **实现自动解析逻辑**
    - [x] 修改 `src/gui/main.py`，解析上传响应，提取 `doc_id`。
    - [x] 调用 `ragflow_client.run_parsing`。
    - [x] 添加 UI 状态反馈。

- [x] **更新测试用例**
    - [x] 修改 `test/unit/gui/test_rag_upload.py`，Mock 上传响应包含 ID。
    - [x] 验证 `run_parsing` 被调用且参数正确。

- [x] **回归验证**
    - [x] 运行单元测试 `python -m pytest test/unit/gui/test_rag_upload.py`。
