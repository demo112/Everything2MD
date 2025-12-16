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

### Windows 可执行文件 (推荐)

无需配置 Python 或 Bash 环境，直接运行打包好的 EXE 文件。

1. **获取程序**: 位于 `dist/Everything2MD.exe`。
2. **依赖准备**: 
   - 需安装 [LibreOffice](https://www.libreoffice.org/) 以支持 Office 文档转换。
   - 程序会自动探测 LibreOffice 路径，或在界面中手动指定。

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

## 贡献与规范

我们欢迎社区贡献！在提交代码前，请务必阅读我们的 [版本管理与贡献规范](docs/rules/VERSIONING.md)。

- **版本策略**: 遵循 Semantic Versioning 2.0.0。
- **提交规范**: 遵循 Conventional Commits。
- **变更日志**: 查看 [CHANGELOG.md](CHANGELOG.md) 了解最新变动。

## 开发与测试

本项目包含 Python 接口/单元测试和 Shell 脚本集成测试。

### 运行测试 (Windows)
使用 PowerShell 运行测试脚本：

```powershell
# 运行所有测试
.\run_tests.ps1

# 仅运行 Python 测试
.\run_tests.ps1 test-python

# 仅运行 Shell 测试 (需安装 Git Bash)
.\run_tests.ps1 test-bats
```

### 运行测试 (Linux/macOS)
使用 Make 命令：

```bash
make test
```

## 使用方法

### Docker 运行（推荐）

本项目提供 `docker-compose.yml` 以简化部署与运行。

```bash
# 1. 启动服务（后台运行）
docker compose up -d

# 2. 访问 Web 界面
# 打开浏览器访问 http://localhost:8000

# 3. 停止服务
docker compose down
```

### Docker 开发与更新指南

当代码、功能或配置发生变更后，请遵循以下步骤制作并在 Docker 中运行最新的镜像：

#### 1. 代码或配置变更
如果仅修改了 `src/` 或 `web/` 下的代码，或 `config/` 下的配置文件：
- 大多数情况下，如果是开发模式（挂载了卷），代码变更会即时生效（取决于是否开启热重载）。
- 如果需要重新打包镜像发布，请执行构建命令。

#### 2. 依赖或 Dockerfile 变更
如果修改了 `requirements.txt`、`Dockerfile` 或需要强制更新环境：

```bash
# 1. 重新构建镜像
# Docker 会自动检测变化。如果修改了 Dockerfile 或 requirements.txt，会自动重装依赖。
# 如果只修改了代码，Docker 会利用缓存加速构建。
docker compose build

# 2. 重启容器应用新镜像
# 建议先停止并移除旧容器，确保干净启动
docker compose down
docker compose up -d

# 或者使用一条命令完成构建与重启（强制重建容器）
docker compose up -d --build --force-recreate
```

#### 3. 验证更新
- 查看容器日志：`docker compose logs -f`
- 进入容器检查：`docker compose exec everything2md bash`

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
│   ├── core/                # [New] Python 核心逻辑 (去 Shell 化)
│   │   ├── config.py        # 配置管理
│   │   ├── engine.py        # 转换引擎
│   │   ├── utils.py         # 通用工具
│   │   └── converters/      # 格式转换器
│   ├── main.sh              # [Legacy] Shell 主程序入口
│   ├── gui/                 # Tkinter 图形界面
│   │   └── main.py          # GUI 主入口 (已适配 Python Core)
│   └── modules/             # [Legacy] Shell 功能模块
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
