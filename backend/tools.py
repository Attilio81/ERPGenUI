"""Tool dell'agent — regime STRICT.

Ogni tool:
  1. esegue la query (dati reali Vittone),
  2. scrive dati + controllo in session_state (→ emesso al frontend via AG-UI STATE),
  3. ritorna all'LLM SOLO un conteggio/conferma.

DeepSeek non vede mai i dati: l'agent è configurato con add_session_state_to_context=False,
quindi il contenuto di session_state non entra nel prompt. Orchestrazione sì, dati no.
"""
from __future__ import annotations

from agno.run import RunContext
from agno.tools import tool

import db

INITIAL_STATE: dict = {
    "view": "table",          # table | detail | chart
    "filtri": {},
    "sort": {"campo": "descrizione", "dir": "asc"},
    "count": 0,
    "selected_codart": None,
    "chart_spec": None,
    # payload dati (resta fuori dal contesto LLM)
    "rows": [],
    "articolo": None,
    "chart_titolo": "",
    "chart_dati": [],
    "rows_ordini": [],
    "ordini_tipo": "clienti",
    "ordini_titolo": "",
}


@tool()
def cerca_articoli(
    run_context: RunContext,
    famiglia: str | None = None,
    fornitore: str | None = None,
    solo_disponibili: bool | None = None,
    testo: str | None = None,
    ordina_per: str | None = None,
    discendente: bool | None = None,
    reset: bool = False,
) -> str:
    """Cerca/filtra/ordina gli articoli e aggiorna la tabella. Filtri "sticky": i parametri
    NON passati ereditano la ricerca precedente (è un raffinamento). Passa solo ciò che cambia.

    Ordina per: descrizione, codice, famiglia, esistenza, disponibile.

    Args:
        famiglia: famiglia/categoria (testo parziale). Ometti per mantenere quella corrente.
        fornitore: ragione sociale fornitore (testo parziale). Ometti per mantenere.
        solo_disponibili: True per soli articoli con esistenza > 0. Ometti per mantenere.
        testo: ricerca libera su descrizione/codice. Ometti per mantenere.
        ordina_per: campo di ordinamento. Ometti per mantenere l'ordinamento corrente.
        discendente: direzione. Ometti: default sensato (esistenza/disponibile = decrescente).
        reset: True per AZZERARE tutti i filtri (es. "mostra tutti gli articoli", "nuova ricerca").
    """
    ss = run_context.session_state
    prev_f = {} if reset else (ss.get("filtri") or {})
    prev_s = {} if reset else (ss.get("sort") or {})

    # merge: il valore nuovo (non None) vince, altrimenti eredita il precedente
    famiglia = famiglia if famiglia is not None else prev_f.get("famiglia")
    fornitore = fornitore if fornitore is not None else prev_f.get("fornitore")
    testo = testo if testo is not None else prev_f.get("testo")
    solo_disponibili = solo_disponibili if solo_disponibili is not None else bool(prev_f.get("solo_disponibili"))
    ordina_per = ordina_per or prev_s.get("campo") or "descrizione"
    if discendente is None:
        discendente = ordina_per in ("esistenza", "disponibile")  # default scorta più alta in cima

    rows = db.cerca_articoli(
        famiglia=famiglia, fornitore=fornitore, solo_disponibili=solo_disponibili,
        testo=testo, ordina_per=ordina_per, discendente=discendente,
    )
    ss["view"] = "table"
    ss["filtri"] = {
        "famiglia": famiglia, "fornitore": fornitore,
        "solo_disponibili": solo_disponibili, "testo": testo,
    }
    ss["sort"] = {"campo": ordina_per, "dir": "desc" if discendente else "asc"}
    ss["count"] = len(rows)
    ss["rows"] = rows
    ss["articolo"] = None

    attivi = []
    if famiglia:
        attivi.append(f"famiglia={famiglia}")
    if fornitore:
        attivi.append(f"fornitore={fornitore}")
    if testo:
        attivi.append(f"testo={testo}")
    if solo_disponibili:
        attivi.append("solo disponibili")
    filtri_str = "; ".join(attivi) or "nessuno"
    verso = "decrescente" if discendente else "crescente"
    # L'eco dei filtri (non sensibili) resta nella storia chat -> abilita i follow-up.
    return (
        f"Mostrati {len(rows)} articoli. Filtri attivi: {filtri_str}. "
        f"Ordinati per {ordina_per} ({verso})."
    )


