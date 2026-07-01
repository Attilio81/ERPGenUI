# -*- coding: utf-8 -*-
"""Eval del ROUTING: la domanda in linguaggio naturale attiva il tool giusto?

Misura ciò che davvero rompe la UX: l'LLM sceglie il tool corretto (e, dove indicato,
i parametri chiave)? Gira con il provider impostato in .env (AI_PROVIDER) → stesso
script per confrontare DeepSeek vs Mistral vs locale.

  AI_PROVIDER=deepseek  backend\\.venv\\Scripts\\python.exe eval_routing.py
  AI_PROVIDER=mistral   backend\\.venv\\Scripts\\python.exe eval_routing.py

Ogni caso usa una sessione isolata (niente contaminazione tra domande).
NB: esegue query reali sul DB di test e consuma token del provider.
"""
from __future__ import annotations

import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")   # console Windows (cp1252) -> evita crash su ✓/✗
except Exception:
    pass

from dotenv import load_dotenv

load_dotenv()

from agent import agent  # noqa: E402  (costruisce l'agent col provider da AI_PROVIDER)

# (domanda, tool_atteso, {param: sottostringa_attesa_in_args} | None)
CASI = [
    ("mostra gli articoli disponibili della famiglia rotoli, ordina per giacenza", "cerca_articoli", {"famiglia": "rotoli"}),
    ("fammi vedere tutti gli articoli", "cerca_articoli", None),
    ("articoli del fornitore Cristianpack", "cerca_articoli", None),
    ("solo i disponibili", "cerca_articoli", None),
    ("azzera i filtri e mostra tutto", "cerca_articoli", None),
    ("scheda dell'articolo ROTO-028", "dettaglio_articolo", {"cod_art": "ROTO-028"}),
    ("dettaglio del codice ALLU-100", "dettaglio_articolo", None),
    ("quanto costa la pellicola H30?", "trova_prezzo", None),
    ("avete l'alluminio? che prezzo?", "trova_prezzo", None),
    ("prezzo e giacenza dei sacchetti carta", "trova_prezzo", None),
    ("quali vaschette avete in magazzino", "trova_prezzo", None),
    ("articoli piu' venduti per valore nel 2025", "grafico_vendite", {"dimensione": "articolo"}),
    ("andamento del valore venduto per anno", "grafico_vendite", None),
    ("quote di fatturato per famiglia nel 2024", "grafico_vendite", None),
    ("migliori clienti per fatturato nel 2024", "grafico_vendite", None),
    ("vendite per agente nel 2023", "grafico_vendite", None),
    ("fai un grafico a torta delle famiglie", "grafico_vendite", None),
    ("ordini clienti da evadere", "ordini_clienti", {"solo_da_evadere": True}),
    ("cosa hanno ordinato i clienti quest'anno", "ordini_clienti", None),
    ("ordini clienti del 2026", "ordini_clienti", None),
    ("ordini ai fornitori per alluminio", "ordini_fornitori", None),
    ("merce in arrivo dai fornitori", "ordini_fornitori", None),
    ("cosa abbiamo ordinato ai fornitori", "ordini_fornitori", None),
    ("cerca i clienti di Rivarolo", "cerca_clienti", None),
    ("elenco clienti", "cerca_clienti", None),
    ("trova i clienti con partita iva che inizia per 04", "cerca_clienti", None),
    ("scheda del cliente Bianchi Giuseppe", "scheda_cliente", None),
    ("situazione e scadenze del cliente Rossi", "scheda_cliente", None),
    ("esposizione del cliente Verdi", "scheda_cliente", None),
]


def tool_names(resp):
    names = []
    for t in (getattr(resp, "tools", None) or []):
        n = getattr(t, "tool_name", None)
        if n is None and isinstance(t, dict):
            n = t.get("tool_name") or t.get("name")
        if n:
            names.append(n)
    return names


def tool_args(resp, tool):
    for t in (getattr(resp, "tools", None) or []):
        n = getattr(t, "tool_name", None) or (t.get("tool_name") if isinstance(t, dict) else None)
        if n == tool:
            a = getattr(t, "tool_args", None)
            if a is None and isinstance(t, dict):
                a = t.get("tool_args") or {}
            return a or {}
    return {}


def main():
    provider = os.environ.get("AI_PROVIDER", "deepseek")
    ok_tool = ok_param = n_param = 0
    print("=" * 88)
    print(f"EVAL ROUTING · provider={provider} · {len(CASI)} casi")
    print("=" * 88)
    for i, (dom, atteso, pcheck) in enumerate(CASI):
        try:
            resp = agent.run(dom, session_id=f"eval-{i}")
            called = tool_names(resp)
        except Exception as e:  # noqa: BLE001
            print(f"[ERR ] {dom[:55]:55s} → {e}")
            continue
        hit = atteso in called
        ok_tool += 1 if hit else 0
        pstr = ""
        if pcheck:
            n_param += 1
            args = tool_args(resp, atteso) if hit else {}
            good = all(str(v).lower() in str(args.get(k, "")).lower()
                       if not isinstance(v, bool) else args.get(k) == v
                       for k, v in pcheck.items())
            ok_param += 1 if good else 0
            pstr = f"  param={'ok' if good else 'NO'} {args}"
        mark = "✓" if hit else "✗"
        primo = called[0] if called else "—"
        print(f"[{mark}] {dom[:52]:52s} atteso={atteso:18s} chiamato={primo}{pstr}")
    print("=" * 88)
    print(f"TOOL corretto: {ok_tool}/{len(CASI)} = {100*ok_tool//len(CASI)}%")
    if n_param:
        print(f"PARAM chiave:  {ok_param}/{n_param} = {100*ok_param//n_param}%")
    print("=" * 88)


if __name__ == "__main__":
    main()
