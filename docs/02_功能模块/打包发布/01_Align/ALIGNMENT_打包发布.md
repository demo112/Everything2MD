# ALIGNMENT_打包发布

## 1. 原始需求
用户要求对项目进行“打包”，即生成独立的可执行文件 (EXE)，以便在未安装 Python 环境的 Windows 机器上运行。

## 2. 项目现状
- **构建工具**: PyInstaller
- **现有配置**: `Everything2MD.spec` 存在，但可能缺少新引入的依赖。
- **最近变更**: 
    - 引入 `pptx2md` (v2.0+) 及其子模块 `entry`, `types`。
    - 依赖 `LibreOffice` (外部依赖，不打包进 EXE，但需文档说明)。
    - 依赖 `Pandoc` (外部依赖)。

## 3. 关键决策
- **更新 Spec 文件**: 必须将 `pptx2md` 及其相关模块添加到 `hiddenimports`。
- **单文件 vs 目录**: 保持现有配置（目录模式或单文件模式需检查 Spec，现有 Spec 看起来是单文件 `EXE(pyz, ..., exclude_binaries=False)`? 不，现有 Spec 是 `exe = EXE(..., a.binaries, ...)`，这通常是单文件模式，或者如果 `Analysis` 输出被收集到 `COLLECT` 则是目录模式。现有 Spec 只有 `EXE` 且包含 `a.binaries`，这看起来是**单文件模式** (One-file)。
    - *纠正*: 查看 Spec 内容，`exe = EXE(..., a.binaries, a.datas, ...)` 是单文件模式。
- **外部依赖处理**: 
    - 必须明确 `soffice` (LibreOffice) 和 `pandoc` 需要用户自行安装，程序通过 PATH 调用。

## 4. 风险评估
- **动态导入丢失**: `pptx2md` 可能使用动态导入，需手动指定。
- **资源路径**: 打包后 `__file__` 路径变化，需确保代码中使用 `sys._MEIPASS` (如果有) 或相对路径处理正确。
