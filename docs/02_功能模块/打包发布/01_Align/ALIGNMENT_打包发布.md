# ALIGNMENT_打包发布

## 1. 原始需求
用户要求对项目进行打包，具体包括：
1.  生成独立的可执行文件 (EXE)，以便在 Windows 上运行。
2.  生成 7z 格式的压缩包，包含 EXE 和其他必要文件。

## 2. 项目现状
-   **构建工具**: PyInstaller (已安装 v6.17.0)
-   **现有配置**: `Everything2MD.spec` 存在，配置为单文件模式 (`EXE` 包含 `a.binaries`)。
-   **压缩工具**: 环境中未找到 `7z` 命令，且 Python 环境未安装 `py7zr`。
-   **入口文件**: `src/gui/main.py`
-   **依赖**:
    -   `pptx2md` 及其子模块已经在 `hiddenimports` 中。
    -   `LibreOffice` 和 `Pandoc` 为外部依赖，不打包。

## 3. 关键决策
-   **EXE 打包**: 继续使用 PyInstaller 和现有的 `Everything2MD.spec`。需确保 spec 文件中的 hiddenimports 覆盖所有动态加载模块。
-   **7z 压缩**: 由于系统无 `7z` 命令，决定引入 `py7zr` Python 库来实现 7z 压缩功能。这需要在构建脚本中动态安装或要求用户安装。
-   **打包产物**:
    -   `dist/Everything2MD.exe` (中间产物)
    -   `release/Everything2MD_v{version}.7z` (最终产物)，包含 exe 和 README。
-   **版本号**: 从代码或配置中获取版本号，若无则使用日期或 git hash。

## 4. 疑问与澄清
-   **Q**: 是否需要包含其他配置文件？
    -   **A**: 根据项目规则，API KEY 在 `.env` 中且不打包。其他配置如果内置在代码中则不需要。如果有外部 `config.json`，需要确认是否打包。目前假设为单文件 exe，配置由用户运行后生成或手动提供。
-   **Q**: 7z 压缩包内结构？
    -   **A**: 根目录下直接放 exe 和 README。

## 5. 风险评估
-   **PyInstaller 兼容性**: 可能遇到新的依赖未被识别。需进行冒烟测试。
-   **py7zr 性能**: 纯 Python 实现的 7z 压缩可能比原生 7z 慢，但在发布流程中可接受。
