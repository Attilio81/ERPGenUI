# PATCH per rizzo-pii/src/data_pipeline/generate_synthetic_pii.py
# Aggiunge un generatore di "ditta individuale" (ragione sociale che CONTIENE un nome
# persona, es. "Autofficina di Giorgio Catalano"), con varianti TUTTO MAIUSCOLO tipiche
# dei gestionali. Tutta la stringa e' etichettata ORG -> insegna al modello i nomi-ditta
# all-caps e i casi misti persona+azienda (il punto debole del tag ORG).
#
# COME APPLICARLA:
#   1. Incolla i due blocchi qui sotto in generate_synthetic_pii.py:
#      - la funzione `ditta_individuale` + `DITTA_PREFIX`/`DITTA_ABBR` vicino a `org_piece`
#      - la funzione `ditta_list` vicino a `mixed_list`
#   2. Registra i due slot nel dizionario SLOTS:
#        "DITTAIND": ditta_individuale, "DITTALIST": ditta_list,
#   3. Copia legal_templates.json in rizzo-pii/dataset/synthetic/
#   4. Genera in --offline (vedi README.md di questa cartella).

# --- BLOCCO 1: vicino a org_piece() -----------------------------------------
DITTA_PREFIX = ["Alimentari", "Macelleria", "Panetteria", "Panificio", "Pasticceria",
                "Salumeria", "Gastronomia", "Rosticceria", "Ristorante", "Trattoria",
                "Osteria", "Pizzeria", "Bar", "Caffe'", "Hotel", "Albergo", "Ferramenta",
                "Autofficina", "Autotrasporti", "Impresa Edile", "Falegnameria", "Cartoleria",
                "Parruccheria", "Estetica", "Ottica", "Idraulica", "Elettrauto", "Tabaccheria"]
DITTA_ABBR = {"Alimentari": "Alim.", "Autotrasporti": "Autotrasp.", "Impresa Edile": "Imp. Edile",
              "Falegnameria": "Falegn.", "Macelleria": "Macell."}

def ditta_individuale():
    pre = random.choice(DITTA_PREFIX)
    if random.random() < 0.35 and pre in DITTA_ABBR:
        pre = DITTA_ABBR[pre]
    g, s, _ = _person()
    g2, s2, _ = _person()
    r = random.random()
    if r < 0.30:
        name = f"{pre} di {g} {s}"
    elif r < 0.50:
        name = f"{pre} {s} di {g} {s}"
    elif r < 0.66:
        name = f"{pre} da {g}"
    elif r < 0.80:
        name = f"{pre} {g} {s}"
    elif r < 0.90:
        name = f"{pre} F.lli {s}"
    else:
        name = f"{pre} {s} & {s2}"
    if random.random() < 0.45:      # grafia gestionale: TUTTO MAIUSCOLO
        name = name.upper()
    return [(name, "ORG")]

# --- BLOCCO 2: vicino a mixed_list() ----------------------------------------
def ditta_list():
    sep = random.choice(LIST_SEPS)
    out = []
    for i in range(random.randint(2, 6)):
        if i:
            out.append((sep, None))
        out.extend(ditta_individuale())
    return out

# --- BLOCCO 3: nel dizionario SLOTS -----------------------------------------
#   "DITTAIND": ditta_individuale, "DITTALIST": ditta_list,
