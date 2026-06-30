# Deploy per test in rete locale

Topologia: l'app gira **sul server `192.168.44.73`**. Il browser degli altri PC parla solo
col **frontend (porta 3000)**; il backend resta su `localhost:8000` del server (non esposto).

```
PC in LAN  ──http://192.168.44.73:3000──►  Frontend Next (server)
                                              │  /api/copilotkit  →  Backend Agno  localhost:8000
                                              │  /api/articolo|cliente  →  Backend  localhost:8000
                                              └─ pagina + chat
Backend  ──pyodbc──►  SQL Server (egmsql2022)      Backend ──https──► DeepSeek (internet)
```

## Prerequisiti sul server
- **Python 3.13 + uv**, **Node 18+**
- **ODBC Driver 17 for SQL Server**
- Accesso di rete a SQL Server `egmsql2022\Nts2022`
- **Internet in uscita** (per l'API DeepSeek). Se il server non ha internet → passare a LLM locale (Ollama).
- `backend/.env` compilato (`DB_CONN`, `DEEPSEEK_API_KEY`, opz. `CODDITT`)
- Porta **3000** aperta nel firewall del server

## Passi
1. **Copia il progetto su disco LOCALE del server** (NON eseguire dalla share `\\192.168.44.73\Prototipi`:
   node_modules/.venv su SMB sono lentissimi). Es. `C:\Apps\ERPGenUI`. Escludi `node_modules/`, `.venv/`, `.next/`.
   In alternativa: `git clone` sul server.
2. Crea `backend\.env` (da `backend\.env.example`).
3. Esegui **`setup.bat`** (una volta): installa dipendenze + build frontend.
4. Apri la porta 3000:
   `netsh advfirewall firewall add rule name="EGM GenUI 3000" dir=in action=allow protocol=TCP localport=3000`
5. Esegui **`avvia-lan.bat`** (apre due finestre: backend :8000, frontend :3000).
6. Dagli altri PC: **http://192.168.44.73:3000**

## Note
- Solo la 3000 va esposta: la chat usa URL relativi (`/api/copilotkit`) → stessa origine, niente CORS.
- Il backend gira su `127.0.0.1:8000` del server: il proxy Next lo raggiunge in locale.
- Per fermare: chiudere le due finestre cmd.
- Reset contesto demo: pulsante **↺ Nuova** nell'app.
- Multitenant: una ditta per deploy → imposta `CODDITT` nel `.env`.
