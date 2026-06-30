"""Guardia PII: anonimizza il testo utente PRIMA del LLM, ripristina in locale.

Flusso (quando PII_GUARD=on):
  1. pre-hook -> anonimizza(messaggio utente) via microservizio rizzo (HTTP locale 5005);
     "Mario Rossi" -> "[FULLNAME_1]". Il LLM vede solo i placeholder.
  2. mapping {placeholder: valore} salvato in session_state["pii_map"].
  3. i tool che usano testo (cerca/scheda) chiamano ripristina() PRIMA della query SQL,
     così la SELECT usa il valore vero ma il modello non l'ha mai visto.

Disattivabile: env PII_GUARD != "on" -> no-op (passthrough), demo invariata.

Fail-CLOSED: se la guardia è attiva ma il servizio non risponde, anonimizza() solleva
PIIServiceError -> il pre-hook blocca la richiesta. Meglio bloccare che far passare PII.
"""
from __future__ import annotations

import os

import httpx

PII_ENABLED = os.environ.get("PII_GUARD", "off").lower() == "on"
PII_URL = os.environ.get("PII_URL", "http://127.0.0.1:5005").rstrip("/")
_TIMEOUT = float(os.environ.get("PII_TIMEOUT", "15"))


class PIIServiceError(RuntimeError):
    """Il microservizio PII non è raggiungibile o ha risposto male."""


def anonimizza(text: str) -> tuple[str, dict]:
    """Ritorna (testo_anonimizzato, mapping). No-op se disattivato.
    Solleva PIIServiceError se attivo e il servizio non risponde (fail-closed)."""
    if not PII_ENABLED or not text or not text.strip():
        return text, {}
    try:
        r = httpx.post(f"{PII_URL}/anonymize", json={"text": text}, timeout=_TIMEOUT)
        r.raise_for_status()
        d = r.json()
    except Exception as e:  # noqa: BLE001
        raise PIIServiceError(str(e)) from e
    return d.get("anonymized_text") or text, d.get("mapping") or {}


def ripristina(text, mapping: dict | None):
    """Rimette i valori veri al posto dei placeholder. Tollerante (sostituzione diretta).
    Placeholder più lunghi prima, per non rompere [X_1] dentro [X_10]."""
    if not text or not mapping or not isinstance(text, str):
        return text
    for ph in sorted(mapping, key=len, reverse=True):
        if ph in text:
            text = text.replace(ph, mapping[ph])
    return text
