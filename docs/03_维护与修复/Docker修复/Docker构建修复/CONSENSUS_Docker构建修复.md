# CONSENSUS_Docker构建修复

## 1. 需求精确描述
修复 `Dockerfile` 中的基础镜像拉取超时问题。

**验收标准**：
1.  Docker 镜像能够成功构建（`docker build` 成功）。
2.  构建过程不出现超时错误。

## 2. 技术实现方案
修改 `Dockerfile`：
1.  引入 `ARG REGISTRY_PREFIX` 参数，允许构建时动态指定前缀。
2.  设置默认值指向国内可用的镜像加速地址（如 `m.daocloud.io/docker.io` 或直接使用华为云镜像）。
3.  更新 `FROM` 指令。

**具体修改**：
```dockerfile
# 使用 ARG 允许覆盖，默认使用国内加速
ARG IMAGE_PREFIX=m.daocloud.io/docker.io/library
FROM ${IMAGE_PREFIX}/ubuntu:22.04
```
或者，考虑到 `ARG` 在 `FROM` 前的支持情况（Docker 17.05+ 支持），这通常是兼容的。

如果 `m.daocloud.io` 不可用，将尝试其他源。
鉴于当前网络环境，**推荐直接修改为硬编码的稳定源**，并在注释中说明。
目前 `swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/ubuntu:22.04` 在国内较为稳定。

**最终决定**：
为了保证用户体验，采用 "ARG + 默认国内源" 的方式。
默认源使用：`registry.cn-hangzhou.aliyuncs.com/google_containers` (通常没有 ubuntu)。
改为使用 `m.daocloud.io/docker.io/library/ubuntu:22.04`。

## 3. 任务边界
仅修改 `Dockerfile`。
