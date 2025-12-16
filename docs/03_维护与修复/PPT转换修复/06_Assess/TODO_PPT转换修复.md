# TODO_PPT转换修复

## 已完成事项
- [x] **修复依赖**: `requirements.txt` 已更新，添加了 `pptx2md`。
- [x] **优化代码**: `src/core/converters/ppt.py` 已增强，支持 `pptx2md` v2.0+ 接口，并优化了 LibreOffice 调用。
- [x] **验证修复**: 创建了 `verify_fix.py` 并确认 PPTX 转换路径工作正常。
- [x] **测试覆盖**: `tests/test_ppt_conversion.py` 已通过，使用模拟文件覆盖了转换管道逻辑。

## 待办事项 (用户侧)
1.  **安装 LibreOffice**:
    - 检测到系统当前未正确配置 LibreOffice。PPT (非 X) 格式转换强烈依赖 LibreOffice。
    - 请安装 LibreOffice 并确保 `soffice` 命令在 PATH 中可用。
2.  **Docker 镜像更新**:
    - 如果使用 Docker 部署，请重新构建镜像以包含新的 `pptx2md` 依赖。
    - 运行: `docker-compose build --no-cache`
3.  **替换测试夹具 (可选)**:
    - `test/fixtures/sample.ppt` 已损坏。如果需要进行真实的二进制 PPT 文件测试，请替换该文件。
