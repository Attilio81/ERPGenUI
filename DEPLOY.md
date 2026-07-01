# Deploy per test in rete locale

L'app gira **sul server `192.168.44.73`**. Gli altri PC aprono solo il **frontend (porta 3000)**;
il backend resta su `127.0.0.1:7000` del server (non esposto).

```
PC in LAN ──http://192.168.44.73:3000──► Frontend Next (server)
                                           │ /api/* → Backend Agno 127.0.0.1:7000
Backend ──pyodbc──► SQL Server (egmsql2022)   Backend ──https──► DeepSeek (internet)
```

## Uso (chiavi in mano)
1. I file sono sul server in `...\Prototipi\ERPGenUI` (copiati su disco locale del server).
2. Assicurati che esista `backend\.env` (vedi `backend\.env.example`):
   - `DB_CONN`, `CODDITT` (opz.)
   - `AI_PROVIDER` = `deepseek` (default) · `mistral` (UE, GDPR) · `local`
   - la chiave del provider scelto: `DEEPSEEK_API_KEY` **oppure** `MISTRAL_API_KEY`
   - `PII_GUARD` = `off` (default) · `on` per attivare la guardia PII (avvia anche pii-service :5005)
3. Doppio click su **`avvia-lan.bat`** — al primo avvio installa dipendenze e fa la build
   (qualche minuto), poi parte. Apre due finestre: backend :7000 e frontend :3000.
4. Di' al collega: **http://192.168.44.73:3000**

> Stop: chiudere le due finestre nere. Reset demo: pulsante **↺ Nuova** nell'app.

## Aggiornare una versione gia' in produzione
1. Ricopia i file aggiornati nella cartella sul server (escludendo `node_modules/`, `.venv/`, `.next/`, `.git/`).
2. Sul server esegui **`aggiorna.bat`** (rinfresca dipendenze + **rebuild forzata** del frontend).
3. Rilancia **`avvia-lan.bat`**.
   (Senza `aggiorna.bat`, il bat normale non ricostruisce se `frontend\.next` esiste gia' → serviresti la versione vecchia.)

## Prerequisiti sul server
- **Python 3.11+** (basta `py`/`python` nel PATH; **NON serve uv**), **Node 18+**, **ODBC Driver 17 for SQL Server**
- Accesso a SQL Server `egmsql2022\Nts2022` + **internet in uscita** verso il provider LLM
  (DeepSeek o Mistral; con `AI_PROVIDER=local` serve invece un LLM self-host, es. Ollama)
- Porta **3000** aperta nel firewall (il bat prova ad aprirla; se serve, lancialo una volta come Amministratore)
- **Solo se `PII_GUARD=on`**: `avvia-lan.bat` crea da sé il venv di `pii-service` e scarica il
  modello (~1GB) al primo avvio, poi lo tiene su `127.0.0.1:5005`. Richiede più spazio/tempo iniziale.

## GDPR
`AI_PROVIDER=mistral` (Mistral La Plateforme, UE + DPA) è la scelta **compliant**: nessun trasferimento
in paese terzo. `deepseek` (server in Cina) è ok solo per test. Dettagli nel README.

## Note
- Solo la 3000 è esposta: la chat usa URL relativi → niente CORS.
- `.env` contiene la password `sa` + la key DeepSeek: tienilo sul server, non su share condivise pubbliche.
- Multitenant: una ditta per deploy → `CODDITT` nel `.env`.
- NON eseguire da percorso di rete `\\...` (SMB lento): usa il disco locale del server.
