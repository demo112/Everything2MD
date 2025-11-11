# 打包任务共识文档

## 明确的需求描述和验收标准

### 需求描述
将现有的Everything2MD项目打包为可在Windows和macOS上直接运行的应用程序，无需用户手动安装依赖。

### 验收标准
1. Windows平台：
   - 生成一个独立的.exe文件
   - 用户双击即可运行，无需安装额外软件
   - 支持命令行参数传递
   - 在Windows 10/11上正常运行

2. macOS平台：
   - 生成一个.app应用程序包
   - 用户可以从Finder中直接运行
   - 支持命令行参数传递
   - 在macOS 10.15+上正常运行

3. 功能完整性：
   - 保持所有现有功能
   - 支持所有原有文件格式转换
   - 支持批量处理模式
   - 支持配置文件和日志功能

## 技术实现方案

### Windows平台打包方案

#### 方案选择：使用MSYS2 + Bash环境打包
由于Everything2MD是一个Bash脚本项目，直接编译为.exe较为困难。我们将采用以下方案：

1. 使用MSYS2环境打包：
   - MSYS2提供了类Unix的环境，可以在Windows上运行Bash脚本
   - 将项目所需的所有依赖（LibreOffice, Pandoc, pptx2md）打包进发行版
   - 创建一个包装器exe文件，启动内部的Bash环境并运行主脚本

2. 打包结构：
   ```
   Everything2MD-Windows/
   ├── bin/
   │   ├── everything2md.exe (包装器)
   │   └── msys2-runtime.dll (MSYS2运行时)
   ├── lib/
   │   └── (MSYS2库文件)
   ├── usr/
   │   ├── bin/
   │   │   ├── bash.exe
   │   │   ├── libreoffice.exe
   │   │   ├── pandoc.exe
   │   │   └── (其他工具)
   │   └── share/
   ├── src/
   │   ├── main.sh
   │   └── modules/
   └── README.txt
   ```

### macOS平台打包方案

#### 方案选择：创建标准的.app应用程序包
对于macOS，我们可以创建一个标准的应用程序包结构：

1. 应用程序包结构：
   ```
   Everything2MD.app/
   ├── Contents/
   │   ├── Info.plist
   │   ├── MacOS/
   │   │   ├── everything2md (可执行脚本)
   │   │   └── launcher (启动器)
   │   ├── Resources/
   │   │   └── (图标等资源文件)
   │   └── Frameworks/
   │       └── (依赖库)
   └── src/
       ├── main.sh
       └── modules/
   ```

2. 实现要点：
   - Info.plist文件定义应用元数据
   - launcher作为C编写的启动器，负责设置环境并调用Bash脚本
   - 将依赖工具（LibreOffice, Pandoc, pptx2md）打包进Frameworks目录
   - 通过AppleScript或Automator创建拖拽安装包

## 技术约束和集成方案

### 技术约束
1. 保持现有Bash脚本代码不变
2. 所有依赖必须打包进发行版
3. Windows版本需要处理路径分隔符差异
4. macOS版本需要处理权限和代码签名问题
5. 两个平台都需要处理相对路径和绝对路径问题

### 集成方案
1. 创建统一的构建脚本，自动为两个平台生成发行版
2. 使用环境变量区分平台特定的代码路径
3. 在打包过程中自动处理依赖项
4. 提供安装脚本简化依赖安装过程

## 任务边界限制

### 包含内容
1. Windows平台.exe打包
2. macOS平台.app打包
3. 依赖项打包和配置
4. 启动器和包装器开发
5. 安装和卸载脚本

### 不包含内容
1. Linux平台支持
2. 应用商店发布
3. 自动更新功能
4. 图形用户界面
5. 网络功能

## 关键假设确认

1. 用户在目标平台上不需要预先安装任何依赖
2. 打包后的应用程序具有足够的权限运行所有功能
3. 项目的所有现有功能在打包后保持正常工作
4. 两个平台的打包版本都能正确处理文件路径和编码