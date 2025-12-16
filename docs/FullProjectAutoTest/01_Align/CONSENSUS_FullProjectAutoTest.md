# 项目共识文档 (CONSENSUS)

## 1. 需求确认
- **目标**: 实现全项目自动化测试，覆盖率 > 80%，核心功能覆盖率 100%。
- **范围**: `src` 目录下的所有 Python 代码，重点是 `src/core`。

## 2. 技术实现方案
- **测试框架**: `pytest`
- **覆盖率工具**: `pytest-cov`
- **Mock 工具**: `pytest-mock`
- **策略**:
    1.  **Core 模块**: 针对 `office.py`, `engine.py`, `ragflow_client.py`, `utils.py` 编写详细的单元测试。利用 `mock` 模拟外部依赖（如 subprocess 调用、HTTP 请求、文件系统操作），确保覆盖所有分支（包括异常处理）。
    2.  **GUI 模块**: 针对 `main.py` 中的逻辑部分编写测试，Mock `tkinter` 对象以避免 GUI 弹窗阻塞测试。
    3.  **Utils 模块**: 补充所有工具函数的单元测试，覆盖各种边界输入。

## 3. 验收标准
- 运行 `python run_tests.py` 输出的覆盖率报告满足：
    - `src/core` 下所有模块: 100%
    - `TOTAL`: > 80%
- 所有测试用例通过。
- 不引入新的 lint 错误。

## 4. 风险控制
- **GUI 测试复杂性**: 如果 `tkinter` 难以 mock，将提取逻辑到独立类中测试。
- **环境差异**: 所有涉及外部命令的测试都必须有 Mock 路径，确保在无 LibreOffice 环境下也能运行并覆盖代码逻辑。
