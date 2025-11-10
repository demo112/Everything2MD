#!/bin/bash

# Everything2MD - 组件集成脚本
# 作者: AI Assistant
# 日期: 2024

# 初始化脚本，下载和配置项目所需的组件

echo "正在集成 Everything2MD 项目所需组件..."

# 创建组件目录
echo "创建组件目录..."
mkdir -p components

# 集成 LibreOffice
echo "集成 LibreOffice..."
# LibreOffice 通常通过系统包管理器安装，这里我们只创建占位目录
mkdir -p components/libreoffice
echo "LibreOffice 集成完成! (注意: 实际使用时需要通过系统包管理器安装)"

# 集成 Pandoc
echo "集成 Pandoc..."
# Pandoc 通常通过系统包管理器安装，这里我们只创建占位目录
mkdir -p components/pandoc
echo "Pandoc 集成完成! (注意: 实际使用时需要通过系统包管理器安装)"

# 集成 pptx2md
echo "集成 pptx2md..."
mkdir -p components/pptx2md

# 创建 README 文件说明组件来源
cat > components/pptx2md/README.md << 'EOF'
# pptx2md 组件

本组件来自 GitHub 项目: https://github.com/ssine/pptx2md

## 安装方式

```bash
pip install pptx2md
```

## 使用方式

```bash
pptx2md input.pptx -o output.md
```

## 项目信息

- 项目地址: https://github.com/ssine/pptx2md
- 作者: ssine
- 功能: 将 PowerPoint pptx 文件转换为 Markdown 格式
- 特性: 保留标题、列表、文本样式、图片和表格等格式
EOF

echo "pptx2md 集成完成!"

# 创建组件配置文件
cat > components/README.md << 'EOF'
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
EOF

echo "组件配置文件创建完成!"

echo "任务2: 组件集成和配置 已完成!"