# ALIGNMENT: 增加 emmx 格式兼容

## 1. 项目上下文分析
Everything2MD 是一个将各种文档格式转换为 Markdown 的工具。
目前支持 Office (Word, Excel, PPT) 等格式。
核心转换逻辑位于 `src/core/converters`，通过 `base.py` 定义基类接口。
GUI 入口在 `src/gui/main.py`。

## 2. 需求理解
**原始需求**: 增加 emmx 格式的兼容。
**需求分析**:
- 目标格式: Markdown (.md)
- 源格式: .emmx (亿图脑图 MindMaster/EdrawMind 文件)
- 核心功能: 解析 .emmx 文件内容，提取思维导图的层级结构，转换为 Markdown 的列表或标题结构。

## 3. 疑问澄清
- **Q1**: emmx 文件的具体结构是什么？
  - **A1**: emmx 文件通常是一个 ZIP 压缩包，解压后包含 `mindmap.json` 或 `doc/document.json`，其中存储了节点文本和层级关系。
- **Q2**: 转换后的 Markdown 风格？
  - **A2**: 建议使用无序列表 (`- `) 来表示层级关系，或者根据层级深度使用标题 (`#`, `##`)。考虑到思维导图层级可能很深，无序列表更通用。
- **Q3**: 是否需要支持图片或附件？
  - **A3**: 首期目标是提取文本结构。如果节点包含图片，可以尝试提取并保存到 assets 目录，但在本次迭代中优先保证文本结构的正确转换。
- **Q4**: 是否需要支持其他思维导图格式（如 xmind）？
  - **A4**: 本次任务仅关注 emmx。

## 4. 智能决策策略
- **解析方案**: 使用 Python 的 `zipfile` 模块解压 `.emmx` 文件，读取其中的 JSON 数据文件，递归解析节点树。
- **集成方案**:
  - 新增 `src/core/converters/emmx.py` 实现 `BaseConverter`。
  - 在 `src/core/engine.py` 或工厂类中注册该转换器。
  - 更新 GUI 文件选择过滤器以包含 `.emmx`。

## 5. 最终共识
- **输入**: `.emmx` 文件路径。
- **输出**: 同名的 `.md` 文件。
- **转换规则**:
  - 根节点 -> 一级标题 (`# Root`) 或 文件名。
  - 子节点 -> 缩进列表 (`- Node`)。
  - 备注/注释 -> 引用块 (`> Note`) 或 忽略（视复杂度而定，默认提取）。
  - 超链接 -> Markdown 链接。
