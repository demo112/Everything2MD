# 组件接口模块

本目录包含 Everything2MD 项目使用的各种外部组件的接口封装。

## 模块列表

1. **libreoffice.sh** - LibreOffice 接口
   - 功能: 将 doc/docx/ppt 文件转换为 PDF
   - 接口: 
     - `check_libreoffice` 函数
     - `convert_to_pdf` 函数

2. **pandoc.sh** - Pandoc 接口
   - 功能: 将各种格式文件转换为 Markdown
   - 接口:
     - `check_pandoc` 函数
     - `convert_to_markdown` 函数
     - `convert_pdf_to_markdown` 函数

3. **pptx2md.sh** - pptx2md 接口
   - 功能: 将 PowerPoint 文件转换为 Markdown
   - 接口:
     - `check_pptx2md` 函数
     - `convert_pptx_to_markdown` 函数

## 使用说明

在其他脚本中使用这些组件接口模块，需要先通过 `source` 命令加载：

```bash
source ./components/libreoffice.sh
source ./components/pandoc.sh
source ./components/pptx2md.sh
```