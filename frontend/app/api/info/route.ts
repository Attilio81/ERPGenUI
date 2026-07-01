import { NextRequest } from "next/server";

const AGENT_URL = (process.env.AGENT_URL || "http://localhost:7000").replace(/\/$/, "");

// Info non sensibili sul modello attivo (provider/model/guard) per il frontend.
export async function GET(_req: NextRequest) {
  try {
    const r = await fetch(`${AGENT_URL}/api/info`, { cache: "no-store" });
    return new Response(await r.text(), {
      status: r.status,
      headers: { "content-type": "application/json" },
    });
  } catch {
    return Response.json({ provider: "?", model: "?", guard: false });
  }
}
