# 依赖集成 - 最终报告

## 项目概述
本项目旨在将核心依赖工具（Pandoc, Poppler）直接集成到项目目录中，以消除对宿主机系统环境变量的依赖，实现“开箱即用”的便携性。

## 架构实现
1. **目录结构**:
   - `tools/pandoc/`: 存放 Pandoc 可执行文件
   - `tools/poppler/`: 存放 Poppler 工具集 (pdftotext 等)

2. **环境加载**:
   - Shell: `src/modules/env_loader.sh` 动态将 `tools` 目录加入 PATH。
   - Python (FastAPI): `web/backend/main.py` 在启动子进程时动态注入 `tools` 路径。

3. **自动化**:
   - `scripts/install_deps.py`: 自动下载并解压依赖到指定目录。

## 达成目标
- [x] 用户无需手动配置系统 PATH。
- [x] 项目在不同机器上（Windows/Linux）具备更好的一致性。
- [x] Docker 容器保持了独立的系统级安装，但也兼容项目结构。

## 下一步计划
- 考虑集成 LibreOffice Portable 以实现完全零依赖转换 Office 文档。
