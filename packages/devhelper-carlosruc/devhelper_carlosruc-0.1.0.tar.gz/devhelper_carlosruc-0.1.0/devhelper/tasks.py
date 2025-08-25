# devhelper/tasks.py
from pathlib import Path

def create_file(filename: str):
    Path(filename).touch()

def list_files(path: str):
    return [p.name for p in Path(path).iterdir() if p.is_file()]