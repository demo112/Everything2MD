# DESIGN: 构建完善的测试体系

## 1. 体系架构

### 1.1 核心原则
*   **金字塔模型**: 大量单元测试，适量集成测试，少量 UI 测试。
*   **独立性**: 测试用例之间不应相互依赖，不应依赖外部不可控环境（网络、特定OS配置）。
*   **可重复**: 任何时间运行结果应一致。

### 1.2 模块设计

#### 1.2.1 `test/conftest.py`
*   **Fixture: `mock_config`**: 提供一个基于内存或临时文件的 `ConfigManager` 实例，避免污染本地 `config.json`。
*   **Fixture: `temp_workspace`**: 提供一个包含测试文件的临时目录，测试结束后自动清理。
*   **Fixture: `mock_rag_client`**: 模拟 `RAGFlowClient`，拦截网络请求。

#### 1.2.2 单元测试 (`test/unit/core/`)
*   `test_config.py`:
    *   测试 `load_config`, `save_config`, `get`, `set`。
    *   测试异常文件处理。
*   `test_engine.py`:
    *   测试 `detect_type`。
    *   测试 `convert_file` (Mock Converter)。
    *   测试 `run` (ThreadPoolExecutor 行为)。
    *   测试回调函数触发。
*   `test_utils.py`:
    *   测试日志记录。

#### 1.2.3 集成测试 (`test/integration/`)
*   `test_conversion_flow.py`:
    *   创建一个真实的 `.txt` 文件。
    *   调用 `ConversionEngine` 进行转换。
    *   验证输出的 `.md` 文件是否存在且内容正确。

### 1.3 运行机制
*   **脚本**: `run_tests.py`
    *   自动安装依赖 (`pip install -r requirements.txt`) - *可选，或者仅检查*。
    *   运行 `pytest`。
    *   生成 Coverage 报告。

## 2. 工具链
*   `pytest`: 核心运行器。
*   `pytest-cov`: 覆盖率分析。
*   `pytest-mock`: 简化 Mock 写法。
