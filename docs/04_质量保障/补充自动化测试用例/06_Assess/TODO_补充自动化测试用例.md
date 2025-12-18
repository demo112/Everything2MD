# 待办事项：补充自动化测试用例

## 1. 待办任务 (TODO)
以下任务为本次项目执行过程中发现的、建议后续跟进的事项：

- [ ] **集成测试环境搭建**
    - 说明：当前测试使用 Mock 模拟了 LibreOffice 和 Pandoc，建议在 CI 流水线中安装真实工具进行端到端测试。
    - 优先级：中

- [ ] **测试覆盖率提升 (Engine & Utils)**
    - 说明：GUI 和 Converters 覆盖率已达标，但 `src/core/engine.py` (0%) 和 `src/core/utils.py` (25%) 覆盖率仍然较低，建议补充。
    - 优先级：低

- [ ] **图片识别真实测试**
    - 说明：当前图片识别测试依赖 Mock API 响应，建议添加少量真实图片和 OCR 服务调用测试（需配置真实 API Key）。
    - 优先级：低

- [ ] **依赖版本锁定**
    - 说明：建议生成 `requirements-test.txt` 锁定测试依赖版本，确保环境一致性。
    - 优先级：低

## 2. 缺失配置
- **无**：本次任务已安装所有必要依赖，并在虚拟环境中运行良好。

## 3. 操作指引
- **运行测试**:
  ```bash
  # 激活虚拟环境
  .\venv\Scripts\activate
  # 运行所有测试并查看覆盖率
  python -m pytest tests/ --cov=src --cov-report=term-missing
  # 运行特定测试文件
  python -m pytest tests/test_gui_main.py
  ```
- **代码格式化**:
  ```bash
  python -m black .
  ```
