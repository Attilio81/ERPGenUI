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
![PII](https://img.shields.io/badge/Guardia%20PII-rizzo--pii--0.3B-7c3a9e)
![License](https://img.shields.io/badge/uso-demo-555)

![Distinta articoli](docs/screenshots/tabella.png)

<p>🛡️ <b>Anonimizzazione PII</b> con il modello <a href="https://huggingface.co/rizzoaiacademy/rizzo-pii-0.3B"><b>rizzoaiacademy/rizzo-pii-0.3B</b></a> ·
repo <a href="https://github.com/Rizzo-AI-Academy/rizzo-pii"><b>Rizzo-AI-Academy/rizzo-pii</b></a> ·
di <b>Simone Rizzo — Rizzo AI Academy</b> (MIT)</p>

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

- 💬 **Chat → UI**: *"mostra i rotoli disponibili, ordina per giacenza"* filtra e ordina una tabella reale.
- 🔄 **Stato condiviso bidirezionale** via protocollo AG-UI (snapshot + delta, SSE).
- 🧩 **Componenti deterministici**: tabella articoli, scheda articolo, grafici, ordini, scheda cliente.
- 📊 **Dati veri**: query parametriche *read-only* su viste SQL Server (anagrafica, giacenze, vendite, listini, ordini, scadenze).
- 🔒 **Privacy STRICT**: le righe di dati restano a schermo, **mai nel prompt**; al modello solo conteggi.
- 🛡️ **Guardia PII opzionale**: anonimizzazione locale del testo utente con [rizzo-pii](https://huggingface.co/rizzoaiacademy/rizzo-pii-0.3B) prima del cloud.
- 🎤 **Voce** (Web Speech) e ✏️ **CRUD** deterministico (modifica articolo/cliente fuori dall'LLM).

## 🏗️ Architettura

```
┌─────────────────────────────┐    AG-UI / SSE     ┌──────────────────────────────┐
│  Next.js + CopilotKit        │ ◄─ stato condiviso ►│  Agno Agent (FastAPI /agui)   │
│  useCoAgent("my_agent")      │  {view, filtri,     │  LLM: DeepSeek (regìa)        │
│  render su state.view:       │   sort, rows,       │  tools read-only              │
│  table·detail·chart·         │   articolo, chart…} │     │                         │
│  ordini·clienti·cliente      │                     │     ▼  pyodbc (SELECT)        │
└─────────────────────────────┘                     │  viste AI del gestionale      │
                                                     └──────────────────────────────┘
                          guardia PII (opzionale, PII_GUARD=on)
   testo utente ──► pii-service :5005 /anonymize ──► placeholder al modello, valore vero in locale
```

| Livello    | Tecnologia |
|------------|------------|
| Frontend   | Next.js 14 · CopilotKit 1.61 · `@ag-ui/agno` · Recharts |
| Protocollo | AG-UI (SSE, snapshot + state delta) |
| Backend    | Python · Agno (interfaccia `AGUI` su FastAPI), porta 7000 |
| LLM        | DeepSeek (`deepseek-chat`) — orchestrazione; endpoint sostituibile (UE/locale) |
| Dati       | SQL Server (pyodbc), viste AI in sola lettura |
| Guardia PII | microservizio locale `pii-service` (porta 5005) — modello [rizzo-pii-0.3B](https://huggingface.co/rizzoaiacademy/rizzo-pii-0.3B), opzionale |

## 🧰 Cosa sa fare l'agente

| Tool | Esempio in chat | Componente |
|------|-----------------|------------|
| `cerca_articoli` | *"articoli disponibili della famiglia rotoli, ordina per giacenza"* | Tabella filtrata/ordinata |
| `trova_prezzo` | *"avete pellicola da 30? quanto costa?"* | Tabella + prezzo/giacenza riferiti a voce |
| `dettaglio_articolo` | *"scheda dell'articolo ROTO-028"* | Scheda: giacenze + listini + ultime vendite + ordini |
| `grafico_vendite` | *"articoli più venduti 2025"*, *"andamento per anno"*, *"quote per famiglia"* | Grafico: l'LLM sceglie il tipo (barre/linea/torta) |
| `ordini_clienti` / `ordini_fornitori` | *"ordini clienti da evadere"*, *"ordini ai fornitori per alluminio"* | Tabella righe ordine (residuo, stato) |
| `cerca_clienti` / `scheda_cliente` | *"cerca i clienti di Rivarolo"*, *"scheda del cliente …"* | Tabella clienti / scheda con KPI, scadenze, ordini |

I filtri di `cerca_articoli` sono **sticky**: nei follow-up (*"ordina per esistenza"*,
*"solo disponibili"*) basta dire ciò che cambia. La ricerca testo è tokenizzata e cerca
anche per famiglia (*"rotoli cassa"* → famiglia "Rotoli cassa e bilancia").

## 🔒 Privacy & GDPR — onesto, senza marketing

"Privacy" è spesso venduta più di quanto sia vera. Qui sotto **cosa esce davvero** e cosa no.

```
Utente: "scheda cliente Mario Rossi"
   │
   ▼  [con PII_GUARD=on] anonimizza in locale → "scheda cliente [FULLNAME_1]"
   ▼
LLM vede:  ① il testo digitato   ← guardia OFF: nome in chiaro ⚠ · guardia ON: [FULLNAME_1] 🛡️
           ② lo schema dei tool (nomi colonne)   ← NON è dato personale ✅
           ③ fatti di prodotto (prezzo/giacenza) ← NON personali ✅
   │  tool: scheda_cliente(testo="[FULLNAME_1]") → ripristina → "Mario Rossi" (locale)
   ▼
Backend: esegue la SELECT
   ├──► righe (anagrafica, scadenze, importi) ──► STATE_SNAPSHOT ──► schermo   [restano QUI]
   └──► all'LLM torna SOLO: "Trovato 1 cliente, 4 scadenze aperte"   ← nessuna riga
```

### Cosa NON è un problema (e spesso viene scambiato per tale)
- **Gli schemi del DB non sono dati personali.** "La tabella `ARTICO` ha colonne `ar_codart`,
  `ar_descr`" è un **metadato strutturale**, comune a ogni ERP. Mandarlo al modello **non viola
  il GDPR**: l'Art. 4 protegge dati di persone fisiche, non i nomi delle colonne.
- **Le righe di dati non passano dal modello.** L'agente gira con
  `add_session_state_to_context=False`: anagrafiche, vendite nominative, scadenze, importi
  **non entrano mai** nel prompt — vanno solo a schermo via STATE_SNAPSHOT.
- **I fatti di prodotto** (descrizione, prezzo, giacenza) NON sono personali: `trova_prezzo`
  può restituirli al modello perché li riferisca a voce (*"la pellicola H30 costa 0,77 €"*).

### L'unico canale residuo: il testo che l'utente digita
Se l'utente scrive *"scheda cliente Mario Rossi"*, la stringa "Mario Rossi" (dato personale)
raggiunge il modello. Canale **sottile** (nessun dump di anagrafica) ma reale. E qui sta il
punto GDPR: l'**API nativa DeepSeek** (`api.deepseek.com`) gira su **server in Cina**, senza
DPA né SCC → quel testo finirebbe in un paese terzo senza base legale (già bloccata in Italia
dal Garante). **Non sono gli schemi a essere non-compliant: è la destinazione del testo utente.**

Due modi (combinabili) per chiuderlo:

**A) Anonimizzazione locale — la guardia PII (in questo progetto).**
Un pre-hook anonimizza il testo utente **prima** del modello e ripristina i valori veri in
locale: il cloud vede solo `[FULLNAME_1]`. È **middleware**, non un tool che il modello chiama.
Microservizio [`pii-service/`](pii-service/) basato sul modello
**[`rizzoaiacademy/rizzo-pii-0.3B`](https://huggingface.co/rizzoaiacademy/rizzo-pii-0.3B)**
(mmBERT fine-tuned, italiano, MIT) della **[Rizzo AI Academy](https://github.com/Rizzo-AI-Academy/rizzo-pii)** —
modello + rete regex/checksum (CF/PIVA/IBAN) + gazetteer ORG per i nomi-ditta italiani.
Si attiva con `PII_GUARD=on` nel `backend/.env` (default `off` → demo invariata).

*Eval onesto su questo progetto:*
- Identificativi (CF/PIVA/IBAN/email/telefono) e indirizzi: **affidabili** (checksum-backed).
- Nomi-persona: ok, anche in **MAIUSCOLO** (i nomi del gestionale lo sono → c'è una
  normalizzazione del case prima del modello, che da solo perdeva i nomi tutto-maiuscolo).
- Nomi-ditta: coperti dal gazetteer per i prefissi noti (Macelleria, Ristorante… + SRL/SNC).
- **Residuo dichiarato:** casi misti ditta+persona con abbreviazioni (es. *"ALIM. GERARD
  IVANA …"*) ancora **parziali**. È un **backstop probabilistico**, non zero assoluto.

**B) Endpoint LLM in UE (la base legale).**
Stesso modello DeepSeek servito da **Azure AI Foundry** / **AWS Bedrock** in region europea:
si cambia solo `base_url`+chiave (API OpenAI-compatible), il testo resta in UE (~+5-30 €/mese).
Oppure **LLM locale** (Qwen / DeepSeek-small self-hosted): nessun dato lascia l'azienda
(costo = GPU). In più restano i **documenti** (DPA, ROPA, eventuale DPIA): l'hosting dà la
base legale, la carta la completa.

> In sintesi: STRICT riduce l'esposizione al **minimo input utente**; la **guardia PII** lo
> anonimizza (best-effort, non zero); l'**endpoint UE/locale** chiude il trasferimento.
> Il modello è agganciato via env `PII_MODEL`: quando uscirà una versione con più dati
> (incluso il maiuscolo) — o l'API/MCP ufficiali di rizzo — si aggiorna senza toccare il resto.

## 🚀 Avvio

Prerequisiti: **Node 18+**, **Python 3.11+** (dev: [uv](https://docs.astral.sh/uv/) comodo,
non obbligatorio), **ODBC Driver 17 for SQL Server**, una chiave **DeepSeek**.

### 1. Backend (porta 7000)
```bash
cd backend
cp .env.example .env      # DB_CONN, DEEPSEEK_API_KEY, (opz.) CODDITT, PII_GUARD
uv run uvicorn agent:app --host 127.0.0.1 --port 7000
```

### 2. Frontend (porta 3000)
```bash
cd frontend
npm install
npm run dev
```
Apri **http://localhost:3000** e scrivi nella chat a destra.

### 3. Guardia PII (porta 5005) — opzionale
Solo se vuoi `PII_GUARD=on`. Primo avvio: crea venv, installa le dipendenze e scarica il
modello (~1 GB), poi parte.
```bash
cd pii-service
avvia-pii.bat            # oppure: python service.py
```
Dettagli in [`pii-service/README.md`](pii-service/README.md).

## 🎤 Voce (caso d'uso banco)

Nel masthead il pulsante **🎤 Voce** detta la domanda invece di scriverla
(es. *"avete pellicola da 30? quanto costa?"*) e parte la stessa pipeline.
Usa la **Web Speech API** del browser (Chrome/Edge), zero dipendenze. C'è anche **↺ Nuova**
per azzerare chat e schermata.

> ⚠️ La Web Speech API può inviare l'audio ai server del browser. Per un kiosk GDPR-clean,
> sostituire lo STT con **Whisper locale** (whisper.cpp / faster-whisper) che alimenta la
> stessa `appendMessage`: così né audio né dati lasciano l'azienda.

## ✏️ Scrittura (demo CRUD)

Dalla scheda articolo/cliente, **✎ Modifica** apre un modale per aggiornare alcuni campi
(es. `ARTICO`: descrizione, note, peso). La scrittura è **deterministica e NON passa
dall'LLM**: form → conferma → `PATCH /api/...` con **whitelist colonne** parametrica.
L'AI naviga e legge; l'umano scrive. Multitenant: `CODDITT` nel `.env`.

## 📁 Struttura

```
backend/
  db.py          # pyodbc + query parametriche sulle viste AI
  tools.py       # tool Agno (STRICT): dati → stato, conteggi → LLM
  agent.py       # Agent DeepSeek + interfaccia AGUI + pre-hook PII
  pii_guard.py   # client anonimizza/ripristina (guardia PII)
  .env.example   # DB_CONN, DEEPSEEK_API_KEY, CODDITT, PII_GUARD, PII_URL
frontend/
  app/page.tsx                 # provider + masthead + CopilotSidebar
  app/api/copilotkit/route.ts  # runtime CopilotKit → AgnoAgent(/agui)
  components/                  # Canvas, Tabella/Scheda Articoli, Grafico, Ordini, Clienti
  lib/state.ts                 # tipi dello stato condiviso
pii-service/                   # guardia PII locale (modello rizzo-pii-0.3B)
  service.py                   # FastAPI /anonymize: modello + regex/checksum + gazetteer ORG
  eval_100.py, eval_esteso.py  # eval con scorecard per categoria
```

## 🎨 Design

Identità "**distinta di magazzino**": tipografia condensata da segnaletica (Saira Condensed)
+ UI/dati IBM Plex (Sans + Mono, cifre tabellari), palette kraft + inchiostro + arancio
segnale. Le tabelle ricalcano una lista di picking stampata.

## ⚠️ Note

- Letture **sola lettura**; l'unica scrittura è la demo CRUD (whitelist + conferma).
- Il nome agente (`my_agent`) deve combaciare tra `route.ts`, il provider e `useCoAgent`.
- `.env` non è versionato: contiene credenziali. Usa `.env.example` come modello.

## 🙏 Crediti

La **guardia PII** di questo progetto usa il modello e il lavoro di **Rizzo AI Academy**:

> ### 🦔 rizzo-pii
> Modello: **[`rizzoaiacademy/rizzo-pii-0.3B`](https://huggingface.co/rizzoaiacademy/rizzo-pii-0.3B)**
> — anonimizzazione PII italiana (mmBERT fine-tuned), **MIT**.
> Repository: **[github.com/Rizzo-AI-Academy/rizzo-pii](https://github.com/Rizzo-AI-Academy/rizzo-pii)**
> — di **Simone Rizzo · [Rizzo AI Academy](https://www.rizzoaiacademy.com/)**.
>
> La logica di detection del microservizio ([`pii-service/`](pii-service/)) è derivata da
> `rizzo-pii/src/app/app.py` (MIT). Grazie per averlo reso open source. ⭐

Altri mattoni: **Agno** (AG-UI / agente), **CopilotKit** (frontend), **DeepSeek** (LLM regìa).

---

<div align="center">
<sub>Demo didattica · Generative UI a stato condiviso · Agno + DeepSeek + CopilotKit ·
Guardia PII con rizzo-pii (Rizzo AI Academy, MIT)</sub>
</div>
