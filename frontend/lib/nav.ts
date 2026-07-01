"use client";

import { useCoAgent } from "@copilotkit/react-core";
import { AgentState, INITIAL_STATE } from "@/lib/state";

// Navigazione drill-down a UN livello: aprire una scheda salva lo stato corrente
// in `prev`; "Indietro" ci ritorna. Nessuno stack (YAGNI). La chat, cambiando vista
// via STATE_SNAPSHOT, rimpiazza lo stato e azzera `prev` da sola.
// Il fetch è diretto (/api/...), NON passa dall'LLM — apertura deterministica.
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
    try {
      const r = await fetch(`/api/articolo?cod=${encodeURIComponent(c)}`);
      const art = await r.json();
      if (art?.codice) {
        setState({ ...state, view: "detail", articolo: art, selected_codart: String(art.codice), prev: snap() });
      }
    } catch {
      /* noop */
    }
  };

  // rif = codice conto oppure ragione sociale: scheda_cliente risolve entrambi.
  const apriCliente = async (rif?: string) => {
    const c = (rif || "").trim();
    if (!c) return;
    try {
      const r = await fetch(`/api/cliente?cod=${encodeURIComponent(c)}`);
      const cli = await r.json();
      if (cli?.codice) {
        setState({ ...state, view: "cliente", cliente: cli, prev: snap() });
      }
    } catch {
      /* noop */
    }
  };

  const indietro = () => {
    if (state.prev) setState({ ...(state.prev as AgentState), prev: undefined });
  };

  return { apriArticolo, apriCliente, indietro, hasPrev: !!state.prev };
}
