# DESIGN_UI交互与体验优化

## 整体架构图

本次修改主要涉及 `ConversionEngine` (核心逻辑) 和 `Everything2MDGUI` (界面交互)。

```mermaid
graph TD
    GUI[Everything2MDGUI] -->|点击取消| Engine[ConversionEngine]
    Engine -->|stop()| ContextMgr[CancellationContextManager]
    ContextMgr -->|abort()| Converter[Office/PptConverter]
    Converter -->|kill()| Subprocess[LibreOffice/Pandoc Process]
    
    GUI -->|点击保存| Config[ConfigManager]
    GUI -->|显示弹窗| User[用户]
```

## 核心设计：CancellationContext

为了在多线程环境下安全地管理和终止子进程，引入 `CancellationContext` 类。

### 1. 类定义
```python
class CancellationContext:
    def __init__(self):
        self.process = None # subprocess.Popen object
        self._lock = threading.Lock()
        
    def set_process(self, proc):
        with self._lock:
            self.process = proc
            
    def abort(self):
        with self._lock:
            if self.process:
                try:
                    self.process.kill() # Force kill
                except Exception:
                    pass
```

### 2. ConversionEngine 修改
- 维护 `self.active_contexts = []` 列表。
- 在 `run` 方法中，为每个任务创建一个 `CancellationContext`。
- 将 `context` 传递给 `convert_file` 和具体的 Converter。
- 在 `stop()` 方法中，遍历 `active_contexts` 并调用 `abort()`。

### 3. Converter 修改
- `OfficeConverter.convert` 和 `PptConverter.convert` 增加 `context` 可选参数。
- 将 `subprocess.run` 替换为 `subprocess.Popen` + `proc.wait()` 模式，以便获取 `proc` 对象并注入到 `context` 中。

## UI 优化设计

### 1. 多选框优化
- 替换 `[x]` 为 `☑`
- 替换 `[ ]` 为 `☐`
- 修改 `on_rag_list_click` 判定逻辑。

### 2. 保存反馈
- 在 `save_config` 方法末尾添加 `messagebox.showinfo`。

### 3. 文本修改
- 直接替换字符串常量。

## 接口契约
- `ConversionEngine.run` 参数保持不变，内部处理 Context。
- `BaseConverter.convert` 签名增加 `context=None`。

## 异常处理
- 进程 Kill 异常需捕获，避免 crash。
- 多线程竞争需加锁保护。
