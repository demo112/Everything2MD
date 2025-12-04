# 依赖集成 - 待办事项

## 优先级: 低
- [ ] **LibreOffice Portable 集成**:
  - 调研 LibreOffice Portable 的自动化下载与解压（体积较大，需考虑下载体验）。
  - 验证 `src/modules/libreoffice_converter.sh` 对便携版路径的支持。

- [ ] **跨平台支持增强**:
  - 当前 `install_deps.py` 主要针对 Windows 下载。需增加 Linux/macOS 的对应二进制包下载逻辑（虽然 Docker 和包管理器通常更好）。
