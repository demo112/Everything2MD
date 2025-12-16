# TASK_打包发布

## 任务清单

- [ ] **Task 1: 更新 Spec 文件**
    - 文件: `Everything2MD.spec`
    - 内容: 添加 `pptx2md.entry`, `pptx2md.types` 到 `hiddenimports`。
    - 依赖: 无。

- [ ] **Task 2: 清理环境**
    - 操作: 删除 `build/` 和 `dist/` 目录。
    - 目的: 防止旧文件干扰。

- [ ] **Task 3: 执行构建**
    - 命令: `pyinstaller Everything2MD.spec --clean --noconfirm`
    - 验证: `dist/Everything2MD.exe` 生成。

- [ ] **Task 4: 冒烟测试**
    - 操作: 运行生成的 EXE。
    - 验证: GUI 正常显示，无立即崩溃。
