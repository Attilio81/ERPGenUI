# -*- coding: utf-8 -*-
"""Prova/eval rapida del modello PII su frasi italiane realistiche (stile gestionale).

Importa analyze() da service.py (carica il modello una volta) e stampa, per ogni frase,
le entità trovate + il testo anonimizzato. Serve a EYEBALLARE il recall sui casi nostri
(nomi clienti, CF, P.IVA, IBAN, indirizzi) PRIMA di fidarsi della guardia.

  python prova.py
"""
from service import analyze

ESEMPI = [
    "scheda cliente Mario Rossi",
    "scadenze ed esposizione del cliente Macelleria Lucco Borlera di Rivarolo",
    "apri la situazione di Bianchi Giuseppe, P.IVA 12345678903",
    "il cliente con codice fiscale RSSMRA85M01H501Z ha pagato?",
    "bonifico su IBAN IT60X0542811101000000123456 per la Panetteria Da Luigi",
    "telefono del cliente 011 1234567, oppure 333 1234567",
    "manda la fattura a mario.rossi@panetteria.it",
    "ordini da evadere della Pasticceria Aurora SRL di Torino (TO)",
    "quanto costa la pellicola H30?",            # nessuna PII -> deve restare intatta
    "articoli disponibili famiglia rotoli, ordina per giacenza",  # nessuna PII
]


def main():
    for t in ESEMPI:
        out = analyze(t)
        print("=" * 78)
        print("IN  :", t)
        print("OUT :", out["anonymized_text"])
        if out["mapping"]:
            for ph, val in out["mapping"].items():
                print(f"      {ph:16s} <- {val!r}")
        else:
            print("      (nessuna PII rilevata)")
    print("=" * 78)


if __name__ == "__main__":
    main()
