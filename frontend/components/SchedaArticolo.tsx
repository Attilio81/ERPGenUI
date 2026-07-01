"use client";

import { AgentState } from "@/lib/state";
import { useNav } from "@/lib/nav";
import { num, num2, euro, dataIt } from "@/lib/format";
import { EditArticolo } from "./EditArticolo";

export function SchedaArticolo({ state }: { state: AgentState }) {
  const { apriCliente, indietro, hasPrev } = useNav(state);
  const a = state.articolo;
  if (!a) {
    return <div className="panel"><div className="empty">Nessuna scheda caricata.</div></div>;
  }

  const d = a.disponibilita ?? { esistenza: 0, ordinato: 0, impegnato: 0 };
  const disponibile = (d.esistenza ?? 0) - (d.impegnato ?? 0);

  return (
    <div className="panel">
      <div className="panel-head">
        <div>
          <h2>{a.descrizione}</h2>
          <p className="muted">
            <span className="mono">{a.codice}</span> · {a.famiglia} · {a.fornitore || "—"}
          </p>
        </div>
        <div className="scheda-actions">
          {hasPrev ? (
            <button type="button" className="edit-btn ghost" onClick={indietro}>
              ← Indietro
            </button>
          ) : null}
          <span className="chip">UM {a.um}</span>
          <EditArticolo art={a} />
        </div>
      </div>

      <div className="stat-row">
        <div className="stat"><span>Esistenza</span><strong>{num(d.esistenza)}</strong></div>
        <div className="stat"><span>Impegnato</span><strong>{num(d.impegnato)}</strong></div>
        <div className="stat"><span>Ordinato forn.</span><strong>{num(d.ordinato)}</strong></div>
        <div className={"stat " + (disponibile > 0 ? "good" : "bad")}>
          <span>Disponibile</span><strong>{num(disponibile)}</strong>
        </div>
      </div>

      <div className="cols">
        <div className="card">
          <h3>Listini</h3>
          {a.listini?.length ? (
            <table className="grid mini">
              <thead><tr><th>List.</th><th>Descrizione</th><th className="r">Prezzo</th></tr></thead>
              <tbody>
                {a.listini.map((l) => (
                  <tr key={l.listino}>
                    <td className="mono">{l.listino}</td>
                    <td className="muted small">{l.descr_listino}</td>
                    <td className="r strong">{euro(l.prezzo)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : <p className="muted">Nessun listino attivo.</p>}
        </div>

        <div className="card">
          <h3>Ultime vendite</h3>
          {a.ultime_vendite?.length ? (
            <table className="grid mini">
              <thead><tr><th>Data</th><th>Cliente</th><th className="r">Q.tà</th><th className="r">Valore</th></tr></thead>
              <tbody>
                {a.ultime_vendite.map((v, i) => (
                  <tr key={i}>
                    <td>{dataIt(v.data)}</td>
                    <td className="muted small">
                      <span className="linkcell" onClick={() => apriCliente(v.cliente)} title="Apri scheda cliente">{v.cliente}</span>
                    </td>
                    <td className="r">{num2(v.quantita)}</td>
                    <td className="r strong">{euro(v.valore)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : <p className="muted">Nessuna vendita recente.</p>}
        </div>

        <div className="card">
          <h3>Ultimi ordini clienti</h3>
          <OrdiniMini righe={a.ordini_clienti} contoLabel="Cliente" vuoto="Nessun ordine cliente." onConto={apriCliente} />
        </div>

        <div className="card">
          <h3>Ultimi ordini fornitori</h3>
          <OrdiniMini righe={a.ordini_fornitori} contoLabel="Fornitore" vuoto="Nessun ordine fornitore." />
        </div>
      </div>
    </div>
  );
}

function OrdiniMini({
  righe,
  contoLabel,
  vuoto,
  onConto,
}: {
  righe?: { data: string; conto: string; quantita: number; residuo: number; stato: string }[];
  contoLabel: string;
  vuoto: string;
  onConto?: (conto: string) => void;
}) {
  if (!righe?.length) return <p className="muted">{vuoto}</p>;
  return (
    <table className="grid mini">
      <thead>
        <tr><th>Data</th><th>{contoLabel}</th><th className="r">Q.tà</th><th>Stato</th></tr>
      </thead>
      <tbody>
        {righe.map((o, i) => (
          <tr key={i}>
            <td className="mono">{dataIt(o.data)}</td>
            <td className="muted small">
              {onConto ? (
                <span className="linkcell" onClick={() => onConto(o.conto)} title="Apri scheda cliente">{o.conto}</span>
              ) : o.conto}
            </td>
            <td className="r">{num2(o.quantita)}</td>
            <td>
              <span className={"stato-pill " + (o.stato === "da evadere" ? "open" : "done")}>{o.stato}</span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
