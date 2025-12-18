# TODO_PPTX_Conversion_Fix

## 待办事项 (用户侧)
1.  **安装 Poppler (可选)**:
    - 当前 PDF 转换依赖 `pdfminer` (纯 Python)，虽然能提取文本，但布局保持不如 `pdftotext`。
    - 建议下载 Poppler for Windows，并将 `bin` 目录添加到系统 PATH。
    - 这样可以消除 `[WARNING] Pandoc 转换 PDF 失败` 和 `[WARNING] 未找到 pdftotext` 的警告。

## 待办事项 (开发侧)
- [ ] 考虑在未来版本中内嵌 `pdftotext` 或提供自动下载脚本。
