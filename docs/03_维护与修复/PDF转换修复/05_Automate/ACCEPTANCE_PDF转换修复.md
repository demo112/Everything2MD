# ACCEPTANCE_PDF转换修复

## 1. 变更摘要
- **依赖**: 引入 `pdfminer.six`。
- **逻辑**: 在 `src/core/converters/ppt.py` 中实现了三级降级逻辑。
    1. Pandoc (PDF -> Markdown)
    2. pdftotext (System Tool)
    3. pdfminer (Python Lib) -> **New**
    4. Copy PDF (Fallback)
- **架构修复**: 修正了 `src/core/engine.py` 中的路由逻辑，确保 `.pdf` 文件正确路由到 `PptConverter`（包含增强的 PDF 处理逻辑），而非误传给 `OfficeConverter`。
- **接口修复**: 更新了 `BaseConverter`, `PptConverter`, `OfficeConverter` 和 `ConversionEngine`，确保在转换过程中如果文件扩展名发生变化（如降级为 PDF），能正确返回最终的文件路径，解决上传时“找不到文件”的问题。

## 2. 验证结果
- **单元测试**: 新增 `test/unit/core/converters/test_pdf_integration.py` (原 `tests/test_pdf_integration.py`)。
    - `test_pdf_direct_conversion_routing`: 验证 `.pdf` 文件正确路由到 `PptConverter`。
    - `test_pdf_fallback_suffix_change`: 验证当转换器返回不同后缀的文件路径时，引擎能正确透传，修复上传路径错误。
    - `test_ppt_converter_pdf_input`: 验证 `PptConverter` 能直接处理 `.pdf` 输入。
    - `test_pdf_conversion_pandoc_success`: 验证 Pandoc 优先转换路径。
    - `test_pdf_conversion_pandoc_fail_pdftotext_success`: 验证 Pandoc 失败后降级到 pdftotext。
    - `test_pdf_conversion_all_cmds_fail_pdfminer_success`: 验证命令行工具失败后降级到 pdfminer。
    - `test_fallback_pdf_parsing_copy_on_failure`: 验证全链路失败后降级为复制 PDF。
- **回归测试**: 修复并运行 `test/unit/core/converters/test_ppt.py`，确保 PPT/PPTX 原有逻辑未受影响。
- **集成测试**: 运行 `test/unit/gui/test_rag_upload.py`，确保上传逻辑（包括失败文件处理）正常。
- **结果**: 所有 15 个相关测试用例全部通过。

## 3. 预期效果
1. 即使 Pandoc 报错且系统无 pdftotext，程序也能通过 `pdfminer` 提取 PDF 中的文本并保存为 Markdown。
2. 直接转换 PDF 文件时，也能享受上述降级保护。
3. 如果转换最终降级为复制 PDF（`.pdf`），GUI 也能正确识别该文件并上传，不会报“文件缺失”错误。
