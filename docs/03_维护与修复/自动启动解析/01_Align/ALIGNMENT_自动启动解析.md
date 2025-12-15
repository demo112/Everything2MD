# ALIGNMENT: 自动启动解析

## 1. 需求背景
用户反馈：上传文件后，系统并未自动启动解析（Parsing）流程。
用户期望：文件上传成功后，应自动触发 RAGFlow 的解析任务。

## 2. 问题分析
- **现状**: `src/gui/main.py` 中的 `upload_selected_files` 方法仅调用了 `ragflow_client.upload_document`，并在上传成功后更新 UI 状态为“已上传”，并未调用 `run_parsing` 接口。
- **原因**: 开发时仅实现了上传功能，解析功能被注释或未实现。

## 3. 解决方案
1. **修改 GUI 逻辑**: 
    - 在 `upload_selected_files` 中，获取 `upload_document` 返回的文档 ID。
    - 调用 `ragflow_client.run_parsing(kb_id, doc_ids)` 触发解析。
    - 更新 UI 状态为“已启动解析”。
2. **验证测试**:
    - 更新 `test/unit/gui/test_rag_upload.py`，验证 `run_parsing` 是否被正确调用。

## 4. 验收标准
- [x] 上传文件后，自动调用解析接口。
- [x] UI 状态正确显示（如“触发解析...”、“已启动解析”）。
- [x] 单元测试通过。
