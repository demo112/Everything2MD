# LibreOffice启动超时修复 - 需求理解与共识

## 1. 问题描述
用户反馈在运行打包后的 App 时，LibreOffice 启动失败。
错误信息：`TypeError: Popen.__init__() got an unexpected keyword argument 'timeout'`

## 2. 根本原因分析
- 代码位置：`src/core/converters/ppt.py` 和 `src/core/converters/office.py` 中的 `_run_subprocess` 方法。
- 逻辑缺陷：
  - 当传入 `context` 时，代码使用 `subprocess.Popen` 启动进程。
  - 调用 `subprocess.Popen(cmd, **kwargs)` 时，直接透传了 `kwargs`。
  - 业务逻辑中传入了 `timeout` 参数（例如 `timeout=120`）。
  - `subprocess.Popen` 的构造函数不支持 `timeout` 参数（该参数仅适用于 `wait` 或 `communicate`）。
  - 因此引发 `TypeError`。

## 3. 漏测原因分析
- **测试覆盖不足**：
  - 现有测试用例要么未传入 `context`（走 `subprocess.run` 分支，支持 `timeout`）。
  - 要么传入 `context` 但未传入 `timeout`。
  - 要么过度 Mock 了 `_run_subprocess`，直接测试了 Mock 对象而非真实逻辑。
- **Mock 粒度问题**：部分测试绕过了 `_run_subprocess` 内部实现，未能暴露参数传递错误。

## 4. 修复目标
1. 修复代码中的参数传递错误。
2. 完善测试用例，覆盖“Context + Timeout”组合场景。
3. 确保修复后 App 能正常运行。
