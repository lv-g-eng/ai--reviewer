@echo off
echo === Installing main requirements ===
venv\Scripts\python.exe -m pip install -r requirements.txt --quiet 2>&1
echo === Installing test requirements ===
venv\Scripts\python.exe -m pip install -r requirements-test.txt --quiet 2>&1
echo === Done ===
venv\Scripts\python.exe -m pytest --version
