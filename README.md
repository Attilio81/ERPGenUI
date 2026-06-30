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
- 🔒 **Privacy STRICT**: le righe di dati restano a schermo, non nel prompt. L'unico testo libero che raggiunge l'LLM è ciò che l'utente digita (vedi sotto, onestamente).
- 📊 **Dati veri**: query parametriche read-only su viste SQL Server (anagrafica, giacenze, vendite, listini).

## 🔒 Privacy & GDPR — onesto, senza marketing

In un flusso agente classico l'LLM vede i risultati dei tool → i dati finirebbero sul
cloud del modello. Qui no — ma vale la pena essere precisi su **cosa esce davvero** e
**cosa no**, perché "privacy" è spesso venduta più di quanto sia vera.

```
Utente: "scheda cliente Mario Rossi"
   │
   ▼
LLM vede:  ① il testo digitato dall'utente   ← QUI può finire un nome/P.IVA  ⚠
           ② lo schema dei tool (nomi colonne)  ← NON è dato personale  ✅
           ③ fatti di prodotto (prezzo/giacenza)  ← NON personali  ✅
   │  tool: scheda_cliente(testo="Mario Rossi")
   ▼
Backend: esegue la SELECT
   ├──► righe (anagrafica, scadenze, importi) ──► STATE_SNAPSHOT ──► schermo   [restano QUI]
   └──► all'LLM torna SOLO: "Trovato 1 cliente, 4 scadenze aperte"   ← nessuna riga
```

### Cosa NON è un problema (e spesso viene scambiato per tale)
- **Gli schemi del DB non sono dati personali.** "La tabella `ARTICO` ha colonne
  `ar_codart`, `ar_descr`" è un **metadato strutturale** — comune a ogni ERP del mondo.
  Mandarlo al modello **non viola il GDPR**. Il GDPR protegge dati di persone fisiche
  (Art. 4), non i nomi delle colonne.
- **Le righe di dati non passano dal modello.** L'agente gira con
  `add_session_state_to_context=False`: il contenuto dello stato (anagrafiche, vendite
  nominative, scadenze, importi) **non entra mai** nel prompt. Va solo a schermo via
  STATE_SNAPSHOT. Verificato sullo stream `/agui`.
- **I fatti di prodotto** (descrizione, prezzo di listino, giacenza) NON sono personali:
  `trova_prezzo` può restituirli all'LLM perché li riferisca a voce — utile al banco
  ("la pellicola H30 costa 0,77 €, ne hai 953").

### L'unico canale residuo reale
**Il testo libero che l'utente digita.** Se scrive *"scheda cliente Mario Rossi"*,
la stringa "Mario Rossi" (un dato personale) raggiunge il modello. È un canale **sottile**
— non c'è un dump di anagrafica — ma esiste.

E qui sta il punto GDPR vero: l'**API nativa DeepSeek** (`api.deepseek.com`) gira su
**server in Cina**, senza DPA né Standard Contractual Clauses → quel poco di testo
personale finirebbe in un paese terzo senza base legale (già bloccata in Italia dal
Garante). **Non sono gli schemi a essere non-compliant: è la destinazione del testo utente.**

### Come si chiude (senza riscrivere l'app)
- **Endpoint UE (consigliato):** stesso modello DeepSeek servito da **Azure AI Foundry**
  o **AWS Bedrock** in region europea. Si cambia solo `base_url`+chiave (API
  OpenAI-compatible). Anche "Mario Rossi" resta in UE. Costo ~+5-30 €/mese.
- **LLM locale (zero terze parti):** pesi aperti (Qwen / DeepSeek-small) self-hosted →
  nessun dato lascia l'azienda. Costo = GPU (~800 € una-tantum).
- Restano comunque da fare i **documenti** (DPA, ROPA, eventuale DPIA): l'hosting dà la
  base legale, la carta la completa.

