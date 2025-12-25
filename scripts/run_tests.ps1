param (
    [string]$Target = "all"
)

# 确保在项目根目录运行
$ScriptDir = $PSScriptRoot
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

$TestDir = "test"
$UnitTestDir = "$TestDir/unit"
$IntegrationTestDir = "$TestDir/integration"
$PythonTestDirs = @("$TestDir/unit", "$TestDir/integration")
$Bats = "$TestDir/bats/bin/bats"
$VenvDir = ".venv"
# Use Join-Path for robust path handling
$Pytest = Join-Path $VenvDir "Scripts\pytest.exe"

# Check if .venv exists
if (-not (Test-Path $VenvDir)) {
    Write-Host "Error: Virtual environment '$VenvDir' not found." -ForegroundColor Red
    Write-Host "Please run 'py -3 -m venv $VenvDir' and install requirements." -ForegroundColor Yellow
    exit 1
}

function Run-Bats {
    param ($Dirs)
    Write-Host "Running Bats tests in: $Dirs" -ForegroundColor Cyan
    
    $GitBashPath = "C:\Program Files\Git\bin\bash.exe"
    if (-not (Test-Path $GitBashPath)) {
        $GitBashPath = "C:\Program Files (x86)\Git\bin\bash.exe"
    }

    if (Test-Path $GitBashPath) {
         & "$GitBashPath" $Bats $Dirs
    } else {
        # Fallback to system bash (might be WSL or other)
        $Bash = Get-Command "bash" -ErrorAction SilentlyContinue
        if ($Bash) {
            Write-Host "Git Bash not found in standard locations. Using system bash: $($Bash.Source)" -ForegroundColor Yellow
            & bash $Bats $Dirs
        } else {
            Write-Host "Error: 'bash' not found in PATH or standard locations. Bats tests require Git Bash or WSL." -ForegroundColor Red
            exit 1
        }
    }
}

function Run-Python {
    Write-Host "Running Python tests..." -ForegroundColor Cyan
    # Check if pytest exists
    if (-not (Test-Path $Pytest)) {
         Write-Host "Error: pytest not found in $Pytest. Please install requirements." -ForegroundColor Red
         exit 1
    }
    & $Pytest $PythonTestDirs
}

function Clean {
    Write-Host "Cleaning up..." -ForegroundColor Cyan
    if (Test-Path "output") { Remove-Item "output" -Recurse -Force }
}

switch ($Target) {
    "test-bats" { Run-Bats "$UnitTestDir $IntegrationTestDir" }
    "test-python" { Run-Python }
    "unit-test" { Run-Bats $UnitTestDir }
    "integration-test" { Run-Bats $IntegrationTestDir }
    "clean" { Clean }
    "test-ui" { 
        Write-Host "Running UI tests..." -ForegroundColor Cyan
        & $Pytest test/ui
    }
    "all" { 
        Run-Python
        if ($IsWindows) {
            Write-Host "Running UI tests..." -ForegroundColor Cyan
            & $Pytest test/ui
        }
        Run-Bats "$UnitTestDir $IntegrationTestDir"
    }
    Default { 
        Write-Host "Unknown target: $Target" -ForegroundColor Red
        Write-Host "Available targets: test-bats, test-python, unit-test, integration-test, clean, all"
    }
}
