# CONSENSUS_修复文件选择组件

## 1. 问题定义
- **现象**: 用户在 Web 界面无法选择路径，"各种路径都选不到"。
- **原因**: 
  1. 后端 `web/backend/main.py` 中 `list_files` 函数针对根目录 (`/`) 的处理逻辑是硬编码的 Windows 盘符检测 (`C:\`, `D:\` 等)。
  2. Docker 容器运行的是 Linux 环境，不存在这些盘符，导致根目录列表为空或异常。
  3. 此外，转换逻辑中 `bash` 路径也是硬编码的 Windows 路径，在 Docker 中会失败。

## 2. 解决方案
- **修改后端逻辑 (`web/backend/main.py`)**:
  - 增加操作系统检测 (`os.name` 或 `platform.system()`)。
  - 在 Linux 环境下，`list_files("/")` 应直接列出根目录内容，而不是扫描盘符。
  - 优化 `bash` 路径查找逻辑，在 Linux 下直接使用 `bash` 或 `/bin/bash`。

## 3. 验收标准
- [ ] 在 Docker 环境中，点击 "Browse" 能正常显示当前目录文件。
- [ ] 能正常导航至根目录 `/` 并显示 `/bin`, `/usr`, `/home` 等 Linux 目录结构。
- [ ] 能选择文件并成功填入输入框。
