# LibreOffice启动超时修复 - 任务分解

## 任务清单

- [x] 代码修复
  - [x] 修改 `src/core/converters/ppt.py` 中的 `_run_subprocess`
  - [x] 修改 `src/core/converters/office.py` 中的 `_run_subprocess`
- [x] 测试完善
  - [x] 创建 `test/unit/core/converters/test_subprocess_helper.py`
  - [x] 编写覆盖 `context` + `timeout` 场景的测试用例
  - [x] 执行测试并确认通过
- [x] 验证交付
  - [x] 重新打包应用
  - [x] 验证打包后的应用启动无误（用户侧）
