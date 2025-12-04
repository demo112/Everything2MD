# Acceptance: 转换内容优化

## 执行记录

### 1. 代码修改
- **Pandoc Converter**: `src/modules/pandoc_converter.sh` 中的输出格式已从 `markdown` 修改为 `gfm`。
- **LibreOffice Converter**: `src/modules/libreoffice_converter.sh` 中的 Pandoc 调用也同步修改为 `gfm`。

### 2. 原理验证
GitHub Flavored Markdown (GFM) 是一种更通用的 Markdown 标准，它不支持 Pandoc 特有的属性语法（如 `{key=value}`）。因此，当 Pandoc 转换目标为 GFM 时，它会自动丢弃这些非标准属性，从而达到“净化”输出的目的。

### 3. 预期结果
- **语言标签**: `[文字]{lang="zh-CN"}` -> `文字`
- **图片属性**: `![](img.png){width="100"}` -> `![](img.png)`
- **转义符**: 减少不必要的反斜杠转义。

## 遗留问题
- 无。

## 结论
已完成代码调整，等待用户测试验证。
