#!/usr/bin/env python3
import sys
import subprocess
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    print(f"[*] Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, cwd=cwd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Command failed: {e}")
        return False
    return True

def test_backend():
    print("[*] Testing Backend...")
    return run_command(["pytest", "tests/"], cwd="backend")

def test_frontend():
    print("[*] Testing Frontend...")
    return run_command(["npm", "run", "test:ci"], cwd="frontend")

def optimize():
    print("[*] Running Optimization Analysis...")
    run_command(["python", "tools/benchmark.py"])
    run_command(["python", "tools/detect_code_duplication.py", "backend", "tools/backend_duplication.json"])

def main():
    if len(sys.argv) < 2:
        print("Usage: python manage.py <command>")
        print("Commands: test-backend, test-frontend, test-all, optimize")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "test-backend":
        test_backend()
    elif cmd == "test-frontend":
        test_frontend()
    elif cmd == "test-all":
        test_backend()
        test_frontend()
    elif cmd == "optimize":
        optimize()
    else:
        print(f"[!] Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
