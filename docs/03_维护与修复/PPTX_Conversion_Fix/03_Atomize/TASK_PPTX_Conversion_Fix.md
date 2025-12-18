# TASK_PPTX_Conversion_Fix

## 任务列表

### 1. 复现与验证
- [ ] **Task 1.1**: 创建复现脚本 `reproduce_issue.py`，模拟 `pptx2md` 调用并验证 Path 对象导致的问题。
- [ ] **Task 1.2**: 创建最小化测试 PPTX 文件 `test_sample.pptx` (使用 python-pptx 生成)。

### 2. 代码修复
- [ ] **Task 2.1**: 修改 `src/core/converters/ppt.py`，实现 `_get_pptx2md_executable` 方法。
- [ ] **Task 2.2**: 修改 `src/core/converters/ppt.py` 中的 `_convert_pptx` 方法，确保传给 `ConversionConfig` 的路径参数为字符串。
- [ ] **Task 2.3**: 修改 `src/core/converters/ppt.py` 中的命令行回退逻辑，使用 `_get_pptx2md_executable` 返回的路径。

### 3. 验证与验收
- [ ] **Task 3.1**: 运行 `reproduce_issue.py` (修改后应作为验证脚本) 确认库调用修复。
- [ ] **Task 3.2**: 运行全量测试，确保未引入回归问题。
- [ ] **Task 3.3**: 更新 `ACCEPTANCE` 文档。

## 依赖关系
Task 1.1 -> Task 1.2 -> Task 2.1 -> Task 2.2 -> Task 2.3 -> Task 3.1
