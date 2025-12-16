# TASK_UI交互与体验优化

## 任务列表

### Task 1: UI 文本与反馈优化
- [ ] 修改 `src/gui/main.py`: 将 "新建KB..." 改为 "新建知识库..."
- [ ] 修改 `src/gui/main.py`: 在 `save_config` 成功后添加 `messagebox.showinfo`
- [ ] 修改 `src/gui/main.py`: 分发中心列表符号替换 (`[x]` -> `☑`, `[ ]` -> `☐`)
- **验收标准**: 界面显示正确，操作有反馈。

### Task 2: 核心引擎支持取消上下文
- [ ] 修改 `src/core/engine.py`: 定义 `CancellationContext` 类
- [ ] 修改 `src/core/engine.py`: `ConversionEngine` 管理 `active_contexts`
- [ ] 修改 `src/core/engine.py`: `stop()` 方法触发 context abort
- **验收标准**: 能够传递 context 对象。

### Task 3: 转换器支持强制终止
- [ ] 修改 `src/core/converters/office.py`: 支持 `context` 参数，使用 `Popen` 替代 `run`
- [ ] 修改 `src/core/converters/ppt.py`: 支持 `context` 参数，使用 `Popen` 替代 `run` (针对 LibreOffice 部分)
- **验收标准**: 转换过程中点击取消，后台进程被强制关闭。

### Task 4: 集成与验证
- [ ] 运行程序验证所有修改点
- [ ] 验证 "取消" 功能是否能杀死卡住的 soffice 进程
- **验收标准**: 功能正常，无回归 bug。
