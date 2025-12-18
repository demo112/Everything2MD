# TASK: Image Recognition (解析增强)

## 1. 依赖与配置

-   [ ] **Task 1.1**: 更新 `requirements.txt` (确保 `httpx` 存在，通常已存在)。
-   [ ] **Task 1.2**: 更新 `src/core/config.py`。
    -   在 `get_default_config` 中添加 `image_recognition` 默认值。
    -   添加新键的 getter/setter。

## 2. 核心实现

-   [ ] **Task 2.1**: 创建 `src/core/image_recognition.py`。
    -   实现 `ImageRecognizer` 类。
    -   使用 `httpx` (异步) 实现 `recognize_image`。
    -   实现 `process_markdown` (管理异步循环的同步包装器)。
    -   实现 Markdown 正则解析和替换。
    -   **提示策略**: 更新系统提示以输出结构化数据（视觉类型、标题、数据点、趋势）。
    -   **注入格式**: 处理带有引用前缀的多行结构化描述。

## 3. 集成

-   [ ] **Task 3.1**: 修改 `src/core/engine.py`。
    -   导入 `ImageRecognizer`。
    -   在 `convert_file` 中，如果启用了功能，则在转换后添加调用 `process_markdown` 的逻辑。

## 4. 用户界面

-   [ ] **Task 4.1**: 修改 `src/gui/main.py`。
    -   添加 `init_parsing_tab` 方法。
    -   在 Notebook 中创建 "解析增强" 页签。
    -   添加启用、API Base、API Key、Model、Max Jobs 的控件。
    -   将控件绑定到 `ConfigManager`。

## 5. 验证

-   [ ] **Task 5.1**: 创建测试脚本 `tests/test_image_recognition.py`。
    -   Mock `httpx` 响应。
    -   测试 Markdown 解析和注入。
-   [ ] **Task 5.2**: 使用 GUI 进行手动验证。
