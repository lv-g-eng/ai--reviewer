@echo off
echo === Checking pytest version ===
venv\Scripts\python.exe -m pytest --version
echo.
echo === Collecting tests (dry run, unit-only) ===
venv\Scripts\python.exe -m pytest tests\test_example.py tests\test_jwt_service.py tests\test_auth_endpoints.py --collect-only -q 2>&1
