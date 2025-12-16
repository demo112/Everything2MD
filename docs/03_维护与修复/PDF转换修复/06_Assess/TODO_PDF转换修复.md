# TODO_PDF转换修复

## 待办事项
- [ ] **OCR 支持**: 目前仅支持文本提取，扫描版 PDF (纯图片) 将无法提取内容。建议未来集成 `tesseract` 或 `ocrmypdf`。
- [ ] **UI 进度条优化**: 上传大文件时，UI 可能会有短暂卡顿，虽然是在后台线程，但进度条更新可能不够平滑。

## 缺失配置
- 无。核心依赖 `pdfminer.six` 已加入 `requirements.txt`。
