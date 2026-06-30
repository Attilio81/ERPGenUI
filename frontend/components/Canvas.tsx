"use client";

import { useCoAgent, useCopilotAction } from "@copilotkit/react-core";
import { AgentState, INITIAL_STATE } from "@/lib/state";
import { TabellaArticoli } from "./TabellaArticoli";
import { SchedaArticolo } from "./SchedaArticolo";
import { GraficoVendite } from "./GraficoVendite";
import { TabellaOrdini } from "./TabellaOrdini";

const TOOL_LABELS: Record<string, string> = {
  cerca_articoli: "Ricerca articoli",
  dettaglio_articolo: "Scheda articolo",
  grafico_vendite: "Grafico vendite",
};

export function Canvas() {
  // Stato condiviso con l'agent Agno (AG-UI). Il backend lo aggiorna via STATE_SNAPSHOT.
  const { state } = useCoAgent<AgentState>({
    name: "my_agent",
    initialState: INITIAL_STATE,
  });

  // Render compatto "a timbro" per ogni chiamata tool (sostituisce la card default).
  useCopilotAction({
    name: "*",
    render: ({ name, status }: { name: string; status: string }) => {
      const done = status === "complete";
      return (
        <div className="toolstamp" data-done={done}>
          <span className="ts-dot" />
          <span className="ts-name">{TOOL_LABELS[name] ?? name}</span>
          <span className="ts-state">{done ? "eseguito" : "in corso…"}</span>
        </div>
      );
    },
  });

  const s = state ?? INITIAL_STATE;
  const view = s.view ?? "table";

  return (
    <section className="canvas">
      {view === "table" && <TabellaArticoli state={s} />}
      {view === "detail" && <SchedaArticolo state={s} />}
      {view === "chart" && <GraficoVendite state={s} />}
      {view === "ordini" && <TabellaOrdini state={s} />}
    </section>
  );
}
