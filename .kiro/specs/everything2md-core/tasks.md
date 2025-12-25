# Implementation Plan: Everything2MD Core System

## Overview

本任务列表涵盖从零开始构建 Everything2MD 文档转换工具的完整实现步骤。采用增量开发方式，先实现核心转换功能，再逐步添加GUI、Web、集成等高级功能。

## Tasks

- [x] 1. 项目初始化与基础架构
  - [x] 1.1 创建项目目录结构
    - 创建 src/core/, src/gui/, src/modules/, web/, test/ 等目录
    - _Requirements: 项目结构_
  - [x] 1.2 配置Python环境
    - 创建 requirements.txt，包含所有依赖
    - 配置 pytest.ini 测试框架
    - _Requirements: 开发环境_
  - [x] 1.3 创建基础工具模块 (utils.py)
    - 实现日志工具函数 (log_info, log_error, log_warn)
    - 实现工具路径检测 (get_soffice_path, get_pandoc_path)
    - 实现文件哈希计算
    - _Requirements: 10.1-10.5_

- [x] 2. 配置管理系统
  - [x] 2.1 实现 ConfigManager 类
    - 实现 JSON 配置文件读写
    - 实现默认配置生成
    - 实现配置项的 get/set 方法
    - _Requirements: 3.1-3.5_
  - [x]* 2.2 编写配置管理单元测试
    - 测试配置加载和保存
    - 测试默认值处理
    - _Requirements: 3.1-3.5_
  - [x]* 2.3 编写配置往返属性测试
    - **Property 2: 配置持久化往返一致性**
    - **Validates: Requirements 3.1, 3.5**

- [x] 3. 核心转换器实现
  - [x] 3.1 创建 BaseConverter 抽象基类
    - 定义 convert() 抽象方法
    - 实现子进程运行辅助方法
    - _Requirements: 1.1-1.7_
  - [x] 3.2 实现 OfficeConverter
    - 实现 LibreOffice → HTML → Markdown 转换流程
    - 实现 Pandoc 直接转换降级方案
    - 实现 Lua 过滤器集成
    - 实现重试机制
    - _Requirements: 1.1, 1.2_
  - [x] 3.3 实现 PptConverter
    - 实现 pptx2md 库调用
    - 实现 LibreOffice 降级方案
    - 实现 PDF 转换流程
    - 实现 pdfminer 最终降级
    - _Requirements: 1.3, 1.4, 1.5_
  - [x] 3.4 实现 EmmxConverter
    - 实现思维导图格式解析
    - _Requirements: 1.7_
  - [x]* 3.5 编写转换器单元测试
    - 测试各格式转换
    - 测试降级流程
    - _Requirements: 1.1-1.7_

- [x] 4. 转换引擎实现
  - [x] 4.1 实现 ConversionEngine 类
    - 实现文件类型检测 (detect_type)
    - 实现单文件转换 (convert_file)
    - 实现批量转换 (run)
    - 实现并行处理 (ThreadPoolExecutor)
    - _Requirements: 1.1-1.7, 2.1-2.5_
  - [x] 4.2 实现任务取消机制
    - 实现 CancellationContext 类
    - 实现 stop() 方法
    - 实现子进程终止
    - _Requirements: 11.1-11.3_
  - [x]* 4.3 编写引擎单元测试
    - 测试文件类型检测
    - 测试批量处理
    - _Requirements: 1.1-1.7, 2.1-2.5_
  - [x]* 4.4 编写文件类型检测属性测试
    - **Property 1: 文件类型检测一致性**
    - **Validates: Requirements 1.1-1.7**

- [x] 5. Checkpoint - 核心功能验证
  - 确保所有转换器测试通过
  - 验证批量处理功能
  - 确认日志输出正确

- [x] 6. 日志系统实现
  - [x] 6.1 实现 LogManager 类
    - 实现多级别日志 (DEBUG, INFO, WARNING, ERROR)
    - 实现文件输出
    - 实现 GUI 队列输出
    - _Requirements: 10.1-10.5_
  - [x]* 6.2 编写日志系统测试
    - 测试日志级别过滤
    - **Property 6: 日志级别过滤正确性**
    - **Validates: Requirements 10.1**

- [x] 7. 大文件分割功能
  - [x] 7.1 实现 split_large_file 函数
    - 实现按大小分割
    - 保持 Markdown 结构完整性
    - 添加序号后缀
    - _Requirements: 9.1-9.3_
  - [x]* 7.2 编写分割功能测试
    - **Property 7: 大文件分割完整性**
    - **Validates: Requirements 9.1-9.3**

- [x] 8. GUI桌面应用实现
  - [x] 8.1 创建主窗口框架
    - 实现 Notebook 标签页结构
    - 配置窗口布局
    - _Requirements: 4.1-4.7_
  - [x] 8.2 实现转换控制标签页
    - 实现文件/目录选择
    - 实现配置控件
    - 实现进度显示
    - 实现日志显示
    - _Requirements: 4.1-4.4_
  - [x] 8.3 实现文件状态列表
    - 实现 Treeview 显示
    - 实现状态更新回调
    - _Requirements: 4.5_
  - [x] 8.4 实现工具路径自动检测
    - 实现 LibreOffice 路径检测
    - 实现 Pandoc 路径检测
    - _Requirements: 4.6_
  - [x] 8.5 实现文件类型扫描
    - 实现目录扫描
    - 实现过滤器复选框
    - _Requirements: 4.7_
  - [x] 8.6 实现转换控制
    - 实现开始/取消按钮
    - 实现配置保存
    - _Requirements: 4.4_
  - [x]* 8.7 编写GUI启动测试
    - 测试窗口创建
    - 测试基本交互
    - _Requirements: 4.1-4.7_

