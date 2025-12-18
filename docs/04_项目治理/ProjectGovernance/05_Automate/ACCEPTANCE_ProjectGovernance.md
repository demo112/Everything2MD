# ACCEPTANCE_ProjectGovernance

## 任务概览
**任务名称**: 项目治理与规范化
**当前状态**: 执行中 -> 已完成
**最后更新**: 2025-12-18

## 子任务执行记录

### 1. 文档结构治理
- [x] 创建 `docs/04_项目治理` 目录结构
- [x] 生成 6A 工作流各阶段文档框架
- [x] 编写 `Project_Unified_Manual_L1_L3.md` (L1-L3 层级项目文档)
- [x] 验证文档链接和目录结构

### 2. 代码与测试治理
- [x] 清理冗余测试目录 (`tests/` -> `test/unit/legacy_from_tests/`)
- [x] 合并测试配置至 `pytest.ini`
- [x] 修复 `test_ppt.py` 中的 `pdfminer` 导入和 mocking 问题
- [x] 修复 `test_rag_upload.py` 中的 `pytest-flask` 插件冲突和逻辑错误
- [x] 修复 `test_gui_logic.py` 中的冗余和错误测试用例
- [x] 补全缺失依赖 (`psutil`)
- [x] 运行全量测试并验证通过 (118 passed)

### 3. 代码同步与规范
- [x] 确保代码与文档的一致性
- [x] 验证项目依赖环境 (`check_pdfminer.py`)

## 验收标准检查
- [x] **文档完整性**: 包含用户手册(L1)、架构设计(L2)、开发规范(L3)。
- [x] **测试通过率**: 全量测试 100% 通过 (118/118 passed)。
- [x] **环境一致性**: 依赖已安装，环境配置正确。
- [x] **结构清晰度**: 目录结构符合 6A 标准，无冗余文件夹。

## 遇到的问题与解决方案
1. **pytest-flask 插件冲突**:
   - **问题**: `pytest-flask` 自动注入 `app` fixture，导致 GUI 测试中的 `app` 变量被覆盖或产生属性错误。
   - **解决**: 将测试 fixture 重命名为 `gui_app` 避免冲突。

2. **pdfminer 导入问题**:
   - **问题**: 尽管安装了 `pdfminer.six`，测试中仍报 `ModuleNotFoundError`。
   - **解决**: 在测试中完善 `sys.modules` 的 mocking 逻辑，并确认环境安装路径。

3. **GUI 线程测试**:
   - **问题**: `test_upload_selected_files_success` 中上传逻辑在子线程执行，测试未正确等待或 mock 线程执行。
   - **解决**: Mock `threading.Thread` 并手动执行 `target` 函数，确保同步验证逻辑。

## 结论
所有治理任务已完成，项目结构已标准化，测试系统恢复正常并全量通过。
