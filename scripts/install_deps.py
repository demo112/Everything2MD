import os
import sys
import shutil
import urllib.request
import zipfile
import tarfile
from pathlib import Path

# Configuration
TOOLS_DIR = Path(__file__).parent.parent / "tools"
PANDOC_URL = "https://github.com/jgm/pandoc/releases/download/3.1.11.1/pandoc-3.1.11.1-windows-x86_64.zip"
POPPLER_URL = "https://github.com/oschwartz10612/poppler-windows/releases/download/v23.11.0-0/Release-23.11.0-0.zip"

def download_file(url, dest_path):
    print(f"Downloading {url}...")
    with urllib.request.urlopen(url) as response, open(dest_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    print("Download complete.")

def extract_zip(zip_path, extract_to):
    print(f"Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Extraction complete.")

def setup_pandoc():
    pandoc_dir = TOOLS_DIR / "pandoc"
    # Force reinstall to be safe
    if pandoc_dir.exists():
        shutil.rmtree(pandoc_dir)

    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = TOOLS_DIR / "pandoc.zip"
    
    try:
        download_file(PANDOC_URL, zip_path)
        extract_zip(zip_path, TOOLS_DIR)
        
        # Move inner folder content to tools/pandoc
        extracted_folders = list(TOOLS_DIR.glob("pandoc-*-windows-x86_64"))
        if not extracted_folders:
            print("Error: Could not find extracted Pandoc folder")
            return

        extracted_folder = extracted_folders[0]
        extracted_folder.rename(pandoc_dir)
        print(f"Pandoc installed to {pandoc_dir}")
        
    except Exception as e:
        print(f"Error setting up Pandoc: {e}")
    finally:
        if zip_path.exists():
            os.remove(zip_path)

def setup_poppler():
    poppler_dir = TOOLS_DIR / "poppler"
    # Force reinstall
    if poppler_dir.exists():
        shutil.rmtree(poppler_dir)

    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = TOOLS_DIR / "poppler.zip"
    
    try:
        download_file(POPPLER_URL, zip_path)
        extract_zip(zip_path, TOOLS_DIR)
        
        extracted_folders = list(TOOLS_DIR.glob("poppler-*-windows*"))
        # Filter out the zip file if glob catches it (unlikely with just *)
        extracted_folders = [f for f in extracted_folders if f.is_dir()]
        
        if not extracted_folders:
            # Fallback for some zips that extract differently
            # Try to find a folder with 'Library' or 'bin' inside
            for item in TOOLS_DIR.iterdir():
                if item.is_dir() and (item / "Library").exists():
                    extracted_folders = [item]
                    break
        
        if not extracted_folders:
             print("Could not find extracted Poppler folder.")
             return

        extracted_folder = extracted_folders[0]
        extracted_folder.rename(poppler_dir)
        print(f"Poppler installed to {poppler_dir}")
            
    except Exception as e:
        print(f"Error setting up Poppler: {e}")
    finally:
        if zip_path.exists():
            os.remove(zip_path)

if __name__ == "__main__":
    print("Setting up dependencies...")
    setup_pandoc()
    setup_poppler()
    print("Setup complete.")
