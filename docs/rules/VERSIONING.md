# 版本管理与贡献规范

## 1. 版本号策略 (Versioning Strategy)

本项目严格遵循 [Semantic Versioning 2.0.0](https://semver.org/lang/zh-CN/) (语义化版本) 规范。

版本格式：`主版本号.次版本号.修订号` (Major.Minor.Patch)

- **主版本号 (Major)**: 当你做了不兼容的 API 修改。
- **次版本号 (Minor)**: 当你做了向下兼容的功能性新增。
- **修订号 (Patch)**: 当你做了向下兼容的问题修正。

### 1.1 开发阶段
在 1.0.0 正式版发布之前（0.y.z），次版本号的变动可能包含破坏性变更，但我们应尽量保持兼容或在 Changelog 中明确说明。

## 2. 分支管理 (Branching Model)

推荐使用 **Feature Branch Workflow**：

- **main**: 主分支，保持随时可发布状态。
- **feat/xxx**: 功能分支，用于开发新功能。
- **fix/xxx**: 修复分支，用于修复 Bug。

## 3. 提交信息规范 (Commit Convention)

本项目采用 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/v1.0.0/) 规范。

格式：`<type>(<scope>): <subject>`

### 3.1 Type (类型)
- **feat**: 新功能 (Feature)
- **fix**: 修补 Bug (Bug Fix)
- **docs**: 文档改变 (Documentation)
- **style**: 代码格式改变 (不影响代码运行的变动)
- **refactor**: 代码重构 (既不是新增功能，也不是修改 bug 的代码变动)
- **perf**: 性能优化
- **test**: 增加测试或修改现有测试
- **chore**: 构建过程或辅助工具的变动 (Build process or auxiliary tools)
- **revert**: 回滚上一个版本

### 3.2 Scope (范围 - 可选)
用于说明 commit 影响的范围，例如：`gui`, `docker`, `core`, `test` 等。

### 3.3 Subject (主题)
- 简短描述变更内容（建议 50 字符以内）。
- 使用祈使句（如 "Add" 而不是 "Added" 或 "Adds"）。
- 结尾不加句号。

**示例**:
- `feat(gui): add file selection dialog`
- `fix(core): handle utf-8 encoding error`
- `docs: update readme with usage instructions`

## 4. 更新日志 (Changelog)

所有显著的更改都记录在项目根目录的 `CHANGELOG.md` 文件中。
该文件格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

### 4.1 更新流程
1. 在开发新功能或修复 Bug 时，请确保你的 Commit Message 清晰。
2. 在准备发布新版本时，从 Git Log 中提取变更。
3. 将变更分类填入 `CHANGELOG.md` 的对应版本号下。
4. 提交 `CHANGELOG.md` 和版本号变更（如 `VERSION` 文件或 Tag）。

### 4.2 类别
- `Added`: 新功能。
- `Changed`: 现有功能变更。
- `Deprecated`: 即将移除的功能。
- `Removed`: 已移除的功能。
- `Fixed`: 问题修复。
- `Security`: 安全性修补。
