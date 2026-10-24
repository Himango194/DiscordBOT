@echo off
setlocal
cd /d "%~dp0"

rem ===== Find Python (py launcher first, then python) =====
set "PY="
py -3 --version >nul 2>&1 && set "PY=py -3"
if not defined PY (
    python --version >nul 2>&1 && set "PY=python"
)
if not defined PY (
    echo [ERROR] Python not found.
    echo Install it from https://www.python.org/downloads/
    echo and check "Add python.exe to PATH" during installation.
    pause
    exit /b 1
)

rem ===== First run: create virtual environment =====
if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    %PY% -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

rem ===== Install / update packages =====
echo [2/3] Installing packages...
".venv\Scripts\python.exe" -m pip install -q --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install packages. Check your internet connection.
    pause
    exit /b 1
)

rem ===== First run: create .env =====
if not exist ".env" (
    echo [3/3] Creating .env
    set /p "TOKEN=Paste your Discord Bot Token: "
    set /p "GUILD=Server ID (optional, press Enter to skip): "
    call :write_env
)

echo.
echo Starting bot... (close this window to stop)
echo.
".venv\Scripts\python.exe" main.py
pause
exit /b

:write_env
> ".env" echo DISCORD_TOKEN=%TOKEN%
>> ".env" echo GUILD_ID=%GUILD%
exit /b
