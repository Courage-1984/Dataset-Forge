@echo off
REM Create virtual environment
C:\Users\<username>\AppData\Local\Programs\Python\Python311\python.exe -m venv venv

REM Install PyTorch with CUDA 12.1 support
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\pip.exe install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

REM Install other requirements
venv\Scripts\pip.exe install -r requirements.txt

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Run install.py (which should run main.py)
py install.py 