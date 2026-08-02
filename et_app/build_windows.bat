@echo off
REM Emergent Thought Documentation App — Windows build script
REM Run this once on your PC to produce dist\EmergentThought.exe

echo Installing dependencies...
pip install fastapi uvicorn sqlalchemy jinja2 python-multipart pywebview pyinstaller

echo.
echo Building EmergentThought.exe...
pyinstaller EmergentThought.spec --clean

echo.
echo Done. Your app is at: dist\EmergentThought.exe
echo Copy that single file anywhere — it does not need Python installed to run.
pause
