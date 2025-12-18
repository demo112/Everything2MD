import os
import shutil
import zipfile
from pathlib import Path

TOOLS_DIR = Path("tools").absolute()


def fix_pandoc():
    print("Checking Pandoc...")
    # Check for likely extracted folders
    for item in TOOLS_DIR.glob("pandoc-*"):
        if item.is_dir() and (item / "pandoc.exe").exists():
            target = TOOLS_DIR / "pandoc"
            if target.exists():
                print(f"Target {target} already exists. Skipping rename of {item}")
            else:
                print(f"Renaming {item} to {target}")
                item.rename(target)
            return

    # Check if we already have tools/pandoc
    if (TOOLS_DIR / "pandoc" / "pandoc.exe").exists():
        print("Pandoc looks correctly installed.")
    else:
        print("Pandoc not found in expected structure.")


def fix_poppler():
    print("Checking Poppler...")
    zip_path = TOOLS_DIR / "poppler.zip"
    target = TOOLS_DIR / "poppler"

    if (target / "Library" / "bin" / "pdftotext.exe").exists() or (
        target / "bin" / "pdftotext.exe"
    ).exists():
        print("Poppler looks correctly installed.")
        if zip_path.exists():
            os.remove(zip_path)
        return

    if zip_path.exists():
        print(f"Found {zip_path}, attempting extraction...")
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(TOOLS_DIR)
            print("Extraction complete.")

            # Find the extracted folder
            # Poppler releases often extract to 'poppler-xx.xx.xx' or 'Release-xx.xx.xx'
            # Let's look for a folder containing 'bin' or 'Library'
            found = False
            for item in TOOLS_DIR.iterdir():
                if item.is_dir() and item.name != "pandoc" and item.name != "poppler":
                    # Check if this is the poppler folder
                    if (
                        (item / "Library").exists()
                        or (item / "bin").exists()
                        or "poppler" in item.name
                    ):
                        print(f"Found extracted folder: {item}")
                        if target.exists():
                            shutil.rmtree(target)
                        item.rename(target)
                        found = True
                        break

            if found:
                print("Poppler setup fixed.")
                os.remove(zip_path)
            else:
                print("Could not identify Poppler folder after extraction.")

        except zipfile.BadZipFile:
            print("Poppler zip file is corrupt. Deleting it.")
            os.remove(zip_path)
        except Exception as e:
            print(f"Error fixing Poppler: {e}")


if __name__ == "__main__":
    if not TOOLS_DIR.exists():
        TOOLS_DIR.mkdir()
    fix_pandoc()
    fix_poppler()
