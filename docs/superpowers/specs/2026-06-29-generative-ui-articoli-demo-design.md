# Demo Generative UI — Articoli Vittone (Agno + CopilotKit)

**Data:** 2026-06-29
**Autore:** EGM Sistemi
**Stato:** Design approvato (in attesa review spec)

## Obiettivo

Demo di **Generative UI a stato condiviso** (caso d'uso 3 del video "Generative UI"):
una chat pilota un'interfaccia tradizionale e deterministica (tabella articoli,
scheda articolo, grafici) su **dati reali** del database `dbVittone` (NTS Business).

L'LLM **non genera** la UI: decide *quali* componenti mostrare e con *quali dati/filtri*,
scrivendo nello **stato condiviso** AG-UI. I componenti restano deterministici
(design system, coerenza, brand). Read-only: nessuna scrittura sul gestionale.

## Stack

| Livello | Tecnologia |
|---|---|
| Frontend | Next.js + CopilotKit (`useCoAgent` per stato condiviso) |
| Protocollo | AG-UI (SSE, snapshot + state delta) |
| Backend | Python + Agno, interfaccia `AGUI` su FastAPI (`POST /agui`) |
| LLM | DeepSeek (classe Agno `DeepSeek`, API OpenAI-compatibile, `DEEPSEEK_API_KEY`) |
| Dati | 4 viste AI di `dbVittone` via tool MCP dbVittone (solo SELECT) |

## Architettura

```
┌─────────────────────────────┐         AG-UI / SSE          ┌──────────────────────────────┐
│  Next.js + CopilotKit        │  ◄── stato condiviso ──►     │  Agno Agent (FastAPI / AGUI)   │
│  - CopilotSidebar (chat)     │   {filtri, sort, rows,       │  - LLM: DeepSeek               │
│  - TabellaArticoli           │    selectedArticolo, chart}  │  - Tools (read-only)           │
│  - SchedaArticolo            │                              │       │                        │
│  - GraficoVendite (recharts) │                              │       ▼  MCP dbVittone (SELECT)│
└─────────────────────────────┘                              │   4 viste vw_EGM_AI_*          │
                                                              └──────────────────────────────┘
```

## Data layer — viste AI di dbVittone

Tutte filtrate per `codditt = 'VITC'`. Join su codice articolo.

1. **`vw_EGM_AI_anagraficaarticoli`** — `CodArticolo`, `DescrArticolo`, `UnitaMisura`,
   `PesoLordo/Netto`, `CodFamiglia`, `DescrFamiglia`, `CodFornitore`/`DescrFornitore`,
   `CodMarca`/`DescrMarca`, `ScontoMinimo`.
2. **`vw_EGM_AI_disponibilita_articoli`** — `codice_articolo`, `esistenza`,
   `ordinato_fornitori`, `impegnato_clienti`.
3. **`vw_EGM_AI_vendite`** — fatto vendite: `CodiceCliente`/`RagioneSocialeCliente`,
   `CodiceAgente`/`DescrizioneAgente`, `DataMovimento`, `CodiceArticolo`/`DescrizioneArticolo`,
   `Quantita`, `ValoreTotale`, `ValoreProvvigionale`, `Anno`, `Codice Famiglia`/`Famiglia`, `Scenario`.
4. **`vw_EGM_AI_listini`** — `NumeroListino`/`DescrizioneListino`, `CodiceArticolo`,
   `Prezzo`, `PrezzoNetto`, `QuantitaDa`/`QuantitaA`, `CodiceClienteSpecifico`,
   `CodiceAgente`, `DataInizioValidita`/`DataFineValidita`.

Chiave di join: `CodArticolo = codice_articolo = CodiceArticolo`.

## Stato condiviso (AG-UI)

```ts
type SharedState = {
  view: "table" | "detail" | "chart";
  filtri: {
    famiglia?: string;       // DescrFamiglia / CodFamiglia
    fornitore?: string;
    soloDisponibili?: boolean; // esistenza > 0
    testo?: string;          // ricerca su DescrArticolo
  };
  sort: { campo: string; dir: "asc" | "desc" };
  rows: ArticoloRow[];        // anagrafica + disponibilità
  selectedArticolo?: ArticoloDettaglio | null; // + listino + ultime vendite
  chart?: { tipo: "bar" | "line"; dimensione: string; misura: string; dati: Punto[] } | null;
};
```

