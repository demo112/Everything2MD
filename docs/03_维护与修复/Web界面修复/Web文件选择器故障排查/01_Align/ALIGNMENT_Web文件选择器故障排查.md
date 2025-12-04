# 需求对齐：Web文件选择器故障排查

## 1. 问题描述
用户反馈在更新 Docker 镜像和代码后，点击选择文件仍然报错：
`调用系统对话框失败: 调用系统组件失败: no display name and no $DISPLAY environment variable`

## 2. 现象分析
- 这个错误信息来自后端 `/api/system/select-path` 接口的返回值（或旧版前端 JS 的报错提示）。
- 我们之前已经修改了 `web/frontend/script.js`，将 `selectPath` 函数改写为调用新的 Web 模态框逻辑，**不再**调用后端那个旧接口。
- 如果仍然报错，说明**前端执行的仍然是旧代码**。

## 3. 可能原因
1.  **浏览器缓存**：浏览器缓存了旧的 `script.js` 文件。
2.  **Docker 挂载未更新**：虽然重建了镜像，但如果是 bind mount (`- .:/work`)，它应该读取宿主机上的最新文件。如果宿主机文件未保存成功（概率低），或者 Docker 内部有其他缓存机制。
3.  **代码未覆盖**：检查 `index.html` 中的按钮是否还绑定了旧的函数名（虽然我们重写了同名函数 `selectPath`，但如果 HTML 里写的是别的...）。

## 4. 排查计划
1.  检查 `web/frontend/script.js` 源码，确认 `selectPath` 函数已被修改。
2.  检查 `web/frontend/index.html`，确认按钮绑定的函数名。
3.  建议用户强制刷新浏览器。

## 5. 交付物
- 确认代码无误的报告。
- 强制刷新的指引。
