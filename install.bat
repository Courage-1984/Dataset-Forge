@echo off
REM Create virtual environment
py -3.12 -m venv venv312

REM Activate the virtual environment
call venv312\Scripts\activate.bat

REM Install PyTorch with CUDA 12.1 support (edit for other CUDA versions if needed)
venv312\Scripts\pip.exe install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

REM Install Dataset Forge and all other requirements
venv312\Scripts\pip.exe install .

REM Print success message
echo Installation complete. To run, activate the venv and use: dataset-forge 