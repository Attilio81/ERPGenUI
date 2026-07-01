@echo off
REM ============================================================
REM  ERP Generative UI - avvio test in rete locale (one-click)
REM  Esegui QUESTO file SUL SERVER (192.168.44.73).
REM  Primo avvio: crea venv + installa dipendenze + build (qualche minuto).
REM  Poi di' al collega di aprire:  http://192.168.44.73:3000
REM  Richiede sul server: Python 3.11+ e Node 18+ (NON serve uv).
REM ============================================================
setlocal
cd /d "%~dp0"

REM --- trova Python (py o python) ---
set "PYEXE=py"
%PYEXE% --version >nul 2>&1
if errorlevel 1 set "PYEXE=python"
%PYEXE% --version >nul 2>&1
if errorlevel 1 (
  echo [ERRORE] Python non trovato nel PATH. Installa Python 3.11+ ^(con "Add to PATH"^).
  pause & exit /b 1
)

REM --- check .env ---
if not exist "backend\.env" (
  echo [ERRORE] Manca backend\.env  -- copia backend\.env.example in backend\.env e compila DB_CONN e DEEPSEEK_API_KEY.
  pause & exit /b 1
)

REM --- setup backend: venv + pip (una volta) ---
if not exist "backend\.venv\Scripts\python.exe" (
  echo [setup] Creo l'ambiente Python ^(venv^)...
  %PYEXE% -m venv "backend\.venv"
  echo [setup] Installo le dipendenze backend ^(pip^)...
  "backend\.venv\Scripts\python.exe" -m pip install --upgrade pip
  "backend\.venv\Scripts\pip.exe" install -r "backend\requirements.txt"
)

REM --- setup frontend: npm install + build (una volta) ---
if not exist "frontend\node_modules" (
  echo [setup] Installo le dipendenze frontend ^(npm install^)...
  pushd frontend & call npm install --no-fund --no-audit & popd
)
if not exist "frontend\.next" (
  echo [setup] Build frontend...
  pushd frontend & call npm run build & popd
)

REM --- guardia PII opzionale: attiva solo se PII_GUARD=on nel backend\.env ---
set "PII=0"
findstr /i /r "^PII_GUARD=on" "backend\.env" >nul 2>&1 && set "PII=1"
if "%PII%"=="1" (
  if not exist "pii-service\.venv\Scripts\python.exe" (
    echo [setup] pii-service: venv + torch CPU + modello ^(~1GB, solo la prima volta^)...
    %PYEXE% -m venv "pii-service\.venv"
    "pii-service\.venv\Scripts\python.exe" -m pip install --upgrade pip
    "pii-service\.venv\Scripts\python.exe" -m pip install torch --index-url https://download.pytorch.org/whl/cpu
    "pii-service\.venv\Scripts\pip.exe" install -r "pii-service\requirements.txt"
  )
)

REM --- apri la porta 3000 nel firewall (serve admin; se fallisce, ignora) ---
netsh advfirewall firewall add rule name="ERP GenUI 3000" dir=in action=allow protocol=TCP localport=3000 >nul 2>&1

REM --- avvio pii-service :5005 (solo se guardia attiva) ---
if "%PII%"=="1" (
  echo [PII] Avvio guardia PII su 127.0.0.1:5005 ...
  start "PII service :5005" cmd /k "cd /d "%~dp0pii-service" && ".venv\Scripts\python.exe" service.py"
  echo Attendo il caricamento del modello PII...
  timeout /t 10 /nobreak >nul
)

REM --- avvio backend :7000 (solo locale) ---
echo [1/2] Avvio backend su 127.0.0.1:7000 ...
start "ERP backend :7000" cmd /k "cd /d "%~dp0backend" && ".venv\Scripts\python.exe" -m uvicorn agent:app --host 127.0.0.1 --port 7000"

echo Attendo l'avvio del backend...
timeout /t 7 /nobreak >nul

REM --- avvio frontend :3000 (esposto in LAN) ---
echo [2/2] Avvio frontend su 0.0.0.0:3000 ...
start "ERP frontend :3000" cmd /k "cd /d "%~dp0frontend" && npm run start"

echo.
echo ============================================================
echo  PRONTO. Di' al collega di aprire:   http://192.168.44.73:3000
echo  (per fermare: chiudi le due finestre nere appena aperte)
echo ============================================================
echo.
pause
