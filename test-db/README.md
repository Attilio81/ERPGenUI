# DB di test (usa-e-getta)

SQL Server 2022 in Docker con le viste che il backend legge, riempito con **dati
sintetici** (nessun dato reale cliente). Serve per far girare il backend dopo un
`git clone` senza accesso al gestionale del cliente.

Cosa NON copre: il modello LLM. Quello lo metti tu (chiave cloud nel `.env`
oppure `AI_PROVIDER=local` con Ollama). Vedi `backend/.env.test`.

## Avvio (1 comando)

Serve **Docker Desktop**.

```bash
cd test-db
docker compose up          # avvia SQL Server + esegue seed.sql (~30-60s la 1ª volta)
```

Il servizio `seed` esce da solo quando ha finito; `db` resta su sulla porta `1433`.
Per fermare e **buttare tutto** (dati inclusi):

```bash
docker compose down -v
```

## Collega il backend

```bash
copy ..\backend\.env.test ..\backend\.env    # Windows
# cp ../backend/.env.test ../backend/.env     # Linux/mac
```

`.env.test` punta già a `localhost,1433 / ERPTEST / sa`. Poi avvia il backend come
di consueto (`avvia-lan.bat`, o `uvicorn agent:app`).

## Verifica rapida

Dalla root del repo, con il venv del backend attivo (non serve la chiave LLM):

```bash
python test-db/smoke_test.py
```

Esercita `backend/db.py` contro il container (scheda articolo, ricerca, prezzi,
grafico, ordini, scheda cliente) e stampa OK/FAIL per ciascuno.

Oppure query diretta nel container:

```bash
docker exec -it erp-testdb /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
  -P 'Test_Str0ng!Pass' -d ERPTEST -Q "SELECT TOP 3 CodArticolo, DescrArticolo FROM vw_EGM_AI_anagraficaarticoli"
```

## Cosa c'è dentro

- 10 articoli (incl. i codici delle demo: `ROTO-028`, `ROTO-029`, `ROTO-025`, `BIPP-049`, pellicola, alluminio…)
- 8 clienti + 1 fornitore, listini (5 fasce/articolo), ~23 righe vendite su 4 anni (2023-2026), ordini clienti/fornitori, scadenze aperte.
- Casi limite utili: articolo esaurito (`ALLU-040`), disponibile negativo (`PELL-045`), cliente bloccato con insoluto (`PRO LOCO CUORGNE`).

Password `sa` di test: `Test_Str0ng!Pass` — **solo per sviluppo locale**.
