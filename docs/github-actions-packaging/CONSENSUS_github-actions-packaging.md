# GitHub Actions 打包工作流 - 共识文档

## 需求描述

实现两个GitHub Actions工作流，分别用于macOS和Windows平台的Everything2MD应用程序自动打包。

## 技术实现方案

### 整体架构

1. 创建两个独立的工作流文件：
   - `build-macos.yml`：用于macOS平台打包
   - `build-windows.yml`：用于Windows平台打包

2. 两个工作流共享相同的基本结构：
   - 使用GitHub Actions标准语法
   - 复用现有构建脚本
   - 上传构建产物作为artifact

### macOS工作流技术细节

- 运行环境：`macos-latest`
- 触发条件：push到main分支或PR到main分支
- 构建步骤：
  1. 代码检出
  2. 设置环境
  3. 设置构建脚本权限
  4. 执行macOS平台构建
  5. 列出构建产物
  6. 上传构建产物

### Windows工作流技术细节

- 运行环境：`windows-latest`
- 触发条件：push到main分支或PR到main分支
- 构建步骤：
  1. 代码检出
  2. 设置环境
  3. 设置构建脚本权限
  4. 执行Windows平台构建
  5. 列出构建产物
  6. 上传构建产物

## 集成方案

### 与现有项目的集成

1. 工作流文件放置在标准位置：`.github/workflows/`
2. 复用现有的`build/build.sh`脚本
3. 使用相同的目录结构和构建产物输出路径
4. 保持与本地构建环境的一致性

## 验收标准

1. macOS工作流能够成功运行并生成构建产物
2. Windows工作流能够成功运行并生成构建产物
3. 构建产物能够通过artifact正确上传和下载
4. 构建产物结构与本地构建一致