# 核心工具模块

本目录包含 Everything2MD 项目的核心工具模块。

## 模块列表

1. **parser.sh** - 参数解析器
   - 功能: 解析命令行参数
   - 接口: `parse_args` 函数

2. **logger.sh** - 日志记录器
   - 功能: 记录程序运行过程中的信息
   - 接口: 
     - `set_verbose` 函数
     - `log_info` 函数
     - `log_warn` 函数
     - `log_error` 函数

3. **file_manager.sh** - 文件管理器
   - 功能: 处理临时文件的创建、使用和清理
   - 接口:
     - `create_temp_dir` 函数
     - `file_exists` 函数
     - `dir_exists` 函数
     - `get_file_extension` 函数
     - `get_file_name` 函数
     - `mkdir_p` 函数

## 使用说明

在其他脚本中使用这些工具模块，需要先通过 `source` 命令加载：

```bash
source ./utils/parser.sh
source ./utils/logger.sh
source ./utils/file_manager.sh
```