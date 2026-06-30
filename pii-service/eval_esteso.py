# -*- coding: utf-8 -*-
"""Eval ESTESO della guardia PII su casi italiani realistici (stile gestionale Vittone).

Per ogni caso confronta le PII attese con quelle rilevate (modello + regex/checksum),
misurando per ogni entità attesa:
  - HIT  : almeno un pezzo del valore è mascherato (protezione parziale)
  - FULL : l'intero valore è coperto dai placeholder (protezione totale)
e conta i FALSI POSITIVI nei casi NEGATIVI (testo senza PII che NON deve scattare).

  python eval_esteso.py

Nota onesta: i casi sono scritti a mano, con valori SINTETICI (CF/PIVA/IBAN validi).
Non è un benchmark statistico: serve a vedere DOVE la guardia tiene e dove perde.
"""
from service import analyze, detect_model, detect_regex, _merge


def kept_spans(text):
    """Entità tenute (modello + regex), con start/end/label/value."""
    cands = detect_model(text)[0] + detect_regex(text)
    out = []
    for e in _merge(cands, text):
        out.append((e["label"], text[e["start"]:e["end"]], e["start"], e["end"]))
    return out


def covered_mask(spans, n):
    m = [False] * n
    for _lab, _val, s, e in spans:
        for i in range(s, min(e, n)):
            m[i] = True
    return m


def coverage_of(value, text, mask):
    """(hit, full) del valore: cerca tutte le occorrenze, valuta la copertura della migliore."""
    best = (False, False)
    start = 0
    vlen = len(value)
    while True:
        i = text.find(value, start)
        if i < 0:
            break
        seg = mask[i:i + vlen]
        any_c = any(seg)
        full_c = all(seg)
        best = (best[0] or any_c, best[1] or full_c)
        start = i + 1
    return best


# (testo, [(label_atteso, valore_atteso), ...])  -- lista vuota = caso NEGATIVO
CASI = [
    # --- persone ---
    ("scheda cliente Mario Rossi", [("FULLNAME", "Mario Rossi")]),
    ("situazione di Bianchi Giuseppe", [("FULLNAME", "Bianchi Giuseppe")]),
    ("il referente è la dott.ssa Anna Maria De Filippo", [("FULLNAME", "Anna Maria De Filippo")]),
    ("ha ordinato Giovanni Esposito ieri", [("FULLNAME", "Giovanni Esposito")]),
    # --- nomi azienda (ORG, il punto debole B2B) ---
    ("scadenze della Macelleria Lucco Borlera", [("ORG", "Macelleria Lucco Borlera")]),
    ("ordini della Panetteria Da Luigi", [("ORG", "Panetteria Da Luigi")]),
    ("fattura a Pasticceria Aurora SRL", [("ORG", "Pasticceria Aurora SRL")]),
    ("cliente Salumeria Il Buongustaio di Torino", [("ORG", "Salumeria Il Buongustaio")]),
    ("Bar Centrale SNC non ha pagato", [("ORG", "Bar Centrale SNC")]),
    ("Hotel Belvedere SPA, saldo aperto", [("ORG", "Hotel Belvedere SPA")]),
    ("Azienda Agricola Le Querce", [("ORG", "Azienda Agricola Le Querce")]),
    # --- identificativi (forti, checksum) ---
    ("codice fiscale RSSMRA85M01H501Z", [("CF", "RSSMRA85M01H501Z")]),
    ("P.IVA 12345678903", [("PIVA", "12345678903")]),
    ("partita iva 00743110157 della ditta", [("PIVA", "00743110157")]),
    ("bonifico IBAN IT60X0542811101000000123456", [("IBAN", "IT60X0542811101000000123456")]),
    ("carta 4539148803436467 scaduta", [("CREDITCARDNUMBER", "4539148803436467")]),
    # --- contatti ---
    ("email mario.rossi@panetteria.it", [("EMAIL", "mario.rossi@panetteria.it")]),
    ("pec ordini@pasticceria.pec.it", [("EMAIL", "ordini@pasticceria.pec.it")]),
    ("telefono 011 1234567", [("TELEPHONENUM", "011 1234567")]),
    ("cellulare +39 333 1234567", [("TELEPHONENUM", "+39 333 1234567")]),
    # --- indirizzi / geo ---
    ("residente in Via Garibaldi 24, Rivarolo Canavese (TO)",
     [("STREET", "Via Garibaldi"), ("CITY", "Rivarolo Canavese"), ("PROVINCE", "TO")]),
    ("consegna a Corso Italia 10, 10128 Torino",
     [("STREET", "Corso Italia"), ("ZIPCODE", "10128"), ("CITY", "Torino")]),
    # --- importi / data / targa ---
    ("insoluto di 1.250,00 € dal 12/06/2024", [("AMOUNT", "1.250,00 €"), ("DATE", "12/06/2024")]),
    ("furgone targa AB123CD in consegna", [("TARGA", "AB123CD")]),
    # --- misti (frase intera) ---
    ("Mario Rossi, CF RSSMRA85M01H501Z, IBAN IT60X0542811101000000123456, tel 333 1234567",
     [("FULLNAME", "Mario Rossi"), ("CF", "RSSMRA85M01H501Z"),
      ("IBAN", "IT60X0542811101000000123456"), ("TELEPHONENUM", "333 1234567")]),

    # --- NEGATIVI: query gestionale senza PII -> NON deve scattare nulla ---
    ("quanto costa la pellicola H30?", []),
    ("articoli disponibili famiglia rotoli, ordina per giacenza", []),
    ("mostra gli ordini da evadere", []),
    ("vendite per famiglia nel 2025", []),
    ("prezzo e giacenza dell'alluminio", []),
    ("cosa abbiamo nei rotoli cassa", []),
    ("grafico a torta delle quote per famiglia", []),
    ("scheda dell'articolo ROTO-028", []),   # codice articolo, NON personale
]


