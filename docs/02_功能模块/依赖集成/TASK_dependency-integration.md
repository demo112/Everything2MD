# 依赖集成任务清单

## 1. 架构设计 (Architecture)
- [x] 设计 `tools/` 目录结构
- [x] 确定需要集成的组件 (Pandoc, Poppler)

## 2. 原子任务 (Atomize)
- [x] 编写依赖下载脚本 `scripts/install_deps.py`
- [x] 执行下载脚本，部署 Pandoc 和 Poppler
- [x] 创建 `src/modules/env_loader.sh`
- [x] 修改 `src/main.sh` 引入环境加载模块
- [x] 修改 `web/backend/main.py` 支持内置工具路径
- [x] 验证 DOCX 转换 (使用内置 Pandoc)
- [x] 验证 PDF 提取 (使用内置 pdftotext)

## 3. 遗留问题
- [ ] LibreOffice 的便携版集成（因体积过大，暂不自动下载，预留目录 `tools/libreoffice`）
