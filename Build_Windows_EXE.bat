@echo off
setlocal
 title Build CS2 Asset Creator 2.1
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher was not found. Install Python 3.10+ from python.org and enable the launcher.
  pause
  exit /b 1
)
py -3 -c "import tkinter; print('Python and Tkinter OK')"
if errorlevel 1 (
  echo Python Tkinter is missing. Reinstall Python and include Tcl/Tk support.
  pause
  exit /b 1
)
py -3 -m pip install --upgrade pyinstaller
if errorlevel 1 (echo Could not install PyInstaller.& pause & exit /b 1)
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed --name CS2_Asset_Creator CS2_Asset_Creator.py
if errorlevel 1 (echo Build failed. Review the errors above.& pause & exit /b 1)
echo.
echo SUCCESS: %CD%\dist\CS2_Asset_Creator.exe
pause
