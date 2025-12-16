# ACCEPTANCE_打包发布

## 1. 执行记录
- **时间**: 2025-12-16
- **版本**: 基于当前 HEAD
- **工具**: PyInstaller

## 2. 变更内容
- 更新了 `Everything2MD.spec`，添加了 `hiddenimports=['pptx2md', 'pptx2md.entry', 'pptx2md.types', ...]`。
- 重新构建了 `dist/Everything2MD.exe`。

## 3. 结果验证
- 构建过程无错误。
- EXE 文件大小约 75MB。
- 包含了最新的 PPTX 修复逻辑。
