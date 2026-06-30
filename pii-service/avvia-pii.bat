@echo off
REM ============================================================
REM  Microservizio PII (rizzo-pii-0.3B) - anonimizzazione locale.
REM  Primo avvio: crea venv + installa deps + scarica il modello (~1GB).
REM  Gira su 127.0.0.1:5005 (override: env PII_PORT).
REM ============================================================
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [setup] creo venv e installo dipendenze (torch CPU + transformers)...
  py -3 -m venv .venv || python -m venv .venv
  ".venv\Scripts\python.exe" -m pip install --upgrade pip
  ".venv\Scripts\python.exe" -m pip install torch --index-url https://download.pytorch.org/whl/cpu
  ".venv\Scripts\pip.exe" install transformers huggingface_hub fastapi uvicorn
)

echo [run] avvio pii-service su http://127.0.0.1:5005 ...
".venv\Scripts\python.exe" service.py
