# Everything2MD 打包任务待办事项清单

## 待办事项

### 1. 用户配置事项
- [ ] 配置环境变量（如需要）
- [ ] 根据实际需求调整依赖项路径

### 2. 部署事项
- [ ] 将Windows发行版上传到分发服务器
- [ ] 将macOS发行版上传到分发服务器
- [ ] 更新项目文档中的下载链接

### 3. 后续优化事项
- [ ] 考虑引入自动化构建系统（如GitHub Actions）
- [ ] 增加Linux平台支持
- [ ] 优化依赖项打包策略，减小发行版体积
- [ ] 增加更多边界条件测试

### 4. 维护事项
- [ ] 定期更新依赖项版本
- [ ] 监控用户反馈，修复潜在问题
- [ ] 根据新需求扩展功能

## 缺失配置

### 1. 环境配置
- 发行版中的依赖项路径已硬编码，如果需要在不同环境中运行，可能需要调整路径设置

### 2. 权限配置
- macOS发行版需要确保启动器脚本具有执行权限
- Windows发行版需要确保批处理文件能够正常运行

### 3. 系统要求
- Windows: 需要支持MSYS2环境的系统
- macOS: 需要支持Bash脚本的系统

## 操作指引

### 1. Windows发行版使用指引
1. 解压Everything2MD-Windows-1.0.0-20251111.zip到目标目录
2. 运行install.bat安装依赖项（首次使用）
3. 双击launcher/windows_launcher.bat启动程序
4. 或者运行everything2md.bat直接启动程序

### 2. macOS发行版使用指引
1. 解压Everything2MD-macOS-1.0.0-20251111.zip到目标目录
2. 将Everything2MD.app拖拽到Applications文件夹
3. 首次运行时可能需要在系统偏好设置中允许应用运行
4. 双击Everything2MD.app启动程序
5. 或者运行launcher/macos_launcher.sh启动程序

### 3. 依赖项说明
- 所有依赖项均已包含在发行版中
- Windows发行版包含便携式LibreOffice、Pandoc和Python
- macOS发行版包含便携式Pandoc
- macOS系统需要预装LibreOffice（如果需要转换Word文档）

### 4. 故障排除
1. 如果启动器报告依赖项缺失：
   - 检查deps目录是否存在且包含所有依赖项
   - 确认启动器脚本具有正确的执行权限
2. 如果转换功能异常：
   - 检查源文件格式是否支持
   - 确认LibreOffice和Pandoc是否正确安装
3. 如果程序无法启动：
   - 检查系统是否满足最低要求
   - 查看控制台输出获取错误信息