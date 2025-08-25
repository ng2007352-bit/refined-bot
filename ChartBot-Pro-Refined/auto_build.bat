@echo off
setlocal
title ChartBot Pro - One-Click Build

echo ==============================
echo   ChartBot Pro - Builder
echo ==============================

:: Ensure Python
python --version >nul 2>&1 || (
  echo Python not found. Downloading...
  powershell -Command "Invoke-WebRequest https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe -OutFile python-installer.exe"
  start /wait "" python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
  del python-installer.exe
)

:: Install deps
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller

:: Verify bundled Tesseract files exist
if not exist tess\tesseract.exe (
  echo ❌ Missing tess\tesseract.exe
  echo    Add portable Tesseract binary at tess\tesseract.exe (GitHub build does this automatically).
  pause
  exit /b 1
)
if not exist tess\tessdata\eng.traineddata (
  echo ❌ Missing tess\tessdata\eng.traineddata
  echo    Add English tessdata at tess\tessdata\eng.traineddata (GitHub build does this automatically).
  pause
  exit /b 1
)

:: Clean and build
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

pyinstaller --onefile --windowed --name "ChartBot" --icon "icon.ico" ^
  --add-binary "tess\tesseract.exe;tess" ^
  --add-data  "tess\tessdata;tess\tessdata" ^
  chartbot.py

echo.
if exist dist\ChartBot.exe (
  echo ✅ Build complete: dist\ChartBot.exe
) else (
  echo ❌ Build failed.
)
pause
