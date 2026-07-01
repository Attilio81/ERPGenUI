// Tipi dello stato condiviso AG-UI — devono combaciare con backend/tools.py INITIAL_STATE.

export type Filtri = {
  famiglia?: string | null;
  fornitore?: string | null;
  solo_disponibili?: boolean;
  testo?: string | null;
};

export type Sort = { campo: string; dir: "asc" | "desc" };

export type ArticoloRow = {
  codice: string;
  descrizione: string;
  famiglia: string;
  fornitore: string;
  um: string;
  esistenza: number;
  impegnato: number;
  ordinato: number;
  disponibile: number;
};

export type Listino = {
  listino: number;
  descr_listino: string;
  prezzo: number;
  prezzo_netto: number;
  um: string;
};

export type VenditaRecente = {
  data: string;
  cliente: string;
  quantita: number;
  valore: number;
};

export type OrdineMini = {
  data: string;
  conto: string;
  quantita: number;
  residuo: number;
  stato: "evaso" | "da evadere";
};

export type ArticoloDettaglio = {
  codice: string;
  descrizione: string;
  famiglia: string;
  fornitore: string;
  um: string;
  peso_netto: number;
  peso_lordo: number;
  note?: string;
  disponibilita: { esistenza: number; ordinato: number; impegnato: number };
  listini: Listino[];
  ultime_vendite: VenditaRecente[];
  ordini_clienti?: OrdineMini[];
  ordini_fornitori?: OrdineMini[];
};

export type PuntoGrafico = { etichetta: string; valore: number };

export type OrdineRow = {
  anno: number;
  numero: number;
  data: string;
  conto: string;
  citta: string;
  codice: string;
  descrizione: string;
  um: string;
  quantita: number;
  evasa: number;
  residuo: number;
  stato: "evaso" | "da evadere";
  consegna: string;
};

export type ClienteRow = {
  codice: string;
  ragione_sociale: string;
  citta: string;
  provincia: string;
  piva: string;
  zona: string;
  stato: string;
  bloccato: string;
};

export type ScadenzaMini = {
  scadenza: string;
  documento: number;
  residuo: number;
  insoluto: string;
  stato: "scaduto" | "insoluto" | "a scadere";
};

export type ClienteDettaglio = {
  codice: string;
  ragione_sociale: string;
  indirizzo: string;
  cap: string;
  citta: string;
  provincia: string;
  telefono?: string;
  cellulare?: string;
  email?: string;
  piva: string;
  cf: string;
  agente: number;
  zona: string;
  stato: string;
  bloccato: string;
  orario?: string;
  giorno_chiusura?: string;
  ultimo_doc?: string;
  note?: string;
  kpi: { esposizione: number; scaduto: number; insoluti: number; n_scadenze: number };
  scadenze: ScadenzaMini[];
  ultimi_ordini: { data: string; articolo: string; quantita: number; residuo: number; stato: string }[];
  top_articoli: { articolo: string; valore: number }[];
};

export type AgentState = {
  view: "table" | "detail" | "chart" | "ordini" | "clienti" | "cliente";
  filtri: Filtri;
  sort: Sort;
  count: number;
  selected_codart: string | null;
  chart_spec: Record<string, unknown> | null;
  rows: ArticoloRow[];
  articolo: ArticoloDettaglio | null;
  chart_titolo: string;
  chart_dati: PuntoGrafico[];
  rows_ordini: OrdineRow[];
  ordini_tipo: "clienti" | "fornitori";
  ordini_titolo: string;
  rows_clienti: ClienteRow[];
  clienti_filtro: string;
  cliente: ClienteDettaglio | null;
  pii_map?: Record<string, string>;
};

export const INITIAL_STATE: AgentState = {
  view: "table",
  filtri: {},
  sort: { campo: "descrizione", dir: "asc" },
  count: 0,
  selected_codart: null,
  chart_spec: null,
  rows: [],
  articolo: null,
  chart_titolo: "",
  chart_dati: [],
  rows_ordini: [],
  ordini_tipo: "clienti",
  ordini_titolo: "",
  rows_clienti: [],
  clienti_filtro: "",
  cliente: null,
};
