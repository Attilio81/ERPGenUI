"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useChatContext } from "@copilotkit/react-ui";
import { HelpModal } from "./HelpModal";
import { MicButton } from "./MicButton";
import { ResetButton } from "./ResetButton";

// La CopilotSidebar rende l'Header senza passargli props: il callback "Nuova" arriva
// via context (fornito da page.tsx attorno alla sidebar).
export const NuovaContext = createContext<() => void>(() => {});

type Info = { provider?: string; model?: string; guard?: boolean };

// provider -> etichetta leggibile + nota giurisdizione (trasparenza LLM/privacy)
const PROVIDER_LABEL: Record<string, string> = {
  mistral: "Mistral · UE",
  deepseek: "DeepSeek · cloud",
  local: "Locale",
};

export function ChatHeader() {
  const { setOpen } = useChatContext();
  const nuova = useContext(NuovaContext);
  const [info, setInfo] = useState<Info>({});

  useEffect(() => {
    fetch("/api/info")
      .then((r) => r.json())
      .then(setInfo)
      .catch(() => {});
  }, []);

  const prov = info.provider ? (PROVIDER_LABEL[info.provider] ?? info.provider) : "";
  const sub = info.model
    ? `${prov} · ${info.model}${info.guard ? " · guardia PII" : ""}`
    : "modello in caricamento…";

  return (
    <div className="chat-header">
      <div className="ch-title">
        <span className="ch-dot" aria-hidden="true" />
        <div className="ch-texts">
          <div className="ch-name">Assistente AI</div>
          <div className="ch-model" title="Modello LLM che pilota l'interfaccia">{sub}</div>
        </div>
      </div>
      <div className="ch-actions">
        <HelpModal />
        <MicButton />
        <ResetButton onNuova={nuova} />
        <button type="button" className="ch-close" onClick={() => setOpen(false)} aria-label="Chiudi chat">
          ✕
        </button>
      </div>
    </div>
  );
}
