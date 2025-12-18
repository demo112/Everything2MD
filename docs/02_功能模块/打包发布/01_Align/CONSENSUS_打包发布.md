# CONSENSUS_打包发布

## 1. 最终需求
-   构建 Windows 单文件 EXE。
-   构建包含 EXE 和 README.md 的 7z 压缩包。
-   输出目录：`release/`。

## 2. 技术方案
### 2.1 EXE 构建
-   工具: PyInstaller
-   配置: `Everything2MD.spec`
-   命令: `pyinstaller Everything2MD.spec --clean --noconfirm`

### 2.2 7z 压缩
-   工具: `py7zr` (Python 库)
-   实现: 编写 Python 脚本 `scripts/package_release.py`。
-   流程:
    1.  调用 PyInstaller 构建 EXE。
    2.  创建 `release` 目录。
    3.  使用 `py7zr` 将 `dist/Everything2MD.exe` 和 `README.md` 压缩到 `release/Everything2MD_<date>.7z`。

### 2.3 依赖管理
-   构建前需安装 `py7zr`: `pip install py7zr`。

## 3. 验收标准
-   [ ] `dist/Everything2MD.exe` 生成且能正常启动 GUI。
-   [ ] `release/*.7z` 生成且包含 exe 和 readme。
-   [ ] 压缩包解压后，exe 能正常运行。
