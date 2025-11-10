# 控制器模块

本目录包含 Everything2MD 项目的核心控制逻辑。

## 模块列表

1. **file_type_detector.sh** - 文件类型检测器
   - 功能: 检测输入文件的类型并确定相应的处理流程
   - 接口: `detect_file_type` 函数

2. **conversion_controller.sh** - 转换流程控制器
   - 功能: 控制整个文件转换流程，根据文件类型调用相应的转换组件
   - 接口:
     - `process_office_file` 函数
     - `process_pdf_file` 函数
     - `process_known_file` 函数

## 使用说明

在其他脚本中使用这些控制器模块，需要先通过 `source` 命令加载：

```bash
source ./core/file_type_detector.sh
source ./core/conversion_controller.sh
```