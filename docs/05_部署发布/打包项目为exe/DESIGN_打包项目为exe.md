# DESIGN: 打包项目为exe (v2 - 2025-12-15)

## 1. 架构设计
基于 `src/gui/main.py` 作为入口点，使用 PyInstaller 进行单文件或目录打包。

### 1.1 组件依赖图
```mermaid
graph TD
    A[Everything2MD.exe] --> B[Python Runtime]
    A --> C[Source Code (src/)]
    A --> D[Resources (src/filters/clean.lua)]
    A --> E[Config (User Home/.config/everything2md/config.json)]
    A -.-> F[External Tools (LibreOffice, Pandoc)]
```

### 1.2 关键路径处理
*   **sys._MEIPASS**: 运行时解压路径，用于访问 `src/filters/clean.lua`。
*   **Path.home()**: 用户配置路径，不受打包影响，确保配置持久化。

### 1.3 打包配置 (Everything2MD.spec)
*   **Entry Point**: `src\gui\main.py`
*   **Hidden Imports**: 
    *   `pptx2md` (可能需要隐式导入，但 PyInstaller 通常能识别)
    *   `PIL` (Image processing dependencies)
*   **Datas**:
    *   `src/filters/clean.lua` -> `src/filters/clean.lua`
*   **Excludes**: `numpy`, `scipy` (减小体积)

## 2. 验证策略
1.  **启动测试**: 双击运行，检查 GUI 是否显示。
2.  **配置测试**: 检查是否能读取/保存配置（API Key）。
3.  **功能测试**: 拖入 DOCX 文件转换，拖入上传 RAGFlow。
4.  **环境隔离**: 确保不依赖当前 Python 虚拟环境（在纯净 cmd 中运行）。
