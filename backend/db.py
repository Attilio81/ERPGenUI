"""Data layer: read-only SELECT sulle viste AI di dbVittone (SQL Server via pyodbc).

Tutte le query sono parametriche e limitate. La vista vendite ha ~1.5M righe:
si filtra/aggrega sempre, mai SELECT *.
"""
from __future__ import annotations

import os
from datetime import datetime, date
from decimal import Decimal
from typing import Any

import pyodbc
from dotenv import load_dotenv

load_dotenv()

_CONN_STR = os.environ["DB_CONN"]
_conn: pyodbc.Connection | None = None


def _get_conn() -> pyodbc.Connection:
    global _conn
    if _conn is None:
        _conn = pyodbc.connect(_CONN_STR, timeout=15)
    return _conn


def _jsonify(v: Any) -> Any:
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, str):
        return v.strip()
    return v


def _rows(cursor) -> list[dict]:
    cols = [c[0] for c in cursor.description]
    return [{c: _jsonify(v) for c, v in zip(cols, row)} for row in cursor.fetchall()]


def _query(sql: str, params: list | None = None) -> list[dict]:
    try:
        cur = _get_conn().cursor()
        cur.execute(sql, params or [])
        return _rows(cur)
    except pyodbc.Error:
        # connessione caduta: reset e retry una volta
        global _conn
        try:
            if _conn:
                _conn.close()
        except Exception:
            pass
        _conn = None
        cur = _get_conn().cursor()
        cur.execute(sql, params or [])
        return _rows(cur)


# --- whitelist ordinamento (anti SQL injection sui nomi colonna) ---
_SORT_MAP = {
    "descrizione": "a.DescrArticolo",
    "codice": "a.CodArticolo",
    "famiglia": "a.DescrFamiglia",
    "esistenza": "ISNULL(d.esistenza, 0)",
    "disponibile": "(ISNULL(d.esistenza,0) - ISNULL(d.impegnato_clienti,0))",
}


def cerca_articoli(
    famiglia: str | None = None,
    fornitore: str | None = None,
    solo_disponibili: bool = False,
    testo: str | None = None,
    ordina_per: str = "descrizione",
    discendente: bool = False,
    limit: int = 200,
) -> list[dict]:
    """Anagrafica + disponibilità, con filtri opzionali."""
    where: list[str] = []
    params: list = []
    if famiglia:
        where.append("(a.DescrFamiglia LIKE ? OR a.CodFamiglia = ?)")
        params += [f"%{famiglia}%", famiglia]
    if fornitore:
        where.append("a.DescrFornitore LIKE ?")
        params.append(f"%{fornitore}%")
    if testo:
        where.append("(a.DescrArticolo LIKE ? OR a.CodArticolo LIKE ?)")
        params += [f"%{testo}%", f"%{testo}%"]
    if solo_disponibili:
        where.append("ISNULL(d.esistenza, 0) > 0")

    order_col = _SORT_MAP.get(ordina_per, _SORT_MAP["descrizione"])
    direction = "DESC" if discendente else "ASC"
    limit = max(1, min(int(limit), 500))
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    sql = f"""
        SELECT TOP {limit}
            a.CodArticolo       AS codice,
            a.DescrArticolo     AS descrizione,
            a.DescrFamiglia     AS famiglia,
            a.DescrFornitore    AS fornitore,
            a.UnitaMisura       AS um,
            ISNULL(d.esistenza, 0)            AS esistenza,
            ISNULL(d.impegnato_clienti, 0)    AS impegnato,
            ISNULL(d.ordinato_fornitori, 0)   AS ordinato,
            (ISNULL(d.esistenza,0) - ISNULL(d.impegnato_clienti,0)) AS disponibile
        FROM vw_EGM_AI_anagraficaarticoli a
        LEFT JOIN vw_EGM_AI_disponibilita_articoli d
               ON a.CodArticolo = d.codice_articolo
        {where_sql}
        ORDER BY {order_col} {direction}
    """
    return _query(sql, params)


