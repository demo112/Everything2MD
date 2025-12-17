# TODO: 大文件自动切分策略

## 待办事项
1.  **GUI 支持**: 在 `src/gui/fixed_main_v2.py` 和 `src/gui/main.py` 的设置界面中添加 "最大输出文件大小 (MB)" 的输入框，绑定到 `max_output_file_size_mb` 配置项。
2.  **高级切分**: 未来可考虑支持按 Markdown 标题（Chapter）切分，而不仅仅是按大小切分，以提供更好的语义分割。

## 操作指引
用户目前需手动修改 `~/.config/everything2md/config.json` 中的 `max_output_file_size_mb` 来调整阈值（默认 50）。
