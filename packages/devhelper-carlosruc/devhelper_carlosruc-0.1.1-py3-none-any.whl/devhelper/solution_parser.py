# devhelper/solution_parser.py
import re
from pathlib import Path
from collections import defaultdict

def parse_solution_file(sln_path: Path):
    """
    Parse a Visual Studio .sln file to extract solution folders and projects.
    Returns a dict {folder_name: [project_names]} and list of root projects
    """

    content = sln_path.read_text(encoding="utf-8", errors="ignore")


    # Match projects
    project_pattern = re.compile(
        r'Project\("\{(?P<type_guid>[^}]*)\}"\)\s=\s"(?P<name>[^"]+)",\s"(?P<path>[^"]+)",\s"\{(?P<guid>[^}]*)\}"',
        re.MULTILINE
    )

    projects = {}
    folders = {}

    for match in project_pattern.finditer(content):
        type_guid = match.group("type_guid").upper()
        name = match.group("name")
        guid = match.group("guid")
        path = match.group("path")

        if type_guid == "2150E333-8FDC-42A3-9474-1A3956D46DE8":
            folders[guid] = name
        else:
            projects[guid] = {"name": name, "path": path}

    # Match NestedProjects
    nested = defaultdict(list)
    nested_pattern = re.compile(r"\{([^}]*)\}\s=\s\{([^}]*)\}")
    nested_section = re.search(r"GlobalSection\(NestedProjects\).*?EndGlobalSection", content, re.DOTALL)
    if nested_section:
        for child, parent in nested_pattern.findall(nested_section.group(0)):
            nested[parent].append(child)

    return folders, projects, nested