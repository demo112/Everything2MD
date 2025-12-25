# Requirements Document

## Introduction

Everything2MD 是一个强大的文档转换工具，旨在将各种格式的办公文档（Word、Excel、PowerPoint、PDF等）统一转换为 Markdown 格式。项目支持命令行、GUI桌面应用和Web界面三种使用方式，并提供批量处理、RAGFlow集成、图片识别增强等高级功能。

## Glossary

- **Conversion_Engine**: 核心转换引擎，负责协调各类转换器完成文档格式转换
- **Office_Converter**: Office文档转换器，处理 .doc/.docx/.xls/.xlsx 格式
- **PPT_Converter**: PPT文档转换器，处理 .ppt/.pptx/.pdf 格式
- **Config_Manager**: 配置管理器，负责读取、保存和管理用户配置
- **GUI_Application**: Tkinter桌面图形界面应用
- **Web_Backend**: FastAPI Web后端服务
- **RAGFlow_Client**: RAGFlow知识库集成客户端
- **Image_Recognizer**: 图片识别模块，使用LLM解析文档中的图片
- **Structure_Cleaner**: 结构化清洗模块，使用LLM优化Markdown结构

## Requirements

### Requirement 1: 多格式文档转换

**User Story:** As a 用户, I want 将各种办公文档转换为Markdown格式, so that 我可以统一管理和编辑文档内容。

#### Acceptance Criteria

1. WHEN 用户提供 .doc 或 .docx 文件, THE Office_Converter SHALL 使用 LibreOffice 转换为 HTML，再通过 Pandoc 转换为 Markdown
2. WHEN 用户提供 .xls 或 .xlsx 文件, THE Office_Converter SHALL 使用 LibreOffice 转换为 HTML，再通过 Pandoc 转换为 Markdown
3. WHEN 用户提供 .pptx 文件, THE PPT_Converter SHALL 优先使用 pptx2md 库进行转换，失败时降级使用 LibreOffice
4. WHEN 用户提供 .ppt 文件, THE PPT_Converter SHALL 使用 LibreOffice 转换为 PDF，再转换为 Markdown
5. WHEN 用户提供 .pdf 文件, THE PPT_Converter SHALL 使用 Pandoc 或 pdftotext 或 pdfminer 进行文本提取
6. WHEN 用户提供 .txt 文件, THE Conversion_Engine SHALL 直接复制文件内容
7. WHEN 用户提供 .emmx 文件, THE Emmx_Converter SHALL 解析思维导图格式并转换为 Markdown

### Requirement 2: 批量处理能力

**User Story:** As a 用户, I want 批量转换整个目录下的文档, so that 我可以高效处理大量文件。

#### Acceptance Criteria

1. WHEN 用户指定输入目录, THE Conversion_Engine SHALL 递归扫描目录下所有符合过滤条件的文件
2. WHEN 批量处理启用时, THE Conversion_Engine SHALL 支持配置并行任务数（1-16）
3. WHEN 批量处理时, THE Conversion_Engine SHALL 保持原始目录结构输出转换结果
4. WHEN 文件已存在于输出目录, THE Conversion_Engine SHALL 跳过该文件并记录日志
5. WHEN 用户配置文件过滤器, THE Conversion_Engine SHALL 仅处理指定扩展名的文件

### Requirement 3: 配置管理

**User Story:** As a 用户, I want 保存和加载转换配置, so that 我不需要每次重复设置参数。

#### Acceptance Criteria

1. THE Config_Manager SHALL 将配置存储为 JSON 格式文件
2. WHEN 配置文件不存在, THE Config_Manager SHALL 创建包含默认值的配置文件
3. WHEN 配置文件损坏, THE Config_Manager SHALL 备份原文件并重置为默认配置
4. THE Config_Manager SHALL 支持配置项包括：日志级别、输出格式、并行任务数、文件过滤器、工具路径、RAGFlow设置、图片识别设置、结构清洗设置
5. WHEN 用户修改配置, THE Config_Manager SHALL 立即持久化到配置文件

### Requirement 4: GUI桌面应用

**User Story:** As a 桌面用户, I want 通过图形界面操作转换工具, so that 我可以直观地选择文件和配置参数。

#### Acceptance Criteria

1. THE GUI_Application SHALL 提供文件/目录选择对话框
2. THE GUI_Application SHALL 显示转换进度条和文件状态列表
3. THE GUI_Application SHALL 实时显示运行日志
4. THE GUI_Application SHALL 支持取消正在进行的转换任务
5. WHEN 转换完成, THE GUI_Application SHALL 在文件状态列表中显示每个文件的转换结果
6. THE GUI_Application SHALL 自动检测 LibreOffice 和 Pandoc 的安装路径
7. THE GUI_Application SHALL 提供扫描输入目录文件类型的功能

