@echo off
REM Activate the virtual environment
call venv312\Scripts\activate.bat

REM Run Dataset Forge via CLI entry point (preferred)
@REM dataset-forge

REM Fallback: run main.py if CLI entry point is not available
py main.py 