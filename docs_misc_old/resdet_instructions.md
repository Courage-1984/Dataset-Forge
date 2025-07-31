# resdet instructions (for 'MSYS2 MINGW64 Shell'):

git clone https://github.com/0x09/resdet.git

Open 'MSYS2 MINGW64 Shell'

pacman -S base-devel mingw-w64-x86_64-toolchain mingw-w64-x86_64-libpng mingw-w64-x86_64-libjpeg-turbo mingw-w64-x86_64-fftw mingw-w64-x86_64-pkg-config autoconf automake libtool

cd C:/path/to/cloned/resdet

export PKG_CONFIG_PATH=/mingw64/lib/pkgconfig

make clean

./configure --prefix=/mingw64 --disable-libpng --disable-libjpegclear

make

DONE

Add 'resdet.exe' to a folder which should also be in your PATH or add it to your PATH

C:/Users/Dieter/Downloads/jubel__x4_4xNomosWebPhoto_esrgan.png


USING WSL:

git clone https://github.com/0x09/resdet.git

cd resdet

./configure

make


cd /mnt/c/Users/Dieter/wsl_resdet/resdet
sudo cp resdet /usr/local/bin/
sudo chmod +x /usr/local/bin/resdet

Or, if you want to use make install:

sudo make install

