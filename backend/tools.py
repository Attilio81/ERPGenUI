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
}


@tool()
def cerca_articoli(
    run_context: RunContext,
    famiglia: str | None = None,
    fornitore: str | None = None,
    solo_disponibili: bool = False,
    testo: str | None = None,
    ordina_per: str = "descrizione",
    discendente: bool = False,
) -> str:
    """Cerca articoli e mostra la tabella all'utente. Filtra per famiglia, fornitore, testo libero,
    solo disponibili (giacenza > 0). Ordina per: descrizione, codice, famiglia, esistenza, disponibile.

    Args:
        famiglia: famiglia/categoria merceologica (testo parziale).
        fornitore: ragione sociale fornitore (testo parziale).
        solo_disponibili: se True mostra solo articoli con esistenza > 0.
        testo: ricerca libera su descrizione o codice articolo.
        ordina_per: campo di ordinamento (descrizione, codice, famiglia, esistenza, disponibile).
        discendente: True per ordine decrescente.
    """
    rows = db.cerca_articoli(
        famiglia=famiglia, fornitore=fornitore, solo_disponibili=solo_disponibili,
        testo=testo, ordina_per=ordina_per, discendente=discendente,
    )
    ss = run_context.session_state
    ss["view"] = "table"
    ss["filtri"] = {
        "famiglia": famiglia, "fornitore": fornitore,
        "solo_disponibili": solo_disponibili, "testo": testo,
    }
    ss["sort"] = {"campo": ordina_per, "dir": "desc" if discendente else "asc"}
    ss["count"] = len(rows)
    ss["rows"] = rows
    ss["articolo"] = None
    return f"Mostrati {len(rows)} articoli in tabella."


@tool()
def dettaglio_articolo(run_context: RunContext, cod_art: str) -> str:
    """Mostra la scheda di dettaglio di un singolo articolo (anagrafica, disponibilità,
    prezzi di listino, ultime vendite).

    Args:
        cod_art: codice articolo esatto (es. 'ROTO-028').
    """
    art = db.dettaglio_articolo(cod_art)
    if art is None:
        return f"Nessun articolo trovato con codice {cod_art}."
    ss = run_context.session_state
    ss["view"] = "detail"
    ss["selected_codart"] = cod_art
    ss["articolo"] = art
    return f"Mostrata la scheda dell'articolo {cod_art}."


@tool()
def grafico_vendite(
    run_context: RunContext,
    dimensione: str = "famiglia",
    misura: str = "valore",
    anno: int | None = None,
    famiglia: str | None = None,
) -> str:
    """Disegna un grafico delle vendite aggregate. Usalo anche per gli articoli più venduti
    (dimensione='articolo'): restituisce i primi per valore/quantità.

    Args:
        dimensione: come raggruppare — 'articolo', 'famiglia', 'agente', 'cliente', 'anno'.
        misura: cosa sommare — 'valore' (€) oppure 'quantita'.
        anno: filtra per anno (es. 2024, 2025, 2026). Opzionale.
        famiglia: filtra per famiglia. Opzionale.
    """
    dati = db.vendite_aggregate(dimensione=dimensione, misura=misura, anno=anno, famiglia=famiglia)
    mis_label = "Valore (€)" if misura == "valore" else "Quantità"
    titolo = f"{mis_label} per {dimensione}" + (f" — {anno}" if anno else "")
    ss = run_context.session_state
    ss["view"] = "chart"
    ss["chart_spec"] = {"dimensione": dimensione, "misura": misura, "anno": anno, "famiglia": famiglia}
    ss["chart_titolo"] = titolo
    ss["chart_dati"] = dati
    return f"Mostrato il grafico: {titolo} ({len(dati)} voci)."


TOOLS = [cerca_articoli, dettaglio_articolo, grafico_vendite]
