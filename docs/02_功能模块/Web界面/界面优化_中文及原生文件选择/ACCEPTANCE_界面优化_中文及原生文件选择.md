# ACCEPTANCE: 界面优化_中文及原生文件选择

## 1. 功能验证
- [x] **后端 API**
    - [x] `GET /api/system/select-path` 存在且逻辑正确。
    - [x] 引入了 `tkinter` 和 `filedialog`。
    - [x] 异常处理：捕获异常并返回 error 字段。
- [x] **前端界面**
    - [x] `index.html` 语言已更新为中文。
    - [x] 文件选择器模态框已移除。
    - [x] 输入框旁新增了“选文件”和“选目录”按钮。
- [x] **前端逻辑**
    - [x] `script.js` 中移除了旧的文件选择逻辑。
    - [x] 新增 `selectPath` 函数调用后端系统弹窗 API。
    - [x] 状态提示信息已中文化。

## 2. 代码质量
- [x] Python 语法检查通过 (`py_compile`).
- [x] HTML 结构完整。
- [x] JS 逻辑无明显引用错误。

## 3. 遗留问题
- 无。

## 4. 结论
- 任务已完成，等待用户运行验证。
