# 准备离线资源脚本
# 该脚本将启动一个临时 Docker 容器，下载构建所需的所有依赖包到本地 docker_resources 目录

$ErrorActionPreference = "Stop"

$ProjectRoot = Get-Location
$ResourceDir = Join-Path $ProjectRoot "docker_resources"
$AptDir = Join-Path $ResourceDir "apt"
$PipDir = Join-Path $ResourceDir "pip"
$ScriptFile = Join-Path $ResourceDir "download.sh"

# 1. 创建目录
Write-Host "Creating directories..."
if (-not (Test-Path $AptDir)) { New-Item -ItemType Directory -Force -Path $AptDir | Out-Null }
if (-not (Test-Path $PipDir)) { New-Item -ItemType Directory -Force -Path $PipDir | Out-Null }

# 2. 转换换行符 (防止 Windows 编辑导致的 CRLF 问题)
Write-Host "Fixing line endings in download.sh..."
(Get-Content $ScriptFile) -join "`n" | Set-Content $ScriptFile -NoNewline -Encoding UTF8

Write-Host "Starting downloader container..."

# 3. 运行容器
# 使用与目标镜像一致的 Ubuntu 22.04
# 注意：挂载 download.sh 到容器内
docker run --rm `
    -v "${ResourceDir}:/output" `
    -v "${ProjectRoot}/requirements.txt:/input/requirements.txt" `
    -v "${ScriptFile}:/download.sh" `
    m.daocloud.io/docker.io/library/ubuntu:22.04 `
    bash /download.sh

if ($LASTEXITCODE -eq 0) {
    Write-Host "Resources downloaded successfully to $ResourceDir"
} else {
    Write-Host "Download failed!" -ForegroundColor Red
}
