# TASK: 文件重复校验与版本管理

## 1. 任务拆分

### Task 1: 核心工具库扩展
- [x] 在 `src/core/utils.py` 中实现 `calculate_file_hash`。
- [x] 编写单元测试 `test/unit/core/test_utils_hash.py`。

### Task 2: RAGFlow 客户端增强
- [x] 在 `src/core/ragflow_client.py` 中实现 `delete_documents`。
- [x] 编写单元测试 `test/unit/core/test_ragflow_client_delete.py`。

### Task 3: 文件名解析逻辑
- [x] 在 `src/gui/main.py` 中实现 `_parse_versioned_filename`。
- [x] 编写单元测试 `test/unit/gui/test_filename_parsing.py`。

### Task 4: GUI 上传流程重构
- [x] 修改 `src/gui/main.py` 的 `_bg_upload` 方法。
- [x] 集成 Hash 计算。
- [x] 集成 知识库文件列表获取与比对。
- [x] 集成 旧版本删除逻辑。
- [x] 集成 版本化重命名上传逻辑。

### Task 5: 验证与验收
- [x] 运行所有单元测试。
- [x] 编写验收报告。

## 2. 依赖关系
Task 1, 2, 3 可并行开发。
Task 4 依赖 Task 1, 2, 3。
Task 5 依赖 Task 4。
