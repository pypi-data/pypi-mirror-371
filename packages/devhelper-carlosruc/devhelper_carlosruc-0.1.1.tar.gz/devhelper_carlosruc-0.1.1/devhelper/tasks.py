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
        return generate_solution_tree(path, sln_files[0])

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

def generate_solution_tree(base_path: Path, sln_file: Path) -> str:
    """
    Generate a solution-folder-aware tree from .sln file
    """

    folders, projects, nested = parse_solution_file(sln_file)
    lines = [sln_file.name]

    def walk_folder(folder_guid, prefix = ""):
        folder_name = folders[folder_guid]
        lines.append(f"{prefix}📂 {folder_name}")
        children = nested.get(folder_guid, [])
        for child in children:
            if child in folders:
                walk_folder(child, prefix + "    ")
            elif child in projects:
                proj = projects[child]
                lines.append(f"{prefix}    📄 {proj['name']} ({proj['path']})")

    # Root solution folders
    root_folders = set(folders.keys()) - set(nested.keys())
    # Root projects not nested in any folder
    nested_projects = {c for children in nested.values() for c in children}
    root_projects = set(projects.keys()) - nested_projects

    for f in root_folders:
        walk_folder(f)
    for p in root_projects:
        proj = projects[p]
        lines.append(f"📄 {proj['name']} ({proj['path']})")
    
    return "\n".join(lines)