@echo off
setlocal
python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
if errorlevel 1 (
  echo Python 3.11 or newer is required to build the release executable.
  exit /b 1
)
python -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name "Ferdi Smart Calculator" ^
  --collect-all customtkinter ^
  main.py
if errorlevel 1 exit /b 1
echo.
echo Build selesai: dist\Ferdi Smart Calculator.exe
