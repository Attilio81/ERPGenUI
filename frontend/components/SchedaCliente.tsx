"use client";

import { AgentState } from "@/lib/state";
import { num2, euro, dataIt } from "@/lib/format";
import { EditCliente } from "./EditCliente";

const statoPill = (s: string) =>
  s === "insoluto" ? "bad" : s === "scaduto" ? "open" : "done";

export function SchedaCliente({ state }: { state: AgentState }) {
  const c = state.cliente;
  if (!c) {
    return <div className="panel"><div className="empty">Nessun cliente caricato.</div></div>;
  }
  const k = c.kpi ?? { esposizione: 0, scaduto: 0, insoluti: 0, n_scadenze: 0 };

  return (
    <div className="panel">
      <div className="panel-head">
        <div>
          <h2>{c.ragione_sociale}</h2>
          <p className="muted">
            <span className="mono">{c.codice}</span>
            {c.piva ? ` · P.IVA ${c.piva}` : ""} · {c.citta || "—"} {c.provincia ? `(${c.provincia})` : ""}
            {c.zona ? ` · ${c.zona}` : ""}
          </p>
        </div>
        <div className="scheda-actions">
          <span className={"stato-pill " + (c.bloccato === "S" ? "bad" : "done")}>
            {c.bloccato === "S" ? "BLOCCATO" : "ATTIVO"}
          </span>
          <EditCliente cli={c} />
        </div>
      </div>

      <div className="stat-row">
        <div className="stat"><span>Esposizione</span><strong>{euro(k.esposizione)}</strong></div>
        <div className={"stat " + (k.scaduto > 0 ? "bad" : "")}><span>Scaduto</span><strong>{euro(k.scaduto)}</strong></div>
        <div className={"stat " + (k.insoluti > 0 ? "bad" : "")}><span>Insoluti</span><strong>{euro(k.insoluti)}</strong></div>
        <div className="stat"><span>Scadenze aperte</span><strong>{num2(k.n_scadenze)}</strong></div>
      </div>

      <div className="cols">
        <div className="card">
          <h3>Scadenze aperte</h3>
          {c.scadenze?.length ? (
            <table className="grid mini">
              <thead><tr><th>Scadenza</th><th>Doc.</th><th className="r">Residuo</th><th>Stato</th></tr></thead>
              <tbody>
                {c.scadenze.map((s, i) => (
                  <tr key={i}>
                    <td className="mono">{dataIt(s.scadenza)}</td>
                    <td className="mono small">{s.documento}</td>
                    <td className="r strong">{euro(s.residuo)}</td>
                    <td><span className={"stato-pill " + statoPill(s.stato)}>{s.stato}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : <p className="muted">Nessuna scadenza aperta.</p>}
        </div>

        <div className="card">
          <h3>Ultimi ordini</h3>
          {c.ultimi_ordini?.length ? (
            <table className="grid mini">
              <thead><tr><th>Data</th><th>Articolo</th><th className="r">Q.tà</th><th>Stato</th></tr></thead>
              <tbody>
                {c.ultimi_ordini.map((o, i) => (
                  <tr key={i}>
                    <td className="mono">{dataIt(o.data)}</td>
                    <td className="muted small">{o.articolo}</td>
                    <td className="r">{num2(o.quantita)}</td>
                    <td><span className={"stato-pill " + (o.stato === "da evadere" ? "open" : "done")}>{o.stato}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : <p className="muted">Nessun ordine.</p>}
        </div>

        <div className="card">
          <h3>Top articoli acquistati</h3>
          {c.top_articoli?.length ? (
            <table className="grid mini">
              <thead><tr><th>Articolo</th><th className="r">Acquistato</th></tr></thead>
              <tbody>
                {c.top_articoli.map((t, i) => (
                  <tr key={i}>
                    <td className="muted small">{t.articolo}</td>
                    <td className="r strong">{euro(t.valore)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : <p className="muted">Nessun acquisto.</p>}
        </div>

        <div className="card">
          <h3>Anagrafica</h3>
          <dl className="anag">
            <dt>Indirizzo</dt><dd>{[c.indirizzo, c.cap, c.citta].filter(Boolean).join(" · ") || "—"}</dd>
            <dt>Telefono</dt><dd>{c.telefono || "—"}</dd>
            <dt>Cellulare</dt><dd>{c.cellulare || "—"}</dd>
            <dt>Email</dt><dd>{c.email || "—"}</dd>
            <dt>C.F.</dt><dd className="mono">{c.cf || "—"}</dd>
            <dt>Ultimo doc.</dt><dd>{c.ultimo_doc ? dataIt(c.ultimo_doc) : "—"}</dd>
            <dt>Note</dt><dd>{c.note || "—"}</dd>
          </dl>
        </div>
      </div>
    </div>
  );
}
