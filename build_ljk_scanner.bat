@echo off
REM ===============================================
REM BATCH FILE: build_ljk_scanner.bat
REM Fungsi: Compile Python ke .exe menggunakan PyInstaller
REM ===============================================

set SCRIPT=ljk_scanner.py
set EXE_NAME=ljk_scanner.exe

REM Cek apakah file script Python ada
if not exist %SCRIPT% (
    echo ❌ GAGAL: File %SCRIPT% tidak ditemukan!
    pause
    exit /b
)

REM Cek dan install pyinstaller jika belum ada
pip show pyinstaller >nul 2>&1
IF ERRORLEVEL 1 (
    echo 📦 PyInstaller belum terinstal. Menginstal sekarang...
    pip install pyinstaller
)

REM Bersihkan build sebelumnya
echo 🧹 Membersihkan build lama...
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist %SCRIPT:.py=.spec% del /q %SCRIPT:.py=.spec%

REM Jalankan PyInstaller
echo 🚀 Membuat file EXE dari %SCRIPT% ...
pyinstaller --noconfirm --onefile --windowed %SCRIPT% > build_log.txt 2>&1

REM Cek hasil
if exist dist\%EXE_NAME% (
    echo ✅ Sukses! File EXE tersedia di folder dist\
    echo 📂 dist\%EXE_NAME%
    start dist\%EXE_NAME%
) else (
    echo ❌ GAGAL: File EXE tidak ditemukan. Lihat log untuk detail.
    notepad build_log.txt
)

pause
