# 任务分解：环境配置修复

## 任务列表

- [ ] **T1. 修改执行策略**
  - 执行命令解除限制。
  - 命令：`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force`

- [ ] **T2. 验证修复**
  - 尝试手动激活虚拟环境。
  - 命令：`& ./venv/Scripts/Activate.ps1`

## 依赖关系
T1 -> T2
