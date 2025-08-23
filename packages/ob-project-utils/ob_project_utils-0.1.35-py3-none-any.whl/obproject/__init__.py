import os
import sys
from pathlib import Path

from .projectbase import ProjectFlow
from .project_events import ProjectEvent, project_trigger
from highlight_card import highlight

METAFLOW_PACKAGE_POLICY = "include"
INCLUDE_IN_PYTHONPATH = ['src']

def _populate_pythonpath():
    REQUIRED = ('.git', 'obproject.toml')
    for path in Path(sys.argv[0]).parents:
        if all(os.path.exists(os.path.join(path, x)) for x in REQUIRED):
            for x in INCLUDE_IN_PYTHONPATH:
                sys.path.append(os.path.join(path, x))

_populate_pythonpath()