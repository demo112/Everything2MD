# 项目总结报告：增加文档目标格式 PDF

## 任务背景
用户需要将文档（Office、PPT）转换为 PDF 格式，作为 Markdown、HTML、TXT 之外的第四种输出选项。

## 核心变更
1.  **GUI 更新**: `src/gui/main.py` 增加了 "pdf" 选项，并更新了校验逻辑。
2.  **引擎逻辑**: `src/core/engine.py` 增加了对 PDF 输出后缀的支持，并正确路由 PDF 输入文件。
3.  **转换器增强**:
    - `OfficeConverter`: 新增 PDF 导出分支，调用 LibreOffice 的 `--convert-to pdf`。
    - `PptConverter`: 新增 PDF 导出分支，在输出为 PDF 时跳过中间 Markdown 转换步骤，直接调用 LibreOffice。
4.  **测试保障**: 新增 `test/unit/core/converters/test_pdf_integration.py` 等测试，覆盖了核心转换路径的 Mock 测试。
5.  **项目维护与清理**:
    - 修复了 `main.py` 中下拉菜单缺失 "pdf" 的 Bug。
    - 整理了项目根目录，将旧版本文件 (`fixed_*.py`, `*.bak`) 归档至 `archive` 目录。
    - 修复了 `scripts/run_tests.ps1` 和 `scripts/prepare_offline_resources.ps1` 的路径依赖问题。
    - 修复了 `requirements.txt` 中的乱码问题。
    - 完善了 `.gitignore` 配置。
    - 验证并修复了所有单元测试，确保 100% 通过 (108/108 pass)。

## 交付物
- 修改后的源代码文件
- 新增的测试文件
- 完整的 6A 工作流文档

## 风险与约束
- 依赖 LibreOffice 进行 PDF 转换，用户环境必须安装 LibreOffice。
- PDF 转 PDF 目前仅支持文件复制，不做内容处理。

## 后续建议
- 考虑增加 PDF 转换的高级参数配置（如页面大小、页边距等，依赖 LibreOffice 参数）。
