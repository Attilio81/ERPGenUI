"use client";

import { useRef, useState } from "react";
import { useCopilotChat } from "@copilotkit/react-core";
import { TextMessage, Role } from "@copilotkit/runtime-client-gql";

// Pulsante voce: usa la Web Speech API del browser (Chrome/Edge) per dettare la domanda.
// NB privacy: la Web Speech API può inviare l'audio ai server del browser. Per un kiosk
// GDPR-clean sostituire con STT locale (Whisper) che alimenta la stessa appendMessage.
export function MicButton() {
  const { appendMessage } = useCopilotChat();
  const [ascolto, setAscolto] = useState(false);
  const recRef = useRef<any>(null);

  const toggle = () => {
    const SR =
      typeof window !== "undefined" &&
      ((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition);
    if (!SR) {
      alert("Riconoscimento vocale non supportato da questo browser. Usa Chrome o Edge.");
      return;
    }
    if (ascolto) {
      recRef.current?.stop();
      return;
    }
    const rec = new SR();
    rec.lang = "it-IT";
    rec.interimResults = false;
    rec.maxAlternatives = 1;
    rec.onresult = (e: any) => {
      const testo = e?.results?.[0]?.[0]?.transcript?.trim();
      if (testo) {
        appendMessage(new TextMessage({ content: testo, role: Role.User }));
      }
    };
    rec.onend = () => setAscolto(false);
    rec.onerror = () => setAscolto(false);
    recRef.current = rec;
    rec.start();
    setAscolto(true);
  };

  return (
    <button
      type="button"
      className={"mic-btn" + (ascolto ? " rec" : "")}
      onClick={toggle}
      title="Parla (riconoscimento vocale)"
      aria-pressed={ascolto}
    >
      <span className="mic-ico" aria-hidden="true">🎤</span>
      {ascolto ? "Ascolto…" : "Voce"}
    </button>
  );
}
