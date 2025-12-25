# CONSENSUS_配置系统重构

## 1. 需求描述与验收标准

### 1.1 需求描述
重构配置管理系统，通过引入集中式映射和自动化绑定机制，解决配置项分散、易遗漏的问题，确保所有配置（特别是新增的结构化清洗配置）都能可靠持久化。

### 1.2 验收标准
1. **代码质量**：`ConfigManager` 中移除针对特定配置项的 `if/else` 判断链，改用字典映射。
2. **自动化同步**：`src/gui/main.py` 中的 `load_config` 和 `save_config` 方法不再包含针对特定配置项的赋值语句，而是遍历绑定列表。
3. **功能验证**：
   - 启动应用，修改“结构化清洗”相关配置（启用、API Key 等）。
   - 关闭应用并重启。
   - 验证配置项是否恢复为修改后的值。
4. **兼容性验证**：
   - 验证旧的配置项（如 `api_key`, `model`, `soffice_path`）读写正常。
   - 验证配置文件格式仍为标准 INI 格式。

## 2. 技术实现方案

### 2.1 ConfigManager 重构
- 新增 `_get_config_mapping(self)` 方法，返回 `Key -> ((Section...), Option)` 的映射字典。
- 重写 `get(key, default)`：查表 -> 定位 Section -> 读取 Option -> 类型转换。
- 重写 `set(key, value)`：查表 -> 定位 Section -> 写入 Option -> 保存文件。

### 2.2 GUI 重构
- 新增 `_init_config_bindings(self)`：定义 `ConfigKey -> (TkinterVar, DefaultValue)` 的绑定字典。
- 重写 `load_config(self)`：遍历绑定字典，从 `ConfigManager` 读取值并设置到 `TkinterVar`。
- 重写 `save_config(self)`：遍历绑定字典，从 `TkinterVar` 读取值并写入 `ConfigManager`。

## 3. 技术约束与集成
- **依赖库**：仅使用标准库 `configparser`。
- **并发控制**：GUI 操作在主线程，配置读写需确保不阻塞（当前文件较小，直接读写即可）。
- **环境**：兼容 Windows/Linux/MacOS。

## 4. 风险评估
- **风险**：键名拼写错误导致映射失败。
- **缓解**：在 `ConfigManager` 中添加日志，当访问未定义的键时输出警告。

## 5. 确认状态
- [x] 需求清晰
- [x] 方案可行
- [x] 风险可控