def dettaglio_articolo(cod_art: str) -> dict | None:
    """Scheda completa: anagrafica + disponibilità + prezzo listino + ultime vendite."""
    ana = _query(
        """
        SELECT TOP 1 CodArticolo AS codice, DescrArticolo AS descrizione,
               DescrFamiglia AS famiglia, DescrFornitore AS fornitore,
               UnitaMisura AS um, PesoNetto AS peso_netto, PesoLordo AS peso_lordo
        FROM vw_EGM_AI_anagraficaarticoli WHERE CodArticolo = ?
        """,
        [cod_art],
    )
    if not ana:
        return None
    art = ana[0]

    disp = _query(
        """
        SELECT TOP 1 esistenza, ordinato_fornitori AS ordinato,
               impegnato_clienti AS impegnato
        FROM vw_EGM_AI_disponibilita_articoli WHERE codice_articolo = ?
        """,
        [cod_art],
    )
    art["disponibilita"] = disp[0] if disp else {"esistenza": 0, "ordinato": 0, "impegnato": 0}

    listino = _query(
        """
        SELECT TOP 5 NumeroListino AS listino, DescrizioneListino AS descr_listino,
               Prezzo AS prezzo, PrezzoNetto AS prezzo_netto, UnitaMisura AS um
        FROM vw_EGM_AI_listini
        WHERE CodiceArticolo = ? AND CodiceClienteSpecifico IS NULL
              AND GETDATE() BETWEEN DataInizioValidita AND DataFineValidita
        ORDER BY NumeroListino
        """,
        [cod_art],
    )
    art["listini"] = listino

    vendite = _query(
        """
        SELECT TOP 8 DataMovimento AS data, RagioneSocialeCliente AS cliente,
               Quantita AS quantita, ValoreTotale AS valore
        FROM vw_EGM_AI_vendite
        WHERE CodiceArticolo = ?
        ORDER BY DataMovimento DESC
        """,
        [cod_art],
    )
    art["ultime_vendite"] = vendite
    return art


_DIM_MAP = {
    "famiglia": "Famiglia",
    "agente": "DescrizioneAgente",
    "cliente": "RagioneSocialeCliente",
    "articolo": "DescrizioneArticolo",
    "anno": "Anno",
}
_MIS_MAP = {
    "valore": "ValoreTotale",
    "quantita": "Quantita",
}


def vendite_aggregate(
    dimensione: str = "famiglia",
    misura: str = "valore",
    anno: int | None = None,
    famiglia: str | None = None,
    limit: int = 15,
) -> list[dict]:
    """Aggregato vendite per grafico: SUM(misura) GROUP BY dimensione."""
    dim_col = _DIM_MAP.get(dimensione, "Famiglia")
    mis_col = _MIS_MAP.get(misura, "ValoreTotale")
    limit = max(1, min(int(limit), 50))

    where: list[str] = []
    params: list = []
    if anno:
        where.append("Anno = ?")
        params.append(int(anno))
    if famiglia:
        where.append("Famiglia LIKE ?")
        params.append(f"%{famiglia}%")
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    order = f"valore DESC" if dimensione != "anno" else f"{dim_col} ASC"
    sql = f"""
        SELECT TOP {limit}
               {dim_col} AS etichetta,
               SUM({mis_col}) AS valore
        FROM vw_EGM_AI_vendite
        {where_sql}
        GROUP BY {dim_col}
        ORDER BY {order}
    """
    return _query(sql, params)


def trova_prezzo(testo: str, limit: int = 12) -> list[dict]:
    """Prodotti che matchano testo/codice, con prezzo (listino 1) e giacenza.
    Solo dati di prodotto: nessun dato personale (clienti/vendite)."""
    limit = max(1, min(int(limit), 30))
    # tokenizza: ogni parola deve comparire (AND) in descrizione o codice.
    tokens = [t for t in (testo or "").split() if t]
    if not tokens:
        return []
    conds, params = [], []
    for t in tokens:
        conds.append("(a.DescrArticolo LIKE ? OR a.CodArticolo LIKE ?)")
        params += [f"%{t}%", f"%{t}%"]
    where = " AND ".join(conds)
    sql = f"""
        SELECT TOP {limit}
            a.CodArticolo    AS codice,
            a.DescrArticolo  AS descrizione,
            a.DescrFamiglia  AS famiglia,
            a.DescrFornitore AS fornitore,
            a.UnitaMisura    AS um,
            ISNULL(d.esistenza, 0)            AS esistenza,
            ISNULL(d.impegnato_clienti, 0)    AS impegnato,
            ISNULL(d.ordinato_fornitori, 0)   AS ordinato,
            (ISNULL(d.esistenza,0) - ISNULL(d.impegnato_clienti,0)) AS disponibile,
            lp.Prezzo        AS prezzo
        FROM vw_EGM_AI_anagraficaarticoli a
        LEFT JOIN vw_EGM_AI_disponibilita_articoli d
               ON a.CodArticolo = d.codice_articolo
        OUTER APPLY (
            SELECT TOP 1 l.Prezzo
            FROM vw_EGM_AI_listini l
            WHERE l.CodiceArticolo = a.CodArticolo
              AND l.NumeroListino = 1
              AND l.CodiceClienteSpecifico IS NULL
              AND GETDATE() BETWEEN l.DataInizioValidita AND l.DataFineValidita
            ORDER BY l.QuantitaDa
        ) lp
        WHERE {where}
        ORDER BY ISNULL(d.esistenza, 0) DESC
    """
    return _query(sql, params)


def anni_disponibili() -> list[int]:
    rows = _query("SELECT DISTINCT Anno FROM vw_EGM_AI_vendite ORDER BY Anno DESC")
    return [int(r["Anno"]) for r in rows if r["Anno"] is not None]
