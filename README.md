# Everything2MD

Everything2MD 是一个强大的文档转换工具，可以将各种格式的文档转换为 Markdown 格式。支持 Office 文档（Word、Excel、PowerPoint）、文本文件等多种格式。

## 功能特性

- 支持多种文档格式转换为 Markdown
- 批量处理模式，可一次处理整个目录
- 模块化设计，易于扩展和维护
- 配置文件支持，可自定义转换参数
- 详细的日志记录和错误处理机制
- 提供源码运行与 Docker 运行方式（推荐 Docker）

## 支持的文件格式

- Microsoft Word: `.doc`, `.docx`
- Microsoft Excel: `.xls`, `.xlsx`
- Microsoft PowerPoint: `.ppt`, `.pptx`
- 文本文件: `.txt`
- 其他文本格式: `.md`, `.markdown`

## 环境依赖

- Bash 4.0 或更高版本（推荐使用最新版本以获得最佳兼容性）
- LibreOffice (用于 Office 文档转换)
- Pandoc (用于格式转换优化)
- pptx2md (用于 PowerPoint 文档转换)

## 安装说明

### 源码运行（开发用途）

1. 确保系统已安装 Bash 4.0 或更高版本：
   ```bash
   # 检查 Bash 版本
   bash --version
   
   # macOS (使用 Homebrew 升级 Bash)
   brew install bash
   
   # Ubuntu/Debian (升级 Bash)
   sudo apt-get update
   sudo apt-get install bash
   ```
2. 安装必要的依赖工具：
   ```bash
   # macOS (使用 Homebrew)
   brew install libreoffice pandoc
   
   # Ubuntu/Debian
   sudo apt-get install libreoffice pandoc
   
   # 安装 pptx2md
   pip install pptx2md
   ```
3. 克隆或下载本项目代码

## 使用方法

### Docker 运行（推荐）

```bash
# 1) 构建镜像（国内环境建议使用国内镜像源与加速）
docker build -t everything2md:latest .

# 2) 挂载输入输出目录并执行转换（设置时区与UTF-8编码）
docker run --rm \
  -e TZ=Asia/Shanghai \
  -v "$PWD/input":/work/input \
  -v "$PWD/output":/work/output \
  everything2md:latest \
  ./src/main.sh -i /work/input/Untitled\ 1.doc -o /work/output/out.md
```

说明：
- 推荐在 Docker 守护进程配置 `registry-mirrors`（如阿里云/腾讯云）以加速镜像拉取。
- 容器内已设置 `TZ=Asia/Shanghai` 与 `LANG/LC_ALL` 为 UTF-8，避免中文乱码。

### 源码运行

```bash
# 转换单个文件
./src/main.sh -i input.docx -o output.md

# 批量处理目录
./src/main.sh -i /path/to/input/dir -o /path/to/output/dir -b
```

### 图形界面（GUI）入口

- 桌面版 GUI 位于 `src/gui/main.py`，提供文件选择、参数配置、进度与日志显示。
- `src/gui/fixed_main.py` 与 `src/gui/fixed_main_v2.py` 为历史示例，已不再作为主入口。

### 命令行参数

- `-i, --input PATH`: 输入文件或目录路径
- `-o, --output PATH`: 输出文件或目录路径
- `-b, --batch`: 批量处理模式
- `-c, --config FILE`: 配置文件路径
- `-l, --log-level LEVEL`: 日志级别 (DEBUG, INFO, WARN, ERROR)
- `-h, --help`: 显示帮助信息

### 配置文件

可以创建配置文件来自定义转换行为：

```ini
# 日志级别
log_level=INFO
```

## 项目结构

```
Everything2MD/
├── src/                     # 源代码目录
│   ├── main.sh              # 主程序入口
│   ├── gui/                 # Tkinter 图形界面
│   │   └── main.py          # GUI 主入口
│   └── modules/             # 功能模块
│       ├── argument_parser.sh      # 参数解析模块
│       ├── batch_processor.sh      # 批量处理模块
│       ├── config_manager.sh       # 配置管理模块
│       ├── dependency_checker.sh   # 依赖检查模块
│       ├── error_handler.sh        # 错误处理模块
│       ├── file_copier.sh          # 文件复制模块
│       ├── file_detector.sh        # 文件类型检测模块
│       ├── libreoffice_converter.sh # LibreOffice转换模块
│       ├── logger.sh               # 日志记录模块
│       ├── pandoc_converter.sh     # Pandoc转换模块
│       └── pptx2md_converter.sh    # pptx2md转换模块
├── build/                   # （已废弃）历史构建目录
│   ├── scripts/             # （已废弃）历史构建脚本
│   ├── dist/                # （已废弃）历史发行版输出目录
│   └── temp/                # （已废弃）历史临时目录
└── docs/                    # 项目文档
```

## 开发指南

### 添加新的文件格式支持

1. 在 `src/modules/` 目录下创建新的转换模块
2. 实现文件类型检测逻辑
3. 在主程序中集成新模块

### Docker 构建与测试

```bash
# 构建镜像
docker build -t everything2md:latest .

# 运行所有测试（在容器内）
docker run --rm -e TZ=Asia/Shanghai -v "$PWD":/work -w /work everything2md:latest \
  test/bats/bin/bats test/unit test/integration
```

### 代码规范

- 使用 Bash 脚本语言
- 遵循模块化设计原则
- 添加适当的注释和文档
- 保持代码风格一致

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。
