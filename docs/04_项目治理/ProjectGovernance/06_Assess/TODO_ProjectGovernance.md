# TODO_ProjectGovernance

## 待办事项清单

### 高优先级 (High Priority)
1. **依赖固化**:
   - [ ] 检查 `requirements.txt`，确保包含 `psutil`, `pdfminer.six`, `pytest`, `pytest-mock`, `pytest-flask` 等所有运行时和测试依赖。
   - [ ] 验证在全新环境下的 `pip install -r requirements.txt` 是否能一键配置成功。

2. **文档维护**:
   - [ ] 将 `docs/00_Global/Project_Unified_Manual_L1_L3.md` 的内容拆分或链接到具体的 `README.md`，方便 GitHub/GitLab 首页展示。

### 中优先级 (Medium Priority)
1. **测试增强**:
   - [ ] 增加对 `src/core/converters/office.py` 的测试覆盖率（目前较低）。
   - [ ] 引入 `tox` 或类似工具进行多环境（Python 3.10/3.11/3.12/3.13）测试。

2. **CI/CD 集成**:
   - [ ] 配置 GitHub Actions 或 GitLab CI，自动运行 `pytest`。

### 低优先级 (Low Priority)
1. **代码重构**:
   - [ ] `src/gui/main.py` 文件较大，考虑进一步拆分为 `gui_components/` 模块。

## 缺少的配置/支持
- **Docker 环境**: 目前项目缺乏 Dockerfile 和 docker-compose.yml，建议添加以标准化开发和部署环境。
- **UI 自动化测试工具**: 缺少如 Selenium 或 Appium (针对桌面应用) 的集成测试工具。
