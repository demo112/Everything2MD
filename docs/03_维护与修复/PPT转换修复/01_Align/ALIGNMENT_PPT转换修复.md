# ALIGNMENT_PPT转换修复

## 1. 项目上下文分析

### 1.1 项目背景
Everything2MD 是一个将各种文档转换为 Markdown 的工具。当前 PPT/PPTX 转换功能存在严重问题，导致用户无法正常转换演示文稿。

### 1.2 技术栈与架构
- **核心语言**: Python (主要逻辑), Shell (辅助脚本)
- **转换核心**: 
  - `pptx2md` (首选，用于 PPTX)
  - `LibreOffice` (降级方案，用于 PPT 和 PPTX 失败时) -> PDF -> `Pandoc` -> Markdown
- **环境**: Windows, Python 3.x, Virtualenv (.venv)

## 2. 需求理解确认

### 2.1 原始需求
用户反馈：
- "ppt和pptx仍然不行"
- 错误日志显示 `pptx2md` 模块未安装。
- 降级使用 LibreOffice 转换 PDF 失败。
- Pandoc 转换 PDF 到 Markdown 失败 (exit code 21)。

### 2.2 核心问题
1.  **依赖缺失**: `requirements.txt` 中缺少 `pptx2md` 和 `python-pptx`，导致 Python 代码无法导入 `pptx2md`。
2.  **LibreOffice 转换失败**: 部分文件 LibreOffice 转换 PDF 失败，原因待查（可能是 LibreOffice 安装问题、文件损坏或命令参数问题）。
3.  **Pandoc 错误**: Exit code 21 通常表示 "Pandoc died of a signal" 或其他转换错误，可能与 PDF 内容（如复杂布局、特定字体）有关。

### 2.3 任务目标
1.  **修复依赖**: 将 `pptx2md` 及相关依赖加入 `requirements.txt` 并确保安装。
2.  **验证 PPTX 转换**: 确保 PPTX 文件优先使用 `pptx2md` 成功转换。
3.  **优化降级策略**: 检查 LibreOffice 和 Pandoc 的调用方式，提升稳定性（虽然首选修复 pptx2md，但降级路径也应尽可能健壮）。
4.  **测试验证**: 添加测试用例覆盖 PPT/PPTX 转换。

## 3. 疑问与决策

### 3.1 疑问澄清
- **Q1**: `pptx2md` 是否支持所有 PPTX 内容？
  - **A**: 主要支持文本和图片，复杂动画不支持。对于 Markdown 转换通常足够。
- **Q2**: LibreOffice 失败的具体原因？
  - **A**: 可能是环境问题或特定文件兼容性。优先修复 `pptx2md` 可规避大部分 PPTX 问题。对于 PPT (非 X)，仍需依赖 LibreOffice。

### 3.2 智能决策
- **决策 1**: 立即在 `requirements.txt` 中添加 `pptx2md` (需确认 PyPI 包名，通常是 `pptx2md` 或直接依赖其仓库，若 PyPI 上有维护良好的版本则优先使用)。
  - *注*: 经查，PyPI 上有 `pptx2md` 包。
- **决策 2**: 完善 `src/core/converters/ppt.py` 中的错误处理，确保明确提示用户安装依赖（如果运行时缺失）。
- **决策 3**: 针对 PPT (非 X) 文件，检查 LibreOffice 调用参数，尝试增加 `--headless` 等参数确保后台运行稳定。

## 4. 最终共识
- 必须修复依赖问题。
- 必须验证修复后的转换流程。
- 必须同步更新 6A 文档。