@tool()
def dettaglio_articolo(run_context: RunContext, cod_art: str | None = None) -> str:
    """Mostra la scheda di un articolo e RESTITUISCE prezzo + giacenza (per dirli a voce).
    Usalo anche per follow-up tipo "quanto costa", "quante ne ho", "dettagli": se NON passi
    cod_art, usa l'articolo della scheda attualmente aperta.

    Args:
        cod_art: codice articolo esatto (es. 'ROTO-028'). Omettilo per l'articolo corrente.
    """
    ss = run_context.session_state
    if not cod_art:
        cod_art = ss.get("selected_codart")
    if not cod_art:
        return "Nessun articolo indicato e nessuna scheda aperta. Dimmi il codice o cerca un prodotto."
    art = db.dettaglio_articolo(cod_art)
    if art is None:
        return f"Nessun articolo trovato con codice {cod_art}."
    ss["view"] = "detail"
    ss["selected_codart"] = cod_art
    ss["articolo"] = art

    # Fatti di PRODOTTO per l'LLM (non personali): prezzo + giacenza, così può
    # rispondere a "quanto costa / quante ne ho". Le ultime vendite (nomi clienti)
    # NON tornano all'LLM: restano solo a schermo.
    disp = art.get("disponibilita") or {}
    esist = disp.get("esistenza", 0) or 0
    imp = disp.get("impegnato", 0) or 0
    dispo = esist - imp
    listini = art.get("listini") or []
    prezzo = next((l.get("prezzo") for l in listini if l.get("listino") == 1), None)
    if prezzo is None and listini:
        prezzo = listini[0].get("prezzo")
    prezzo_str = f"{prezzo:.2f} €" if prezzo is not None else "n/d"
    return (
        f"Scheda di {cod_art} — {art.get('descrizione','')}. "
        f"Prezzo di listino: {prezzo_str}. Esistenza {int(esist)}, "
        f"disponibile {int(dispo)} {art.get('um','')}. "
        f"Listini completi e ultime vendite sono mostrati a schermo."
    )


@tool()
def grafico_vendite(
    run_context: RunContext,
    dimensione: str = "famiglia",
    misura: str = "valore",
    anno: int | None = None,
    famiglia: str | None = None,
    tipo_grafico: str | None = None,
) -> str:
    """Disegna un grafico delle vendite aggregate. Usalo anche per gli articoli più venduti
    (dimensione='articolo'): restituisce i primi per valore/quantità.

    Args:
        dimensione: come raggruppare — 'articolo', 'famiglia', 'agente', 'cliente', 'anno'.
        misura: cosa sommare — 'valore' (€) oppure 'quantita'.
        anno: filtra per anno (es. 2024, 2025, 2026). Opzionale.
        famiglia: filtra per famiglia. Opzionale.
        tipo_grafico: tipo di visualizzazione — scegli in base alla domanda:
            'linea' per ANDAMENTI nel tempo (es. per anno), 'torta' per QUOTE/composizione
            (poche categorie), 'barre' per CLASSIFICHE/confronti. Ometti per il default.
    """
    dati = db.vendite_aggregate(dimensione=dimensione, misura=misura, anno=anno, famiglia=famiglia)
    mis_label = "Valore (€)" if misura == "valore" else "Quantità"
    titolo = f"{mis_label} per {dimensione}" + (f" — {anno}" if anno else "")

    # tipo: default sensato + guardrail (constrained UI)
    richiesto = (tipo_grafico or "").lower()
    tipo = richiesto if richiesto in ("barre", "linea", "torta", "area") else (
        "linea" if dimensione == "anno" else "barre"
    )
    # torta: per restare leggibile, top 7 + "Altri" (somma della coda)
    chart_dati = dati
    note = ""
    if tipo == "torta" and len(dati) > 8:
        coda = sum(d["valore"] for d in dati[7:])
        chart_dati = dati[:7] + [{"etichetta": "Altri", "valore": coda}]
        note = f" (torta: prime 7 voci + 'Altri'; {len(dati)} totali)"

    ss = run_context.session_state
    ss["view"] = "chart"
    ss["chart_spec"] = {"dimensione": dimensione, "misura": misura, "anno": anno,
                        "famiglia": famiglia, "tipo": tipo}
    ss["chart_titolo"] = titolo
    ss["chart_dati"] = chart_dati

    tipo_str = f"grafico a {tipo}{note}"
    # Dimensioni personali (cliente/agente): le etichette sono nomi -> solo a schermo.
    if dimensione in ("cliente", "agente"):
        return (
            f"Mostrato {tipo_str}: {titolo} ({len(dati)} voci). Le etichette per "
            f"'{dimensione}' sono dati personali: NON elencarle, sono solo a schermo."
        )
    # Dimensioni non personali (articolo/famiglia/anno): puoi riferire i primi.
    def _v(x):
        return f"{x:.2f} €" if misura == "valore" else f"{int(x)}"
    top = dati[:5]
    righe = "\n".join(f"- {d['etichetta']}: {_v(d['valore'])}" for d in top)
    extra = f"\n(+ altre {len(dati) - 5} voci a schermo)" if len(dati) > 5 else ""
    return (
        f"Mostrato {tipo_str}: {titolo} ({len(dati)} voci). "
        f"Primi {len(top)} (riportabili):\n{righe}{extra}"
    )


