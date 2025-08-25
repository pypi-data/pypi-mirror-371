# devhelper/solution_parser.py
import re
from pathlib import Path
from collections import defaultdict

def parse_solution_file(sln_path: Path):
    ignore_folders = {"bin", "obj", ".vs"}

    text = sln_path.read_text(encoding="utf-8", errors="ignore")

    project_pattern = re.compile(
        r'Project\("\{(?P<type_guid>[^}]+)\}"\)\s*=\s*"(?P<name>[^"]+)",\s*"(?P<path>[^"]*)",\s*"\{(?P<id>[^}]+)\}"'
        r'(?:\r?\n\tProjectSection\(SolutionItems\) = preProject(?P<items>.*?)EndProjectSection)?\s*EndProject',
        re.DOTALL
    )

    projects = {}
    solution_folders = set()

    # Parse projects and solution folders
    for match in project_pattern.finditer(text):
        type_guid = match.group("type_guid").upper()
        proj_id = match.group("id")
        name = match.group("name")
        path = match.group("path")
        items_text = match.group("items")

        items = []
        if items_text:
            for line in items_text.splitlines():
                line = line.strip()
                if line and "=" in line:
                    items.append(line.split("=")[0].strip())

        projects[proj_id] = {
            "name": name,
            "path": path,
            "type_guid": type_guid,
            "contents": items
        }

        if type_guid == "2150E333-8FDC-42A3-9474-1A3956D46DE8":
            solution_folders.add(proj_id)

    # Parse nested projects
    nested_match = re.search(r'GlobalSection\(NestedProjects\).*?EndGlobalSection', text, re.DOTALL)
    if nested_match:
        for line in nested_match.group(0).splitlines():
            line = line.strip()
            if "=" in line:
                child_id, parent_id = map(lambda s: s.strip().strip("{}"), line.split("="))
                if parent_id in projects:
                    projects[parent_id]["contents"].append(child_id)

    sln_base = sln_path.parent.resolve()

    def resolve_contents(item_ids):
        resolved = []
        for item in item_ids:
            if item in projects:
                proj = projects[item]
                # Solution folder
                if proj["type_guid"] == "2150E333-8FDC-42A3-9474-1A3956D46DE8":
                    resolved.append({proj["name"]: resolve_contents(proj["contents"])})
                # Normal project
                else:
                    proj_path = (sln_base / proj["path"]).parent.resolve()
                    files_list = []
                    if proj_path.exists():
                        for p in proj_path.rglob("*"):
                            if p.is_file() and not any(part in ignore_folders for part in p.parts):
                                files_list.append(str(p.relative_to(proj_path)))
                    # Include solution items if any (filter ignored folders too)
                    for item_file in proj["contents"]:
                        if not any(part in ignore_folders for part in Path(item_file).parts):
                            files_list.append(item_file)
                    resolved.append({proj["name"]: files_list})
            else:
                # Solution item file
                if not any(part in ignore_folders for part in Path(item).parts):
                    resolved.append(item)
        return resolved

    result = {}
    for folder_id in solution_folders:
        folder = projects[folder_id]
        result[folder["name"]] = resolve_contents(folder["contents"])

    print(result)
    return result