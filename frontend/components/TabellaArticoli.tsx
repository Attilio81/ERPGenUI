"use client";

import { AgentState } from "@/lib/state";
import { num } from "@/lib/format";

const chip = (label: string, value?: string | boolean | null) => {
  if (value === undefined || value === null || value === false || value === "") return null;
  const text = value === true ? label : `${label}: ${value}`;
  return (
    <span key={label} className="chip">
      {text}
    </span>
  );
};

export function TabellaArticoli({ state }: { state: AgentState }) {
  const { rows, filtri, sort, count } = state;

  const chips = [
    chip("famiglia", filtri?.famiglia),
    chip("fornitore", filtri?.fornitore),
    chip("ricerca", filtri?.testo),
    chip("solo disponibili", filtri?.solo_disponibili),
  ].filter(Boolean);

  return (
    <div className="panel">
      <div className="panel-head">
        <div>
          <h2>Articoli</h2>
          <p className="muted">
            {count} risultati · ordinati per <strong>{sort?.campo}</strong> ({sort?.dir})
          </p>
        </div>
        <div className="chips">{chips.length ? chips : <span className="muted">nessun filtro</span>}</div>
      </div>

      {rows?.length ? (
        <div className="table-wrap">
          <table className="grid">
            <thead>
              <tr>
                <th>Codice</th>
                <th>Descrizione</th>
                <th>Famiglia</th>
                <th>Fornitore</th>
                <th className="r">Esist.</th>
                <th className="r">Impeg.</th>
                <th className="r">Ordin.</th>
                <th className="r">Dispon.</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.codice}>
                  <td className="mono">{r.codice}</td>
                  <td>{r.descrizione}</td>
                  <td className="muted small">{r.famiglia}</td>
                  <td className="muted small">{r.fornitore}</td>
                  <td className="r">{num(r.esistenza)}</td>
                  <td className="r">{num(r.impegnato)}</td>
                  <td className="r">{num(r.ordinato)}</td>
                  <td className={"r strong " + (r.disponibile > 0 ? "ok" : "ko")}>{num(r.disponibile)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty">
          Nessun dato. Chiedi all'assistente di mostrare degli articoli.
        </div>
      )}
    </div>
  );
}
