# LibreOffice中文文件名处理问题修复说明

## 问题描述

在使用Everything2MD工具处理包含中文文件名的Office文档时，出现了以下错误：

```
[ERROR] LibreOffice转换后的HTML文件不存在: /var/folders/wx/4n7vzxbj4sl72qyxv4519_4h0000gn/T/tmp.of3HZk68Mu/测试部门年度述职报告.html
```

## 问题原因分析

经过分析和测试，发现该问题是由以下原因造成的：

1. **文件路径编码问题**：LibreOffice在处理包含非ASCII字符（如中文）的文件路径时，可能会出现编码不一致的问题。

2. **文件名匹配不准确**：原代码中使用固定的文件名模式`$(basename "${input_file%.*}").html`来查找转换后的HTML文件，但在处理特殊字符文件名时，实际生成的文件名可能与预期不符。

3. **临时文件处理**：直接使用原始文件路径传递给LibreOffice，可能导致在某些系统环境下处理异常。

## 解决方案

针对上述问题，我们采取了以下修复措施：

1. **安全的临时文件处理**：
   - 将输入文件复制到临时目录中，使用更安全的文件名处理方式
   - 通过`local safe_input_file="$temp_dir/$(basename "$input_file")"`创建安全的临时文件路径

2. **改进HTML文件查找逻辑**：
   - 使用通配符匹配方式查找生成的HTML文件：`for file in "$temp_dir"/*.html`
   - 添加备用文件名匹配机制，尝试多种可能的文件名模式
   - 提供更详细的错误信息，包括临时目录内容，便于调试

3. **增强错误处理**：
   - 添加更详细的错误日志，包含输入文件信息和临时目录内容
   - 改进文件存在性检查逻辑

## 代码变更

主要修改了`src/modules/libreoffice_converter.sh`文件中的`convert_office_to_md`函数：

1. 添加了安全的临时文件处理机制
2. 改进了HTML文件查找逻辑
3. 增强了错误处理和日志记录

## 验证测试

### 4.1 单元测试

1. **LibreOffice转换器单元测试**:
   ```bash
   # 运行单元测试
   make unit-test
   
   # 验证中文文件名处理功能
   # 测试用例覆盖各种中文字符和特殊字符
   ```

### 4.2 集成测试

1. **中文文件名转换测试**:
   ```bash
   # 创建包含中文文件名的测试文件
   cp test/fixtures/sample.docx "测试文档.docx"
   
   # 运行转换
   ./everything2md.sh "测试文档.docx"
   
   # 验证输出文件存在
   ls -la "测试文档.md"
   
   # 验证内容不为空
   [ -s "测试文档.md" ] && echo "转换成功" || echo "转换失败"
   ```

2. **特殊字符文件名测试**:
   ```bash
   # 测试包含空格和特殊字符的文件名
   cp test/fixtures/sample.docx "测试 文档 (2024).docx"
   
   # 运行转换
   ./everything2md.sh "测试 文档 (2024).docx"
   
   # 验证输出
   ls -la "测试 文档 (2024).md"
   ```

3. **错误处理测试**:
   ```bash
   # 测试不存在的文件
   ./everything2md.sh "不存在的中文文件.docx"
   
   # 验证错误信息
   # 应该显示清晰的错误提示，而不是HTML文件不存在错误
   ```

4. **临时文件清理测试**:
   ```bash
   # 转换前记录临时目录状态
   temp_count_before=$(ls /tmp/everything2md_* 2>/dev/null | wc -l)
   
   # 运行转换
   ./everything2md.sh "测试文档.docx"
   
   # 转换后检查临时文件是否被清理
   temp_count_after=$(ls /tmp/everything2md_* 2>/dev/null | wc -l)
   
   # 验证临时文件被正确清理
   [ $temp_count_after -le $temp_count_before ] && echo "清理成功" || echo "清理失败"
   ```

## 后续建议

1. 建议进一步测试其他特殊字符文件名的处理情况
2. 可以考虑添加更全面的国际化支持
3. 建议增加更多边界情况的测试用例