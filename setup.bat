@echo off
REM Setup una-tantum sul server: installa dipendenze e build del frontend.
cd /d "%~dp0"

echo === Backend: dipendenze (uv) ===
cd /d "%~dp0backend"
uv sync
if not exist .env (
  echo.
  echo  ATTENZIONE: manca backend\.env  -- copia da .env.example e compila DB_CONN e DEEPSEEK_API_KEY
)

echo === Frontend: dipendenze + build ===
cd /d "%~dp0frontend"
call npm install --no-fund --no-audit
call npm run build

echo.
echo Setup completato. Ora lancia  avvia-lan.bat
