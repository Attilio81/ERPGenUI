"""Smoke test del DB di test: esercita backend/db.py contro il container.

Uso (dalla root del repo, con il venv del backend attivo e il container su):
    python test-db/smoke_test.py

Non serve la chiave LLM: chiama solo il data layer. Esce 0 se tutto ok, 1 altrimenti.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

# carica backend/.env (DB_CONN). Se manca, ripiega su .env.test.
from dotenv import load_dotenv  # noqa: E402

if (BACKEND / ".env").exists():
    load_dotenv(BACKEND / ".env")
else:
    load_dotenv(BACKEND / ".env.test")
os.environ.setdefault("CODDITT", "VITC")

import db  # noqa: E402


def _check(nome: str, cond: bool, extra: str = "") -> bool:
    print(f"  [{'OK ' if cond else 'FAIL'}] {nome} {extra}")
    return cond


def main() -> int:
    print(f"DB_CONN -> {os.environ.get('DB_CONN', '(mancante)')[:60]}...")
    ok = True

    art = db.dettaglio_articolo("ROTO-028")
    ok &= _check("dettaglio_articolo('ROTO-028')", bool(art and art.get("codice") == "ROTO-028"))
    ok &= _check("  ha listini", bool(art and art.get("listini")), f"({len(art.get('listini', [])) if art else 0})")
    ok &= _check("  ha vendite", bool(art and art.get("ultime_vendite")))

    rows = db.cerca_articoli(famiglia="rotoli")
    ok &= _check("cerca_articoli(famiglia='rotoli')", len(rows) >= 2, f"({len(rows)} righe)")

    prezzi = db.trova_prezzo("pellicola")
    ok &= _check("trova_prezzo('pellicola')", len(prezzi) >= 1, f"({len(prezzi)} righe)")

    graf = db.vendite_aggregate(dimensione="famiglia", misura="valore", anno=2025)
    ok &= _check("vendite_aggregate(2025)", len(graf) >= 1, f"({len(graf)} gruppi)")

    ord_c = db.ordini_clienti(solo_da_evadere=True)
    ok &= _check("ordini_clienti(da_evadere)", len(ord_c) >= 1, f"({len(ord_c)} righe)")

    cli = db.scheda_cliente("MACELLERIA")
    ok &= _check("scheda_cliente('MACELLERIA')", bool(cli and cli.get("codice")), cli.get("ragione_sociale", "") if cli else "")
    ok &= _check("  ha kpi scadenze", bool(cli and cli.get("kpi")))
    # drill-down: gli articoli in scheda cliente devono avere il CODICE (per aprirne la scheda)
    top = (cli or {}).get("top_articoli") or []
    ok &= _check("  top_articoli col codice", bool(top and top[0].get("codice")), top[0].get("codice", "") if top else "")
    ordc = (cli or {}).get("ultimi_ordini") or []
    ok &= _check("  ultimi_ordini col codice", bool(ordc and ordc[0].get("codice")), ordc[0].get("codice", "") if ordc else "")

    anni = db.anni_disponibili()
    ok &= _check("anni_disponibili()", len(anni) >= 3, str(anni))

    print("\n=> TUTTO OK" if ok else "\n=> QUALCOSA NON VA")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
