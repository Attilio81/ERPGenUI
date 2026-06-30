# -*- coding: utf-8 -*-
"""Eval su ~100 casi italiani generati (valori SINTETICI ma con checksum VALIDI).

Compone frasi realistiche da pool (persone, nomi-ditta, indirizzi) + identificativi
generati con checksum corretti (CF/PIVA/IBAN), così la rete regex/checksum li tratta
come veri. Misura hit/full per categoria + falsi positivi sui casi negativi.

  python eval_100.py

Seed fisso -> riproducibile. Solo dati sintetici, nessuna PII reale.
"""
import random

from eval_esteso import kept_spans, covered_mask, coverage_of

random.seed(42)

# --- generatori di identificativi con checksum VALIDO -------------------------
_CF_ODD = {"0": 1, "1": 0, "2": 5, "3": 7, "4": 9, "5": 13, "6": 15, "7": 17, "8": 19,
           "9": 21, "A": 1, "B": 0, "C": 5, "D": 7, "E": 9, "F": 13, "G": 15, "H": 17,
           "I": 19, "J": 21, "K": 2, "L": 4, "M": 18, "N": 20, "O": 11, "P": 3, "Q": 6,
           "R": 8, "S": 12, "T": 14, "U": 16, "V": 10, "W": 22, "X": 25, "Y": 24, "Z": 23}
_LET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def gen_cf():
    body = ("".join(random.choice(_LET) for _ in range(6))
            + f"{random.randint(0,99):02d}" + random.choice(_LET)
            + f"{random.randint(1,28):02d}" + random.choice(_LET)
            + f"{random.randint(100,999):03d}")
    t = sum((_CF_ODD[ch] if i % 2 == 0 else (int(ch) if ch.isdigit() else ord(ch) - 65))
            for i, ch in enumerate(body))
    return body + chr(65 + t % 26)


def gen_piva():
    d = [random.randint(0, 9) for _ in range(10)]
    t = 0
    for i, c in enumerate(d):
        if i % 2 == 0:
            t += c
        else:
            x = c * 2
            t += x - 9 if x > 9 else x
    return "".join(map(str, d)) + str((10 - t % 10) % 10)


def gen_iban():
    bban = random.choice(_LET) + "".join(str(random.randint(0, 9)) for _ in range(22))
    rearr = bban + "IT00"
    n = int("".join(str(ord(c) - 55) if c.isalpha() else c for c in rearr))
    check = 98 - (n % 97)
    return f"IT{check:02d}{bban}"


def gen_phone():
    if random.random() < 0.5:
        return f"+39 3{random.randint(10,99)} {random.randint(100,999)} {random.randint(1000,9999)}"
    return f"0{random.randint(11,99)} {random.randint(100000,9999999)}"


# --- pool testuali ------------------------------------------------------------
NOMI = ["Mario Rossi", "Giuseppe Bianchi", "Anna Verdi", "Luca Ferrari", "Maria Esposito",
        "Giovanni Russo", "Francesca Romano", "Paolo Gallo", "Chiara Conti", "Marco Greco",
        "Elena Costa", "Andrea Bruno", "Sara Rizzo", "Davide Marino", "Laura Ferri",
        "Stefano Lombardi", "Giulia Moretti", "Roberto Barbieri"]
ORG_PRE = ["Macelleria", "Panetteria", "Pasticceria", "Salumeria", "Bar", "Hotel",
           "Ristorante", "Trattoria", "Gastronomia", "Forno", "Azienda Agricola", "Caseificio"]
ORG_CORE = ["Aurora", "Da Luigi", "Il Buongustaio", "Centrale", "Belvedere", "San Marco",
            "Le Querce", "Del Borgo", "Da Mario", "La Fontana", "Vittoria", "Moderna"]
ORG_SUF = ["", " SRL", " SNC", " SAS", " SPA", ""]
CITTA = ["Torino", "Rivarolo Canavese", "Cuneo", "Asti", "Ivrea", "Chieri", "Pinerolo", "Alba"]
PROV = ["TO", "CN", "AT", "AL", "BI", "VC"]
VIE = ["Via Garibaldi", "Corso Italia", "Via Roma", "Piazza Castello", "Via Torino", "Corso Francia"]
PROD_NEG = [
    "quanto costa la pellicola H30?",
    "articoli disponibili famiglia rotoli, ordina per giacenza",
    "mostra gli ordini da evadere",
    "vendite per famiglia nel 2025",
    "prezzo e giacenza dell'alluminio",
    "cosa abbiamo nei rotoli cassa",
    "grafico a torta delle quote per famiglia",
    "scheda dell'articolo ROTO-028",
    "andamento del valore venduto per anno",
    "quali vaschette avete in magazzino",
    "ordini ai fornitori per alluminio",
    "i 10 articoli piu' venduti per valore",
    "giacenza dei sacchetti carta",
    "famiglia pasticceria, solo disponibili",
    "al contrario, ordina per esistenza",
]


