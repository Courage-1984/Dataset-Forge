@echo off
echo ========================================
echo Dataset Forge Installation Script
echo ========================================
echo.

REM Check if Python 3.12+ is available
set PYTHON_PATH=C:\Users\anon\AppData\Local\Programs\Python\Python312\python.exe

REM Check if the specific Python path exists
if not exist "%PYTHON_PATH%" (
    echo ERROR: Python is not found at expected location: %PYTHON_PATH%
    echo Please install Python 3.12+ from https://python.org
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('"%PYTHON_PATH%" --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python version: %PYTHON_VERSION%

REM Create virtual environment if it doesn't exist
if not exist "venv312" (
    echo Creating virtual environment...
    "%PYTHON_PATH%" -m venv venv312
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv312\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Run the Python installation script
echo Running installation script...
"%PYTHON_PATH%" tools\install.py
if errorlevel 1 (
    echo ERROR: Installation failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo You can now run Dataset Forge using:
echo   run.bat
echo   or
echo   python main.py
echo.
pause
