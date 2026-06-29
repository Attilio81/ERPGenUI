"use client";

import { useEffect, useState } from "react";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import { Canvas } from "@/components/Canvas";

export default function Page() {
  const [oggi, setOggi] = useState("");
  useEffect(() => {
    setOggi(new Date().toLocaleDateString("it-IT", { day: "2-digit", month: "2-digit", year: "numeric" }));
  }, []);

  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent="my_agent">
      <div className="layout">
        <main className="stage">
          <header className="masthead">
            <div className="masthead-inner">
              <div className="barcode" aria-hidden="true" />
              <div className="brand">
                <div className="word">
                  Vittone<b>.</b>
                </div>
                <div className="tag">Magazzino · Distinta</div>
              </div>
              <div className="doc">
                <div>DITTA <b>VITC</b> · MAG <b>01</b></div>
                <div>DATA <b>{oggi || "—"}</b></div>
                <div className="regia">
                  <span className="dot" /> DeepSeek · regìa
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
