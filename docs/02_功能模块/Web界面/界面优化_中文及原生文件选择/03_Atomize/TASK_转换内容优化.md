# TASK: 转换内容优化

## 任务分解

### Task 1: 修改 Pandoc 转换参数
- [ ] 编辑 `src/modules/pandoc_converter.sh`。
- [ ] 将 `pandoc_cmd+=" -t markdown"` 修改为 `pandoc_cmd+=" -t gfm"`。
- [ ] 或者尝试 `-t markdown-raw_attribute-native_spans`。

### Task 2: 验证转换效果
- [ ] 使用用户提供的案例（如果无法获取原文件，则创建一个包含类似结构的 DOCX）。
- [ ] 运行转换并检查输出内容。

### Task 3: 后处理清理（备选）
- [ ] 如果 GFM 格式仍保留某些标签，编写 `sed` 命令进行清理。
- [ ] 集成到 `process_single_file` 流程中。

## 依赖关系
无外部依赖，仅修改脚本。
