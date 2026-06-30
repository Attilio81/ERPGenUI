@echo off
REM ============================================================
REM  ERP Generative UI - AGGIORNA dopo aver copiato file nuovi.
REM  Rinfresca dipendenze backend/frontend e forza la rebuild,
REM  cosi' la versione servita e' quella aggiornata.
REM  Poi rilancia  avvia-lan.bat
REM ============================================================
setlocal
cd /d "%~dp0"

set "PYEXE=py"
%PYEXE% --version >nul 2>&1
if errorlevel 1 set "PYEXE=python"
%PYEXE% --version >nul 2>&1
if errorlevel 1 ( echo [ERRORE] Python non trovato nel PATH. & pause & exit /b 1 )

echo [1/3] Backend: dipendenze...
if not exist "backend\.venv\Scripts\python.exe" %PYEXE% -m venv "backend\.venv"
"backend\.venv\Scripts\python.exe" -m pip install --upgrade pip
"backend\.venv\Scripts\pip.exe" install -r "backend\requirements.txt"

echo [2/3] Frontend: dipendenze...
pushd frontend
call npm install --no-fund --no-audit

echo [3/3] Frontend: rebuild forzata...
if exist ".next" rmdir /s /q ".next"
call npm run build
popd

echo.
echo Aggiornamento completato. Ora lancia  avvia-lan.bat
pause
