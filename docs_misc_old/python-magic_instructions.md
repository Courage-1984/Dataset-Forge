# python-magic instructions (for 'Directory Utilities'):

python-magic==0.4.27
python-magic-bin==0.4.14
libmagic==1.0

pip install python-magic python-magic-bin libmagic

.\assets\libmagicwin64-master.zip contains:
    libgnurx-0.dll
    magic.mgc
    magic1.dll
These files should go in C:/Windows/System32/
Source: https://github.com/pidydx/libmagicwin64

These files  are for using libmagic with 64 bit Windows and were compiled using MSYS2. Hopefully this will save someone else a lot of pain. Huge thanks to the MSYS2 folks because getting the tool chain to build this natively was a horrible pain.

Drop the dlls in C:\Windows\System32 and python magic will import correctly.

file_magic = magic.Magic(magic_file="c:\path\to\magic.mgc")


✅ python-magic initialized with magic file: C:/Windows/System32/magic.mgc

