@echo off
REM Tools Launcher for Dataset Forge
REM This batch file provides easy access to the tools launcher

REM Activate the virtual environment
call venv312\Scripts\activate

REM Run `python tools\launcher.py`
python tools\launcher.py
