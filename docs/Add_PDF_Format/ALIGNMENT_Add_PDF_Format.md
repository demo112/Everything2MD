# 增加文档目标格式：PDF - Alignment Document

## 1. 项目上下文分析
- **项目目标**: 将各种文档（Office, PDF, PPT 等）转换为 Markdown。
- **当前状态**:
  - 核心逻辑位于 `src/core`。
  - GUI 位于 `src/gui`。
  - 转换器支持 Office (via LibreOffice/Pandoc) 和 PPT (via pptx2md/LibreOffice)。
  - 目前默认输出格式为 Markdown (及部分 HTML/Txt 支持)。
- **相关文件**:
  - `src/gui/fixed_main_v2.py`: GUI 配置入口。
  - `src/core/engine.py`: 转换引擎。
  - `src/core/converters/office.py`: Office 文档转换器。
  - `src/core/converters/ppt.py`: PPT 文档转换器。

## 2. 需求理解确认
- **原始需求**: 增加文档目标格式：PDF。
- **需求拆解**:
  1.  GUI 界面允许用户选择 "PDF" 作为输出格式。
  2.  后端转换逻辑支持将各类源文件转换为 PDF。
  3.  对于 Office 文档 (Word, Excel, PPT)，使用 LibreOffice 直接转换为 PDF。
  4.  对于 PDF 文档，直接复制到输出目录。
  5.  对于 Text/Markdown 文档，暂不支持转 PDF (或者使用 Pandoc，需确认)。
- **边界确认**:
  - 暂时只关注 Office 和 PPT 格式转 PDF。
  - 文本/Markdown 转 PDF 如果 Pandoc 环境就绪可以支持，否则作为后续优化。
  - 不涉及 OCR 功能的变更。

## 3. 智能决策策略
- **问题 1**: 如何处理 Markdown/Text 转 PDF？
  - *策略*: 检查 Pandoc 是否可用。如果可用，尝试使用 Pandoc 转 PDF (需 latex 引擎，通常较重)。
  - *决策*: 第一版暂不支持 Text/MD 转 PDF，除非 Pandoc 环境非常完善。主要聚焦于 Office/PPT 原生转 PDF。如果用户选了 PDF 但输入是 Text，可以报错或降级处理（复制原文件或转 MD）。
  - *修正*: 考虑到 Pandoc 转 PDF 需要 LaTeX 引擎，环境配置复杂，建议第一版对于 Text 输入跳过或报错，或者仅支持 Office/PPT 转 PDF。

- **问题 2**: 如何在 Engine 中传递格式信息？
  - *策略*: `engine.convert_file` 接收 `output_path`。GUI 或调用者负责生成带有正确后缀 (.pdf) 的 `output_path`。Engine 内部根据后缀判断目标格式。
  - *决策*: 保持 Engine 接口简洁，通过 `output_path.suffix` 判断目标格式。

## 4. 关键决策点
- **GUI**: 在 "常规设置" -> "输出格式" 下拉框中增加 "pdf"。
- **Logic**: 
  - 修改 `OfficeConverter` 和 `PptConverter`，在 `convert` 方法中检测 `output_path.suffix == '.pdf'`。
  - 如果是 PDF 目标，调整 LibreOffice 的 `--convert-to` 参数为 `pdf`。
  - 对于 `PptConverter`，如果是 `.pptx` 且目标是 PDF，不使用 `pptx2md`，而是降级使用 LibreOffice 转 PDF。

## 5. 最终共识
- **目标**: 实现 Office (Doc/Docx/Xls/Xlsx) 和 PPT (Ppt/Pptx) 转 PDF 功能。
- **GUI**: 增加 PDF 选项。
- **实现**: 利用 LibreOffice 的 PDF 导出功能。
