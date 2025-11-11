# Everything2MD

Everything2MD 是一个强大的文档转换工具，可以将各种格式的文档转换为 Markdown 格式。支持 Office 文档（Word、Excel、PowerPoint）、文本文件等多种格式。

## 功能特性

- 支持多种文档格式转换为 Markdown
- 批量处理模式，可一次处理整个目录
- 模块化设计，易于扩展和维护
- 配置文件支持，可自定义转换参数
- 详细的日志记录和错误处理机制
- 提供Windows和macOS平台的启动器应用

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

### 方法一：使用预编译的启动器应用（推荐）

#### Windows平台
1. 从发布页面下载Everything2MD-Windows-*.zip文件
2. 解压到任意目录
3. 运行`everything2md.bat`即可使用

#### macOS平台
1. 从发布页面下载Everything2MD-macOS-*.dmg文件
2. 挂载DMG并拖拽Everything2MD.app到Applications文件夹
3. 在终端中运行`/Applications/Everything2MD.app/Contents/MacOS/everything2md`即可使用

### 方法二：从源码运行

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

### 方法一：使用启动器应用

#### Windows平台
```cmd
# 转换单个文件
everything2md.bat -i input.docx -o output.md

# 批量处理目录
everything2md.bat -i C:\path\to\input\dir -o C:\path\to\output\dir -b
```

#### macOS平台
```bash
# 转换单个文件
/Applications/Everything2MD.app/Contents/MacOS/everything2md -i input.docx -o output.md

# 批量处理目录
/Applications/Everything2MD.app/Contents/MacOS/everything2md -i /path/to/input/dir -o /path/to/output/dir -b
```

### 方法二：从源码运行

```bash
# 转换单个文件
./src/main.sh -i input.docx -o output.md

# 批量处理目录
./src/main.sh -i /path/to/input/dir -o /path/to/output/dir -b
```

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
├── build/                   # 构建目录
│   ├── scripts/             # 构建脚本
│   ├── dist/                # 发行版输出目录
│   └── temp/                # 临时文件目录
└── docs/                    # 项目文档
```

## 开发指南

### 添加新的文件格式支持

1. 在 `src/modules/` 目录下创建新的转换模块
2. 实现文件类型检测逻辑
3. 在主程序中集成新模块

### 构建和发行

本项目支持构建Windows和macOS平台的发行版：

#### Windows平台构建
```bash
# 在Windows环境中运行
build/scripts/windows_packager.bat
```

#### macOS平台构建
```bash
# 在macOS环境中运行
build/scripts/macos_packager.sh
```

构建产物将输出到 `build/dist/` 目录。

### 代码规范

- 使用 Bash 脚本语言
- 遵循模块化设计原则
- 添加适当的注释和文档
- 保持代码风格一致

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。