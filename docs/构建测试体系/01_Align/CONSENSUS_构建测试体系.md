# CONSENSUS: 构建完善的测试体系

## 1. 最终共识
我们一致同意采用以下方案构建测试体系：

### 1.1 技术选型
*   **测试框架**: `pytest`
*   **Mock 工具**: `unittest.mock` (标准库) + `pytest-mock`
*   **覆盖率**: `pytest-cov`

### 1.2 目录结构
```
test/
  ├── unit/                 # 单元测试
  │   ├── core/             # src/core 测试
  │   │   ├── test_config.py
  │   │   ├── test_engine.py
  │   │   ├── test_utils.py
  │   │   └── test_ragflow_client.py
  │   └── gui/              # GUI 逻辑测试
  │       └── test_gui_logic.py
  ├── integration/          # 集成测试
  │   └── test_conversion_flow.py
  ├── fixtures/             # 测试数据
  ├── conftest.py           # Pytest 配置 & Fixtures
  └── bats/                 # (保留) Shell 测试
```

### 1.3 实施步骤
1.  重构 `test` 目录。
2.  为 `ConfigManager`, `ConversionEngine` 编写单元测试。
3.  编写端到端集成测试（模拟文件转换）。
4.  配置 `pytest.ini` 和运行脚本。

## 2. 边界限制
*   不涉及真实的 GUI 自动化点击测试（如 Selenium/PyAutoGUI），仅测试逻辑。
*   不涉及真实的 RAGFlow 服务器交互，全部使用 Mock。

## 3. 验收标准
*   所有新编写的测试用例通过。
*   `python run_tests.py` 可执行并生成报告。
