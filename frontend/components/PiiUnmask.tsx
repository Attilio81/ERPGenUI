"use client";

import { useEffect } from "react";
import { useCoAgent } from "@copilotkit/react-core";
import { AgentState, INITIAL_STATE } from "@/lib/state";

// Restore PII lato client: la risposta del modello può contenere placeholder ([FULLNAME_1])
// che, con streaming, arrivano a schermo prima del restore server-side. Qui li ri-sostituiamo
// con i valori veri usando `pii_map` (già nello stato condiviso, quindi in locale sul browser).
// Logica tollerante ispirata a rizzo-pii/src/app/app.py `reverse()` (MIT): il markdown può
// rendere "[FULLNAME_1]" come "**[FULLNAME_1]**" o senza parentesi -> matcho in modo flessibile.
export function PiiUnmask() {
  const { state } = useCoAgent<AgentState>({ name: "my_agent", initialState: INITIAL_STATE });
  const map = ((state as AgentState | undefined)?.pii_map ?? {}) as Record<string, string>;
  const mapKey = JSON.stringify(map);

  useEffect(() => {
    const entries = Object.entries(map);
    if (!entries.length) return;

    // placeholder più lunghi prima (evita [X_1] dentro [X_10]); parentesi/spazi opzionali
    const esc = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const rules = entries
      .map(([ph, val]) => ({ inner: ph.replace(/^\[|\]$/g, ""), val }))
      .sort((a, b) => b.inner.length - a.inner.length)
      .map(({ inner, val }) => ({ rx: new RegExp(`\\[?\\s*${esc(inner)}\\s*\\]?`, "g"), val }));

    const fix = (root: Node) => {
      const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
      let node = walker.nextNode();
      while (node) {
        const v = node.nodeValue;
        if (v) {
          let nv = v;
          for (const { rx, val } of rules) nv = nv.replace(rx, val);
          if (nv !== v) node.nodeValue = nv;
        }
        node = walker.nextNode();
      }
    };

    fix(document.body);
    const obs = new MutationObserver((muts) => {
      for (const mu of muts) {
        if (mu.type === "characterData" && mu.target) fix(mu.target);
        mu.addedNodes.forEach((n) => fix(n));
      }
    });
    obs.observe(document.body, { subtree: true, childList: true, characterData: true });
    return () => obs.disconnect();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mapKey]);

  return null;
}
