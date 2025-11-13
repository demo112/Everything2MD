#!/bin/bash

# macOS平台打包模块
# 负责将Everything2MD打包为macOS应用程序

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$(dirname "$SCRIPT_DIR")"
TEMP_DIR="$BUILD_DIR/temp"
DIST_DIR="$BUILD_DIR/dist"
PROJECT_ROOT="$(dirname "$BUILD_DIR")"

echo "macOS打包模块初始化..."

# 配置变量
APP_NAME="Everything2MD"
APP_BUNDLE_DIR="$TEMP_DIR/$APP_NAME.app"
INSTALLER_DIR="$DIST_DIR/macos"

# 创建App Bundle结构
create_app_bundle() {
    echo "创建App Bundle结构..."
    
    # 创建App Bundle目录结构
    mkdir -p "$APP_BUNDLE_DIR/Contents/MacOS"
    mkdir -p "$APP_BUNDLE_DIR/Contents/Resources"
    mkdir -p "$APP_BUNDLE_DIR/Contents/Frameworks"
    
    # 创建Info.plist
    cat > "$APP_BUNDLE_DIR/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>English</string>
    <key>CFBundleExecutable</key>
    <string>everything2md</string>
    <key>CFBundleGetInfoString</key>
    <string>Everything2MD 1.0.0</string>
    <key>CFBundleIconFile</key>
    <string>app.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.everything2md.everything2md</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Everything2MD</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>NSAppleScriptEnabled</key>
    <string>YES</string>
    <key>NSMainNibFile</key>
    <string>MainMenu</string>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>
EOF
    
    echo "App Bundle结构创建完成"
}

# 打包项目依赖项
package_dependencies() {
    echo "打包项目依赖项..."
    
    # 创建依赖目录
    mkdir -p "$INSTALLER_DIR/deps"
    mkdir -p "$APP_BUNDLE_DIR/Contents/Resources/deps"
    
    # 从 dist/macos/deps 复制到 .app Bundle 内
    if [ -f "$DIST_DIR/macos/deps/pandoc" ]; then
        echo "复制Pandoc到 .app..."
        cp "$DIST_DIR/macos/deps/pandoc" "$APP_BUNDLE_DIR/Contents/Resources/deps/pandoc"
        chmod +x "$APP_BUNDLE_DIR/Contents/Resources/deps/pandoc"
    else
        echo "警告: 未在 dist/macos/deps 中找到 Pandoc"
    fi
    
    # LibreOffice 保留在发行目录供用户手动安装
    
    echo "依赖项打包完成"
}

# 编译macOS启动器
compile_launcher() {
    echo "编译macOS启动器..."
    
    # 创建启动器目录
    mkdir -p "$INSTALLER_DIR/launcher"
    
    # 复制启动器脚本到App Bundle
    cp "$SCRIPT_DIR/macos_launcher.sh" "$APP_BUNDLE_DIR/Contents/MacOS/everything2md"
    
    # 复制启动器脚本到launcher目录
    cp "$SCRIPT_DIR/macos_launcher.sh" "$INSTALLER_DIR/launcher/"
    
    # 添加执行权限
    chmod +x "$APP_BUNDLE_DIR/Contents/MacOS/everything2md"
    chmod +x "$INSTALLER_DIR/launcher/macos_launcher.sh"
    
    echo "macOS启动器创建完成"
}

# 整合所有组件
integrate_components() {
    echo "整合所有组件..."
    
    # 创建Resources目录
    mkdir -p "$APP_BUNDLE_DIR/Contents/Resources/src"
    
    # 复制源代码
    echo "复制源代码..."
    cp -r "$PROJECT_ROOT/src" "$APP_BUNDLE_DIR/Contents/Resources/"
    
    # 添加执行权限
    echo "设置执行权限..."
    find "$APP_BUNDLE_DIR/Contents/Resources/src" -name "*.sh" -exec chmod +x {} \;
    
    # 复制README
    echo "复制文档..."
    cp "$PROJECT_ROOT/README.md" "$APP_BUNDLE_DIR/Contents/Resources/"
    
    echo "组件整合完成"
}

# 生成最终发行版
generate_installer() {
    echo "生成最终发行版..."
    
    # 设置版本信息
    VERSION="1.0.0"
    BUILD_DATE=$(date +%Y%m%d)
    
    # 创建发行版目录
    FINAL_DIR="$DIST_DIR/Everything2MD-macOS-$VERSION-$BUILD_DATE"
    mkdir -p "$FINAL_DIR"
    
    # 复制App Bundle到发行版目录
    cp -r "$APP_BUNDLE_DIR" "$FINAL_DIR/"
    
    # 同步依赖目录到最终发行版
    if [ -d "$DIST_DIR/macos/deps" ]; then
        cp -r "$DIST_DIR/macos/deps" "$FINAL_DIR/deps"
    fi
    
    # 创建简单的安装说明
    cat > "$FINAL_DIR/安装说明.txt" << EOF
Everything2MD for macOS 安装说明

1. 将 Everything2MD.app 拖拽到 Applications 文件夹即可完成安装
2. 首次运行时可能需要在系统偏好设置中允许打开此应用
3. 在终端中运行以下命令使用:
   /Applications/Everything2MD.app/Contents/MacOS/everything2md [选项]
   
例如:
   /Applications/Everything2MD.app/Contents/MacOS/everything2md -i input.docx -o output.md
EOF
    
    echo "macOS发行版已生成: $FINAL_DIR"
}

# 主函数
main() {
    echo "开始macOS平台打包..."
    
    # 创建App Bundle结构
    create_app_bundle
    
    # 运行依赖打包脚本，准备 dist/macos/deps
    "$SCRIPT_DIR/macos_deps_packager.sh"

    # 打包依赖项
    package_dependencies
    
    # 编译启动器
    compile_launcher
    
    # 整合组件
    integrate_components
    
    # 生成发行版
    generate_installer
    
    echo "macOS平台打包完成"
}

# 执行主函数
main "$@"