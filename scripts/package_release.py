import os
import sys
import subprocess
import datetime
import shutil
import time

def log(msg):
    print(f"[PACKAGER] {msg}")

def install_py7zr():
    try:
        import py7zr
        log("py7zr already installed.")
    except ImportError:
        log("py7zr not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "py7zr"])
        log("py7zr installed successfully.")

def build_exe():
    log("Starting PyInstaller build...")
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build", ignore_errors=True)
    if os.path.exists("dist"):
        shutil.rmtree("dist", ignore_errors=True)
    
    cmd = [
        "pyinstaller",
        "Everything2MD.spec",
        "--clean",
        "--noconfirm"
    ]
    subprocess.check_call(cmd)
    
    exe_path = os.path.join("dist", "Everything2MD.exe")
    if not os.path.exists(exe_path):
        raise FileNotFoundError(f"Build failed: {exe_path} not found.")
    
    log(f"EXE built successfully at {exe_path}")
    return exe_path

def create_7z_package(exe_path):
    import py7zr  # Dynamic import after installation
    
    release_dir = "release"
    if not os.path.exists(release_dir):
        os.makedirs(release_dir)
        
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    archive_name = f"Everything2MD_{date_str}.7z"
    archive_path = os.path.join(release_dir, archive_name)
    
    log(f"Creating 7z archive: {archive_path}")
    
    readme_path = "README.md"
    
    with py7zr.SevenZipFile(archive_path, 'w') as archive:
        archive.write(exe_path, arcname="Everything2MD.exe")
        if os.path.exists(readme_path):
            archive.write(readme_path, arcname="README.md")
        else:
            log("Warning: README.md not found, skipping.")
            
    log(f"Package created successfully: {archive_path}")
    return archive_path

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root_dir)
    log(f"Working directory: {root_dir}")
    
    try:
        install_py7zr()
        exe_path = build_exe()
        archive_path = create_7z_package(exe_path)
        log("Done.")
    except Exception as e:
        log(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
