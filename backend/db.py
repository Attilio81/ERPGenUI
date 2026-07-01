"""Data layer: read-only SELECT sulle viste AI di dbVittone (SQL Server via pyodbc).

Tutte le query sono parametriche e limitate. La vista vendite ha ~1.5M righe:
si filtra/aggrega sempre, mai SELECT *.
"""
from __future__ import annotations

import os
import threading
from datetime import datetime, date
from decimal import Decimal
from typing import Any

import pyodbc
from dotenv import load_dotenv

load_dotenv()

_CONN_STR = os.environ["DB_CONN"]
_CODDITT = os.environ.get("CODDITT", "VITC")  # multitenant: una ditta per deploy

# Una connessione per thread: FastAPI (endpoint sync) e i tool dell'agente girano
# sul threadpool anyio. pyodbc.Connection NON è thread-safe: condividerne una sola
# globale tra thread concorrenti corrompe la connessione -> ECONNRESET. thread-local
# dà a ogni thread la propria connessione, nessuna collisione.
_local = threading.local()


def _get_conn() -> pyodbc.Connection:
    conn = getattr(_local, "conn", None)
    if conn is None:
        conn = _local.conn = pyodbc.connect(_CONN_STR, timeout=15)
    return conn


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
        # connessione caduta: reset (solo di questo thread) e retry una volta
        conn = getattr(_local, "conn", None)
        try:
            if conn:
                conn.close()
        except Exception:
            pass
        _local.conn = None
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
        # tokenizza: ogni parola deve comparire (AND) in descrizione, codice o famiglia
        for tok in testo.split():
            where.append("(a.DescrArticolo LIKE ? OR a.CodArticolo LIKE ? OR a.DescrFamiglia LIKE ?)")
            params += [f"%{tok}%", f"%{tok}%", f"%{tok}%"]
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

    _ord_sql = """
        SELECT TOP 5 data_ordine AS data, ragione_sociale AS conto,
               quantita, (quantita - quantita_evasa) AS residuo,
               CASE WHEN quantita_evasa >= quantita THEN 'evaso' ELSE 'da evadere' END AS stato
        FROM {vista} WHERE codice_articolo = ? ORDER BY data_ordine DESC
    """
    art["ordini_clienti"] = _query(_ord_sql.format(vista="vw_EGM_AI_ordini_clienti"), [cod_art])
    art["ordini_fornitori"] = _query(_ord_sql.format(vista="vw_EGM_AI_ordini_fornitori"), [cod_art])

    # campi editabili (note non è nella vista AI: letto dalla tabella artico)
    nota = _query("SELECT TOP 1 ar_note AS note FROM artico WHERE ar_codart = ? AND codditt = ?", [cod_art, _CODDITT])
    art["note"] = (nota[0]["note"] if nota else None) or ""
    return art


# --- Scrittura (CRUD demo): whitelist colonne modificabili su ARTICO ---
_EDITABILI = {
    "descrizione": "ar_descr",
    "note": "ar_note",
    "peso_netto": "ar_pesonet",
}


def _execute_write(sql: str, params: list) -> int:
    global _conn
    try:
        cur = _get_conn().cursor()
        cur.execute(sql, params)
        _conn.commit()
        return cur.rowcount
    except pyodbc.Error:
        try:
            if _conn:
                _conn.close()
        except Exception:
            pass
        _conn = None
        cur = _get_conn().cursor()
        cur.execute(sql, params)
        _conn.commit()
        return cur.rowcount


def aggiorna_articolo(cod_art: str, campi: dict) -> int:
    """UPDATE su ARTICO, SOLO colonne in whitelist, parametrico. Ritorna righe modificate."""
    set_parts, params = [], []
    for chiave, valore in (campi or {}).items():
        col = _EDITABILI.get(chiave)
        if col is None or valore is None:
            continue
        set_parts.append(f"{col} = ?")
        params.append(valore)
    if not set_parts:
        return 0
    params += [cod_art, _CODDITT]
    sql = f"UPDATE artico SET {', '.join(set_parts)} WHERE ar_codart = ? AND codditt = ?"
    return _execute_write(sql, params)


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
        conds.append("(a.DescrArticolo LIKE ? OR a.CodArticolo LIKE ? OR a.DescrFamiglia LIKE ?)")
        params += [f"%{t}%", f"%{t}%", f"%{t}%"]
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