- [x] 9. Checkpoint - GUI功能验证
  - 确保GUI正常启动
  - 验证转换流程
  - 确认配置保存正确

- [x] 10. RAGFlow集成
  - [x] 10.1 实现 RAGFlowClient 类
    - 实现 API 连接
    - 实现知识库列表获取
    - 实现文件上传
    - _Requirements: 6.1-6.5_
  - [x] 10.2 实现 GUI 分发中心标签页
    - 实现连接配置
    - 实现知识库选择
    - 实现批量上传
    - _Requirements: 6.1-6.5_
  - [x]* 10.3 编写RAGFlow集成测试
    - 测试API调用（需要真实服务）
    - _Requirements: 6.1-6.5_

- [x] 11. 图片识别增强
  - [x] 11.1 实现 ImageRecognizer 类
    - 实现 Markdown 图片扫描
    - 实现 LLM API 调用
    - 实现结果插入
    - _Requirements: 7.1-7.5_
  - [x] 11.2 实现 GUI 解析增强标签页
    - 实现图片识别配置
    - _Requirements: 7.1-7.5_
  - [x]* 11.3 编写图片识别测试
    - 测试图片扫描
    - 测试API调用（mock）
    - _Requirements: 7.1-7.5_

- [x] 12. 结构化清洗
  - [x] 12.1 实现 StructureCleaner 类
    - 实现 LLM API 调用
    - 实现 Markdown 优化
    - _Requirements: 8.1-8.3_
  - [x] 12.2 实现 GUI 配置
    - 实现结构清洗配置
    - _Requirements: 8.1-8.3_

- [x] 13. Checkpoint - 增强功能验证
  - 确保RAGFlow集成正常
  - 验证图片识别功能
  - 确认结构清洗功能

- [x] 14. Web后端实现
  - [x] 14.1 创建 FastAPI 应用
    - 配置 CORS
    - 配置静态文件服务
    - _Requirements: 5.1, 5.5_
  - [x] 14.2 实现配置 API
    - GET /api/config
    - POST /api/config
    - _Requirements: 5.1_
  - [x] 14.3 实现文件系统 API
    - GET /api/fs/list
    - 支持挂载盘符访问
    - _Requirements: 5.3_
  - [x] 14.4 实现转换 API
    - POST /api/convert
    - 异步任务执行
    - _Requirements: 5.4_
  - [x] 14.5 实现 WebSocket 日志推送
    - WS /ws/logs
    - 实时日志广播
    - _Requirements: 5.2_
  - [x]* 14.6 编写Web API测试
    - 测试各API端点
    - _Requirements: 5.1-5.5_

- [x] 15. Web前端实现
  - [x] 15.1 创建 HTML 页面结构
    - 实现响应式布局
    - _Requirements: 5.1_
  - [x] 15.2 实现文件选择器
    - 实现目录浏览
    - 实现文件选择
    - _Requirements: 5.3_
  - [x] 15.3 实现转换控制
    - 实现开始转换
    - 实现日志显示
    - _Requirements: 5.4_
  - [x] 15.4 实现 WebSocket 连接
    - 实现实时日志接收
    - _Requirements: 5.2_

- [x] 16. Docker部署
  - [x] 16.1 创建 Dockerfile
    - 安装 LibreOffice、Pandoc
    - 配置 Python 环境
    - 配置中文支持
    - _Requirements: 12.1, 12.3, 12.4_
  - [x] 16.2 创建 docker-compose.yml
    - 配置端口映射
    - 配置卷挂载
    - _Requirements: 12.2_
  - [x]* 16.3 编写Docker构建测试
    - 测试镜像构建
    - 测试服务启动
    - _Requirements: 12.1-12.4_

- [x] 17. Shell脚本遗留接口
  - [x] 17.1 实现 main.sh 主入口
    - 实现参数解析
    - 实现模块加载
    - _Requirements: CLI接口_
  - [x] 17.2 实现各功能模块
    - argument_parser.sh
    - batch_processor.sh
    - config_manager.sh
    - dependency_checker.sh
    - error_handler.sh
    - file_detector.sh
    - libreoffice_converter.sh
    - pandoc_converter.sh
    - pptx2md_converter.sh
    - logger.sh
    - _Requirements: CLI接口_
  - [x]* 17.3 编写Shell脚本测试
    - 使用 bats 框架测试
    - _Requirements: CLI接口_

- [x] 18. Lua过滤器
  - [x] 18.1 创建 clean.lua 过滤器
    - 清理 HTML 残留标签
    - 优化 Markdown 格式
    - _Requirements: 1.1, 1.2_

- [x] 19. Final Checkpoint - 全功能验证
  - 确保所有测试通过
  - 验证GUI、Web、CLI三种入口
  - 确认Docker部署正常
  - 验证文档完整性

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- 本任务列表反映项目当前已实现的功能状态