Mutazione **bidirezionale**: l'agent scrive lo stato via state delta; la UI può a sua volta
aggiornarlo (es. utente cambia sort cliccando) e l'agent ne è consapevole.

## Tools dell'agent (read-only)

Ogni tool esegue una SELECT parametrica sulle viste via MCP dbVittone e scrive nello stato.

| Tool | Input | Effetto sullo stato |
|---|---|---|
| `cerca_articoli` | `famiglia?`, `fornitore?`, `solo_disponibili?`, `testo?`, `ordina_per?` | `view="table"`, popola `rows`, aggiorna `filtri`/`sort` |
| `dettaglio_articolo` | `cod_art` | `view="detail"`, `selectedArticolo` = anagrafica + disponibilità + prezzo listino + ultime N vendite |
| `vendite_aggregate` | `dimensione` (famiglia/agente/cliente/anno), `misura` (valore/quantità), `anno?`, `famiglia?` | `view="chart"`, popola `chart.dati` |

Esempi chat → azione:
- "Mostra gli articoli della famiglia rotoli pellicola disponibili" → `cerca_articoli`
- "Ordina per esistenza decrescente" → `cerca_articoli` (ri-sort) o delta `sort`
- "Dettaglio dell'articolo ALPE-003" → `dettaglio_articolo`
- "Grafico del valore venduto per famiglia nel 2024" → `vendite_aggregate`

## Componenti frontend (deterministici)

- **`TabellaArticoli`** — colonne: codice, descrizione, famiglia, fornitore, UM, esistenza,
  disponibilità; sort cliccabile; binding su `rows`/`sort`/`filtri`.
- **`SchedaArticolo`** — header anagrafica, box disponibilità (esistenza/ordinato/impegnato),
  prezzo listino, mini-storico ultime vendite. Binding su `selectedArticolo`.
- **`GraficoVendite`** — recharts bar/line. Binding su `chart`.
- **`CopilotSidebar`** — chat AG-UI.

Il render è guidato da `state.view`; i dati arrivano sempre dallo stato condiviso.

## Struttura progetto

```
C:\Progetti Pilota\UI\
  backend/                 # Python / Agno
    agent.py               # Agent DeepSeek + AGUI interface + AgentOS.serve
    tools.py               # cerca_articoli / dettaglio_articolo / vendite_aggregate (via MCP)
    queries.py             # SQL parametrico sulle 4 viste
    pyproject.toml / requirements.txt
    .env.example           # DEEPSEEK_API_KEY, conn dbVittone / MCP
  frontend/                # Next.js + CopilotKit
    app/                   # pagina demo + CopilotKit provider
    components/            # TabellaArticoli, SchedaArticolo, GraficoVendite
    lib/state.ts           # tipi stato condiviso
  docs/superpowers/specs/  # questo documento
```

## Dipendenze / rischi da risolvere in fase di plan

1. **Accesso MCP dbVittone dal processo Agno.** L'MCP dbVittone è configurato in Claude Code.
   Per usarlo da Agno serve il comando di avvio del server MCP (`MCPTools` stdio) **oppure**
   fallback a connessione diretta SQL Server (pyodbc) con la stessa connection string.
   → Decisione preferita: MCP; fallback pyodbc documentato.
2. **`DEEPSEEK_API_KEY`** da procurare e mettere in `.env`.
3. **Versione CopilotKit + AG-UI** compatibile con interfaccia `AGUI` di Agno (verificare in fase plan via docs).
4. **Performance viste** su grandi volumi vendite → applicare sempre filtro `Anno`/`TOP` nei tool.
5. **Cartella progetto non è un repo git** → `git init` in fase di setup per versionare.

## Fuori scope (YAGNI)

- Scrittura/modifica gestionale.
- Multi-ditta (solo VITC).
- Autenticazione/multi-utente.
- Generazione UI puramente LLM (caso "Far West" del video) — esplicitamente evitato.

## Criteri di successo

- Chat in linguaggio naturale filtra/ordina la tabella articoli su dati reali Vittone.
- "Dettaglio articolo X" apre scheda con disponibilità + prezzo + vendite reali.
- "Grafico valore per famiglia 2024" disegna un grafico coerente.
- Lo stato è realmente condiviso: modifiche UI visibili all'agent e viceversa.
