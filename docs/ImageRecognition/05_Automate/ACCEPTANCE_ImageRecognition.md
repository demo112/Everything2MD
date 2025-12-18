# ACCEPTANCE: Image Recognition (解析增强)

## 任务执行概览

| 任务ID | 任务名称 | 状态 | 备注 |
|:-----------------|:-----------------|:-----------------|:-----------------|
| Task 1.1 | Update requirements.txt | 已完成 | `httpx` 已存在 |
| Task 1.2 | Update src/core/config.py | 已完成 | 添加了 image_recognition 配置项 |
| Task 2.1 | Create src/core/image_recognition.py | 已完成 | 核心逻辑已实现 |
| Task 3.1 | Modify src/core/engine.py | 已完成 | 已集成到转换流程，修复了调用逻辑缺失问题 |
| Task 4.1 | Modify src/gui/main.py | 已完成 | 新增了"解析增强"页签及配置控件 |
| Task 5.1 | Create tests/test_image_recognition.py | 已完成 | 自动化测试通过 |
| Task 5.2 | Manual Verification | 待执行 | 需启动 GUI 进行手动验证 |

## 验证详情

### 1. 自动化测试验证

执行命令：`python -m pytest tests/test_image_recognition.py` 结果：Passed - **Mock Config**: 验证了配置读取逻辑。 - **Mock HTTPX**: 验证了图片上传和 API 调用逻辑。 - **Process Markdown**: 验证了 Markdown 解析、图片路径解析和文本注入逻辑。 - **Disabled State**: 验证了功能禁用时不会触发 API 调用。

### 2. 代码逻辑检查

-   **GUI**: `src/gui/main.py` 已添加 `init_parsing_tab`，并绑定了 `ConfigManager`。
-   **Config**: 修复了 `ConfigManager.get` 方法中缺失的 image_recognition 配置项读取逻辑，确保配置持久化生效。
-   **Engine**: `src/core/engine.py` 修复了 `ImageRecognizer` 调用逻辑，确保在转换成功且生成 MD 文件后触发。
-   **ImageRecognizer**:
    -   使用 `asyncio.Semaphore` 控制并发，符合需求。
    - **[NEW] Prompt Strategy**: 已更新 System Prompt，要求输出 `Visual Type`, `Title`, `Data Points`, `Trends / Insights` 等结构化字段。
    - **[NEW] Injection Format**: 修复了多行描述的 Markdown 注入逻辑，确保每行都带有 `> ` 前缀。
    - **[FIX] URL Decoding**: 修复了图片路径包含 URL 编码字符（如中文）时导致无法找到文件的问题。

## 遗留问题 / 后续计划

-   [ ] 手动启动 GUI，配置 API Key，转换一个带图片的 Word 文档，验证最终效果。