# Docker服务化 - 架构设计

## 背景
用户需要将Everything2MD运行为Docker服务，以便于部署和环境隔离。

## 设计目标
1. 提供一键启动的Docker环境。
2. 满足国内网络环境要求（镜像加速）。
3. 满足项目规范（venv, 中文支持）。

## 方案设计
### 容器架构
- Base Image: Ubuntu 22.04 (使用国内镜像)
- Python环境: venv at `/opt/venv`
- 依赖管理: apt + pip (国内源)
- 挂载:
  - `/work`: 映射宿主机代码根目录
  - `/work/input`: 输入文件
  - `/work/output`: 输出文件

### 服务编排
使用 `docker-compose` 管理容器，定义 `everything2md` 服务。

## 关键决策
- 使用 `/opt/venv` 避免宿主机 venv 冲突。
- 使用 `m.daocloud.io` 加速 Ubuntu 镜像拉取。
