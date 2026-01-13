@echo off
REM Build script for AI Assistant Windows Desktop App
REM This script builds the Windows executable using PyInstaller

echo ================================================
echo AI Assistant - Windows App Build Script
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Step 1: Installing required dependencies...
python -m pip install --upgrade pip
python -m pip install pywebview pyinstaller pillow

echo.
echo Step 2: Building Windows executable...
pyinstaller windows_app.spec --clean --noconfirm

echo.
if exist "dist\AIAssistant\AIAssistant.exe" (
    echo ================================================
    echo ✓ Build completed successfully!
    echo ================================================
    echo.
    echo Your Windows app is located at:
    echo   dist\AIAssistant\AIAssistant.exe
    echo.
    echo You can now:
    echo   1. Run dist\AIAssistant\AIAssistant.exe to start the app
    echo   2. Copy the entire AIAssistant folder to share with others
    echo   3. Create a desktop shortcut to AIAssistant.exe
    echo.
) else (
    echo ================================================
    echo ✗ Build failed!
    echo ================================================
    echo Please check the error messages above.
    echo.
)

pause
