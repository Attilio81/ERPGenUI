"use client";

import { useCopilotChat, useCoAgent } from "@copilotkit/react-core";
import { AgentState, INITIAL_STATE } from "@/lib/state";

export function ResetButton({ onNuova }: { onNuova: () => void }) {
  const { reset } = useCopilotChat();
  const { setState } = useCoAgent<AgentState>({ name: "my_agent", initialState: INITIAL_STATE });

  const nuova = () => {
    // 1) pulizia immediata lato client
    setState({ ...INITIAL_STATE });
    reset?.();
    // 2) nuovo threadId -> nuova sessione backend: storia e session_state azzerati
    onNuova();
  };

  return (
    <button type="button" className="reset-btn" onClick={nuova} title="Nuova conversazione">
      ↺ Nuova
    </button>
  );
}
