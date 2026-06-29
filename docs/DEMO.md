# Domande di esempio

La chat pilota l'interfaccia tramite 3 tool (`cerca_articoli`, `dettaglio_articolo`,
`grafico_vendite`). Ecco cosa puoi chiedere, in linguaggio naturale.

> Uso tipico: addetto al banco / reception → dato puntuale veloce, niente analisi.
> L'assistente non mostra mai numeri inventati: i dati arrivano dal database, deterministici.

## 🔎 Ricerca + filtri (tabella)
- «mostra tutti gli articoli»
- «articoli della famiglia rotoli»
- «cosa ho disponibile della famiglia pellicole?»
- «articoli del fornitore Cristianpack»
- «cerca pellicola per alimenti»
- «sacchetti biocompostabili disponibili»
- «articoli con "scotch" nel nome»
- «solo articoli con giacenza, famiglia cancelleria»

## ↕️ Ordinamenti
- «articoli disponibili ordinati per giacenza decrescente»
- «i rotoli con più scorta in alto»
- «ordina per descrizione»
- «famiglia vaschette per disponibilità crescente»

## 📄 Scheda articolo (dato puntuale)
- «scheda dell'articolo ROTO-028»
- «dettaglio ALPE-012»
- «quanti ne ho in giacenza del ROTO-025?»
- «che prezzo ha l'articolo ROTO-028?»
- «ultime vendite del ROTO-028»

## 📊 Classifiche / grafici vendite
- «articoli più venduti per valore nel 2025»
- «top articoli per quantità nel 2024»
- «valore venduto per famiglia nel 2024»
- «vendite per agente nel 2023»
- «migliori clienti per fatturato 2024»
- «andamento del valore venduto per anno»
- «famiglie più vendute per quantità»

## 🗣️ Linguaggio naturale "da banco"
- «cosa abbiamo di disponibile nei rotoli cassa?»
- «quali sacchetti freezer ho a magazzino?»
- «fammi la scheda del termico omologato 57x30»

## ⚠️ Casi limite (robustezza)
- «vendite del 2030» → l'anno non esiste: lo dice e propone il più vicino disponibile
- «scheda articolo XYZ-999» → "nessun articolo trovato"
- «qual è l'articolo più venduto?» → usa il grafico per articolo

---

I valori di filtro (famiglie, fornitori, codici) dipendono dai dati del tuo database.
Gli esempi sopra usano valori reali di una base dati di magazzino di distribuzione.
