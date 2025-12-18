import os

dirs = [
    "docs/FullProjectAutoTest/01_Align",
    "docs/FullProjectAutoTest/02_Architect",
    "docs/FullProjectAutoTest/03_Atomize",
    "docs/FullProjectAutoTest/04_Approve",
    "docs/FullProjectAutoTest/05_Automate",
    "docs/FullProjectAutoTest/06_Assess",
]

for d in dirs:
    os.makedirs(d, exist_ok=True)
    print(f"Created {d}")
