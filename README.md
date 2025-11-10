# Everything2MD

一个将各种文档格式（doc, docx, ppt, pptx）转换为Markdown格式的工具。

## 功能特点

- 支持多种文档格式转换为Markdown
- 集成LibreOffice、Pandoc和pptx2md组件
- 采用流水线方式连续转换
- 不侵入源项目代码，保持纯净性

## 技术架构

本项目通过fork以下组件并在独立路径下集成：
- LibreOffice：处理doc/docx到pdf的转换
- Pandoc：处理pdf到markdown的转换
- pptx2md：专门处理pptx到markdown的转换

## 使用方法

```bash
# 转换单个文件
./everything2md.sh input.docx output.md

# 批量转换
./everything2md.sh --batch input_folder output_folder
```