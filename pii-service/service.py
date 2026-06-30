# -*- coding: utf-8 -*-
"""Microservizio locale di anonimizzazione PII (italiano).

Espone l'anonimizzazione REVERSIBILE come HTTP locale, così il backend Agno può
mascherare il testo utente PRIMA di inviarlo al LLM (pre-hook) e ri-sostituire i
valori veri in locale.

  POST /anonymize  {text}        -> {anonymized_text, mapping, ...}
  GET  /health                   -> {ok, model, device}

Modello: rizzoaiacademy/rizzo-pii-0.3B (mmBERT fine-tuned, MIT) — env PII_MODEL.
Porta:   env PII_PORT (default 5005).

La logica di detection (modello + rete regex/checksum + merge + ID reversibili) è
derivata da rizzo-pii/src/app/app.py (MIT, © Simone Rizzo — Rizzo AI Academy),
qui ridotta al solo percorso testo (niente UI/PDF) ed esposta come API.
"""
from __future__ import annotations

import os
import re

import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

MODEL_ID = os.environ.get("PII_MODEL", "rizzoaiacademy/rizzo-pii-0.3B")
MAX_WORDS = 120      # parole per chunk (~180 subword, sotto i 512 del training)
OVERLAP = 20         # parole di sovrapposizione tra chunk consecutivi

device = 0 if torch.cuda.is_available() else -1
print(f"[pii] carico {MODEL_ID} su {'GPU' if device == 0 else 'CPU'}...")
nlp = pipeline(
    "token-classification",
    model=MODEL_ID,
    tokenizer=MODEL_ID,
    aggregation_strategy="simple",
    device=device,
)
print("[pii] modello pronto.")


# --------------------------------------------------------------------------- #
# Rete REGEX + CHECKSUM (affianca il modello: campi a forma specifica)
# --------------------------------------------------------------------------- #
def iban_ok(s):
    s = re.sub(r"\s", "", s).upper()
    if not (15 <= len(s) <= 34):
        return False
    r = s[4:] + s[:4]
    try:
        n = int("".join(str(ord(c) - 55) if c.isalpha() else c for c in r))
    except ValueError:
        return False
    return n % 97 == 1


def piva_ok(p):
    p = re.sub(r"\D", "", p)
    if len(p) != 11:
        return False
    t = 0
    for i, c in enumerate(map(int, p[:10])):
        if i % 2 == 0:
            t += c
        else:
            x = c * 2
            t += x - 9 if x > 9 else x
    return (10 - t % 10) % 10 == int(p[10])


_CF_ODD = {"0": 1, "1": 0, "2": 5, "3": 7, "4": 9, "5": 13, "6": 15, "7": 17, "8": 19,
           "9": 21, "A": 1, "B": 0, "C": 5, "D": 7, "E": 9, "F": 13, "G": 15, "H": 17,
           "I": 19, "J": 21, "K": 2, "L": 4, "M": 18, "N": 20, "O": 11, "P": 3, "Q": 6,
           "R": 8, "S": 12, "T": 14, "U": 16, "V": 10, "W": 22, "X": 25, "Y": 24, "Z": 23}


def cf_ok(c):
    c = c.strip().upper()
    if len(c) != 16 or not c.isalnum():
        return False
    b = c[:15]
    try:
        t = sum((_CF_ODD[ch] if i % 2 == 0
                 else (int(ch) if ch.isdigit() else ord(ch) - 65))
                for i, ch in enumerate(b))
    except KeyError:
        return False
    return chr(65 + t % 26) == c[15]


def luhn_ok(s):
    d = re.sub(r"\D", "", s)
    if not (13 <= len(d) <= 19):
        return False
    tot, alt = 0, False
    for ch in reversed(d):
        n = int(ch)
        if alt:
            n *= 2
            if n > 9:
                n -= 9
        tot += n
        alt = not alt
    return tot % 10 == 0


