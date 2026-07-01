"use client";

import { useEffect, useState } from "react";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import { Canvas } from "@/components/Canvas";
import { ResetButton } from "@/components/ResetButton";
import { MicButton } from "@/components/MicButton";
import { HelpModal } from "@/components/HelpModal";
import { PiiUnmask } from "@/components/PiiUnmask";

// Etichetta del modello nel masthead (non hardcodata al provider). Override: NEXT_PUBLIC_LLM_LABEL.
const LLM_LABEL = process.env.NEXT_PUBLIC_LLM_LABEL || "LLM";

export default function Page() {
  const [oggi, setOggi] = useState("");
  // threadId controllato: cambiarlo = nuova sessione backend (contesto azzerato).
  const [threadId, setThreadId] = useState("default");
  useEffect(() => {
    setOggi(new Date().toLocaleDateString("it-IT", { day: "2-digit", month: "2-digit", year: "numeric" }));
  }, []);

  const nuovaConversazione = () => setThreadId("t-" + Date.now());

  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent="my_agent" threadId={threadId}>
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
                  <span className="dot" /> {LLM_LABEL} · regìa
                </div>
                <span className="masthead-actions">
                  <HelpModal />
                  <MicButton />
                  <ResetButton onNuova={nuovaConversazione} />
                </span>
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

      <CopilotSidebar
        defaultOpen
        clickOutsideToClose={false}
        labels={{
          title: "Banco · Assistente",
          initial:
            "Comando la distinta per te. Prova:\n\n• «articoli disponibili della famiglia rotoli, ordina per giacenza»\n• «scheda dell'articolo ROTO-028»\n• «articoli più venduti per valore nel 2025»",
        }}
      />
    </CopilotKit>
  );
}
