@echo off
REM Avvio per test in rete locale. Eseguire sul server (192.168.44.73), da disco LOCALE.
REM Backend su localhost:8000, frontend esposto su 0.0.0.0:3000.
REM Gli altri PC aprono:  http://192.168.44.73:3000

cd /d "%~dp0"

echo [1/2] Avvio backend (Agno) su :8000 ...
start "EGM backend :8000" cmd /k "cd /d "%~dp0backend" && uv run uvicorn agent:app --host 127.0.0.1 --port 8000"

echo Attendo l'avvio del backend...
timeout /t 6 /nobreak >nul

echo [2/2] Avvio frontend (Next) su :3000 (LAN) ...
start "EGM frontend :3000" cmd /k "cd /d "%~dp0frontend" && npm run start"

echo.
echo Aperto. Dagli altri PC:  http://192.168.44.73:3000
echo (la prima volta esegui PRIMA  setup.bat  per installare le dipendenze e fare la build)
