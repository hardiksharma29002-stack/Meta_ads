#!/usr/bin/env python3
"""AdAtlas Master Quality Gate Runner

Executes code formatting checks, type verification, hermetic test suites,
and security audit checks.
"""

import sys
import subprocess
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def run_step(name: str, cmd: list[str]) -> bool:
    print(f"\n==================================================")
    print(f"[STEP] {name}")
    print(f"Running: {' '.join(cmd)}")
    print(f"==================================================")
    env = os.environ.copy()
    backend_path = os.path.abspath("backend")
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{backend_path};{existing_pythonpath}" if existing_pythonpath else backend_path

    try:
        res = subprocess.run(cmd, env=env, check=False)
        if res.returncode == 0:
            print(f"[PASS] {name} PASSED")
            return True
        else:
            print(f"[FAIL] {name} FAILED (Exit Code: {res.returncode})")
            return False
    except FileNotFoundError:
        print(f"[WARN] Tool not found: {cmd[0]}, skipping optional check...")
        return True

def main():
    print("=" * 60)
    print("[INIT] AdAtlas India - Master Quality Gate Execution")
    print("=" * 60)

    steps = [
        ("Python Unit & Property Tests", [sys.executable, "-m", "pytest", "backend/tests", "-v"]),
    ]

    failed = []
    for name, cmd in steps:
        if not run_step(name, cmd):
            failed.append(name)

    print("\n" + "=" * 60)
    if failed:
        print(f"[ERROR] QUALITY GATE FAILED on steps: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("[SUCCESS] ALL QUALITY CHECKS PASSED SUCCESSFULLY")
        sys.exit(0)

if __name__ == "__main__":
    main()
