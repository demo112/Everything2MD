# ALIGNMENT: 打包项目为exe

## 1. 原始需求
用户要求将 `Everything2MD` 项目打包为 Windows 可执行文件 (`.exe`)。

## 2. 项目现状分析
### 2.1 架构现状
- **GUI 层**: 使用 Python `tkinter` 编写 (`src/gui/main.py`)。
- **核心逻辑层**: 深度依赖 Bash Shell 脚本 (`src/main.sh`, `src/modules/*.sh`)。
- **外部依赖**: 
  - LibreOffice (`soffice` 命令)
  - Pandoc
  - Bash 环境 (WSL 或 Git Bash)
- **调用方式**: GUI 通过 `subprocess.run(["bash", ...])` 调用 Shell 脚本。

### 2.2 关键挑战
直接使用 PyInstaller 打包 `src/gui/main.py` 会导致生成的 exe 无法在标准 Windows 环境下运行，原因如下：
1.  **依赖缺失**: exe 不包含 Bash 解释器，无法执行 `.sh` 脚本。
2.  **路径问题**: Shell 脚本中的路径处理与 Windows 不兼容。
3.  **环境依赖**: 即使在安装了 Git Bash 的机器上，调用路径也可能不匹配。

## 3. 解决方案：Python Native 重构
为了实现真正的 "打包为 exe" 并保证可移植性，必须将核心 Shell 脚本逻辑移植为 Python 代码。

### 3.1 重构范围
1.  **配置管理**: `src/modules/config_manager.sh` -> Python `ConfigManager` 类。
2.  **核心调度**: `src/main.sh` -> Python `ConversionEngine` 类。
3.  **模块移植**:
    - `file_detector.sh` -> Python 文件类型检测。
    - `libreoffice_converter.sh` -> Python `subprocess` 调用 `soffice`。
    - `pandoc_converter.sh` -> Python `subprocess` 调用 `pandoc`。
    - `batch_processor.sh` -> Python `concurrent.futures` 线程池。

### 3.2 外部工具处理
- **LibreOffice & Pandoc**: 依然作为外部工具依赖。exe 运行时需要检测这些工具是否已安装并配置在 PATH 中。
- **打包策略**: PyInstaller 仅打包 Python 代码。用户需自行安装 LibreOffice 和 Pandoc（或提供便携版）。

## 4. 决策确认
- **方向**: 拒绝 "仅打包 GUI 外壳" 的无效方案，采用 "Python 重构 + PyInstaller" 的稳健方案。
- **交付物**: 
  - 重构后的 Python 核心代码。
  - 更新后的 GUI 代码（调用 Python 核心而非 Shell）。
  - 单文件 exe (`Everything2MD.exe`)。
