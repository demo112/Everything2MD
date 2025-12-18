# ALIGNMENT_PPTX_Conversion_Fix

## 1. 项目上下文分析

### 1.1 问题背景
用户反馈日志显示 PPTX 转换过程中出现多重失败：
1. `pptx2md` 库调用报错 `'NoneType' object has no attribute 'write'`。
2. `pptx2md` 命令行回退报错 `[WinError 2] 系统找不到指定的文件`。
3. `Pandoc` 转换 PDF 失败 (Exit code 21)。
4. 最终回退到 `pdfminer` 成功提取文本。

### 1.2 现有架构
- **语言**: Python
- **PPTX 转换**: 优先 `pptx2md` (库调用 -> 命令行调用)，失败则降级为 LibreOffice -> PDF -> Pandoc/pdftotext/pdfminer。

## 2. 需求理解确认

### 2.1 核心问题
1.  **pptx2md 库调用错误**: 极可能是参数类型不匹配（传递了 `Path` 对象而非 `str`）或配置初始化问题。
2.  **命令行路径问题**: `subprocess` 无法在 PATH 中找到 `pptx2md` 可执行文件，尤其是在 Windows 虚拟环境下。
3.  **Pandoc 问题**: Pandoc 转换 PDF 依赖外部工具（如 pdftotext），环境缺失导致失败。

### 2.2 任务目标
1.  修复 `pptx2md` 库调用逻辑，确保首选方案可用。
2.  修复 `pptx2md` 命令行调用逻辑，作为稳健的备选方案。
3.  保持 `pdfminer` 作为最后的兜底方案。

## 3. 智能决策

### 3.1 决策点
- **参数类型转换**: 在调用 `pptx2md` API 之前，显式将 `Path` 对象转换为字符串。
- **可执行文件定位**: 动态查找 `pptx2md` 可执行文件路径（检查 `sys.prefix/Scripts` 或 `sys.executable` 同级目录）。
- **错误处理**: 完善日志，明确指示用户安装缺失的外部工具（如 Pandoc/Poppler），但不阻断流程。

## 4. 最终共识
- 优先修复 `pptx2md` 流程，因为它是 PPTX 的最佳转换方式。
- 确保命令行回退机制能正确找到可执行文件。
