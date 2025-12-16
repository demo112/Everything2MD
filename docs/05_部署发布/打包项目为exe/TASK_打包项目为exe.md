# TASK: 打包项目为exe (v2 - 2025-12-15)

## 1. 任务拆解
### Task 1: 清理环境
- [ ] 删除旧的 `build/` 和 `dist/` 目录。
- [ ] 确保 `src/filters/clean.lua` 存在。

### Task 2: 执行打包
- [ ] 运行 `pyinstaller Everything2MD.spec --clean --noconfirm`。
- [ ] 检查构建日志是否有 Error。

### Task 3: 验证构建
- [ ] 检查 `dist/Everything2MD.exe` 是否生成。
- [ ] 运行 exe，验证 GUI 启动。
- [ ] 验证配置读取（检查是否加载了上次保存的 API Key）。

## 2. 依赖关系
必须在 `Automate` 阶段成功执行 Task 2 后，才能进行 Task 3 的验证。
