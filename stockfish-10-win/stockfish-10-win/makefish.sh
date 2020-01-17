#!/bin/bash
# makefish.sh

# install packages if not already installed
unzip -v &> /dev/null || pacman -S --noconfirm unzip
make -v &> /dev/null || pacman -S --noconfirm make
g++ -v &> /dev/null || pacman -S --noconfirm mingw-w64-x86_64-gcc

# download the Stockfish source code
wget https://github.com/official-stockfish/Stockfish/archive/master.zip
unzip master.zip
cd Stockfish-master/src

# find the CPU architecture
# CPU without popcnt and bmi2 instructions (e.g. older than Intel Sandy Bridge)
arch_cpu=x86-64
# CPU with popcnt instruction (e.g. Intel Sandy Bridge)
if [ "$(g++ -Q -march=native --help=target | grep mpopcnt | grep enabled)" ] ; then
  arch_cpu=x86-64-modern
# CPU with bmi2 instruction (e.g. Intel Haswell or newer)
elif [ "$(g++ -Q -march=native --help=target | grep mbmi2 | grep enabled)" ] ; then
  arch_cpu=x86-64-bmi2
fi

# build the fastest stockfish executable
# delete CXXFLAGS='-march=native' if you want distribute the executable
CXXFLAGS='-march=native' make -j profile-build ARCH=${arch_cpu} COMP=mingw
strip stockfish.exe
mv stockfish.exe ../../stockfish_${arch_cpu}.exe
make clean 
cd