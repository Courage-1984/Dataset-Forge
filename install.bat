@echo off
echo ========================================
echo Dataset Forge Installation Launcher
echo ========================================
echo.

REM Check if tools/install.bat exists
if not exist "tools\install.bat" (
    echo ERROR: tools\install.bat not found!
    echo Please ensure you're running this from the Dataset Forge root directory.
    pause
    exit /b 1
)

REM Run the installation script from tools directory
echo Running installation script from tools directory...
call tools\install.bat

REM Exit with the same code as the called script
exit /b %errorlevel%
