@echo off
REM Create virtual environment
@REM C:\Users\<username>\AppData\Local\Programs\Python\Python311\python.exe -m venv venv
py -3.12 -m venv venv312

REM Install PyTorch with CUDA 12.1 support
venv312\Scripts\python.exe -m pip install --upgrade pip
venv312\Scripts\pip.exe install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121


REM Install other requirements
venv312\Scripts\pip.exe install -r requirements.txt

REM Activate the virtual environment
call venv312\Scripts\activate.bat

REM Run install.py (which should run main.py)
py install.py 