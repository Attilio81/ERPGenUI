"use client";

import { useCopilotChat } from "@copilotkit/react-core";
import { TextMessage, Role } from "@copilotkit/runtime-client-gql";

// Mostrato al primo apri (view=table, nessun dato, nessun filtro): spiega il
// funzionamento e offre scorciatoie che partono in chat. Vedi Canvas per il gate.

const PASSI: { n: string; testo: string }[] = [
  { n: "1", testo: "Chiedi a voce o per iscritto (linguaggio naturale)" },
  { n: "2", testo: "L'assistente AI comanda la distinta e sceglie la vista" },
  { n: "3", testo: "I dati restano a schermo — non vengono riportati in chat" },
];

const ESEMPI: string[] = [
  "mostra tutti gli articoli",
  "articoli disponibili della famiglia rotoli, ordina per giacenza",
  "scheda dell'articolo ROTO-028",
  "articoli più venduti per valore nel 2025",
  "ordini clienti da evadere",
];

export function Benvenuto() {
  const { appendMessage } = useCopilotChat();

  const chiedi = (q: string) =>
    appendMessage(new TextMessage({ content: q, role: Role.User }));

  return (
    <div className="panel">
      <div className="panel-head">
        <div>
          <div className="modal-eyebrow">Generative UI · assistente del banco</div>
          <h2>Benvenuto</h2>
          <p className="muted">chiedi in linguaggio naturale · la distinta si compone da sola</p>
        </div>
      </div>

      <div className="welcome-body">
        <ol className="steps">
          {PASSI.map((p) => (
            <li key={p.n} className="step">
              <span className="step-n">{p.n}</span>
              <span className="step-t">{p.testo}</span>
            </li>
          ))}
        </ol>

        <div className="help-group">
          <h4>Prova subito</h4>
          <div className="help-qs">
            {ESEMPI.map((q) => (
              <button key={q} type="button" className="help-q" onClick={() => chiedi(q)}>
                {q}
              </button>
            ))}
          </div>
          <p className="muted small" style={{ margin: "4px 0 0" }}>
            Puoi dettare con 🎤 Voce · tutte le domande nel pulsante <strong>? Guida</strong>.
          </p>
        </div>
      </div>
    </div>
  );
}
