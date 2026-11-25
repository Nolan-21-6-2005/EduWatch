@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Tao moi truong ao .venv ...
    py -3 -m venv .venv 2>nul || python -m venv .venv
    if errorlevel 1 ( echo Khong tao duoc moi truong ao. Hay cai Python 3.10+ va tick "Add to PATH". & pause & exit /b 1 )
)
call ".venv\Scripts\activate.bat"

if not exist ".venv\.deps_installed" (
    echo Cai thu vien lan dau, co the mat vai phut ...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 ( echo Cai thu vien that bai. & pause & exit /b 1 )
    echo ok> ".venv\.deps_installed"
)

python run_app.py
pause
