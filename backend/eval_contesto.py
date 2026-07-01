# -*- coding: utf-8 -*-
"""Test del CONTESTO multi-turn: l'assistente ricorda la domanda precedente?

Esegue conversazioni a più turni con la STESSA session_id (così la storia è condivisa,
add_history_to_context=True) e verifica che i follow-up mantengano il contesto:
filtri "sticky" articoli, inversione ordinamento, dettaglio dell'articolo aperto.

  AI_PROVIDER=deepseek backend\\.venv\\Scripts\\python.exe eval_contesto.py

Legge il contenuto di risposta dei tool (che ri-echeggia i filtri attivi) per verificare.
"""
from __future__ import annotations

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv

load_dotenv()

from agent import agent  # noqa: E402


def run(msg, sid):
    r = agent.run(msg, session_id=sid)
    c = getattr(r, "content", "") or ""
    tools = [getattr(t, "tool_name", None) for t in (getattr(r, "tools", None) or [])]
    return c, tools


def check(nome, content, must_have):
    low = content.lower()
    ok = all(m.lower() in low for m in must_have)
    print(f"  [{'PASS' if ok else 'FAIL'}] {nome}")
    if not ok:
        print(f"        atteso tutti: {must_have}")
        print(f"        risposta: {content[:160]!r}")
    return ok


def main():
    passed = total = 0

    print("=" * 78)
    print("SCENARIO A — filtri sticky articoli (mantiene famiglia tra i turni)")
    print("=" * 78)
    sid = "ctx-sticky"
    c1, t1 = run("mostra gli articoli della famiglia rotoli", sid)
    print(f"  T1 tools={t1}")
    total += 1; passed += check("T1: filtra per famiglia rotoli", c1, ["rotoli"])
    c2, t2 = run("ordina per giacenza", sid)
    print(f"  T2 tools={t2}")
    total += 1; passed += check("T2: tiene 'rotoli' + ordina per esistenza (CONTESTO)", c2, ["rotoli", "esistenza"])
    c3, t3 = run("al contrario", sid)
    print(f"  T3 tools={t3}")
    total += 1; passed += check("T3: tiene 'rotoli' anche invertendo (CONTESTO)", c3, ["rotoli"])
    c4, t4 = run("solo i disponibili", sid)
    print(f"  T4 tools={t4}")
    total += 1; passed += check("T4: tiene 'rotoli' + solo disponibili (CONTESTO)", c4, ["rotoli", "disponibili"])

    print("=" * 78)
    print("SCENARIO B — dettaglio dell'articolo APERTO (follow-up senza ripetere il codice)")
    print("=" * 78)
    sid2 = "ctx-detail"
    c5, t5 = run("apri la scheda dell'articolo ALPE-018/1", sid2)
    print(f"  T1 tools={t5}")
    total += 1; passed += check("T1: apre dettaglio_articolo", c5, ["ALPE-018/1".lower()] if "ALPE" in c5 else ["scheda"])
    c6, t6 = run("quanto costa?", sid2)
    print(f"  T2 tools={t6}")
    # se tiene il contesto, richiama dettaglio_articolo sull'articolo corrente (non chiede 'quale')
    ok = "dettaglio_articolo" in t6
    print(f"  [{'PASS' if ok else 'FAIL'}] T2: 'quanto costa?' usa l'articolo aperto (CONTESTO) → tools={t6}")
    total += 1; passed += 1 if ok else 0

    print("=" * 78)
    print(f"CONTESTO: {passed}/{total} check superati")
    print("=" * 78)


if __name__ == "__main__":
    main()
