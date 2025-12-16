# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.7.0] - 2025-12-16
### Added
- Feat(测试): 添加核心模块的单元测试覆盖率
- Feat(打包): 优化exe打包配置并增强格式支持检测

### Changed
- Chore: 移除大型测试夹具并强制文件大小限制
- Chore: 移除构建产物并更新 gitignore

## [0.6.0] - 2025-12-15
### Added
- Feat: 添加RAGFlow集成与测试体系增强

### Changed
- Chore: 合并更新，重组文档，并排除大型二进制文件 (2025-12-04)

## [0.5.0] - 2025-11-28
### Added
- Feat(docker): 添加docker-compose配置并优化Dockerfile

### Changed
- Docs: 重构项目文档结构并更新内容

## [0.4.0] - 2025-11-27
### Added
- Feat: 优化Tkinter GUI界面与功能

## [0.3.0] - 2025-11-13
### Added
- Feat(构建): 添加Windows原生可执行程序支持并改进LibreOffice检测
- Feat(打包脚本): 添加BusyBox支持并改进Windows安装脚本

### Changed
- Chore: 移除废弃的构建脚本和工具文件
- Ci(workflows): 禁用Go模块缓存以节省构建时间
- Ci(workflows): 更新构建工作流以显示最终发布目录内容
- Feat(配置管理器): 修复GUI配置保存时的编码问题并改进配置管理 (2025-11-12)

## [0.2.0] - 2025-11-11
### Added
- Feat(gui): 添加图形用户界面支持
- Feat: 添加Bats测试框架及相关测试文件
- Feat: 实现跨平台打包功能并添加相关文档

### Fixed
- Fix(ppt): 修复PPT文件处理乱码问题并优化文件类型检测

### Changed
- Docs: 更新文档以反映测试体系和模块改进
- Ci: Update GitHub Actions workflows

## [0.1.0] - 2025-11-10
### Added
- Feat: 初始化Everything2MD项目并添加核心功能
- Feat: 实现Everything2MD文档转换工具核心功能

### Changed
- Docs: 添加项目对齐阶段文档
- Docs: 重构文档结构并添加详细规划文档
