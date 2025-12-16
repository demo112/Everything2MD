# ALIGNMENT: 打包项目为exe (v2 - 2025-12-15)

## 1. 原始需求
用户要求将 `Everything2MD` 项目打包为 Windows 可执行文件 (`.exe`)。
**当前迭代**: 基于 2025-12-15 的最新代码库（包含上传修复、API Key 持久化、去重逻辑）进行重新打包。

## 2. 项目现状分析
### 2.1 架构现状 (已完成 Python 重构)
- **GUI 层**: `src/gui/main.py` (Tkinter)。
- **核心逻辑层**: 纯 Python 实现 (`src/core/*.py`)，不再依赖 Bash Shell。
- **外部依赖**: 
  - LibreOffice (`soffice.exe`)
  - Pandoc (`pandoc.exe`)
  - RAGFlow Server (HTTP API)
- **资源文件**:
  - `src/filters/clean.lua`: Pandoc 过滤器，必须打包。

### 2.2 打包策略
- **工具**: PyInstaller
- **配置**: 复用现有的 `Everything2MD.spec`。
- **包含内容**:
  - 所有 Python 源码 (`src/`)
  - 必要的资源文件 (`src/filters/`)
- **排除内容**:
  - `numpy`, `scipy` (除非 `pptx2md` 显式依赖且无法裁剪，但之前的打包已确认可排除以减小体积)。
  - 外部工具 (LibreOffice, Pandoc 需用户自备或放置在 `tools/` 目录)。

## 3. 风险评估
- **pptx2md 兼容性**: `pptx2md` 库是否能被 PyInstaller 正确识别和打包。
- **路径问题**: 运行时的 `sys._MEIPASS` 临时目录路径处理（代码中需使用 `resource_path` 函数）。
- **Config 持久化**: 确认 `config.json` 生成位置是否正确（应在 `os.getcwd()` 或 User Profile，而非 exe 内部）。

## 4. 交付物
- 更新后的 `Everything2MD.exe`。
- 验证报告。