def org():
    return (random.choice(ORG_PRE) + " " + random.choice(ORG_CORE) + random.choice(ORG_SUF)).strip()


# --- costruzione casi ---------------------------------------------------------
def build_cases():
    casi = []
    # FULLNAME (18)
    tmpl_p = ["scheda cliente {x}", "situazione di {x}", "{x} ha ordinato ieri",
              "le scadenze di {x}", "chiama {x} per il saldo", "il referente e' {x}"]
    for nome in NOMI:
        casi.append((random.choice(tmpl_p).format(x=nome), [("FULLNAME", nome)]))
    # ORG (24)
    tmpl_o = ["scadenze della {x}", "ordini della {x}", "fattura a {x}", "cliente {x}",
              "{x} non ha pagato", "saldo aperto di {x}", "apri la {x}"]
    for _ in range(24):
        o = org()
        casi.append((random.choice(tmpl_o).format(x=o), [("ORG", o)]))
    # CF (10)
    for _ in range(10):
        cf = gen_cf()
        casi.append((f"codice fiscale {cf} del cliente", [("CF", cf)]))
    # PIVA (10)
    for _ in range(10):
        p = gen_piva()
        casi.append((f"P.IVA {p} della ditta", [("PIVA", p)]))
    # IBAN (8)
    for _ in range(8):
        ib = gen_iban()
        casi.append((f"bonifico su IBAN {ib}", [("IBAN", ib)]))
    # EMAIL (8)
    for _ in range(8):
        nome = random.choice(NOMI).lower().replace(" ", ".")
        em = f"{nome}@azienda.it"
        casi.append((f"manda la fattura a {em}", [("EMAIL", em)]))
    # TELEFONO (8)
    for _ in range(8):
        ph = gen_phone()
        casi.append((f"telefono {ph}", [("TELEPHONENUM", ph)]))
    # INDIRIZZI (6) — multi-entita'
    for _ in range(6):
        via = random.choice(VIE); citta = random.choice(CITTA); pr = random.choice(PROV)
        casi.append((f"residente in {via} {random.randint(1,99)}, {citta} ({pr})",
                     [("STREET", via), ("CITY", citta), ("PROVINCE", pr)]))
    # MISTI (4)
    for _ in range(4):
        nome = random.choice(NOMI); cf = gen_cf(); ph = gen_phone()
        casi.append((f"{nome}, CF {cf}, tel {ph}",
                     [("FULLNAME", nome), ("CF", cf), ("TELEPHONENUM", ph)]))
    # NEGATIVI (15)
    for q in PROD_NEG:
        casi.append((q, []))
    return casi


def main():
    casi = build_cases()
    by_label, fp_neg, n_neg = {}, [], 0
    org_misses = []
    for text, expect in casi:
        spans = kept_spans(text)
        mask = covered_mask(spans, len(text))
        if not expect:
            n_neg += 1
            if spans:
                fp_neg.append((text, [(l, v) for l, v, _s, _e in spans]))
            continue
        for label, value in expect:
            hit, full = coverage_of(value, text, mask)
            rec = by_label.setdefault(label, [0, 0, 0])
            rec[0] += 1; rec[1] += 1 if hit else 0; rec[2] += 1 if full else 0
            if label == "ORG" and not full:
                org_misses.append((value, "PARZIALE" if hit else "MANCATO"))

    print("=" * 78)
    print(f"CASI: {len(casi)}  (positivi {len(casi)-n_neg}, negativi {n_neg})")
    print("=" * 78)
    print(f"{'LABEL':16s} {'attesi':>7} {'hit':>6} {'full':>6}   copertura")
    print("-" * 78)
    tot = [0, 0, 0]
    for label in sorted(by_label):
        n, hit, full = by_label[label]
        tot[0] += n; tot[1] += hit; tot[2] += full
        print(f"{label:16s} {n:>7} {hit:>6} {full:>6}   "
              f"hit {100*hit//n}% · full {100*full//n}%")
    print("-" * 78)
    n, hit, full = tot
    print(f"{'TOTALE':16s} {n:>7} {hit:>6} {full:>6}   hit {100*hit//n}% · full {100*full//n}%")
    print("=" * 78)
    print(f"NEGATIVI: {n_neg} senza PII · falsi positivi: {len(fp_neg)}")
    for text, ents in fp_neg:
        print(f"  [FP] {text}  -> {ents}")
    if org_misses:
        print("-" * 78)
        print("ORG non-full (il punto debole):")
        for v, k in org_misses:
            print(f"  {k:9s} {v!r}")
    print("=" * 78)


if __name__ == "__main__":
    main()
