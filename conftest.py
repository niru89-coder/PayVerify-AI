"""
Pytest configuration - adds the flat-module engine directories to sys.path.

Project folders use hyphenated names per the master project structure spec
(rule-engine/, validation-engine/, services/, agents/), which are not valid
Python package names. Instead of nesting packages, each directory's modules
are imported as flat top-level modules (e.g. `import epf`, `from base import
...`) with their directory added to sys.path here (for tests) and in
backend/app/bootstrap.py (for the running API).
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent

for sub in ["rule-engine", "validation-engine", "services", "agents"]:
    p = str(ROOT / sub)
    if p not in sys.path:
        sys.path.insert(0, p)
