"use client";

import { useState } from "react";
import { useCopilotChat } from "@copilotkit/react-core";
import { TextMessage, Role } from "@copilotkit/runtime-client-gql";

type Gruppo = { titolo: string; icona: string; esempi: string[] };

const GRUPPI: Gruppo[] = [
  {
    titolo: "Articoli",
    icona: "📦",
    esempi: [
      "mostra tutti gli articoli",
      "articoli disponibili della famiglia rotoli, ordina per giacenza",
      "articoli del fornitore Cristianpack",
      "cosa abbiamo nei rotoli cassa?",
      "scheda dell'articolo ROTO-028",
    ],
  },
  {
    titolo: "Prezzi e giacenze (anche a voce)",
    icona: "💶",
    esempi: [
      "avete pellicola da 30? quanto costa?",
      "prezzo e giacenza dell'alluminio",
      "quanto costa? (dopo aver aperto una scheda)",
    ],
  },
  {
    titolo: "Vendite e grafici",
    icona: "📊",
    esempi: [
      "articoli più venduti per valore nel 2025",
      "andamento del valore venduto per anno",
      "quote di fatturato per famiglia nel 2024",
      "migliori clienti per fatturato nel 2024",
      "vendite per agente nel 2023",
    ],
  },
  {
    titolo: "Ordini",
    icona: "📋",
    esempi: [
      "ordini clienti da evadere",
      "ordini ai fornitori per alluminio",
      "ordini clienti del 2026",
    ],
  },
  {
    titolo: "Clienti",
    icona: "👥",
    esempi: [
      "cerca i clienti di Rivarolo",
      "scheda del cliente Macelleria Lucco Borlera",
      "scadenze ed esposizione del cliente ...",
    ],
  },
  {
    titolo: "Affinare (follow-up)",
    icona: "↩️",
    esempi: [
      "ordina per esistenza",
      "al contrario",
      "solo disponibili",
      "mostra tutti gli articoli",
    ],
  },
];

export function HelpModal() {
  const [open, setOpen] = useState(false);
  const { appendMessage } = useCopilotChat();

  const chiedi = (q: string) => {
    appendMessage(new TextMessage({ content: q, role: Role.User }));
    setOpen(false);
  };

  return (
    <>
      <button type="button" className="reset-btn" onClick={() => setOpen(true)} title="Cosa posso chiedere">
        ? Guida
      </button>

      {open && (
        <div className="modal-overlay" onClick={() => setOpen(false)}>
          <div className="modal-card wide" onClick={(e) => e.stopPropagation()}>
            <div className="modal-head">
              <div>
                <div className="modal-eyebrow">Guida</div>
                <h3 className="modal-title">Cosa posso chiedere</h3>
              </div>
              <button type="button" className="modal-x" onClick={() => setOpen(false)} aria-label="Chiudi">✕</button>
            </div>

            <div className="modal-body help-body">
              <p className="muted small" style={{ margin: 0 }}>
                Clicca una domanda per provarla. Puoi anche dettare con 🎤 Voce.
              </p>
              {GRUPPI.map((g) => (
                <div key={g.titolo} className="help-group">
                  <h4>{g.icona} {g.titolo}</h4>
                  <div className="help-qs">
                    {g.esempi.map((q) => (
                      <button key={q} type="button" className="help-q" onClick={() => chiedi(q)}>
                        {q}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="modal-foot">
              <span className="modal-hint">I dati restano a schermo · l'assistente non li riporta in chat</span>
              <button type="button" className="edit-btn ghost" onClick={() => setOpen(false)}>Chiudi</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