@tool()
def trova_prezzo(run_context: RunContext, testo: str) -> str:
    """Trova prodotti per nome o codice e RESTITUISCE prezzo e giacenza, così puoi dirli
    a voce all'utente. Usalo per domande tipo "quanto costa X", "avete X?", "prezzo di X".
    Restituisce SOLO dati di prodotto (codice, descrizione, prezzo di listino, giacenza):
    sono informazioni non personali, puoi riportarle nella risposta. Mostra anche la tabella.

    Args:
        testo: parola/e da cercare nella descrizione o codice (es. "pellicola 30", "alluminio").
    """
    rows = db.trova_prezzo(testo)
    ss = run_context.session_state
    ss["view"] = "table"
    ss["filtri"] = {"testo": testo}
    ss["sort"] = {"campo": "esistenza", "dir": "desc"}
    ss["count"] = len(rows)
    ss["rows"] = rows
    ss["articolo"] = None

    if not rows:
        return f"Nessun prodotto trovato per '{testo}'."

    righe = []
    for r in rows[:8]:
        prezzo = f"{r['prezzo']:.2f} €" if r.get("prezzo") is not None else "prezzo n/d"
        righe.append(
            f"- {r['codice']} · {r['descrizione']} · {prezzo} · giacenza {int(r['disponibile'])} {r['um']}"
        )
    extra = f"\n(+ altri {len(rows) - 8} in tabella)" if len(rows) > 8 else ""
    return (
        f"Trovati {len(rows)} prodotti per '{testo}' (prezzo di listino, giacenza disponibile). "
        f"Puoi riferire questi dati di prodotto:\n" + "\n".join(righe) + extra
    )


def _mostra_ordini(ss, tipo: str, titolo: str, rows: list) -> str:
    ss["view"] = "ordini"
    ss["ordini_tipo"] = tipo
    ss["ordini_titolo"] = titolo
    ss["rows_ordini"] = rows
    ss["count"] = len(rows)
    da_evadere = sum(1 for r in rows if r.get("stato") == "da evadere")
    return f"Mostrati {len(rows)} righe d'ordine in tabella ({da_evadere} da evadere)."


@tool()
def ordini_clienti(
    run_context: RunContext,
    solo_da_evadere: bool = False,
    articolo: str | None = None,
    anno: int | None = None,
) -> str:
    """Mostra le righe degli ORDINI dei CLIENTI (cosa hanno ordinato i clienti).

    Args:
        solo_da_evadere: True per i soli ordini non ancora evasi (residuo > 0).
        articolo: filtra per descrizione/codice articolo (parole-chiave).
        anno: filtra per anno dell'ordine.
    """
    rows = db.ordini_clienti(solo_da_evadere=solo_da_evadere, articolo=articolo, anno=anno)
    titolo = "Ordini clienti" + (" da evadere" if solo_da_evadere else "")
    return _mostra_ordini(run_context.session_state, "clienti", titolo, rows)


@tool()
def ordini_fornitori(
    run_context: RunContext,
    solo_da_evadere: bool = False,
    articolo: str | None = None,
    anno: int | None = None,
) -> str:
    """Mostra le righe degli ORDINI ai FORNITORI (cosa abbiamo ordinato / merce in arrivo).

    Args:
        solo_da_evadere: True per i soli ordini non ancora evasi (in arrivo).
        articolo: filtra per descrizione/codice articolo (parole-chiave).
        anno: filtra per anno dell'ordine.
    """
    rows = db.ordini_fornitori(solo_da_evadere=solo_da_evadere, articolo=articolo, anno=anno)
    titolo = "Ordini fornitori" + (" da evadere (in arrivo)" if solo_da_evadere else "")
    return _mostra_ordini(run_context.session_state, "fornitori", titolo, rows)


TOOLS = [cerca_articoli, dettaglio_articolo, grafico_vendite, trova_prezzo,
         ordini_clienti, ordini_fornitori]
