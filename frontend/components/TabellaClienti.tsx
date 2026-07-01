"use client";

import { useCoAgent } from "@copilotkit/react-core";
import { AgentState, INITIAL_STATE } from "@/lib/state";

export function TabellaClienti({ state }: { state: AgentState }) {
  const rows = state.rows_clienti ?? [];
  const filtro = state.clienti_filtro;
  const { setState } = useCoAgent<AgentState>({ name: "my_agent", initialState: INITIAL_STATE });

  // click su riga -> apre la scheda del cliente (fetch diretto, NON passa dall'LLM)
  const apriCliente = async (cod: string) => {
    try {
      const r = await fetch(`/api/cliente?cod=${encodeURIComponent(cod)}`);
      const cli = await r.json();
      if (cli?.codice) setState({ ...state, view: "cliente", cliente: cli });
    } catch {
      /* noop */
    }
  };

  return (
    <div className="panel">
      <div className="panel-head">
        <div>
          <h2>Clienti</h2>
          <p className="muted">{rows.length} risultati</p>
        </div>
        {filtro ? <span className="chip">RICERCA: {filtro}</span> : <span className="muted">tutti</span>}
      </div>

      {rows.length ? (
        <div className="table-wrap">
          <table className="grid">
            <thead>
              <tr>
                <th>Codice</th>
                <th>Ragione sociale</th>
                <th>Città</th>
                <th>Pr.</th>
                <th>P.IVA</th>
                <th>Zona</th>
                <th>Stato</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((c, i) => (
                <tr key={`${c.codice}-${i}`} className="clickable" onClick={() => apriCliente(c.codice)} title="Apri scheda cliente">
                  <td className="mono" data-label="Codice">{c.codice}</td>
                  <td data-label="Ragione sociale">{c.ragione_sociale}</td>
                  <td className="muted small" data-label="Città">{c.citta}</td>
                  <td className="muted small" data-label="Pr.">{c.provincia}</td>
                  <td className="mono small" data-label="P.IVA">{c.piva}</td>
                  <td className="muted small" data-label="Zona">{c.zona}</td>
                  <td data-label="Stato">
                    <span className={"stato-pill " + (c.bloccato === "S" ? "open" : "done")}>
                      {c.bloccato === "S" ? "bloccato" : "attivo"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty">Nessun cliente. Chiedi all'assistente di cercare un cliente.</div>
      )}
    </div>
  );
}
