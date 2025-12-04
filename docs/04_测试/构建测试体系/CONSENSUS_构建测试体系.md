# CONSENSUS_构建测试体系

## 1. 需求精确描述
构建一个覆盖 Python 后端接口、核心逻辑以及 Shell 脚本集成的混合测试体系。

**验收标准**：
1. **Python 测试环境**：
   - 配置 `pytest` 及相关插件（`pytest-asyncio`, `httpx`）。
   - 建立 `tests/python` 目录结构。
2. **Web 接口测试**：
   - 覆盖 `/api/config` (GET, POST)。
   - 覆盖 WebSocket 连接（基础连接测试）。
3. **单元测试**：
   - 覆盖 Python 配置模型验证 (`pydantic` models)。
   - 覆盖 GUI 中的非界面逻辑（如配置加载/保存）。
4. **集成测试**：
   - 确保 Python 能正确调用底层 Shell 脚本（Mock subprocess 或实际调用）。
5. **文档**：
   - 提供测试运行指南。

## 2. 技术实现方案
- **框架**：`pytest`
- **HTTP Client**：`TestClient` (from `fastapi.testclient`)
- **Mocking**：`unittest.mock` (用于模拟 subprocess 和文件系统)
- **目录结构**：
  ```
  test/
    bats/           # 现有 Shell 测试
    python/         # 新增 Python 测试
      conftest.py   # 共享 Fixtures
      test_web_api.py
      test_gui_logic.py
  ```

## 3. 任务边界
- 重点在于 Python 层的测试补全。
- 保持现有 `test/bats` 结构不变，但需确保在统一命令下可运行（如 Makefile 或脚本）。
