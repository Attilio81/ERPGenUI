<div align="center">

# ERP Generative UI

**Una chat che pilota un'interfaccia gestionale deterministica — su dati reali.**

Generative UI a *stato condiviso*: l'LLM non disegna la UI, ne **orchestra** i componenti.
Tabella, scheda articolo/cliente e grafici tradizionali, guidati dal linguaggio naturale.

![Next.js](https://img.shields.io/badge/Next.js-14-000000?logo=next.js)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Agno](https://img.shields.io/badge/Agno-AG--UI-DA481B)
![CopilotKit](https://img.shields.io/badge/CopilotKit-1.61-6963FF)
![LLM](https://img.shields.io/badge/LLM-Mistral%C2%B7DeepSeek%C2%B7local-4D6BFE)
![GDPR](https://img.shields.io/badge/GDPR-Mistral%20UE-1F6B3B)
![PII](https://img.shields.io/badge/Guardia%20PII-rizzo--pii--0.3B-7c3a9e)
![Responsive](https://img.shields.io/badge/UI-responsive-1F6B3B)
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

## ⚙️ Come funziona (in 4 passi)

L'LLM **non sceglie un componente direttamente**: sceglie una **funzione**, ed è la funzione a
decidere la vista. La catena:

1. **Frase** → l'utente scrive (o detta) in chat (*"articoli più venduti nel 2025"*).
2. **Funzione** → l'LLM abbina la frase alla **funzione** (tool) che calza, per **nome +
   descrizione + istruzioni di regia**, ed estrae i parametri (*"nel 2025"* → `anno=2025`).
   Le funzioni sono un **elenco chiuso** (`cerca_articoli`, `scheda_cliente`, `grafico_vendite`…):
   l'AI può solo sceglierne una, non inventarne — per questo è affidabile.
3. **Vista** → la funzione gira **sul backend**, interroga il DB e scrive nello **stato condiviso**
   il campo `view` (`table` / `detail` / `chart` / `ordini` / `clienti` / `cliente`) + i dati.
4. **Componente** → CopilotKit sincronizza lo stato allo schermo (AG-UI/SSE) e il **Canvas** mostra
   il **componente deterministico** corrispondente a `view`.

```
frase → [LLM sceglie la FUNZIONE] → la funzione imposta la VISTA → il Canvas mostra il COMPONENTE
              (per nome+descrizione)        (nello stato condiviso)         (elenco chiuso, nostro)
```

> Privacy: i **dati** vanno solo nello stato → a schermo; all'LLM torna **solo un conteggio/conferma**
> (*"trovati 183 articoli"*), mai le righe. L'LLM decide *cosa* mostrare, non *vede* i dati.

## ⭐ Caratteristiche

- 💬 **Chat → UI**: *"mostra i rotoli disponibili, ordina per giacenza"* filtra e ordina una tabella reale.
- 🔄 **Stato condiviso bidirezionale** via protocollo AG-UI (snapshot + delta, SSE).
- 🧩 **Componenti deterministici**: tabella articoli/clienti/ordini, scheda articolo, scheda cliente, grafici.
- 🖱️ **Drill-down navigabile**: ovunque compaia un articolo o un cliente lo si **clicca** per aprirne
  la scheda (fetch diretto, non passa dall'LLM); un tasto **← Indietro** torna alla vista precedente.
- 📊 **Dati veri**: query parametriche *read-only* su viste SQL Server (anagrafica, giacenze, vendite, listini, ordini, scadenze).
- 🔒 **Privacy STRICT**: le righe di dati restano a schermo, **mai nel prompt**; al modello solo conteggi.
- 🇪🇺 **LLM a scelta** via `AI_PROVIDER`: **Mistral** (La Plateforme, UE → GDPR-compliant · consigliato), **DeepSeek** (dev/costo), **local** (self-host). Cambio da `.env`, codice invariato.
- 🛡️ **Guardia PII opzionale**: anonimizzazione locale del testo utente con [rizzo-pii](https://huggingface.co/rizzoaiacademy/rizzo-pii-0.3B) prima del cloud.
- 🎤 **Voce** (Web Speech) e ✏️ **CRUD** deterministico (modifica articolo/cliente fuori dall'LLM).
- 📱 **Responsive**: layout ottimizzato per telefono e tablet — le tabelle diventano card, la chat va a schermo intero (caso d'uso "banco").
- 🧪 **DB di test usa-e-getta** (SQL Server in Docker + dati sintetici): gira dopo un `git clone` senza il gestionale del cliente.

## 🏗️ Architettura

![Architettura: Next.js + CopilotKit ⇄ (AG-UI/SSE, stato condiviso) ⇄ Agno Agent FastAPI, pyodbc su viste SQL Server; click articolo/cliente via GET /api diretto senza LLM](docs/diagrams/architettura.png)

| Livello    | Tecnologia |
|------------|------------|
| Frontend   | Next.js 14 · CopilotKit 1.61 · `@ag-ui/agno` · Recharts |
| Protocollo | AG-UI (SSE, snapshot + state delta) |
| Backend    | Python · Agno (interfaccia `AGUI` su FastAPI), porta 7000 · sessioni in SQLite (`session.db`) |
| LLM        | Pluggable via `AI_PROVIDER` (`model_factory.py`): **Mistral** UE · **DeepSeek** · **local**. Solo orchestrazione |
| Dati       | SQL Server (pyodbc), viste AI in sola lettura · connessione **per-thread** |
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
*"solo disponibili"*) basta dire ciò che cambia; *"mostra tutti gli articoli"* fa `reset`.
La ricerca testo è tokenizzata e cerca anche per famiglia. L'agente ha in contesto **la data
odierna e gli anni con dati** (per non allucinare periodi inesistenti), tiene gli **ultimi 5
scambi** di storia per i follow-up e sui rate-limit (429) **ritenta** con backoff.

## 🖱️ Navigazione, drill-down e UI

- **Tutto è navigabile.** In tabella articoli/clienti la riga apre la scheda; in tabella ordini
  il **codice articolo** e il **conto cliente** sono cliccabili; nelle schede lo sono i clienti
  (ultime vendite, ordini) e gli articoli (ultimi ordini, top acquistati).
- **Come.** Il click fa un `fetch` diretto a `GET /api/articolo|cliente` (**non** passa dall'LLM:
  apertura deterministica) e imposta la vista. Hook unico [`lib/nav.ts`](frontend/lib/nav.ts).
- **← Indietro** a **un livello**: aprire una scheda salva lo stato precedente in `prev`; il tasto
  ci ritorna. Niente stack (YAGNI). Quando la **chat** cambia vista (nuovo STATE_SNAPSHOT) `prev`
  si azzera da solo, così click e chat restano coerenti.
- **Benvenuto**: al primo apri (nessun dato, nessun filtro) il Canvas mostra un pannello "come
  funziona" con esempi cliccabili, invece di una tabella vuota.
- **F5 = conversazione nuova**: ogni caricamento pagina genera un `threadId` nuovo → chat pulita,
  nessuna vecchia conversazione ripescata da `session.db`. Il pulsante **↺ Nuova** fa lo stesso.
- **Responsive**: sotto 900px la chat non è più affiancata (canvas a tutto schermo, chat a
  schermo intero col toggle di CopilotKit); sotto 640px le tabelle diventano **card impilate** e
  i modali diventano bottom-sheet.

## 🔒 Privacy & GDPR — onesto, senza marketing

"Privacy" è spesso venduta più di quanto sia vera. Qui sotto **cosa esce davvero** e cosa no.

![Privacy STRICT: il testo utente viene anonimizzato in locale (PII_GUARD); l'LLM vede solo testo mascherato, schema dei tool e fatti di prodotto (non personali); le righe di dati vanno solo a schermo via STATE_SNAPSHOT, all'LLM torna solo un conteggio](docs/diagrams/privacy.png)

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

### La via consigliata: provider LLM in UE (Mistral)

La compliance vera **non** viene dall'app: viene dalla **scelta del provider**. Basta cambiare
`AI_PROVIDER` da `deepseek` a **`mistral`** ([`model_factory.py`](backend/model_factory.py),
una riga di `.env`) e il modello gira su **Mistral La Plateforme** (Parigi):

- **Azienda UE** → **nessun trasferimento in paese terzo**: il problema Art. 44 non si pone.
- **DPA diretto**, **dati in UE** di default, opzione **Zero Data Retention** (piano Scale).
- Stesso ruolo (regìa della UI), API OpenAI-compatible, function-calling nativo.

Restano — lato tuo — i **documenti**: DPA firmato con Mistral, voce nel ROPA, eventuale DPIA.
Quella è la base legale; il codice è già pronto. Alternativa "zero terzi": `AI_PROVIDER=local`
(Qwen / Mistral self-hosted, costo = GPU).

> **Routing misurato** ([`backend/eval_routing.py`](backend/eval_routing.py)): **DeepSeek 28/29 = 96%**
> in batch. **Mistral routa correttamente a ritmo reale** (verificato live nel frontend, 5/5 viste);
> il batch fitto è limitato solo dal **TPM del tier free** (i 429 tornano vuoti, l'`exponential_backoff`
> ritenta), non dalla capacità. Si sceglie **col numero**, non a fede.

### Difesa in più (opzionale): guardia PII locale

Con Mistral **non è necessaria** (la compliance c'è già). Resta come *data minimization*: se vuoi
non far uscire i nomi **nemmeno** verso il processore UE. Il giro è completo:

```
testo utente → [pre-hook] anonimizza → LLM (vede [FULLNAME_1]) → risposta
   ├─ tool: ripristina prima della SELECT (query col nome vero)
   └─ chat: PiiUnmask ri-sostituisce lato client (l'utente vede il nome vero, il cloud no)
```

Il cloud vede solo `[FULLNAME_1]`; l'utente, sul suo schermo, vede il nome reale. È **fail-closed**:
se il servizio PII non risponde, la richiesta viene bloccata (non si "sfugge" al mascheramento).
Microservizio [`pii-service/`](pii-service/) sul modello
**[`rizzoaiacademy/rizzo-pii-0.3B`](https://huggingface.co/rizzoaiacademy/rizzo-pii-0.3B)**
(mmBERT, italiano, MIT — [Rizzo AI Academy](https://github.com/Rizzo-AI-Academy/rizzo-pii)):
modello + rete regex/checksum (CF/PIVA/IBAN) + gazetteer ORG.
Si attiva con `PII_GUARD=on` (default `off`).

*Eval onesto:* identificativi (CF/PIVA/IBAN/email/telefono), indirizzi e nomi-persona (anche
MAIUSCOLO, via normalizzazione del case) **affidabili**; nomi-ditta coperti dal gazetteer;
**residuo dichiarato** sui casi misti ditta+persona (es. *"ALIM. GERARD IVANA …"*). È un
**backstop probabilistico**, non zero — per questo la base legale resta il provider UE.

> In sintesi: **compliance = provider UE (Mistral + DPA)**. STRICT tiene i dati fuori dal
> prompt; la guardia PII è cintura extra opzionale. Cambi modello dal `.env`, il resto non si tocca.

## 🚀 Avvio

Prerequisiti: **Node 18+**, **Python 3.11+** (dev: [uv](https://docs.astral.sh/uv/) comodo,
non obbligatorio), **ODBC Driver 17 for SQL Server**, e una chiave LLM (o Ollama per `local`).

> **Non hai il gestionale del cliente?** Usa il **DB di test usa-e-getta** (SQL Server in
> Docker + dati sintetici) in [`test-db/`](test-db/): `cd test-db && docker compose up`, poi
> `copy backend\.env.test backend\.env`. Include i codici delle demo (ROTO-028, BIPP-049, …).
> L'LLM resta a carico tuo (chiave cloud o `AI_PROVIDER=local` con Ollama). Vedi
> [`test-db/README.md`](test-db/README.md).

### 1. Backend (porta 7000)
```bash
cd backend
cp .env.example .env      # DB_CONN, AI_PROVIDER + chiave, (opz.) CODDITT, PII_GUARD
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

### Avvio "one-click" in LAN (Windows)
Sul server: `avvia-lan.bat` (setup + avvio backend :7000 e frontend :3000 esposto in LAN).
Dopo aver aggiornato i sorgenti: `aggiorna.bat` (rinfresca dipendenze e **forza la rebuild**),
poi ri-lancia `avvia-lan.bat`.

## 🎤 Voce (caso d'uso banco)

Nell'header della chat il pulsante **🎤 Voce** detta la domanda invece di scriverla
(es. *"avete pellicola da 30? quanto costa?"*) e parte la stessa pipeline.
Usa la **Web Speech API** del browser (Chrome/Edge), zero dipendenze. C'è anche **↺ Nuova**
per azzerare chat e schermata, e **? Guida** con gli esempi cliccabili.

> ⚠️ La Web Speech API può inviare l'audio ai server del browser. Per un kiosk GDPR-clean,
> sostituire lo STT con **Whisper locale** (whisper.cpp / faster-whisper) che alimenta la
> stessa `appendMessage`: così né audio né dati lasciano l'azienda.

## ✏️ Scrittura (demo CRUD)

Dalla scheda articolo/cliente, **✎ Modifica** apre un modale per aggiornare alcuni campi
(es. `ARTICO`: descrizione, note, peso; `ANAGRA`: telefono, cellulare, email, note). La scrittura
è **deterministica e NON passa dall'LLM**: form → conferma → `PATCH /api/...` con **whitelist
colonne** parametrica. L'AI naviga e legge; l'umano scrive. Multitenant: `CODDITT` nel `.env`.

## 📁 Struttura

```
backend/
  db.py            # pyodbc + query parametriche sulle viste AI (connessione per-thread)
  tools.py         # tool Agno (STRICT): dati → stato, conteggi → LLM
  agent.py         # Agent + interfaccia AGUI + endpoint GET/PATCH /api/... + hook PII + backoff
  model_factory.py # provider LLM da AI_PROVIDER (mistral / deepseek / local)
  pii_guard.py     # client anonimizza/ripristina (guardia PII)
  eval_routing.py, eval_contesto.py  # eval del tool-routing / del contesto
  .env.example     # DB_CONN, AI_PROVIDER, MISTRAL/DEEPSEEK key, CODDITT, PII_GUARD
  .env.test        # config pronta per il DB di test (test-db/)
frontend/
  app/page.tsx                 # provider + masthead + Canvas + CopilotSidebar + threadId/responsive
  app/layout.tsx               # metadata + viewport (responsive)
  app/globals.css              # design system "distinta" + breakpoint mobile/tablet
  app/api/{articolo,cliente,copilotkit,info}/route.ts   # proxy verso il backend
  components/                  # Canvas, Benvenuto, Tabelle (Articoli/Clienti/Ordini),
                               # Schede (Articolo/Cliente), GraficoVendite, Edit*, ChatHeader,
                               # MicButton, ResetButton, HelpModal, PiiUnmask
  lib/state.ts                 # tipi dello stato condiviso (+ `prev` per il drill-down)
  lib/nav.ts                   # hook navigazione: apri scheda articolo/cliente + Indietro
  lib/format.ts                # formattazione numeri/date/euro
pii-service/                   # guardia PII locale (modello rizzo-pii-0.3B)
  service.py                   # FastAPI /anonymize: modello + regex/checksum + gazetteer ORG
  eval_100.py, eval_esteso.py  # eval con scorecard per categoria
test-db/                       # DB di test usa-e-getta (senza il gestionale del cliente)
  docker-compose.yml           # SQL Server 2022 + seed one-shot
  seed.sql                     # viste AI (come tabelle) + artico/anagra, dati sintetici
  smoke_test.py                # esercita backend/db.py contro il container
```

## 🎨 Design

Identità "**distinta di magazzino**": tipografia condensata da segnaletica (Saira Condensed)
+ UI/dati IBM Plex (Sans + Mono, cifre tabellari), palette kraft + inchiostro + arancio
segnale. Le tabelle ricalcano una lista di picking stampata; su telefono diventano card.

## ⚠️ Note

- Letture **sola lettura**; l'unica scrittura è la demo CRUD (whitelist + conferma).
- Il nome agente (`my_agent`) deve combaciare tra `route.ts`, il provider e `useCoAgent`.
- `.env` non è versionato: contiene credenziali. Usa `.env.example` (o `.env.test`) come modello.
- Deploy in LAN = **copia dei sorgenti** + `aggiorna.bat` (rebuild) + riavvio backend
  (`db.py` gira senza reload).

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

Altri mattoni: **Agno** (AG-UI / agente), **CopilotKit** (frontend), **Recharts** (grafici).

---

<div align="center">
<sub>Demo didattica · Generative UI a stato condiviso · Agno + CopilotKit ·
LLM Mistral·DeepSeek·local · Guardia PII con rizzo-pii (Rizzo AI Academy, MIT)</sub>
</div>