### Requirement 5: Web界面

**User Story:** As a Docker用户, I want 通过Web界面操作转换工具, so that 我可以在容器环境中使用该工具。

#### Acceptance Criteria

1. THE Web_Backend SHALL 提供 RESTful API 用于配置管理和转换任务
2. THE Web_Backend SHALL 通过 WebSocket 实时推送转换日志
3. THE Web_Backend SHALL 提供文件系统浏览 API，支持访问挂载的磁盘
4. WHEN 用户发起转换请求, THE Web_Backend SHALL 异步执行转换任务
5. THE Web_Backend SHALL 提供静态文件服务托管前端页面

### Requirement 6: RAGFlow知识库集成

**User Story:** As a 知识管理用户, I want 将转换后的文档上传到RAGFlow知识库, so that 我可以构建可检索的知识库。

#### Acceptance Criteria

1. THE RAGFlow_Client SHALL 支持配置 API 地址和密钥
2. WHEN 连接RAGFlow, THE RAGFlow_Client SHALL 获取并显示可用的知识库列表
3. WHEN 用户选择知识库, THE RAGFlow_Client SHALL 支持批量上传转换后的文件
4. THE RAGFlow_Client SHALL 显示上传进度和结果状态
5. IF RAGFlow连接失败, THEN THE RAGFlow_Client SHALL 显示错误信息并允许重试

### Requirement 7: 图片识别增强

**User Story:** As a 用户, I want 自动识别文档中的图片内容, so that 图片信息也能被转换为文本。

#### Acceptance Criteria

1. WHEN 图片识别启用, THE Image_Recognizer SHALL 扫描Markdown中的图片引用
2. THE Image_Recognizer SHALL 调用配置的LLM API（如GPT-4 Vision）解析图片内容
3. THE Image_Recognizer SHALL 将识别结果作为图片描述插入Markdown
4. THE Image_Recognizer SHALL 支持配置并发数和上下文长度
5. IF 图片识别失败, THEN THE Image_Recognizer SHALL 记录警告日志并继续处理

### Requirement 8: 结构化清洗

**User Story:** As a 用户, I want 优化转换后的Markdown结构, so that 文档更加规范和易读。

#### Acceptance Criteria

1. WHEN 结构清洗启用, THE Structure_Cleaner SHALL 调用LLM API优化Markdown格式
2. THE Structure_Cleaner SHALL 修复标题层级、列表格式、表格结构等问题
3. IF 结构清洗失败, THEN THE Structure_Cleaner SHALL 记录警告日志并保留原内容

### Requirement 9: 大文件分割

**User Story:** As a 用户, I want 自动分割过大的输出文件, so that 文件便于处理和上传。

#### Acceptance Criteria

1. WHEN 输出文件超过配置的最大大小, THE Conversion_Engine SHALL 自动分割为多个文件
2. THE Conversion_Engine SHALL 在分割点保持Markdown结构完整性
3. THE Conversion_Engine SHALL 为分割后的文件添加序号后缀

### Requirement 10: 全链路日志

**User Story:** As a 运维人员, I want 完整的日志记录, so that 我可以追踪和排查问题。

#### Acceptance Criteria

1. THE Log_Manager SHALL 支持 DEBUG、INFO、WARNING、ERROR 四个日志级别
2. THE Log_Manager SHALL 同时输出到文件和GUI/控制台
3. THE Log_Manager SHALL 记录每个文件的转换开始、结束、成功/失败状态
4. THE Log_Manager SHALL 记录所有外部工具调用的命令和返回结果
5. WHEN 发生错误, THE Log_Manager SHALL 记录完整的错误堆栈信息

### Requirement 11: 任务取消

**User Story:** As a 用户, I want 取消正在进行的转换任务, so that 我可以中止不需要的操作。

#### Acceptance Criteria

1. WHEN 用户点击取消, THE Conversion_Engine SHALL 设置停止标志
2. THE Conversion_Engine SHALL 终止所有活动的子进程
3. WHEN 任务被取消, THE Conversion_Engine SHALL 记录取消状态并清理临时文件

### Requirement 12: Docker部署

**User Story:** As a 运维人员, I want 通过Docker部署服务, so that 我可以快速搭建转换环境。

#### Acceptance Criteria

1. THE Dockerfile SHALL 包含所有必要的依赖（LibreOffice、Pandoc、Python等）
2. THE docker-compose.yml SHALL 配置端口映射和卷挂载
3. THE Docker镜像 SHALL 支持中文文件名和时区设置
4. THE Docker镜像 SHALL 配置国内镜像源以加速构建
