from pathlib import Path


def list_files(startpath):
    output = []
    startpath = Path(startpath)
    if not startpath.exists():
        return ["Path does not exist"]

    for path in startpath.rglob("*"):
        output.append(str(path.relative_to(startpath.parent)))
    return output


tools_dir = Path(__file__).parent.parent / "tools"
layout = list_files(tools_dir)

with open(Path(__file__).parent / "tools_layout.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(layout))
