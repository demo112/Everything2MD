# DESIGN_PDF转换修复

## 1. 架构变更
在 PDF 转 Markdown 的环节增加一层 Python 库处理。

```mermaid
graph TD
    A[PDF File] --> B{Pandoc Installed?}
    B -->|Yes| C[Run Pandoc]
    C -->|Success| D[Markdown Output]
    C -->|Fail| E{pdftotext Installed?}
    B -->|No| E
    E -->|Yes| F[Run pdftotext]
    F -->|Success| D
    F -->|Fail| G{Use Python Lib}
    E -->|No| G
    G -->|pdfminer.six| H[Extract Text]
    H -->|Save| D
    H -->|Fail| I[Copy PDF (Fallback)]
```

## 2. 依赖变更
- `requirements.txt`: 添加 `pdfminer.six>=20221105`
- `Everything2MD.spec`: 检查是否需要 `hiddenimports` (通常 pdfminer 不需要，但需验证)。

## 3. 代码修改
- 修改 `src/core/converters/ppt.py`:
    - 在 `_convert_ppt` 方法中，在 `pdftotext` 尝试失败后，增加 `pdfminer` 调用逻辑。
    - 需编写一个内部辅助函数 `_extract_text_with_pdfminer(pdf_path, output_path)`。

## 4. 验证计划
- 构造一个模拟 PDF 文件。
- 模拟 Pandoc 和 pdftotext 缺失（或 mock 失败）。
- 验证是否成功生成包含文本的 Markdown。