def _ordini(vista: str, solo_da_evadere: bool, articolo: str | None, anno: int | None, limit: int) -> list[dict]:
    limit = max(1, min(int(limit), 300))
    where, params = [], []
    if anno:
        where.append("anno = ?")
        params.append(int(anno))
    if solo_da_evadere:
        where.append("quantita > quantita_evasa")
    if articolo:
        for tok in articolo.split():
            where.append("(descrizione_articolo LIKE ? OR codice_articolo LIKE ?)")
            params += [f"%{tok}%", f"%{tok}%"]
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    sql = f"""
        SELECT TOP {limit}
            anno,
            numero_ordine            AS numero,
            data_ordine              AS data,
            ragione_sociale          AS conto,
            citta,
            codice_articolo          AS codice,
            descrizione_articolo     AS descrizione,
            unita_misura             AS um,
            quantita,
            quantita_evasa           AS evasa,
            (quantita - quantita_evasa) AS residuo,
            CASE WHEN quantita_evasa >= quantita THEN 'evaso' ELSE 'da evadere' END AS stato,
            data_consegna            AS consegna
        FROM {vista}
        {where_sql}
        ORDER BY data_ordine DESC, numero_ordine DESC
    """
    return _query(sql, params)


def ordini_clienti(solo_da_evadere: bool = False, articolo: str | None = None,
                   anno: int | None = None, limit: int = 200) -> list[dict]:
    """Righe ordini clienti (cosa hanno ordinato i clienti)."""
    return _ordini("vw_EGM_AI_ordini_clienti", solo_da_evadere, articolo, anno, limit)


def ordini_fornitori(solo_da_evadere: bool = False, articolo: str | None = None,
                     anno: int | None = None, limit: int = 200) -> list[dict]:
    """Righe ordini fornitori (cosa abbiamo ordinato ai fornitori / in arrivo)."""
    return _ordini("vw_EGM_AI_ordini_fornitori", solo_da_evadere, articolo, anno, limit)


# ============================ CLIENTI ============================

def cerca_clienti(testo: str | None = None, solo_con_scaduto: bool = False, limit: int = 200) -> list[dict]:
    """Elenco clienti (anagrafiche tipo Cliente) con match su ragione sociale / città / P.IVA."""
    limit = max(1, min(int(limit), 500))
    where = ["a.TipoAnagrafica = 'Cliente'"]
    params: list = []
    if testo:
        for tok in testo.split():
            where.append("(a.RagioneSociale LIKE ? OR a.Citta LIKE ? OR a.PartitaIVA LIKE ?)")
            params += [f"%{tok}%", f"%{tok}%", f"%{tok}%"]
    where_sql = " AND ".join(where)
    sql = f"""
        SELECT DISTINCT TOP {limit}
            a.CodiceConto    AS codice,
            a.RagioneSociale AS ragione_sociale,
            a.Citta          AS citta,
            a.Provincia      AS provincia,
            a.PartitaIVA     AS piva,
            a.DescrizioneZona AS zona,
            a.Stato          AS stato,
            a.Bloccato       AS bloccato
        FROM vw_EGM_AI_anagrafiche a
        WHERE {where_sql}
        ORDER BY a.RagioneSociale
    """
    return _query(sql, params)


