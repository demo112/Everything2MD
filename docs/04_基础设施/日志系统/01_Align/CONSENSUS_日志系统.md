# CONSENSUS_日志系统

## 1. 最终共识

经过分析和决策，我们达成以下共识，作为后续架构设计和开发的基准。

### 1.1 核心策略
*   **统一入口**: 所有 Python 代码通过 `src.core.logger` 获取 logger 实例。
*   **被动捕获**: Shell 脚本和外部工具（Pandoc/LibreOffice）不直接写日志文件，而是由 Python 主进程在调用时捕获其 stdout/stderr 并记录。
*   **双重分发**: GUI 模式下，日志同时分发到**文件**（持久化）和**界面控件**（实时显示）。
*   **就近存储**: 生产环境（EXE）下，日志文件强制生成在 EXE 同级目录，确保用户可见可达。

### 1.2 详细规范

#### A. 日志文件
*   **文件名**: `everything2md.log`
*   **位置**:
    *   Frozen (EXE): `sys.executable` 所在目录。
    *   Dev (Python): 项目根目录下的 `logs/` 文件夹。
*   **轮转**: Max 10MB, Backup Count 5, Encoding UTF-8.
*   **格式**: `[%(asctime)s] [%(levelname)s] [%(module)s:%(lineno)d] %(message)s`

#### B. 记录内容
1.  **启动阶段**:
    *   打印 Header: "=== Everything2MD Session Start ==="
    *   应用版本, Git Commit (如果有)
    *   操作系统详情 (Windows Version, Release)
    *   Python 版本 / PyInstaller 信息
    *   检测到的外部依赖路径 (Pandoc, LibreOffice, Docker)
    *   **脱敏后**的当前配置 (Config)
2.  **运行阶段**:
    *   API 调用 / 按钮点击事件
    *   文件转换任务的生命周期 (Start, Processing, Success/Fail)
    *   `subprocess.run/Popen` 的完整命令行参数
    *   `subprocess` 的输出结果 (截取前 1KB，避免日志爆炸，或仅在 DEBUG/ERROR 时记录全量)
3.  **异常阶段**:
    *   全局 `sys.excepthook` 捕获未处理异常。
    *   具体的 `try-except` 块中记录 `exc_info=True`。

#### C. 代码实现结构
*   新增 `src/core/logger.py`:
    *   `setup_logging(log_level, log_dir=None)`: 初始化函数。
    *   `get_logger(name)`: 工厂函数。
    *   `GuiHandler(logging.Handler)`: 专门用于将日志 emit 到 GUI Queue。
    *   `mask_sensitive_data(config_dict)`: 脱敏工具函数。

### 1.3 验收标准
1.  **文件存在性**: 运行 EXE 后，同级目录出现 `everything2md.log`。
2.  **内容完整性**: 日志包含 OS 信息、配置信息。
3.  **异常捕获**: 人为触发异常（如除零错误），日志文件中包含完整堆栈。
4.  **外部命令**: 执行转换时，日志包含 pandoc/soffice 的调用命令。
5.  **GUI 同步**: 界面显示的日志与文件中记录的日志一致（文件可能更详细）。

## 2. 变更影响
*   需修改 `src/core/utils.py`: 移除旧的 logger 配置，转为引用新模块。
*   需修改 `src/gui/main.py`: 初始化时调用 `setup_logging`，并移除其内部部分的日志格式化逻辑，转为使用 `GuiHandler`。
*   需修改 `src/core/converter.py` (假设存在): 确保 subprocess 调用使用了新的日志记录方式。

