@echo off
echo Installing test dependencies...
venv\Scripts\python.exe -m pip install pytest pytest-asyncio pytest-cov pytest-mock httpx pytest-json-report pytest-xdist faker freezegun anyio 2>&1
echo Done.
