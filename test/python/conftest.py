import sys
import os
from pathlib import Path

# Add project root to sys.path to allow imports from web.backend and src
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "web" / "backend"))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

print(f"Added {PROJECT_ROOT} to sys.path")
