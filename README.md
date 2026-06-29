<div align="center">

# ERP Generative UI

**Una chat che pilota un'interfaccia gestionale deterministica — su dati reali.**

Generative UI a *stato condiviso*: l'LLM non disegna la UI, ne **orchestra** i componenti.
Tabella, scheda articolo e grafici tradizionali, guidati dal linguaggio naturale.

![Next.js](https://img.shields.io/badge/Next.js-14-000000?logo=next.js)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Agno](https://img.shields.io/badge/Agno-AG--UI-DA481B)
![CopilotKit](https://img.shields.io/badge/CopilotKit-1.61-6963FF)
![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek-4D6BFE)
![License](https://img.shields.io/badge/uso-demo-555)

![Distinta articoli](docs/screenshots/tabella.png)

</div>

---

## Cos'è

Esperimento di **Generative UI** sul pattern più solido: lo **stato condiviso** (AG-UI).
A differenza del "tutto dentro la chat", qui l'interfaccia resta quella classica e ottimizzata
per i dati — molte righe, ordinamenti, grafici — mentre l'AI fa da **regista**: capisce la
richiesta e decide *quale* componente mostrare e con *quali filtri/dati*.

L'LLM non genera HTML/React arbitrario: compone componenti registrati e deterministici.
Coerenza, design system e controllo restano dalla parte dell'applicazione.

> Ispirato al filone "Generative UI" (AI SDK / CopilotKit / AG-UI / MCP), ma con backend
> **Python/Agno** invece che TypeScript: il contratto AG-UI è identico, il linguaggio no.

## ⭐ Caratteristiche

- 💬 **Chat → UI**: "mostra i rotoli disponibili, ordina per giacenza" filtra e ordina una tabella reale.
- 🔄 **Stato condiviso bidirezionale** via protocollo AG-UI (snapshot + delta, SSE).
- 🧩 **Componenti deterministici**: tabella, scheda articolo, grafico vendite.
- 🔒 **Privacy STRICT**: i dati non vengono mai inviati all'LLM (vedi sotto).
- 📊 **Dati veri**: query parametriche read-only su viste SQL Server (anagrafica, giacenze, vendite, listini).

## 🔒 Privacy — l'LLM fa solo da regista

Il punto chiave. In un flusso agente classico l'LLM vede i risultati dei tool → i dati
finirebbero sul cloud del modello. Qui no:

```
Utente: "rotoli disponibili, ordina per giacenza"
   │
   ▼
DeepSeek vede SOLO: messaggio utente + parametri tool      ← nessun dato sensibile
   │  tool: cerca_articoli(famiglia="rotoli", solo_disp=true, sort="esistenza")
   ▼
Backend: esegue la SELECT
   ├──► dati nello stato condiviso ──► STATE_SNAPSHOT ──► Frontend (render)   [dati qui]
   └──► all'LLM torna SOLO: "Mostrati 183 articoli"        ← nessuna riga
```

L'agente gira con `add_session_state_to_context=False`: il contenuto dello stato (le righe,
i nomi clienti, i prezzi) **non entra mai** nel prompt. Verificato sullo stream `/agui`:
il modello riceve solo conteggi, i dati viaggiano verso la UI.

## 🏗️ Architettura

```
┌──────────────────────────────┐      AG-UI / SSE       ┌──────────────────────────────┐
│  Next.js + CopilotKit         │  ◄── stato condiviso ─►│  Agno Agent (FastAPI /agui)    │
│  useCoAgent("my_agent")       │   {view, filtri, sort, │  LLM: DeepSeek (regìa)         │
│  render su state.view:        │    rows, articolo,     │  tools read-only               │
│   table · detail · chart      │    chart…}             │     │                          │
└──────────────────────────────┘                        │     ▼  pyodbc (SELECT)         │
                                                         │  viste AI del gestionale       │
                                                         └──────────────────────────────┘
```

| Livello   | Tecnologia |
|-----------|------------|
| Frontend  | Next.js 14 · CopilotKit 1.61 · `@ag-ui/agno` · Recharts |
| Protocollo| AG-UI (SSE, snapshot + state delta) |
| Backend   | Python · Agno (interfaccia `AGUI` su FastAPI) |
| LLM       | DeepSeek (`deepseek-chat`) — orchestrazione, mai i dati |
| Dati      | SQL Server (pyodbc), viste AI in sola lettura |

## 🧰 Cosa sa fare l'agente

| Tool | Esempio in chat | Componente |
|------|-----------------|------------|
| `cerca_articoli` | *"articoli disponibili della famiglia rotoli, ordina per giacenza"* | Tabella filtrata/ordinata |
| `dettaglio_articolo` | *"scheda dell'articolo ROTO-028"* | Scheda: giacenze + listini + ultime vendite |
| `grafico_vendite` | *"articoli più venduti per valore nel 2025"* | Grafico a barre aggregato |

## 🖼️ Schermate

| Scheda articolo | Grafico vendite |
|---|---|
| ![Scheda](docs/screenshots/scheda.png) | ![Grafico](docs/screenshots/grafico.png) |

## 🚀 Avvio

Prerequisiti: **Node 18+**, **Python 3.13** + [uv](https://docs.astral.sh/uv/),
**ODBC Driver 17 for SQL Server**, una chiave **DeepSeek**.

### 1. Backend (porta 8000)
```bash
cd backend
cp .env.example .env      # compila DB_CONN e DEEPSEEK_API_KEY
uv run uvicorn agent:app --host 127.0.0.1 --port 8000
```

### 2. Frontend (porta 3000)
```bash
cd frontend
npm install
npm run dev
```

Apri **http://localhost:3000** e scrivi nella chat a destra.

## 📁 Struttura

```
backend/
  db.py        # pyodbc + query parametriche sulle viste AI
  tools.py     # tool Agno (STRICT): dati → stato, conteggi → LLM
  agent.py     # Agent DeepSeek + interfaccia AGUI su FastAPI
  .env.example # variabili d'ambiente (DB_CONN, DEEPSEEK_API_KEY)
frontend/
  app/api/copilotkit/route.ts  # runtime CopilotKit → AgnoAgent(/agui)
  app/page.tsx                 # provider + masthead + CopilotSidebar
  components/                  # Canvas, TabellaArticoli, SchedaArticolo, GraficoVendite
  lib/state.ts                 # tipi dello stato condiviso
```

## 🎨 Design

Identità "**distinta di magazzino**": tipografia condensata da segnaletica
(Saira Condensed) + UI/dati IBM Plex (Sans + Mono, cifre tabellari), palette kraft +
inchiostro + arancio segnale. Le tabelle ricalcano una lista di picking stampata.

## ⚠️ Note

- Demo **read-only**: nessuna scrittura sul gestionale.
- Il nome agente (`my_agent`) deve combaciare tra `route.ts`, il provider e `useCoAgent`.
- `.env` non è versionato: contiene credenziali. Usa `.env.example` come modello.

---

<div align="center">
<sub>Demo didattica · Generative UI a stato condiviso · Agno + DeepSeek + CopilotKit</sub>
</div>
