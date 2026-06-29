"use client";

import { useCopilotChat, useCoAgent } from "@copilotkit/react-core";
import { AgentState, INITIAL_STATE } from "@/lib/state";

export function ResetButton() {
  const { reset } = useCopilotChat();
  const { setState } = useCoAgent<AgentState>({ name: "my_agent", initialState: INITIAL_STATE });

  const nuova = () => {
    reset?.();                 // svuota la chat
    setState({ ...INITIAL_STATE }); // riporta la schermata a vuoto
  };

  return (
    <button type="button" className="reset-btn" onClick={nuova} title="Nuova conversazione">
      ↺ Nuova
    </button>
  );
}
