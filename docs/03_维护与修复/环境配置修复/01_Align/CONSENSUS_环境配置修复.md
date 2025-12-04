# 共识文档：环境配置修复

## 1. 目标
解除 PowerShell 脚本执行限制，允许虚拟环境激活脚本运行。

## 2. 操作步骤
1.  **检查当前策略**：`Get-ExecutionPolicy -List`
2.  **修改策略**：
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    ```
    *注：使用 `CurrentUser` 作用域通常无需管理员权限即可生效。*

## 3. 验证
重新运行激活脚本：`& .\venv\Scripts\Activate.ps1`，确认无报错。
