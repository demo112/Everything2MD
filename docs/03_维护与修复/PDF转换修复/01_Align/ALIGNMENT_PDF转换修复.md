# ALIGNMENT_PDF转换修复

## 1. 原始需求
用户反馈 `Pandoc` 转换 PDF 失败 (Exit code 21)，且系统未找到 `pdftotext`，导致无法生成 Markdown 文件。
这是 PPT 转换流程中“降级路径”的一部分（PPT -> PDF -> Markdown），或者是直接的 PDF 转换。
核心诉求是：在缺少外部工具（Pandoc/pdftotext）或外部工具失败的情况下，仍能尽可能解析出文本内容。

## 2. 问题分析
- **错误代码 21**: Pandoc 转换 PDF 失败。通常是因为 Pandoc 自身不具备 OCR 或深度 PDF 解析能力，依赖外部 `pdftotext`，如果版本不匹配或文件复杂会失败。
- **环境缺失**: 用户环境没有安装 `pdftotext` (Poppler 工具集)。
- **当前逻辑**: `LibreOffice` -> `PDF` -> `Pandoc` -> (Fail) -> `pdftotext` -> (Missing) -> `Copy PDF`。
- **改进方向**: 引入纯 Python 的 PDF 解析库作为“最后的保底”，确保即使没有外部工具也能提取文本。

## 3. 技术方案
- **引入依赖**: `pdfminer.six` (纯 Python，提取效果好，支持布局分析)。
- **降级链条**: `Pandoc` -> `pdftotext` (System) -> `pdfminer` (Python Lib) -> `Copy PDF` (Final Fallback)。
- **实现位置**: `src/core/converters/ppt.py` 中的 `_convert_ppt` 方法（以及任何其他处理 PDF 的地方）。

## 4. 关键决策
- **选择 pdfminer.six**: 相比 PyPDF2，它的文本提取（尤其是有布局的文档）效果更好。
- **依赖管理**: 需要更新 `requirements.txt` 和 `Everything2MD.spec`（因为要打包）。
