# DESIGN: 打包项目为exe (Python Native 重构)

## 1. 架构概览
为了消除对 Bash 的依赖，将在 `src/core` 目录下构建全新的 Python 核心层，替代原有的 `src/modules/*.sh`。

### 1.1 目录结构
```
src/
  gui/
    main.py          # 更新后的 GUI，调用 src/core
  core/
    __init__.py
    config.py        # 替代 config_manager.sh
    engine.py        # 替代 main.sh (核心调度)
    utils.py         # 通用工具 (日志、文件检测)
    converters/      # 转换器模块
      __init__.py
      base.py        # 抽象基类
      office.py      # LibreOffice 转换逻辑
      pandoc.py      # Pandoc 转换逻辑
      ppt.py         # PPT 处理逻辑
```

## 2. 模块设计

### 2.1 ConfigManager (`src/core/config.py`)
负责配置文件的加载、保存和默认值管理。
- `load_config()`: 加载 JSON 配置。
- `save_config()`: 保存 JSON 配置。
- `get(key, default)`: 获取配置项。

### 2.2 ConversionEngine (`src/core/engine.py`)
负责任务调度和批量处理。
- `submit_task(input_file, output_dir)`: 提交转换任务。
- `run_batch(input_dir, output_dir)`: 批量处理（使用 `concurrent.futures.ThreadPoolExecutor`）。
- 信号与回调：通过回调函数向 GUI 报告进度和日志。

### 2.3 Converters (`src/core/converters/`)
- `BaseConverter`: 定义 `convert(input_path, output_path)` 接口。
- `OfficeConverter`: 封装 `soffice` 命令行调用。
  - 自动探测 LibreOffice 安装路径（Windows 注册表或常见路径）。
- `PandocConverter`: 封装 `pandoc` 命令行调用。

## 3. 数据流
1.  GUI 初始化 -> `ConfigManager.load()`
2.  用户点击开始 -> `ConversionEngine.run()`
3.  Engine 遍历文件 -> 识别类型 -> 选择 Converter
4.  Converter -> `subprocess.Popen` (调用外部工具) -> 返回结果
5.  Engine -> 回调 GUI 更新进度条

## 4. 异常处理
- **工具缺失**: 启动时检查 LibreOffice/Pandoc，若缺失抛出明确异常。
- **转换失败**: 单个文件失败不影响批量任务，记录错误日志。
