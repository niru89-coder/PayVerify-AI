"""
Bootstrap: adds the flat-module engine directories to sys.path so the FastAPI
app can `import` the rule-engine / validation-engine / services / agents
modules despite their hyphenated (non-package) directory names.

Must be imported before any of those modules are imported anywhere in the
backend package (main.py imports this first).
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

for sub in ["rule-engine", "validation-engine", "services", "agents"]:
    p = str(ROOT / sub)
    if p not in sys.path:
        sys.path.insert(0, p)
