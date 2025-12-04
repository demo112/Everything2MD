# DESIGN_构建测试体系

## 1. 架构图 (Mermaid)

```mermaid
graph TD
    TestRunner[Test Runner (pytest/bats)]
    
    subgraph Python_Tests [Python Test Suite]
        API_Tests[Web API Tests]
        GUI_Tests[GUI Logic Tests]
        Mock_Sys[Mocks (Subprocess/FS)]
        
        API_Tests --> Mock_Sys
        GUI_Tests --> Mock_Sys
    end
    
    subgraph Shell_Tests [Shell Test Suite]
        Bats_Core[Bats Core]
        Unit_Bats[Unit Scripts]
        Integration_Bats[Integration Scripts]
        
        Bats_Core --> Unit_Bats
        Bats_Core --> Integration_Bats
    end
    
    TestRunner --> Python_Tests
    TestRunner --> Shell_Tests
```

## 2. 分层设计
1.  **Unit Layer (Python)**:
    -   针对 `web/backend/main.py` 中的 `ConfigModel` 和工具函数。
    -   针对 `src/gui/main.py` 中的配置处理逻辑（需重构/解耦以便测试）。
2.  **Interface Layer (Web API)**:
    -   使用 `TestClient` 测试 FastAPI 路由。
    -   验证输入输出格式、状态码。
3.  **Integration Layer (Shell)**:
    -   现有的 Bats 测试。

## 3. 模块依赖
-   `pytest`: 核心测试运行器。
-   `httpx`: 用于 FastAPI TestClient。
-   `pytest-asyncio`: 用于异步接口测试。

## 4. 接口契约
-   测试文件命名遵循 `test_*.py`。
-   Shell 测试遵循 `*.bats`。
