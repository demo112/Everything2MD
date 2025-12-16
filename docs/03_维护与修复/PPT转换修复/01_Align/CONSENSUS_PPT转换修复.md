# CONSENSUS_PPT转换修复

## 1. 需求描述与验收标准
- **需求**: 修复 PPT/PPTX 转换失败的问题。
- **验收标准**:
  1.  `requirements.txt` 包含必要的 `pptx2md` 依赖。
  2.  在安装依赖后，运行转换工具不再报 "pptx2md模块未安装"。
  3.  PPTX 文件能成功转换为 Markdown。
  4.  PPT 文件（依赖 LibreOffice）能尽可能成功转换，或给出清晰错误提示。
  5.  新增/更新测试用例通过。

## 2. 技术实现方案
1.  **依赖管理**:
    - 添加 `pptx2md` 到 `requirements.txt`。
    - 添加 `python-pptx` (通常 `pptx2md` 会自动安装，但显式声明更好)。
2.  **代码修正**:
    - 检查 `src/core/converters/ppt.py` 的导入逻辑。
    - 确保 `pptx2md` 调用方式正确（库调用 vs 命令行调用）。
3.  **测试增强**:
    - 在 `tests/` 下添加针对 PPT/PPTX 的集成测试。

## 3. 边界限制
- 仅修复转换逻辑和依赖。
- 不涉及 LibreOffice 软件本身的安装（假设用户环境已安装，但需检查路径检测逻辑）。
- 不保证所有复杂 PPT 格式（如复杂图表、OLE 对象）都能完美还原，重点是文本和图片。

## 4. 风险评估
- `pptx2md` 可能有版本兼容性问题，需锁定版本或测试最新版。
- LibreOffice 在不同系统（尤其是 Windows 服务模式）下可能不稳定。
