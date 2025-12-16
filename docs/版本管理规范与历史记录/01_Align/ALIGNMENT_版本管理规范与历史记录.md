# ALIGNMENT: 版本管理规范与历史记录

## 1. 项目背景
项目目前已经历了多次迭代，包含了核心功能开发、GUI 界面、Docker 支持、测试体系构建以及 RAGFlow 集成等重要里程碑。然而，目前缺乏统一的版本号管理策略和结构化的变更日志（CHANGELOG），这使得追踪项目演进和发布管理变得困难。

## 2. 原始需求
1. **根据 git 编写该工具的版本迭代记录**：需要从 Git 提交历史中提取信息，整理出清晰的版本迭代历史。
2. **项目添加规则**：制定工具的版本号管理策略（如 Semantic Versioning）和更新内容的生成要求（如 Conventional Commits）。

## 3. 需求理解与分析
### 3.1 现状分析
- Git 提交记录已经初步遵循了 Conventional Commits 规范（使用了 `feat`, `fix`, `chore`, `docs` 等前缀）。
- 项目功能模块清晰（核心转换、GUI、Docker、测试、部署）。
- 缺乏显式的 Tag 或 Release 记录（根据 git log 推断）。

### 3.2 目标定义
- **版本策略**：采用 [Semantic Versioning 2.0.0](https://semver.org/) (主版本号.次版本号.修订号)。
- **提交规范**：正式确立 [Conventional Commits](https://www.conventionalcommits.org/) 规范。
- **更新日志**：生成 `CHANGELOG.md`，遵循 [Keep a Changelog](https://keepachangelog.com/) 格式。
- **自动化/工具化**：虽然不一定马上引入复杂的 CI/CD 自动发布，但需要制定手动或半自动的生成规则。

## 4. 关键决策点 (智能决策)
- **版本号起点**：鉴于项目已经有较多功能，建议当前版本定为 `0.7.0` 或 `1.0.0`。考虑到仍在快速迭代且未正式声明稳定版，建议以 `0.7.0` 作为当前开发版本，或者回顾历史整理出 `0.1.0` 到 `0.6.0` 的演进。
  - **建议**：梳理历史版本，当前定为 `0.7.0`。
- **历史记录回溯**：是否需要人为地为过去的 Commit 划分版本号？
  - **建议**：是，基于时间点和功能集人为划分过去的版本，以便生成一份完整的 CHANGELOG。

## 5. 疑问澄清
- **Q**: 是否需要为旧的 Commit 打 Git Tag？
  - **A**: 建议在整理完历史后，补打 Tag 以便 Git 历史清晰（可选，视用户权限而定，文档中只做建议）。
- **Q**: 版本号管理策略具体包含哪些？
  - **A**: 包括版本号递增规则（Breaking change -> Major, Feature -> Minor, Fix -> Patch）、预发布版本规则等。

## 6. 拟定规范草案
### 版本号策略 (SemVer)
- **Major**: 不兼容的 API 修改。
- **Minor**: 向下兼容的功能性新增。
- **Patch**: 向下兼容的问题修正。

### 提交信息规范 (Conventional Commits)
格式：`<type>(<scope>): <subject>`
- `feat`: 新功能
- `fix`: 修补 bug
- `docs`: 文档改变
- `style`: 代码格式改变（不影响功能）
- `refactor`: 代码重构
- `test`: 增加测试
- `chore`: 构建过程或辅助工具的变动

### 更新日志规范
文件：`CHANGELOG.md`
格式：
```markdown
## [版本号] - YYYY-MM-DD
### Added
- 新增功能...
### Changed
- 变更功能...
### Fixed
- 修复问题...
```
