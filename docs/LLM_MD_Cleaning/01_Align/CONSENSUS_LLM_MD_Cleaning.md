# CONSENSUS: LLM Markdown Cleaning (解析增强 - 结构化清洗)

## 1. 需求共识

### 1.1 核心目标
在 "解析增强" 模块中引入 **结构化清洗** 功能，利用 LLM 对转换后的 Markdown 进行格式优化（如标题层级修复、列表规范化、表格整理），同时 **绝对保证** 文本内容不被篡改。

### 1.2 关键决策
1.  **配置独立性**: 该功能拥有独立的 LLM 配置（API Base, Key, Model），不强制与图片识别共享，以支持用户针对不同任务选择最具性价比的模型（如使用 DeepSeek-V3 进行清洗，GPT-4V 进行识图）。
2.  **零容忍验证机制**: 
    - 采用 **"剥离-对比"** 策略：在应用 LLM 结果前，分别剥离 原文 和 新文 的所有 Markdown 标记（保留纯文本）。
    - 计算并比对纯文本的 Hash 值（或直接字符串比对）。
    - **任何不匹配都将导致操作回滚**，保留原文件，并记录 "清洗失败：内容完整性校验未通过" 的日志。
3.  **处理策略**: 
    - 仅支持长窗口模型处理完整文档，不进行分块（避免切分导致结构断裂）。
    - 若文档超过 Context Window，跳过并记录警告。

## 2. 详细规格

### 2.1 用户界面 (UI)
- **位置**: `src/gui/main.py` -> "解析增强" 页签。
- **新增区域**: "Markdown 结构化清洗 (LLM)"。
- **控件**:
    - [x] 启用开关 (Enable Structure Cleaning)
    - [ ] API Base URL (默认: https://api.openai.com/v1)
    - [ ] API Key (掩码显示)
    - [ ] Model Name (默认: gpt-3.5-turbo 或 deepseek-chat)
    - [ ] Temperature (固定为 0 或极低值，用户不可见或高级选项)

### 2.2 核心流程
1.  **转换完成**: `ConversionEngine` 生成初步 Markdown。
2.  **图片识别 (可选)**: 如果启用，先执行图片识别注入。
3.  **清洗触发**: 如果启用清洗且上一步成功。
4.  **LLM 处理**:
    - System Prompt: 强调 "Format only. Do not change text content."
    - User Prompt: 传入 Markdown 内容。
5.  **安全校验**:
    - `text_original = remove_markdown(original_content)`
    - `text_cleaned = remove_markdown(llm_response)`
    - If `text_original == text_cleaned`: 保存新文件。
    - Else: 丢弃，Log Error。

## 3. 技术栈
- **HTTP Client**: `httpx` (复用现有依赖)。
- **Text Comparison**: Python 标准库 `re` (正则剥离 Markdown) 或 `BeautifulSoup` (如果转 HTML 后提取文本，但可能太重)。推荐使用 `markdown` 库转 HTML 后提取 text，或者简单的正则去除常见 MD 标记。为了性能和准确性，建议使用 `re` 去除 `#, *, -, [], (), >` 等符号后对比。
- **UI**: `tkinter` / `ttkbootstrap`。

## 4. 验收标准
- [ ] UI 配置项完整且能保存到 `config.json`。
- [ ] 能成功调用 LLM 并获取返回结果。
- [ ] **正向用例**: 输入格式混乱但内容正确的 MD，输出格式规范且校验通过。
- [ ] **负向用例 (模拟)**: 强制 LLM 修改文本（通过篡改 Prompt 模拟），系统必须检测到不一致并拒绝保存。
- [ ] **日志**: 清晰记录 "清洗开始"、"校验通过/失败"、"清洗耗时"。
