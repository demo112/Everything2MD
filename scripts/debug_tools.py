import os
import shutil
import zipfile
import sys
from pathlib import Path

# Use relative path from script location to ensure correctness
BASE_DIR = Path(__file__).parent.parent
TOOLS_DIR = BASE_DIR / "tools"
LOG_FILE = BASE_DIR / "debug_tools_v2.log"


def log(msg):
    print(msg)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception as e:
        print(f"Failed to write log: {e}")


def run():
    log(f"CWD: {os.getcwd()}")
    log(f"Base Dir: {BASE_DIR}")
    log(f"Tools Dir: {TOOLS_DIR}")

    if not TOOLS_DIR.exists():
        log("Tools dir does not exist")
        return

    # List current
    log("Current contents:")
    for item in TOOLS_DIR.iterdir():
        log(f" - {item.name} ({'dir' if item.is_dir() else 'file'})")

    # Rename Pandoc
    pandoc_folder = TOOLS_DIR / "pandoc-3.1.11.1"
    target_pandoc = TOOLS_DIR / "pandoc"

    if pandoc_folder.exists():
        log(f"Found {pandoc_folder}")
        if target_pandoc.exists():
            log(f"Target {target_pandoc} already exists. Removing it.")
            shutil.rmtree(target_pandoc)

        try:
            pandoc_folder.rename(target_pandoc)
            log(f"Renamed to {target_pandoc}")
        except Exception as e:
            log(f"Error renaming pandoc: {e}")
    else:
        log("pandoc-3.1.11.1 not found")

    # Extract Poppler
    zip_path = TOOLS_DIR / "poppler.zip"
    target_poppler = TOOLS_DIR / "poppler"

    if zip_path.exists():
        log(f"Found {zip_path}")
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(TOOLS_DIR)
            log("Extracted poppler.zip")

            # Find extracted folder
            extracted = None
            for item in TOOLS_DIR.iterdir():
                if item.name.startswith("poppler-") and item.is_dir():
                    extracted = item
                    break

            if extracted:
                log(f"Found extracted folder: {extracted}")
                if target_poppler.exists():
                    shutil.rmtree(target_poppler)
                extracted.rename(target_poppler)
                log(f"Renamed to {target_poppler}")
                os.remove(zip_path)
            else:
                log("Could not find extracted poppler folder")

        except Exception as e:
            log(f"Error extracting poppler: {e}")

    # List final
    log("Final contents:")
    for item in TOOLS_DIR.iterdir():
        log(f" - {item.name} ({'dir' if item.is_dir() else 'file'})")


if __name__ == "__main__":
    run()
