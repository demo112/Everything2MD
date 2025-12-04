# ALIGNMENT_Docker构建修复

## 1. 原始需求与边界确认
**需求描述**：
用户在构建 Docker 镜像时遇到 `ERROR [internal] load metadata for docker.io/library/ubuntu:22.04` 错误，提示连接超时。
这表明 Docker 无法从默认的 Docker Hub 拉取基础镜像。

**核心目标**：
1.  修复 Dockerfile，使其能够在国内网络环境下成功构建。
2.  遵循用户规则中的 "配置国内镜像加速" 原则。

**边界**：
- **包含**：
  - 修改 Dockerfile 使用国内可访问的基础镜像源。
  - 验证构建过程。
- **不包含**：
  - 修改用户的 Docker Daemon 配置（因为这涉及宿主机系统级配置，脚本权限可能受限，且不够便携）。
  - *注意*：虽然用户规则提到"配置国内镜像加速"通常指配置 Daemon，但作为代码仓库，最便携的方式是在 Dockerfile 中指定或者提供配置脚本。为了立即解决构建问题，优先修改 Dockerfile 或提供构建参数。

## 2. 项目现状分析
**现有 Dockerfile**：
```dockerfile
FROM ubuntu:22.04
# ... 后续已配置了 apt 和 pip 的国内源 ...
```
**问题点**：
`FROM ubuntu:22.04` 默认使用 `docker.io`，在国内访问不稳定。

## 3. 歧义澄清 (Q&A)
- **Q**: 是否应该修改 Docker Daemon `daemon.json`？
  - **A**: 这是最佳实践，但作为项目代码，强制要求用户修改系统配置门槛较高。
  - **决策**: 
    1. 优先尝试在 Dockerfile 中使用国内镜像代理（如 `m.daocloud.io` 或阿里云公共镜像）。
    2. 如果修改 Dockerfile 不合适（保持通用性），可以提供一个 `build.ps1` 脚本，在构建时通过 `--build-arg` 传入镜像前缀，或者直接修改 Dockerfile。
    3. 考虑到用户直接运行了 build 命令，直接修改 Dockerfile 是最快反馈。

- **Q**: 选用哪个镜像源？
  - **A**: 
    - 阿里云容器镜像服务（需要注册，有时不稳定）。
    - DaoCloud (`m.daocloud.io`)。
    - 南京大学/中科大等（通常用于 apt/pip，不直接提供 Docker Registry 代理）。
    - **策略**: 暂时使用 `swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/ubuntu:22.04` (华为云) 或 `m.daocloud.io/docker.io/ubuntu:22.04`。或者直接使用 `registry.cn-hangzhou.aliyuncs.com/google_containers/ubuntu` (可能没有)。
    - 最稳妥的方式是：建议用户配置 daemon，或者在 Dockerfile 中使用ARG。

**方案调整**：
为了不硬编码特定的 Mirror（可能随时间失效），我们可以使用 `ARG`。
```dockerfile
ARG UBUNTU_MIRROR=ubuntu:22.04
FROM ${UBUNTU_MIRROR}
```
然后在构建脚本中传入。但用户是直接运行 docker build。
为了"开箱即用"，我将直接替换为一个目前高可用的国内 Mirror，并添加注释说明。

**备选 Mirror**:
- `dockerproxy.com` (已停止服务)
- `docker.m.daocloud.io` (DaoCloud) -> `m.daocloud.io/docker.io/ubuntu:22.04`
- 华为云: `swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/ubuntu:22.04`

我将尝试使用 **DaoCloud** 或 **华为云** 的代理格式。
同时，我会检查是否还有其他网络依赖。
