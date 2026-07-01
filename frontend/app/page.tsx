"use client";

import { useEffect, useState } from "react";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import { Canvas } from "@/components/Canvas";
import { PiiUnmask } from "@/components/PiiUnmask";
import { ChatHeader, NuovaContext } from "@/components/ChatHeader";

export default function Page() {
  const [oggi, setOggi] = useState("");
  // threadId controllato: cambiarlo = nuova sessione backend (contesto azzerato).
  // Ogni caricamento pagina (incluso F5) parte da un thread nuovo -> chat pulita,
  // niente vecchia conversazione ripescata da session.db. Fissato in useEffect
  // (non nell'inizializzatore) per evitare mismatch di hydration SSR/client.
  const [threadId, setThreadId] = useState("default");
  // Su mobile la chat parte CHIUSA (canvas a tutto schermo); il pulsante toggle
  // di CopilotSidebar la apre a schermo intero (vedi globals.css). Su desktop
  // resta il pannello persistente affiancato.
  // `defaultOpen` viene letto SOLO al mount della sidebar: quindi montiamo la
  // sidebar dopo aver rilevato il viewport (gate `mounted`), altrimenti su mobile
  // partirebbe aperta col valore SSR e coprirebbe il canvas.
  const [mounted, setMounted] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  useEffect(() => {
    setOggi(new Date().toLocaleDateString("it-IT", { day: "2-digit", month: "2-digit", year: "numeric" }));
    setThreadId("t-" + Date.now());
    setSidebarOpen(!window.matchMedia("(max-width: 900px)").matches);
    setMounted(true);
  }, []);

  const nuovaConversazione = () => setThreadId("t-" + Date.now());

  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent="my_agent" threadId={threadId} showDevConsole={false}>
      <PiiUnmask />
      <div className="layout">
        <main className="stage">
          <header className="masthead">
            <div className="masthead-inner">
              <div className="barcode" aria-hidden="true" />
              <div className="brand">
                <div className="word">
                  Acme<b>.</b>
                </div>
                <div className="tag">Magazzino · Distinta</div>
              </div>
              <div className="doc">
                <div>DITTA <b>DEMO</b> · MAG <b>01</b></div>
                <div>DATA <b>{oggi || "—"}</b></div>
                <div className="regia">
                  <span className="dot" /> assistente AI · regìa
                </div>
              </div>
            </div>
            <div className="eyebrow-row">
              <span>Generative UI</span>
              <span className="sep" />
              <span>stato condiviso AG-UI</span>
              <span className="sep" />
              <span>sola lettura</span>
            </div>
          </header>

          <Canvas />
        </main>
      </div>

      {mounted && (
        <NuovaContext.Provider value={nuovaConversazione}>
          <CopilotSidebar
            defaultOpen={sidebarOpen}
            clickOutsideToClose={false}
            Header={ChatHeader}
            labels={{
              title: "Banco · Assistente AI",
              initial:
                "Sono l'assistente AI del banco: comando la distinta per te. Prova:\n\n• «articoli disponibili della famiglia rotoli, ordina per giacenza»\n• «scheda dell'articolo ROTO-028»\n• «articoli più venduti per valore nel 2025»",
            }}
          />
        </NuovaContext.Provider>
      )}
    </CopilotKit>
  );
}
