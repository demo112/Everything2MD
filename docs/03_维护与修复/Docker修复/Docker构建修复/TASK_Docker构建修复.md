# TASK_Docker构建修复

## 1. 原子任务列表

### Task 1: 修改 Dockerfile
- **输入**: `Dockerfile`
- **输出**: 修改后的 `Dockerfile`
- **内容**: 
  - 添加 `ARG UBUNTU_REGISTRY=m.daocloud.io/docker.io/library`
  - 修改 `FROM` 指令。

### Task 2: 验证构建
- **输入**: 修改后的 `Dockerfile`
- **操作**: 运行 `docker build --pull --rm -f 'Dockerfile' -t 'everything2md:0.1' '.'`
- **输出**: 成功构建的镜像。

## 2. 依赖关系
Task 1 -> Task 2
