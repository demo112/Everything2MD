# TASK_PPT转换修复

## 任务列表

### 1. 依赖管理
- [ ] **Task 1.1**: 更新 `requirements.txt` 添加 `pptx2md` 和 `python-pptx`。
- [ ] **Task 1.2**: 安装新依赖到虚拟环境。

### 2. 代码修复
- [ ] **Task 2.1**: 检查并优化 `src/core/converters/ppt.py` 中的 `_convert_pptx` 方法，确保正确导入和调用 `pptx2md`。
- [ ] **Task 2.2**: 增强 `src/core/converters/ppt.py` 的错误处理，完善日志记录。

### 3. 测试验证
- [ ] **Task 3.1**: 创建 PPTX 转换的集成测试用例 `tests/test_ppt_conversion.py`。
- [ ] **Task 3.2**: 运行测试验证修复结果。
- [ ] **Task 3.3**: 手动验证（如果自动化测试难以覆盖 LibreOffice 环境）。

## 依赖关系
Task 1.1 -> Task 1.2 -> Task 2.1 -> Task 2.2 -> Task 3.1 -> Task 3.2