def main():
    by_label = {}        # label -> [n, hit, full]
    fp_neg = []          # falsi positivi nei casi negativi
    n_neg = 0
    print("=" * 90)
    for text, expect in CASI:
        spans = kept_spans(text)
        mask = covered_mask(spans, len(text))
        if not expect:                         # caso negativo
            n_neg += 1
            if spans:
                fp_neg.append((text, [(l, v) for l, v, _s, _e in spans]))
            continue
        misses = []
        for label, value in expect:
            hit, full = coverage_of(value, text, mask)
            rec = by_label.setdefault(label, [0, 0, 0])
            rec[0] += 1
            rec[1] += 1 if hit else 0
            rec[2] += 1 if full else 0
            if not full:
                misses.append(f"{label}:{value!r} -> {'PARZIALE' if hit else 'MANCATO'}")
        if misses:
            print(f"[!] {text}")
            for mtxt in misses:
                print(f"      {mtxt}")

    print("=" * 90)
    print(f"{'LABEL':18s} {'attesi':>7} {'hit':>6} {'full':>6}   copertura")
    print("-" * 90)
    tot = [0, 0, 0]
    for label in sorted(by_label):
        n, hit, full = by_label[label]
        tot[0] += n; tot[1] += hit; tot[2] += full
        print(f"{label:18s} {n:>7} {hit:>6} {full:>6}   "
              f"hit {100*hit//n if n else 0}% · full {100*full//n if n else 0}%")
    print("-" * 90)
    n, hit, full = tot
    print(f"{'TOTALE':18s} {n:>7} {hit:>6} {full:>6}   "
          f"hit {100*hit//n if n else 0}% · full {100*full//n if n else 0}%")
    print("=" * 90)
    print(f"NEGATIVI: {n_neg} casi senza PII · falsi positivi: {len(fp_neg)}")
    for text, ents in fp_neg:
        print(f"  [FP] {text}")
        for l, v in ents:
            print(f"        {l}: {v!r}")
    print("=" * 90)


if __name__ == "__main__":
    main()
