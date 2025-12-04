# CONSENSUS: 转换内容优化

## 需求定义
1. **移除语言标签**: 去除 `[text]{lang="zh-CN"}` 这种格式，只保留 `text`。
2. **简化图片语法**: 去除 `{width="..." height="..."}` 属性。
3. **格式通用化**: 输出标准的 GitHub Flavored Markdown (GFM) 或 CommonMark，以获得更好的兼容性。

## 技术实现方案

### 方案 A: Pandoc 扩展参数 (推荐)
Pandoc 支持通过 `-t` 参数指定输出格式的变体。
- 使用 `-t gfm` (GitHub Flavored Markdown) 通常会产生更干净的输出，自动忽略很多 Pandoc 特有的属性。
- 或者使用 `-t markdown-raw_attribute-native_spans-bracketed_spans` 来禁用特定扩展。

### 方案 B: 正则表达式后处理 (Sed)
如果 Pandoc 参数无法完全去除，可以使用 `sed` 进行后处理。
- 去除语言标签: `sed -E 's/\[([^]]+)\]\{lang="[^"]+"}/\1/g'` (复杂，且容易误伤)。
- 去除属性: `sed -E 's/\{[^}]+\}//g'`。

### 决策
优先尝试修改 `src/modules/pandoc_converter.sh` 中的 Pandoc 命令，将目标格式从 `markdown` 改为 `gfm`（GitHub Flavored Markdown）。GFM 不支持 Pandoc 的 `{attr}` 语法，因此 Pandoc 会自动将其剥离。

## 验收标准
- 转换后的 Markdown 文件中不应包含 `{lang="zh-CN"}`。
- 图片标记应为标准的 `![](image.png)`，不带 `{width...}`。
- 内容可读性大幅提升。