# (label, regex, validatore-o-None, strict). strict=True: scarta se checksum fallisce.
DETECTORS = [
    ("EMAIL", re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"), None, True),
    ("CF", re.compile(r"\b[A-Za-z]{6}\d{2}[A-Za-z]\d{2}[A-Za-z]\d{3}[A-Za-z]\b"), cf_ok, False),
    ("IBAN", re.compile(r"\b[A-Za-z]{2}\d{2}[A-Za-z0-9]{11,30}\b"), iban_ok, True),
    ("CREDITCARDNUMBER", re.compile(r"(?<!\d)(?:\d[ \-]?){13,19}(?!\d)"), luhn_ok, True),
    ("PIVA", re.compile(r"(?<!\d)\d{11}(?!\d)"), piva_ok, True),
    ("TELEPHONENUM",
     re.compile(r"(?<![\w.])(?:\+39[\s.]?)?(?:3\d{2}[\s.]?\d{3}[\s.]?\d{3,4}"
                r"|0\d{1,3}[\s.]?\d{5,8})(?![\w])"), None, True),
    ("AMOUNT",
     re.compile(r"(?:€|EUR|euro)\s?\d{1,3}(?:[.\s]\d{3})*(?:,\d{2})?"
                r"|\d{1,3}(?:\.\d{3})*,\d{2}\s?(?:€|EUR|euro)", re.IGNORECASE), None, True),
    ("TARGA", re.compile(r"\b[A-Za-z]{2}\s?\d{3}\s?[A-Za-z]{2}\b"), None, True),
]


def detect_regex(text):
    ents = []
    for label, rx, validator, strict in DETECTORS:
        for m in rx.finditer(text):
            ok = validator(m.group(0)) if validator else False
            if validator and strict and not ok:
                continue
            ents.append({"label": label, "start": m.start(), "end": m.end(),
                         "score": 1.0 if ok else 0.9, "validated": ok, "source": "regex"})
    return ents


def chunk_text(text, max_words=MAX_WORDS, overlap=OVERLAP):
    words = list(re.finditer(r"\S+", text))
    if not words:
        return []
    chunks, i = [], 0
    step = max(1, max_words - overlap)
    while i < len(words):
        block = words[i:i + max_words]
        start, end = block[0].start(), block[-1].end()
        chunks.append((text[start:end], start))
        if i + max_words >= len(words):
            break
        i += step
    return chunks


def detect_model(text):
    chunks = chunk_text(text)
    ents = []
    if chunks:
        results = nlp([c for c, _ in chunks])
        if isinstance(results, dict):
            results = [results]
        for (_, off), res in zip(chunks, results):
            for e in res:
                ents.append({"label": e["entity_group"], "start": int(e["start"]) + off,
                             "end": int(e["end"]) + off, "score": float(e["score"]),
                             "validated": False, "source": "modello"})
    return ents, len(chunks)


def _merge(cands, text):
    """Greedy senza overlap. Priorità: checksum-valido > regex > score > lunghezza."""
    order = sorted(cands, key=lambda e: (1 if e["validated"] else 0,
                                         1 if e["source"] == "regex" else 0,
                                         e["score"], e["end"] - e["start"]), reverse=True)
    kept = []
    for e in order:
        if all(e["end"] <= k["start"] or e["start"] >= k["end"] for k in kept):
            kept.append(e)
    for e in kept:
        while e["start"] < e["end"] and text[e["start"]].isspace():
            e["start"] += 1
        while e["end"] > e["start"] and text[e["end"] - 1].isspace():
            e["end"] -= 1
    kept = [e for e in kept if e["end"] > e["start"]]
    kept.sort(key=lambda e: e["start"])
    return kept


def _norm(s):
    return re.sub(r"\s+", " ", s.strip()).casefold()


def analyze(text):
    model_ents, _ = detect_model(text)
    kept = _merge(model_ents + detect_regex(text), text)

    counters, seen, mapping = {}, {}, {}
    for e in kept:
        val = text[e["start"]:e["end"]]
        key = (e["label"], _norm(val))
        if key in seen:
            e["ph"] = seen[key]
        else:
            counters[e["label"]] = counters.get(e["label"], 0) + 1
            ph = f"[{e['label']}_{counters[e['label']]}]"
            seen[key] = ph
            mapping[ph] = val
            e["ph"] = ph

    anon, by_label, pos = [], {}, 0
    for e in kept:
        if e["start"] > pos:
            anon.append(text[pos:e["start"]])
        anon.append(e["ph"])
        by_label[e["label"]] = by_label.get(e["label"], 0) + 1
        pos = e["end"]
    if pos < len(text):
        anon.append(text[pos:])

    return {"anonymized_text": "".join(anon), "mapping": mapping,
            "n_entities": len(kept), "by_label": by_label}


# --------------------------------------------------------------------------- #
# API
# --------------------------------------------------------------------------- #
app = FastAPI(title="pii-service", version="1.0.0")


class AnonReq(BaseModel):
    text: str


@app.get("/health")
def health():
    return {"ok": True, "model": MODEL_ID, "device": "GPU" if device == 0 else "CPU"}


@app.post("/anonymize")
def anonymize(req: AnonReq):
    text = (req.text or "").strip()
    if not text:
        return {"anonymized_text": "", "mapping": {}, "n_entities": 0, "by_label": {}}
    return analyze(text)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PII_PORT", "5005")))
