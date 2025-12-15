# TASK: 修复上传及完善测试

## 任务分解

- [x] **修复上传 Bug**
    - [x] 定位 `src/gui/main.py` 中的索引错误。
    - [x] 修正为 `vals[1]` 获取文件名。

- [x] **完善测试用例**
    - [x] 创建 `test/unit/gui/test_rag_upload.py`，覆盖上传选择逻辑。
    - [x] 创建 `test/unit/core/converters/test_office_retry.py`，覆盖文件占用重试逻辑。
    - [x] 修正 `test/unit/core/test_engine.py` 以适配新的回调签名。

- [x] **回归验证**
    - [x] 运行所有单元测试 (`python -m pytest test/unit`)。
    - [x] 验证覆盖率提升。
