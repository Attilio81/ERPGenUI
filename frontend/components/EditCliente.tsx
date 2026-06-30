"use client";

import { useState } from "react";
import { ClienteDettaglio } from "@/lib/state";

// CRUD demo cliente: modifica contatti (telefono/cellulare/email/note) su ANAGRA.
// NON passa dall'LLM — write deterministico con conferma, whitelist lato backend.
export function EditCliente({ cli }: { cli: ClienteDettaglio }) {
  const [open, setOpen] = useState(false);
  const [tel, setTel] = useState(cli.telefono ?? "");
  const [cell, setCell] = useState(cli.cellulare ?? "");
  const [email, setEmail] = useState(cli.email ?? "");
  const [note, setNote] = useState(cli.note ?? "");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const apri = () => {
    setTel(cli.telefono ?? ""); setCell(cli.cellulare ?? "");
    setEmail(cli.email ?? ""); setNote(cli.note ?? "");
    setMsg(null); setOpen(true);
  };

  const salva = async () => {
    const payload: Record<string, unknown> = { cod_conto: cli.codice };
    if (tel !== (cli.telefono ?? "")) payload.telefono = tel;
    if (cell !== (cli.cellulare ?? "")) payload.cellulare = cell;
    if (email !== (cli.email ?? "")) payload.email = email;
    if (note !== (cli.note ?? "")) payload.note = note;

    const cambiati = Object.keys(payload).filter((k) => k !== "cod_conto");
    if (cambiati.length === 0) { setMsg({ ok: false, text: "Nessuna modifica da salvare." }); return; }
    if (!window.confirm(`Confermi la modifica del cliente ${cli.codice} (${cambiati.join(", ")})?`)) return;

    setBusy(true); setMsg(null);
    try {
      const r = await fetch("/api/cliente", {
        method: "PATCH",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await r.json();
      setMsg(data.ok
        ? { ok: true, text: `Salvato. Campi aggiornati: ${data.campi.join(", ")}.` }
        : { ok: false, text: data.errore || "Modifica non riuscita." });
    } catch {
      setMsg({ ok: false, text: "Errore di rete." });
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <button type="button" className="edit-btn" onClick={apri} title="Modifica contatti cliente">
        ✎ Modifica
      </button>

      {open && (
        <div className="modal-overlay" onClick={() => !busy && setOpen(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-head">
              <div>
                <div className="modal-eyebrow">Modifica cliente</div>
                <h3 className="modal-title">{cli.codice}</h3>
              </div>
              <button type="button" className="modal-x" onClick={() => setOpen(false)} aria-label="Chiudi">✕</button>
            </div>

            <div className="modal-body">
              <label className="field"><span>Telefono</span>
                <input value={tel} onChange={(e) => setTel(e.target.value)} autoFocus /></label>
              <label className="field"><span>Cellulare</span>
                <input value={cell} onChange={(e) => setCell(e.target.value)} /></label>
              <label className="field"><span>Email</span>
                <input value={email} onChange={(e) => setEmail(e.target.value)} /></label>
              <label className="field"><span>Note</span>
                <textarea value={note} onChange={(e) => setNote(e.target.value)} rows={2} /></label>
              {msg && <div className={"modal-msg " + (msg.ok ? "ok" : "ko")}>{msg.text}</div>}
            </div>

            <div className="modal-foot">
              <span className="modal-hint">Scrive su ANAGRA · ditta corrente</span>
              <div className="modal-actions">
                <button type="button" className="edit-btn ghost" onClick={() => setOpen(false)} disabled={busy}>Annulla</button>
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
