@echo off
REM Setup una-tantum sul server (alternativa: lo fa gia' avvia-lan.bat al primo avvio).
REM Richiede: Python 3.11+ e Node 18+ nel PATH. NON serve uv.
setlocal
cd /d "%~dp0"

set "PYEXE=py"
%PYEXE% --version >nul 2>&1
if errorlevel 1 set "PYEXE=python"
%PYEXE% --version >nul 2>&1
if errorlevel 1 ( echo [ERRORE] Python non trovato nel PATH. & pause & exit /b 1 )

echo === Backend: venv + dipendenze ===
%PYEXE% -m venv "backend\.venv"
"backend\.venv\Scripts\python.exe" -m pip install --upgrade pip
"backend\.venv\Scripts\pip.exe" install -r "backend\requirements.txt"
if not exist "backend\.env" echo  ATTENZIONE: manca backend\.env  -- copia da .env.example e compila.

echo === Frontend: dipendenze + build ===
pushd frontend & call npm install --no-fund --no-audit & call npm run build & popd

echo.
echo Setup completato. Ora lancia  avvia-lan.bat
