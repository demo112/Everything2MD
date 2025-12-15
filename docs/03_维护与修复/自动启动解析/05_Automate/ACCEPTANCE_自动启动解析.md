# ACCEPTANCE: 自动启动解析

## 验收记录

### 1. 自动解析功能验证
- **测试项**: 文件上传后自动解析
- **预期**: 上传成功后，代码应自动提取 doc_id 并调用 run_parsing 接口。
- **结果**: 通过单元测试 `test_rag_upload.py` 验证：
    - Mock 了上传返回 `{'id': 'doc_id_123'}`。
    - 断言 `ragflow_client.run_parsing` 被调用，参数为 `('kb_id_123', ['doc_id_123'])`。

### 2. UI 状态反馈验证
- **测试项**: UI 状态更新
- **预期**: 状态栏或列表状态应显示解析相关信息。
- **结果**: 代码中已添加 `self.rag_file_list.set(..., value='已启动解析')`，测试虽未直接断言 UI 文本变化（因 Mock 了 Treeview），但逻辑路径已覆盖。

## 结论
功能已实现并通过单元测试验收。
