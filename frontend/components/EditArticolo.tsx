"use client";

import { useState } from "react";
import { ArticoloDettaglio } from "@/lib/state";

// CRUD demo: modifica alcuni campi di ARTICO. NON passa dall'LLM — write deterministico,
// con conferma esplicita. Whitelist lato backend (descrizione, note, peso_netto).
export function EditArticolo({ art }: { art: ArticoloDettaglio }) {
  const [open, setOpen] = useState(false);
  const [descr, setDescr] = useState(art.descrizione ?? "");
  const [note, setNote] = useState(art.note ?? "");
  const [peso, setPeso] = useState(String(art.peso_netto ?? 0));
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const apri = () => {
    setDescr(art.descrizione ?? "");
    setNote(art.note ?? "");
    setPeso(String(art.peso_netto ?? 0));
    setMsg(null);
    setOpen(true);
  };

  const salva = async () => {
    const payload: Record<string, unknown> = { cod_art: art.codice };
    if (descr !== art.descrizione) payload.descrizione = descr;
    if (note !== (art.note ?? "")) payload.note = note;
    if (Number(peso) !== Number(art.peso_netto)) payload.peso_netto = Number(peso);

    const cambiati = Object.keys(payload).filter((k) => k !== "cod_art");
    if (cambiati.length === 0) {
      setMsg({ ok: false, text: "Nessuna modifica da salvare." });
      return;
    }
    if (!window.confirm(`Confermi la modifica di ${art.codice} (${cambiati.join(", ")}) sul gestionale?`)) return;

    setBusy(true);
    setMsg(null);
    try {
      const r = await fetch("/api/articolo", {
        method: "PATCH",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await r.json();
      setMsg(
        data.ok
          ? { ok: true, text: `Salvato. Campi aggiornati: ${data.campi.join(", ")}.` }
          : { ok: false, text: data.errore || "Modifica non riuscita." }
      );
    } catch {
      setMsg({ ok: false, text: "Errore di rete." });
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <button type="button" className="edit-btn" onClick={apri} title="Modifica articolo">
        ✎ Modifica
      </button>

      {open && (
        <div className="modal-overlay" onClick={() => !busy && setOpen(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-head">
              <div>
                <div className="modal-eyebrow">Modifica articolo</div>
                <h3 className="modal-title">{art.codice}</h3>
              </div>
              <button type="button" className="modal-x" onClick={() => setOpen(false)} aria-label="Chiudi">✕</button>
            </div>

            <div className="modal-body">
              <label className="field">
                <span>Descrizione</span>
                <input value={descr} onChange={(e) => setDescr(e.target.value)} maxLength={255} autoFocus />
              </label>
              <label className="field">
                <span>Note</span>
                <textarea value={note} onChange={(e) => setNote(e.target.value)} rows={2} />
              </label>
              <label className="field field-short">
                <span>Peso netto</span>
                <input type="number" step="0.001" value={peso} onChange={(e) => setPeso(e.target.value)} />
              </label>

              {msg && <div className={"modal-msg " + (msg.ok ? "ok" : "ko")}>{msg.text}</div>}
            </div>

            <div className="modal-foot">
              <span className="modal-hint">Scrive su ARTICO · ditta corrente</span>
              <div className="modal-actions">
                <button type="button" className="edit-btn ghost" onClick={() => setOpen(false)} disabled={busy}>
                  Annulla
                </button>
                <button type="button" className="edit-btn save" onClick={salva} disabled={busy}>
                  {busy ? "Salvataggio…" : "Salva modifiche"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
