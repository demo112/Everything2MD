# TODO: 版本管理规范与历史记录

## 1. 待办事项
- [ ] **Git Tag 补打**: 建议拥有 git 权限的管理员按照 `CHANGELOG.md` 中的日期和版本号，为历史 commit 补打 tag (如 `git tag -a v0.7.0 -m "Release v0.7.0" <commit-hash>`)。
- [ ] **CI 集成**: 未来可以考虑在 GitHub Actions 中集成 `semantic-release` 或类似工具，自动生成 changelog 和发布 release。

## 2. 缺少的配置
- 目前无硬性缺少的配置，但若要强制规范，可引入 `husky` + `commitlint`。
