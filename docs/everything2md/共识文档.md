# CONSENSUS: Everything2MD 文档转换项目

## 1. 明确的需求描述和验收标准

### 需求描述
开发一个文档转换工具，能够将以下格式的文件统一转换为 Markdown 格式：
- Microsoft Word 文档 (.doc, .docx)
- PowerPoint 演示文稿 (.ppt, .pptx)

### 验收标准
1. 支持 .doc, .docx, .ppt, .pptx 格式到 Markdown 的转换
2. 转换后的 Markdown 文件保留原文档的基本结构和内容
3. 提供命令行接口，支持单文件转换和批量转换
4. 集成 LibreOffice、Pandoc 和 pptx2md 三个组件
5. 各组件在项目中保持独立，不修改源代码
6. 转换过程采用流水线方式，自动选择合适的转换路径

## 2. 技术实现方案

### 整体架构
```
Input File -> 格式检测 -> 转换路径选择 -> 组件调用 -> Markdown 输出
```

### 转换路径设计
1. **doc/docx 路径**：
   - 使用 LibreOffice 将 doc/docx 转换为 pdf
   - 使用 Pandoc 将 pdf 转换为 md

2. **pptx 路径**：
   - 直接使用 pptx2md 将 pptx 转换为 md

3. **ppt 路径**：
   - 使用 LibreOffice 将 ppt 转换为 pdf
   - 使用 Pandoc 将 pdf 转换为 md

### 技术选型
- **LibreOffice**：处理 Office 文档到 PDF 的转换
  - 命令示例：`soffice --headless --convert-to pdf input.docx`
- **Pandoc**：处理 PDF 到 Markdown 的转换
  - 命令示例：`pandoc -f pdf -t markdown input.pdf -o output.md`
- **pptx2md**：专门处理 pptx 到 Markdown 的转换
  - 命令示例：`pptx2md input.pptx`

## 3. 任务边界限制

### 功能边界
- 仅支持指定的四种文档格式转换
- 不处理加密或受保护的文档
- 不保证复杂的格式（如特殊字体、动画等）完全保留
- 不处理网络文档或云存储文档

### 技术约束
- 必须使用指定的三个组件
- 各组件必须 fork 到项目独立路径下
- 不允许修改组件源代码
- 项目需保持简洁，避免不必要的复杂性

## 4. 集成方案

### 项目结构
```
Everything2MD/
├── README.md
├── docs/
│   └── everything2md/
│       ├── ALIGNMENT_everything2md.md
│       ├── CONSENSUS_everything2md.md
│       ├── DESIGN_everything2md.md
│       ├── TASK_everything2md.md
│       ├── ACCEPTANCE_everything2md.md
│       └── FINAL_everything2md.md
├── components/
│   ├── libreoffice/
│   ├── pandoc/
│   └── pptx2md/
├── src/
│   └── main.sh
└── tests/
```

### 组件集成方式
1. 将各组件作为 git submodule 添加到项目中
2. 通过 shell 脚本调用各组件的命令行接口
3. 实现统一的入口脚本处理不同格式的转换

## 5. 关键假设确认

1. 用户环境中已安装必要的依赖项或项目提供安装脚本
2. 输入文件是有效的办公文档格式
3. 磁盘空间足够处理转换过程中的临时文件
4. 各组件在目标平台上可用且功能正常