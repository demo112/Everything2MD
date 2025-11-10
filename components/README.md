# 组件说明

本目录包含 Everything2MD 项目所需的所有第三方组件。

## 组件列表

1. **LibreOffice**
   - 用途: 将 doc/docx/ppt 文件转换为 pdf
   - 安装: 通过系统包管理器安装
   - 项目地址: https://www.libreoffice.org/

2. **Pandoc**
   - 用途: 将 pdf 文件转换为 Markdown
   - 安装: 通过系统包管理器安装
   - 项目地址: https://github.com/jgm/pandoc

3. **pptx2md**
   - 用途: 将 pptx 文件转换为 Markdown
   - 安装: pip install pptx2md
   - 项目地址: https://github.com/ssine/pptx2md

## 安装说明

请根据您的操作系统使用相应的包管理器安装 LibreOffice 和 Pandoc。

对于 pptx2md，可以使用 pip 安装:

```bash
pip install pptx2md
```

## 注意事项

- 本项目不修改任何组件的源代码
- 所有组件保持独立，便于维护和升级
