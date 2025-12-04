# 需求对齐：环境配置修复

## 1. 问题描述
用户反馈在终端执行命令时，IDE 自动尝试激活虚拟环境 `venv\Scripts\Activate.ps1`，但报错：
`无法加载文件 ... 因为在此系统上禁止运行脚本。`
错误代码：`UnauthorizedAccess`。

## 2. 原因分析
Windows PowerShell 默认的执行策略（Execution Policy）通常为 `Restricted`，禁止运行任何脚本。
要运行 `Activate.ps1`，需要将策略调整为允许本地脚本运行（如 `RemoteSigned`）。

## 3. 解决方案
使用 PowerShell 命令修改当前用户的执行策略。
命令：`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`。

## 4. 预期结果
执行修复命令后，再次尝试激活虚拟环境应不再报错。
这将确保后续所有依赖 Python 虚拟环境的操作（如果有的话）也能顺畅执行。
