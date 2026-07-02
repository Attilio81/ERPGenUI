"use client";

import { useCoAgent } from "@copilotkit/react-core";
import { AgentState, INITIAL_STATE } from "@/lib/state";

// Navigazione drill-down a UN livello: aprire una scheda salva lo stato corrente
// in `prev`; "Indietro" ci ritorna. Nessuno stack (YAGNI). La chat, cambiando vista
// via STATE_SNAPSHOT, rimpiazza lo stato e azzera `prev` da sola.
// Il fetch è diretto (/api/...), NON passa dall'LLM — apertura deterministica.

// Anti doppio-click: se una richiesta per la stessa risorsa è già in volo, i click
// successivi vengono ignorati (ri-cliccare non accelera, accoda solo query al DB).
const inFlight = new Set<string>();

export function useNav(state: AgentState) {
  const { setState } = useCoAgent<AgentState>({ name: "my_agent", initialState: INITIAL_STATE });

  // snapshot dello stato corrente da mettere in `prev` (un livello: azzera il suo prev)
  const snap = (): Omit<AgentState, "prev"> => {
    const { prev: _drop, ...rest } = state;
    return rest;
  };

  const apriArticolo = async (cod?: string) => {
    const c = (cod || "").trim();
    if (!c) return;
    const key = `articolo:${c}`;
    if (inFlight.has(key)) return; // già in volo: ignora il ri-click
    inFlight.add(key);
    try {
      const r = await fetch(`/api/articolo?cod=${encodeURIComponent(c)}`);
      const art = await r.json();
      if (art?.codice) {
        setState({ ...state, view: "detail", articolo: art, selected_codart: String(art.codice), prev: snap() });
      }
    } catch {
      /* noop */
    } finally {
      inFlight.delete(key);
    }
  };

  // rif = codice conto oppure ragione sociale: scheda_cliente risolve entrambi.
  const apriCliente = async (rif?: string) => {
    const c = (rif || "").trim();
    if (!c) return;
    const key = `cliente:${c}`;
    if (inFlight.has(key)) return; // già in volo: ignora il ri-click
    inFlight.add(key);
    try {
      const r = await fetch(`/api/cliente?cod=${encodeURIComponent(c)}`);
      const cli = await r.json();
      if (cli?.codice) {
        setState({ ...state, view: "cliente", cliente: cli, prev: snap() });
      }
    } catch {
      /* noop */
    } finally {
      inFlight.delete(key);
    }
  };

  const indietro = () => {
    if (state.prev) setState({ ...(state.prev as AgentState), prev: undefined });
  };

  return { apriArticolo, apriCliente, indietro, hasPrev: !!state.prev };
}
