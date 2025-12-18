# CONSENSUS_PPTX_Conversion_Fix

## 1. 需求描述与验收标准

### 1.1 需求描述
修复 PPTX 转换过程中 `pptx2md` 库调用和命令行调用的双重失败问题，确保 PPTX 文件能稳定转换为 Markdown。

### 1.2 验收标准
1.  **库调用修复**: `src/core/converters/ppt.py` 中调用 `pptx2md` 时不再抛出 `'NoneType' object has no attribute 'write'`。
2.  **命令行修复**: 如果库调用失败，降级到命令行调用时，能正确找到 `pptx2md.exe` 可执行文件。
3.  **日志完整**: 转换过程中的关键步骤和错误信息应准确记录到日志中。
4.  **测试通过**: 包含一个针对此问题的复现/验证脚本，证明修复有效。

## 2. 技术实现方案

### 2.1 修复 pptx2md 库调用
- **类型转换**: 在构建 `ConversionConfig` 时，强制将 `input_path`, `output_path`, `image_dir` 等 `Path` 对象转换为字符串 (`str(path)`)。`pptx2md` 内部可能使用了不支持 `Path` 对象的字符串操作。
- **配置检查**: 检查 `ConversionConfig` 的其他参数是否符合 `pptx2md` 最新版要求。

### 2.2 修复命令行调用
- **路径定位**: 不直接调用 `pptx2md` 命令，而是使用绝对路径。
  - 在 Windows 虚拟环境中，可执行文件通常位于 `sys.prefix/Scripts/pptx2md.exe`。
  - 实现一个 `get_pptx2md_executable()` 辅助函数来动态查找。

### 2.3 降级策略
- 保持现有的 `pptx2md (Lib)` -> `pptx2md (Cmd)` -> `LibreOffice` -> `Pandoc` -> `pdfminer` 链条。
- 优化错误日志，明确区分是“找不到工具”还是“工具执行失败”。

## 3. 边界限制
- 仅修复 Python 代码逻辑。
- 假设 `pptx2md` 库已安装在环境中（由 `requirements.txt` 保证）。
- 不负责修复 `Pandoc` 或 `LibreOffice` 的安装问题，但需提供清晰的报错。

## 4. 风险评估
- `pptx2md` 库的内部 API 可能会随版本变化。当前修复基于 `pptx2md>=2.0.0`。