def scheda_cliente(testo: str) -> dict | None:
    """Scheda cliente completa: anagrafica + KPI scadenze + scadenze aperte + ultimi ordini + top articoli."""
    testo = (testo or "").strip()
    if not testo:
        return None
    # 1) risoluzione cliente: prima codice esatto, poi miglior match ragione sociale
    base = """
        SELECT TOP 1 CodiceConto AS codice, RagioneSociale AS ragione_sociale,
               Indirizzo AS indirizzo, CAP AS cap, Citta AS citta, Provincia AS provincia,
               Telefono AS telefono, Cellulare AS cellulare, Email AS email,
               PartitaIVA AS piva, CodiceFiscale AS cf, CodiceAgente AS agente,
               DescrizioneZona AS zona, Stato AS stato, Bloccato AS bloccato,
               OrarioApertura AS orario, GiornoChiusura AS giorno_chiusura,
               DataUltimoDocumento AS ultimo_doc, Note AS note
        FROM vw_EGM_AI_anagrafiche WHERE TipoAnagrafica = 'Cliente' AND {cond}
    """
    rows = _query(base.format(cond="CodiceConto = ?"), [testo]) if testo.isdigit() else []
    if not rows:
        conds, params = [], []
        for tok in testo.split():
            conds.append("RagioneSociale LIKE ?")
            params.append(f"%{tok}%")
        rows = _query(base.format(cond=" AND ".join(conds) + " ORDER BY DataUltimoDocumento DESC"), params) if conds else []
    if not rows:
        return None
    cli = rows[0]
    cod = cli["codice"]

    kpi = _query(
        """
        SELECT ISNULL(SUM(importo_residuo),0) AS esposizione,
               ISNULL(SUM(CASE WHEN data_scadenza < GETDATE() THEN importo_residuo ELSE 0 END),0) AS scaduto,
               ISNULL(SUM(CASE WHEN flag_insoluto='S' THEN importo_residuo ELSE 0 END),0) AS insoluti,
               COUNT(*) AS n_scadenze
        FROM vw_EGM_AI_scadenze_aperte WHERE codice_cliente = ?
        """,
        [cod],
    )
    cli["kpi"] = kpi[0] if kpi else {"esposizione": 0, "scaduto": 0, "insoluti": 0, "n_scadenze": 0}

    cli["scadenze"] = _query(
        """
        SELECT TOP 30 data_scadenza AS scadenza, numero_documento AS documento,
               importo_residuo AS residuo, flag_insoluto AS insoluto,
               CASE WHEN flag_insoluto='S' THEN 'insoluto'
                    WHEN data_scadenza < GETDATE() THEN 'scaduto'
                    ELSE 'a scadere' END AS stato
        FROM vw_EGM_AI_scadenze_aperte WHERE codice_cliente = ?
        ORDER BY data_scadenza
        """,
        [cod],
    )

    cli["ultimi_ordini"] = _query(
        """
        SELECT TOP 6 data_ordine AS data, descrizione_articolo AS articolo,
               quantita, (quantita - quantita_evasa) AS residuo,
               CASE WHEN quantita_evasa >= quantita THEN 'evaso' ELSE 'da evadere' END AS stato
        FROM vw_EGM_AI_ordini_clienti WHERE codice_conto = ?
        ORDER BY data_ordine DESC
        """,
        [cod],
    )

    cli["top_articoli"] = _query(
        """
        SELECT TOP 8 DescrizioneArticolo AS articolo, SUM(ValoreTotale) AS valore
        FROM vw_EGM_AI_vendite WHERE CodiceCliente = ?
        GROUP BY DescrizioneArticolo ORDER BY valore DESC
        """,
        [cod],
    )
    return cli


_EDITABILI_CLIENTE = {
    "telefono": "an_telef",
    "cellulare": "an_cell",
    "email": "an_email",
    "note": "an_note",
}


def aggiorna_cliente(cod_conto: str, campi: dict) -> int:
    """UPDATE su ANAGRA, whitelist colonne (telefono/cellulare/email/note), parametrico."""
    set_parts, params = [], []
    for chiave, valore in (campi or {}).items():
        col = _EDITABILI_CLIENTE.get(chiave)
        if col is None or valore is None:
            continue
        set_parts.append(f"{col} = ?")
        params.append(valore)
    if not set_parts:
        return 0
    params += [cod_conto, _CODDITT]
    sql = f"UPDATE anagra SET {', '.join(set_parts)} WHERE an_conto = ? AND codditt = ?"
    return _execute_write(sql, params)


def anni_disponibili() -> list[int]:
    rows = _query("SELECT DISTINCT Anno FROM vw_EGM_AI_vendite ORDER BY Anno DESC")
    return [int(r["Anno"]) for r in rows if r["Anno"] is not None]
