import { NextRequest } from "next/server";

const AGENT_URL = (process.env.AGENT_URL || "http://localhost:8000").replace(/\/$/, "");

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
