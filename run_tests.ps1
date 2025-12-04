param (
    [string]$Target = "all"
)

$TestDir = "test"
$UnitTestDir = "$TestDir/unit"
$IntegrationTestDir = "$TestDir/integration"
$PythonTestDir = "$TestDir/python"
$Bats = "$TestDir/bats/bin/bats"
$Pytest = "venv/Scripts/pytest"

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "Error: Virtual environment 'venv' not found. Please run 'py -3 -m venv venv' and install requirements." -ForegroundColor Red
    exit 1
}

function Run-Bats {
    param ($Dirs)
    Write-Host "Running Bats tests in: $Dirs" -ForegroundColor Cyan
    # Bats is a bash script, so we need to run it via bash if available, or rely on the user having a way to run it.
    # On Windows, 'bats' file in bin is a shell script. 
    # Usually requires Git Bash or WSL. 
    # However, since the user has 'bats' in the repo, let's try to run it via 'bash' if possible, 
    # or check if there is a windows batch wrapper.
    # Looking at the file list, there is 'test/bats/bin/bats' which is likely the shell script.
    
    # Check for git bash
    $Bash = Get-Command "bash" -ErrorAction SilentlyContinue
    if ($Bash) {
        & bash $Bats $Dirs
    } else {
        Write-Host "Error: 'bash' not found in PATH. Bats tests require Git Bash or WSL." -ForegroundColor Red
        # Try to find git bash in standard locations
        $GitBashPath = "C:\Program Files\Git\bin\bash.exe"
        if (Test-Path $GitBashPath) {
             & "$GitBashPath" $Bats $Dirs
        } else {
            exit 1
        }
    }
}

function Run-Python {
    Write-Host "Running Python tests..." -ForegroundColor Cyan
    & $Pytest $PythonTestDir
}

function Clean {
    Write-Host "Cleaning up..." -ForegroundColor Cyan
    if (Test-Path "output") { Remove-Item "output" -Recurse -Force }
    Get-ChildItem -Filter "*.md" | Remove-Item -Force
}

switch ($Target) {
    "test-bats" { Run-Bats "$UnitTestDir $IntegrationTestDir" }
    "test-python" { Run-Python }
    "unit-test" { Run-Bats $UnitTestDir }
    "integration-test" { Run-Bats $IntegrationTestDir }
    "clean" { Clean }
    "all" { 
        Run-Python
        Run-Bats "$UnitTestDir $IntegrationTestDir"
    }
    Default { 
        Write-Host "Unknown target: $Target" -ForegroundColor Red
        Write-Host "Available targets: test-bats, test-python, unit-test, integration-test, clean, all"
    }
}
