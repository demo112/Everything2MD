# PPT文件处理乱码问题修复说明

## 问题描述
用户报告在使用Everything2MD工具转换PPT文件时，生成的Markdown文件出现乱码问题。

## 问题分析
经过分析，发现以下问题：

1. PPT文件被识别为"office"类型，使用LibreOffice转换器进行处理
2. LibreOffice转换器将PPT转换为HTML，再用Pandoc转换为Markdown
3. 这个过程在处理中文内容时容易出现编码问题，导致乱码

## 解决方案
为了解决这个问题，我们采取了以下措施：

1. 创建了专门的PPT转换器模块 (`ppt_converter.sh`)
2. 修改了文件类型检测逻辑，将PPT文件识别为独立的"ppt"类型
3. 在主脚本中添加了对"ppt"类型的处理逻辑
4. PPT转换器使用以下流程：
   - 使用LibreOffice直接将PPT转换为PDF
   - 使用pdftotext工具提取PDF中的文本内容
   - 生成UTF-8编码的Markdown文件

## 技术实现细节

### 新增PPT转换器模块
- 文件路径: `src/modules/ppt_converter.sh`
- 功能: 专门处理PPT文件转换
- 依赖工具: LibreOffice, pdftotext

### 文件类型检测修改
- 文件路径: `src/modules/file_detector.sh`
- 修改内容: 将PPT文件从"office"类型中分离，单独识别为"ppt"类型

### 主脚本更新
- 文件路径: `src/main.sh`
- 修改内容: 添加对"ppt"类型的处理逻辑，调用专门的PPT转换器

## 测试验证
使用测试文件 `test/fixtures/测试部门年度述职报告.ppt` 进行测试：
- 转换成功完成
- 生成的Markdown文件内容正确显示中文
- 无乱码问题

## 依赖要求
- LibreOffice (必需)
- pdftotext (来自poppler工具包，用于PDF文本提取)

## 使用方法
用户现在可以正常转换PPT文件，系统会自动选择合适的转换器进行处理。

## 后续优化建议
1. 可以考虑添加更多PPT转换选项
2. 优化转换后的Markdown格式
3. 添加图片提取功能