import { NextRequest } from "next/server";

const AGENT_URL = (process.env.AGENT_URL || "http://localhost:7000").replace(/\/$/, "");

// Apertura scheda articolo da click UI (no LLM): dettaglio completo.
export async function GET(req: NextRequest) {
  const cod = new URL(req.url).searchParams.get("cod") || "";
  const r = await fetch(`${AGENT_URL}/api/articolo?cod=${encodeURIComponent(cod)}`);
  return new Response(await r.text(), {
    status: r.status,
    headers: { "content-type": "application/json" },
  });
}

// Proxy verso il backend (evita CORS). Modifica articolo — write deterministico, no LLM.
export async function PATCH(req: NextRequest) {
  const body = await req.text();
  const r = await fetch(`${AGENT_URL}/api/articolo`, {
    method: "PATCH",
    headers: { "content-type": "application/json" },
    body,
  });
  return new Response(await r.text(), {
    status: r.status,
    headers: { "content-type": "application/json" },
  });
}
