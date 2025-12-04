# DESIGN_Docker构建修复

## 1. 架构变更
无架构变更，仅涉及 Dockerfile 的基础镜像源替换。

## 2. 详细设计
**Dockerfile**:
```dockerfile
# 增加 ARG 指令，放在 FROM 之前
ARG UBUNTU_REGISTRY=m.daocloud.io/docker.io/library

FROM ${UBUNTU_REGISTRY}/ubuntu:22.04

# ... (其余保持不变)
```

**兼容性说明**:
- 如果用户在国外，可以通过 `--build-arg UBUNTU_REGISTRY=library` 或 `docker.io/library` 来恢复默认。
- 默认情况下，使用 `m.daocloud.io` 加速。

**风险**:
- 镜像代理服务可能随时不可用。
- 备选方案：如果 DaoCloud 失效，可以使用华为云 `swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io`。

## 3. 验证计划
- 运行 `docker build` 命令。
- 观察是否能成功拉取 Metadata。
