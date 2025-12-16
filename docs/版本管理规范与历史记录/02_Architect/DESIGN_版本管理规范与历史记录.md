# DESIGN: 版本管理规范与历史记录

## 1. 整体设计
本任务旨在建立项目的版本管理体系，不涉及代码逻辑的变更，主要是文档和规范的建立。
核心产出物为：
1. `CHANGELOG.md`: 位于项目根目录，记录完整的历史版本变更。
2. `docs/rules/VERSIONING.md`: 详细的版本管理和提交规范说明文档。
3. `README.md` 更新: 引用上述规范文档。

## 2. 文档结构设计

### 2.1 CHANGELOG.md
遵循 Keep a Changelog 标准。
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.7.0] - 2025-12-16
### Added
- 核心模块单元测试覆盖率提升 (commit: 6aa8085)
- exe 打包配置优化及增强格式支持检测 (commit: 9fc5579)

### Changed
- 移除大型测试夹具并强制文件大小限制 (commit: fba000c)
- 移除构建产物并更新 gitignore (commit: 2c4ec83)

... (Older versions)
```

### 2.2 VERSIONING.md
- **标题**: 版本管理与贡献规范
- **内容章节**:
  - 版本号策略 (SemVer)
  - 分支管理策略 (建议 Trunk Based 或 Feature Branch)
  - Commit Message 规范 (Conventional Commits)
  - Changelog 维护指南

## 3. 依赖关系
- `CHANGELOG.md` 的生成依赖于对 `git log` 的准确解析和人工分类（Align 阶段已完成）。
- `README.md` 的更新依赖于 `VERSIONING.md` 的创建。

## 4. 接口/交互设计
无代码接口。
用户交互主要体现在阅读文档和执行 git commit 时遵循规范。
