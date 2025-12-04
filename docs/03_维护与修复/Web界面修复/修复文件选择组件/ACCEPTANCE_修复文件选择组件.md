# ACCEPTANCE_修复文件选择组件

## 1. 验收标准
- [x] **路径兼容性**: 后端 `list_files` 能正确处理 Linux 根目录 `/`，不再强制扫描 Windows 盘符。
- [x] **Bash 路径**: 在 Linux 环境下，`convert` 任务能正确调用系统 `bash`。
- [x] **依赖完善**: 补充了缺失的 `websockets` 依赖，确保日志功能正常。
- [x] **功能验证**:
  - 访问 `/api/files?path=/` 返回 Linux 目录结构。
  - 访问 `/api/files?path=/work` 返回项目挂载目录。

## 2. 验证记录
- **API 测试**: 使用 `Invoke-WebRequest` 测试了根目录和工作目录的列出功能，均返回 200 OK 及正确 JSON 数据。
- **构建测试**: Docker 容器重建成功，服务正常启动。

## 3. 结论
修复任务完成，文件选择组件在 Docker 环境下已可用。
