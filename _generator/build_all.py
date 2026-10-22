#!/usr/bin/env python3
"""Run every generator in the right order. build_meta.py must run last, because it adds metadata to the pages
the others write.

Run:  python3 _generator/build_all.py
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = ["build_boards.py", "build_guides.py", "build_roles.py", "build_glossary.py",
         "build_antipatterns.py", "build_practices.py", "build_industries.py", "build_prompts.py", "build_scenarios.py", "build_recipes.py",
         "build_meta.py"]

for step in STEPS:
    print(f"== {step}", flush=True)
    result = subprocess.run([sys.executable, str(HERE / step)], stdout=subprocess.DEVNULL)
    if result.returncode:
        sys.exit(f"{step} failed")
print("all generators ran")