> In sintesi: l'architettura STRICT riduce l'esposizione al **minimo input utente**, non
> a zero. Per un deploy GDPR-clean, spostare l'endpoint LLM in UE (o in locale).

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
| LLM       | DeepSeek (`deepseek-chat`) — orchestrazione + testo utente; endpoint sostituibile (UE/locale) |
| Dati      | SQL Server (pyodbc), viste AI in sola lettura |

## 🧰 Cosa sa fare l'agente

| Tool | Esempio in chat | Componente |
|------|-----------------|------------|
| `cerca_articoli` | *"articoli disponibili della famiglia rotoli, ordina per giacenza"* | Tabella filtrata/ordinata |
| `trova_prezzo` | *"avete pellicola da 30? quanto costa?"* | Tabella + prezzo/giacenza riferiti a voce |
| `dettaglio_articolo` | *"scheda dell'articolo ROTO-028"* | Scheda: giacenze + listini + ultime vendite + ultimi ordini clienti/fornitori |
| `grafico_vendite` | *"articoli più venduti 2025"*, *"andamento per anno"*, *"quote per famiglia"* | Grafico: l'LLM sceglie il tipo (barre / linea / torta) dalla domanda |
| `ordini_clienti` | *"ordini clienti da evadere"* | Tabella righe ordine (residuo, stato) |
| `ordini_fornitori` | *"ordini ai fornitori per alluminio"* | Tabella righe ordine / merce in arrivo |

I filtri di `cerca_articoli` sono **sticky**: nei follow-up ("ordina per esistenza",
"solo disponibili") basta dire ciò che cambia, gli altri filtri restano. La ricerca testo
è tokenizzata e cerca anche per famiglia ("rotoli cassa" → famiglia "Rotoli cassa e bilancia").

## 🖼️ Schermate

| Scheda articolo | Grafico vendite |
|---|---|
| ![Scheda](docs/screenshots/scheda.png) | ![Grafico](docs/screenshots/grafico.png) |

## 🚀 Avvio

Prerequisiti: **Node 18+**, **Python 3.13** + [uv](https://docs.astral.sh/uv/),
**ODBC Driver 17 for SQL Server**, una chiave **DeepSeek**.

### 1. Backend (porta 7000)
```bash
cd backend
cp .env.example .env      # compila DB_CONN e DEEPSEEK_API_KEY
uv run uvicorn agent:app --host 127.0.0.1 --port 7000
```

### 2. Frontend (porta 3000)
```bash
cd frontend
npm install
npm run dev
```

Apri **http://localhost:3000** e scrivi nella chat a destra.

## 🎤 Voce (caso d'uso banco)

Nel masthead c'è il pulsante **🎤 Voce**: detti la domanda invece di scriverla
(es. *"avete pellicola da 30? quanto costa?"*) e parte la stessa pipeline.
Usa la **Web Speech API** del browser (Chrome/Edge) — zero dipendenze.

> ⚠️ La Web Speech API può inviare l'audio ai server del browser. Per un kiosk
> GDPR-clean, sostituire lo STT con **Whisper locale** (whisper.cpp / faster-whisper)
> che alimenta la stessa `appendMessage`: così né audio né dati lasciano l'azienda.

C'è anche **↺ Nuova** per azzerare chat e schermata.

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

## ✏️ Scrittura (demo CRUD)

Dalla scheda articolo, il pulsante **✎ Modifica** apre un modale per aggiornare alcuni
campi di `ARTICO` (descrizione, note, peso netto). La scrittura è **deterministica e NON
passa dall'LLM**: form → conferma → endpoint `PATCH /api/articolo` con **whitelist colonne**
parametrica. L'AI naviga e legge; l'umano scrive. Multitenant: `CODDITT` nel `.env`.

## ⚠️ Note

- Letture **sola lettura**; l'unica scrittura è la demo CRUD sopra (whitelist + conferma).
- Il nome agente (`my_agent`) deve combaciare tra `route.ts`, il provider e `useCoAgent`.
- `.env` non è versionato: contiene credenziali. Usa `.env.example` come modello.

---

<div align="center">
<sub>Demo didattica · Generative UI a stato condiviso · Agno + DeepSeek + CopilotKit</sub>
</div>
