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

export type ArticoloDettaglio = {
  codice: string;
  descrizione: string;
  famiglia: string;
  fornitore: string;
  um: string;
  peso_netto: number;
  peso_lordo: number;
  disponibilita: { esistenza: number; ordinato: number; impegnato: number };
  listini: Listino[];
  ultime_vendite: VenditaRecente[];
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

export type AgentState = {
  view: "table" | "detail" | "chart" | "ordini";
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
};
