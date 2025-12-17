# FINAL_打包发布

## 1. 总结
成功使用 PyInstaller 将项目打包为单文件可执行程序 (`Everything2MD.exe`)。
打包配置已更新，确保了 `pptx2md` 等新增依赖被正确包含。

**2025-12-16 更新**: 
- 重新打包以包含 PDF 导出功能及相关 Bug 修复。
- 验证版本包含 `src/gui/main.py` 的最新更改（PDF 选项）。

## 2. 交付物
- `dist/Everything2MD.exe`: 最终可执行文件。
- `Everything2MD.spec`: 更新后的打包配置文件。

## 3. 注意事项
- **外部依赖**: 该 EXE 不包含 LibreOffice 和 Pandoc。用户必须在运行机器上安装这些软件，并确保它们在系统 PATH 中。
- **启动时间**: 单文件模式启动时需要解压，初次启动可能稍慢。
- **防毒软件**: 未签名的 EXE 可能会被部分杀毒软件误报。

## 4. 后续建议
- 考虑添加版本号资源文件。
- 考虑使用 Inno Setup 制作安装包，将 Pandoc 甚至 LibreOffice (便携版) 捆绑发布。
