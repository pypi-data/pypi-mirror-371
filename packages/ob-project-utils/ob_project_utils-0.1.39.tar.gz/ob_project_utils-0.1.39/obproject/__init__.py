import os
import sys
from pathlib import Path

from .projectbase import ProjectFlow
from .project_events import ProjectEvent, project_trigger
from highlight_card import highlight

METAFLOW_PACKAGE_POLICY = "include"
INCLUDE_IN_PYTHONPATH = ["src"]


def _populate_pythonpath():
    REQUIRED = (".git", "obproject.toml")
    print("argv[0]", os.path.abspath(sys.argv[0]))
    for path in Path(os.path.abspath(sys.argv[0])).parents:
        has_git = os.path.exists(os.path.join(path, ".git"))
        obproj = os.path.exists(os.path.join(path, "obproject.toml"))
        print(f"path {path} has .git {has_git} has proj {obproj}")
        if all(os.path.exists(os.path.join(path, x)) for x in REQUIRED):
            print("found", path)
            for x in INCLUDE_IN_PYTHONPATH:
                sys.path.append(os.path.join(path, x))
            break
    else:
        print(
            """
WARNING: It seems you are importing `obproject` outside 
of a project repository with obproject.toml. Automatic
importing of `src/` packages won't work. If you need those
packages, set PYTHONPATH manually.
"""
        )


_populate_pythonpath()
