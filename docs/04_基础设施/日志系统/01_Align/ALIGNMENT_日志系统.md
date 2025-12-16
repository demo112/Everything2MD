# ALIGNMENT_日志系统

## 1. 项目背景与现状

目前 Everything2MD 项目的日志系统较为分散，主要存在以下问题：
*   **Python Core**: 使用标准 `logging` 库，主要输出到控制台。
*   **GUI**: 也就是 `src/gui/main.py`，有自己的一套基于 `Queue` 的日志显示机制，主要用于界面展示，未见持久化存储。
*   **Shell Scripts**: 独立的 bash 函数 (`log_info` 等)，直接输出到 stdout/stderr。
*   **Web Backend**: 使用 `logging` 输出到控制台，并通过 WebSocket 推送。
*   **持久化缺失**: 没有统一的日志文件存储，导致用户反馈问题时难以追溯。
*   **复现困难**: 缺乏环境信息、配置快照等关键上下文，难以仅凭日志复现问题。

## 2. 任务目标

为整个项目搭建统一、全面的日志系统，实现以下目标：
1.  **全功能覆盖**: 覆盖 GUI、CLI、Web、Core 以及被调用的 Shell 脚本/外部工具。
2.  **完全复现**: 日志内容需包含环境信息、配置参数、用户操作序列、异常堆栈等，足以复现工作流。
3.  **本地持久化**: 日志文件必须保存在 EXE (或脚本入口) 同级目录下，方便用户查找。
4.  **统一管理**: 建立统一的日志初始化入口，规范日志格式。

## 3. 需求规范

### 3.1 日志存储规范
*   **路径**: 
    *   开发环境: 项目根目录/logs/everything2md.log
    *   生产环境(EXE): EXE所在目录/everything2md.log
*   **轮转策略**: 使用 `RotatingFileHandler`，单个文件最大 10MB，保留 5 个备份。
*   **编码**: UTF-8。

### 3.2 日志内容规范
*   **格式**: `%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s`
*   **启动时记录**:
    *   系统信息 (OS, Arch, Version)
    *   Python 版本 / EXE 版本
    *   关键依赖工具路径及版本 (Pandoc, LibreOffice, Docker)
    *   当前配置快照 (Config)
*   **运行时记录**:
    *   用户关键操作 (点击按钮, 选择文件)
    *   核心任务状态变更 (开始转换, 转换成功, 失败)
    *   外部命令执行 (subprocess call) 及其输出
    *   异常堆栈 (Uncaught Exceptions)

### 3.3 模块集成规范
*   **GUI**: 保持界面显示功能，同时将日志写入文件。建议实现自定义 `Handler` 将日志发送到 GUI Queue。
*   **Core**: 统一使用 `src.core.logger` 获取 logger。
*   **Shell/Subprocess**: Python 在调用外部命令时，必须捕获 stdout/stderr 并以 INFO/ERROR 级别写入 Python 日志系统。

## 4. 关键决策点 (需确认)

1.  **Shell 脚本的独立运行**: 如果用户单独运行 Shell 脚本（不通过 Python），日志是否需要写入同一个文件？
    *   *建议*: 鉴于 Shell 脚本主要是被 Python 调用的模块，且 Shell 写入同一文件涉及并发锁问题，建议**不**让 Shell 脚本直接写文件，而是依赖调用方 (Python) 捕获输出。如果用户手动运行 Shell，仅输出到控制台即可。
2.  **敏感信息**: 日志中是否需要自动脱敏（如 API Key）？
    *   *建议*: 是，必须对 Config 中的敏感字段进行掩码处理。

## 5. 风险评估
*   **性能影响**: 频繁的文件写入和控制台输出可能影响转换速度。 -> 使用异步日志或合理的日志级别控制。
*   **并发写入**: 多进程/多线程写入同一个文件。 -> Python `logging` 模块是线程安全的，但多进程需要额外处理（本项目主要是多线程 + 子进程调用外部命令，主进程负责写日志应该是安全的）。

