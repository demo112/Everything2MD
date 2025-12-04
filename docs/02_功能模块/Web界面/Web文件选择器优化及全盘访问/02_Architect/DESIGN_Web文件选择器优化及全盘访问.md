# Design: Web文件选择器优化及全盘访问

## 架构图 (Mermaid)

```mermaid
graph TD
    User[用户] -->|点击选择文件| FE[Frontend: Web UI]
    FE -->|API Request: list_files(path)| BE[Backend: FastAPI]
    BE -->|Read Directory| FS[File System]
    FS -->|Mount| Host[Host Drives (C, D, E, F)]
    
    subgraph Docker Container
        BE
        FS
        MountPoint["/mnt/c, /mnt/d..."]
    end
    
    subgraph Frontend Logic
        Modal[File Picker Modal]
        Style[style.css (Dark Theme)]
        Logic[script.js]
    end
    
    Logic -->|Render| Modal
    Style -->|Apply| Modal
```

## 模块设计

### 1. Docker Layer
- **配置**: `docker-compose.yml`
- **变更**: 添加 Volumes
  - `c:/:/mnt/c`
  - `d:/:/mnt/d`
  - `e:/:/mnt/e`
  - `f:/:/mnt/f`

### 2. Backend Layer
- **接口**: `GET /api/fs/list`
- **逻辑**:
  - 参数 `path`: 默认为空字符串。
  - 特殊值 `ROOT`: 返回虚拟根目录列表。
  - 扫描 `/mnt` 目录识别挂载点。
  - 返回数据结构升级：支持 `{"name": "显示名", "path": "真实路径"}` 的对象格式。

### 3. Frontend Layer
- **样式 (CSS)**:
  - `.modal-overlay`: 全屏遮罩，Flex 居中。
  - `.modal`: 弹窗容器，使用 `var(--bg-secondary)`。
  - `.file-item`: 文件列表项，Hover 效果。
- **逻辑 (JS)**:
  - `fetchFileList(path)`: 处理 API 请求。
  - `renderFileList(data)`: 渲染列表，处理 `ROOT` 视图。
  - `navigateUp()`: 基于 `parent_path` 导航。
