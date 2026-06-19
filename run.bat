@echo off
title NetVizor Baslatici
color 0B

echo ======================================
echo         NetVizor Baslatici   
echo ======================================
echo.

:: Python kontrolu
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python bulunamadi. Lutfen Python 3.10+ yukleyin ve PATH'e ekleyin.
    pause
    exit /b
)

:: Sanal ortam kurulumu
if not exist venv (
    echo [+] Sanal ortam [venv] olusturuluyor...
    python -m venv venv
)

echo [+] Bagimliliklar kontrol ediliyor...
call venv\Scripts\pip install -r requirements.txt >nul 2>&1

echo.
echo NetVizor iki farkli modda calisabilir:
echo   1) Temel Mod    : Bant genisligi, surecler ve TCP baglantilari
echo   2) Gelismis Mod : Npcap gerektirir. Sudo yetkisiyle paket inceleme.
echo.
set /p MODE="Hangi modda baslatmak istersiniz? (1/2) [Varsayilan: 1]: "
if "%MODE%"=="" set MODE=1

echo.
echo [+] NetVizor baslatiliyor... (Tarayiciniz otomatik acilacaktir)

:: Tarayiciyi biraz gecikmeli baslat
start "" "http://localhost:8765"

if "%MODE%"=="2" (
    echo [!] Gelismis mod secildi. Lutfen terminalin Yonetici olarak calistigindan emin olun.
    call venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8765
) else (
    call venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8765
)

pause
