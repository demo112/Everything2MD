# CONSENSUS: 打包项目为exe

## 1. 需求定义
将 `Everything2MD` 工具打包为独立的 Windows 可执行文件 (`.exe`)，使其能够在 Windows 环境下脱离 Python 解释器运行。

## 2. 核心共识
鉴于项目当前严重依赖 Shell 脚本，必须先进行 **Python Native 重构**，再进行打包。

### 2.1 重构目标
- 移除 GUI 对 `bash` 和 `.sh` 脚本的所有调用。
- 使用 Python 标准库重写配置管理、文件转换调度、批量处理等逻辑。
- 保持原有功能逻辑和参数接口不变。

### 2.2 打包策略
- 工具：`PyInstaller`
- 模式：单文件模式 (`--onefile`) 或 目录模式 (`--onedir`)。
- 外部依赖：LibreOffice 和 Pandoc 不会被打包进 exe，程序启动时需检测环境变量。

## 3. 验收标准
1.  **功能完整**: exe 能完成 GUI 中定义的所有转换任务（Word/PPT/PDF -> Markdown）。
2.  **无 Bash 依赖**: 在未安装 Git Bash/WSL 的 Windows 环境下能正常运行。
3.  **配置持久化**: exe 能正确读写配置文件（`config.json`）。
4.  **日志正常**: 能正常记录日志到文件和 GUI 控制台。

## 4. 风险控制
- **工作量**: 重写 Shell 逻辑需要一定时间，需按模块分步进行。
- **外部工具路径**: Windows 下查找 LibreOffice 路径可能较复杂（注册表或默认路径），需增加自动探测逻辑。
