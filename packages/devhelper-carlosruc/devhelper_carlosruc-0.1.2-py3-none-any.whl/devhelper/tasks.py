# devhelper/tasks.py
from pathlib import Path
from .solution_parser import parse_solution_file

def create_file(filename: str):
    Path(filename).touch()

def list_files(path: str):
    return [p.name for p in Path(path).iterdir() if p.is_file()]

def generate_tree(path: str, prefix: str = "") -> str:
    """
    Generate a directory tree starting from path
    """

    path = Path(path)
    if not path.exists():
        return f"Path not found: {path}"
    
    # check for .sln
    sln_files = list(path.glob("*.sln"))
    if sln_files:
        return generate_solution_tree(sln_files[0])

    lines = []

    def walk(directory: Path, prefix: str = ""):
        entries = sorted(directory.iterdir(), key=lambda e: (e.is_file(), e.name.lower()))
        for i, entry in enumerate(entries):
            connector = "└──" if i == len(entries) - 1 else "├──"
            lines.append(f"{prefix}{connector}{entry.name}")
            if entry.is_dir():
                extension = "    " if i == len(entries) - 1 else "│   "
                walk(entry, prefix + extension)
                
    lines.append(path.name)
    walk(path, prefix)
    return "\n".join(lines)

def generate_solution_tree(sln_path: Path) -> str:
    """
    Generate a solution-folder-aware tree from .sln file, including Solution Items,
    and ignore folders like bin/obj if needed. Returns a string.
    """
    solution_dict = parse_solution_file(sln_path)
    lines = []

    def build_node(node, indent=0):
        prefix = "    " * indent
        for key, value in node.items():

            lines.append(f"{prefix}📂 {key}")
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        lines.append(f"{prefix}    📑 {item}")
                    elif isinstance(item, dict):
                        build_node(item, indent + 1)
                    else:
                        lines.append(f"{prefix}    ❓ Unknown item: {item}")
            else:
                lines.append(f"{prefix}    ❓ Unknown value: {value}")

    lines.append(f"📦 {sln_path.name}")
    build_node(solution_dict)
    return "\n".join(lines)