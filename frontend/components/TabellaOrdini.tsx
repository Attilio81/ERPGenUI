"use client";

import { AgentState } from "@/lib/state";
import { num2, dataIt } from "@/lib/format";

export function TabellaOrdini({ state }: { state: AgentState }) {
  const rows = state.rows_ordini ?? [];
  const tipo = state.ordini_tipo ?? "clienti";
  const intestColonna = tipo === "fornitori" ? "Fornitore" : "Cliente";
  const daEvadere = rows.filter((r) => r.stato === "da evadere").length;

  return (
    <div className="panel">
      <div className="panel-head">
        <div>
          <h2>{state.ordini_titolo || "Ordini"}</h2>
          <p className="muted">
            {rows.length} righe · {daEvadere} da evadere
          </p>
        </div>
        <span className="chip">{tipo === "fornitori" ? "FORNITORI" : "CLIENTI"}</span>
      </div>

      {rows.length ? (
        <div className="table-wrap">
          <table className="grid">
            <thead>
              <tr>
                <th>Ordine</th>
                <th>Data</th>
                <th>{intestColonna}</th>
                <th>Articolo</th>
                <th className="r">Q.tà</th>
                <th className="r">Evasa</th>
                <th className="r">Residuo</th>
                <th>Stato</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i}>
                  <td className="mono" data-label="Ordine">{r.anno}/{r.numero}</td>
                  <td className="mono" data-label="Data">{dataIt(r.data)}</td>
                  <td className="muted small" data-label={intestColonna}>{r.conto}{r.citta ? ` · ${r.citta}` : ""}</td>
                  <td data-label="Articolo">
                    <span className="mono">{r.codice}</span>
                    <div className="muted small">{r.descrizione}</div>
                  </td>
                  <td className="r" data-label="Q.tà">{num2(r.quantita)} {r.um}</td>
                  <td className="r" data-label="Evasa">{num2(r.evasa)}</td>
                  <td className={"r strong " + (r.residuo > 0 ? "ko" : "ok")} data-label="Residuo">{num2(r.residuo)}</td>
                  <td data-label="Stato">
                    <span className={"stato-pill " + (r.stato === "da evadere" ? "open" : "done")}>
                      {r.stato}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty">Nessun ordine. Chiedi all'assistente gli ordini clienti o fornitori.</div>
      )}
    </div>
  );
}
