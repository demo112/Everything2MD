# ALIGNMENT: 转换内容优化

## 原始需求
用户反馈转换出来的 Markdown 内容包含大量冗余信息，具体表现为：
1. **多余的语言标签**: 如 `[打开]{lang="zh-CN"}`，这通常是 Pandoc 从 Word 文档转换时保留的语言属性。
2. **图片尺寸属性**: 如 `{width="109" height="111"}`，虽然这是标准的 Pandoc Markdown 扩展，但在某些渲染器下可能不需要，或者用户希望更简洁。
3. **反斜杠转义**: 如 `\ `，可能是换行符转换导致的。

## 现状分析
- **转换链路**: DOCX -> LibreOffice (HTML) -> Pandoc (Markdown)。
- **Pandoc 参数**: 目前 `src/modules/pandoc_converter.sh` 中仅使用了基本的 `-f html -t markdown`。
- **问题根源**: Word 文档中的样式和语言设置被转换成了 Pandoc 的 Span 属性。

## 目标
净化输出的 Markdown 内容，移除不必要的属性标签，使其更干净、更通用。

## 疑问与澄清
- **Q**: 是否需要保留图片？
  - **A**: 是，图片是内容的一部分。
- **Q**: 是否完全移除 `{lang="zh-CN"}`？
  - **A**: 是，对于纯文本阅读，这属于干扰信息。
- **Q**: 图片尺寸属性是否移除？
  - **A**: 建议移除，让 Markdown 阅读器自适应图片大小。

## 结论
需要优化 Pandoc 的转换参数，使用 Lua 过滤器或正则表达式后期处理来清理这些冗余标签。考虑到 Shell 脚本处理复杂正则的局限性，优先调整 Pandoc 参数（如使用 `markdown-raw_attribute` 扩展禁用属性输出，或者 `gfm` 格式）。
