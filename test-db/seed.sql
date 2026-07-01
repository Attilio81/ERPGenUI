/* ============================================================================
   ERP Generative UI — DB di TEST (SQL Server, usa-e-getta)
   ----------------------------------------------------------------------------
   Ricrea SOLO la superficie che backend/db.py legge/scrive:
     - 7 "viste AI" (qui come TABELLE: db.py fa solo SELECT, non gli importa)
     - tabelle editabili  artico / anagra  (PATCH note/telefono/... )
   Dati 100% SINTETICI (nessun dato reale cliente). Include i codici usati
   nelle demo/guida (ROTO-028, BIPP-049, pellicola, alluminio, ...) così gli
   esempi cliccabili tornano risultati.
   Idempotente: si può rilanciare. codditt = 'VITC' (default CODDITT).
   ============================================================================ */

IF DB_ID('ERPTEST') IS NULL CREATE DATABASE ERPTEST;
GO
USE ERPTEST;
GO

/* -------- pulizia (drop se esistono) -------- */
DROP TABLE IF EXISTS vw_EGM_AI_anagraficaarticoli;
DROP TABLE IF EXISTS vw_EGM_AI_disponibilita_articoli;
DROP TABLE IF EXISTS vw_EGM_AI_listini;
DROP TABLE IF EXISTS vw_EGM_AI_vendite;
DROP TABLE IF EXISTS vw_EGM_AI_ordini_clienti;
DROP TABLE IF EXISTS vw_EGM_AI_ordini_fornitori;
DROP TABLE IF EXISTS vw_EGM_AI_anagrafiche;
DROP TABLE IF EXISTS vw_EGM_AI_scadenze_aperte;
DROP TABLE IF EXISTS artico;
DROP TABLE IF EXISTS anagra;
GO

/* ============================ SCHEMA ============================ */

CREATE TABLE vw_EGM_AI_anagraficaarticoli (
    CodArticolo    NVARCHAR(30)  NOT NULL PRIMARY KEY,
    DescrArticolo  NVARCHAR(120) NULL,
    DescrFamiglia  NVARCHAR(80)  NULL,
    CodFamiglia    NVARCHAR(20)  NULL,
    DescrFornitore NVARCHAR(80)  NULL,
    UnitaMisura    NVARCHAR(8)   NULL,
    PesoNetto      DECIMAL(18,6) NULL,
    PesoLordo      DECIMAL(18,6) NULL
);

CREATE TABLE vw_EGM_AI_disponibilita_articoli (
    codice_articolo    NVARCHAR(30)  NOT NULL PRIMARY KEY,
    esistenza          DECIMAL(18,6) NULL,
    ordinato_fornitori DECIMAL(18,6) NULL,
    impegnato_clienti  DECIMAL(18,6) NULL
);

CREATE TABLE vw_EGM_AI_listini (
    CodiceArticolo         NVARCHAR(30)  NOT NULL,
    NumeroListino          INT           NOT NULL,
    DescrizioneListino     NVARCHAR(60)  NULL,
    Prezzo                 DECIMAL(18,6) NULL,
    PrezzoNetto            NVARCHAR(4)    NULL,
    UnitaMisura            NVARCHAR(8)   NULL,
    CodiceClienteSpecifico NVARCHAR(20)  NULL,   -- NULL = listino generale
    QuantitaDa             DECIMAL(18,6) NULL,
    DataInizioValidita     DATETIME      NULL,
    DataFineValidita       DATETIME      NULL
);

CREATE TABLE vw_EGM_AI_vendite (
    CodiceArticolo          NVARCHAR(30)  NULL,
    DescrizioneArticolo     NVARCHAR(120) NULL,
    Famiglia                NVARCHAR(80)  NULL,
    CodiceCliente           NVARCHAR(20)  NULL,
    RagioneSocialeCliente   NVARCHAR(120) NULL,
    DescrizioneAgente       NVARCHAR(80)  NULL,
    Anno                    INT           NULL,
    DataMovimento           DATETIME      NULL,
    Quantita                DECIMAL(18,6) NULL,
    ValoreTotale            DECIMAL(18,4) NULL
);

CREATE TABLE vw_EGM_AI_ordini_clienti (
    codice_articolo      NVARCHAR(30)  NULL,
    descrizione_articolo NVARCHAR(120) NULL,
    unita_misura         NVARCHAR(8)   NULL,
    codice_conto         NVARCHAR(20)  NULL,
    ragione_sociale      NVARCHAR(120) NULL,
    citta                NVARCHAR(60)  NULL,
    anno                 INT           NULL,
    numero_ordine        INT           NULL,
    data_ordine          DATETIME      NULL,
    data_consegna        DATETIME      NULL,
    quantita             DECIMAL(18,6) NULL,
    quantita_evasa       DECIMAL(18,6) NULL
);

CREATE TABLE vw_EGM_AI_ordini_fornitori (
    codice_articolo      NVARCHAR(30)  NULL,
    descrizione_articolo NVARCHAR(120) NULL,
    unita_misura         NVARCHAR(8)   NULL,
    codice_conto         NVARCHAR(20)  NULL,
    ragione_sociale      NVARCHAR(120) NULL,
    citta                NVARCHAR(60)  NULL,
    anno                 INT           NULL,
    numero_ordine        INT           NULL,
    data_ordine          DATETIME      NULL,
    data_consegna        DATETIME      NULL,
    quantita             DECIMAL(18,6) NULL,
    quantita_evasa       DECIMAL(18,6) NULL
);

CREATE TABLE vw_EGM_AI_anagrafiche (
    CodiceConto         NVARCHAR(20)  NOT NULL PRIMARY KEY,
    TipoAnagrafica      NVARCHAR(20)  NULL,   -- 'Cliente' | 'Fornitore'
    RagioneSociale      NVARCHAR(120) NULL,
    Indirizzo           NVARCHAR(120) NULL,
    CAP                 NVARCHAR(10)  NULL,
    Citta               NVARCHAR(60)  NULL,
    Provincia           NVARCHAR(4)   NULL,
    Telefono            NVARCHAR(30)  NULL,
    Cellulare           NVARCHAR(30)  NULL,
    Email               NVARCHAR(80)  NULL,
    PartitaIVA          NVARCHAR(20)  NULL,
    CodiceFiscale       NVARCHAR(20)  NULL,
    CodiceAgente        INT           NULL,
    DescrizioneZona     NVARCHAR(60)  NULL,
    Stato               NVARCHAR(20)  NULL,
    Bloccato            NVARCHAR(4)   NULL,
    OrarioApertura      NVARCHAR(60)  NULL,
    GiornoChiusura      NVARCHAR(30)  NULL,
    DataUltimoDocumento DATETIME      NULL,
    Note                NVARCHAR(400) NULL
);

CREATE TABLE vw_EGM_AI_scadenze_aperte (
    codice_cliente   NVARCHAR(20)  NULL,
    numero_documento INT           NULL,
    data_scadenza    DATETIME      NULL,
    importo_residuo  DECIMAL(18,4) NULL,
    flag_insoluto    NVARCHAR(2)   NULL   -- 'S' | 'N'
);

/* tabelle editabili (scrittura PATCH) */
CREATE TABLE artico (
    codditt    NVARCHAR(8)   NOT NULL,
    ar_codart  NVARCHAR(30)  NOT NULL,
    ar_descr   NVARCHAR(120) NULL,
    ar_note    NVARCHAR(400) NULL,
    ar_pesonet DECIMAL(18,6) NULL,
    CONSTRAINT PK_artico PRIMARY KEY (codditt, ar_codart)
);
CREATE TABLE anagra (
    codditt  NVARCHAR(8)  NOT NULL,
    an_conto NVARCHAR(20) NOT NULL,
    an_telef NVARCHAR(30) NULL,
    an_cell  NVARCHAR(30) NULL,
    an_email NVARCHAR(80) NULL,
    an_note  NVARCHAR(400) NULL,
    CONSTRAINT PK_anagra PRIMARY KEY (codditt, an_conto)
);
GO

/* ============================ DATI ============================ */

INSERT INTO vw_EGM_AI_anagraficaarticoli
    (CodArticolo, DescrArticolo, DescrFamiglia, CodFamiglia, DescrFornitore, UnitaMisura, PesoNetto, PesoLordo) VALUES
 ('ROTO-028','Rotolo termoretraibile omologato MM57X30MTX12AN','ROTOLI','RTL','BRENTA SRL','RT',0.180,0.200),
 ('ROTO-029','Rotolo termoretraibile N.V.C.S.F. MM57X30MTX12AN','ROTOLI','RTL','BRENTA SRL','RT',0.180,0.200),
 ('ROTO-025','Rotoli POS termici bianchi MM57X15MTX12AN','ROTOLI CASSA','RTC','CRISTIANPACK','NR',0.060,0.070),
 ('BIPP-049','Piatto rotondo in polpa di cellulosa 170 MM','PIATTI MONOUSO','PMU','BRENTA SRL','PZ',0.012,0.013),
 ('BICC-020','Bicchiere bio PLA 200 CC','PIATTI MONOUSO','PMU','BRENTA SRL','PZ',0.008,0.009),
 ('PELL-030','Pellicola estensibile trasparente MM300','PELLICOLE','PEL','CRISTIANPACK','RT',1.200,1.300),
 ('PELL-045','Pellicola alimentare in rotolo MM450','PELLICOLE','PEL','CRISTIANPACK','RT',1.800,1.900),
 ('ALLU-100','Alluminio in rotolo alimentare MT100','ALLUMINIO','ALL','POOL PACK NORD OVEST SPA','RT',2.400,2.500),
 ('ALLU-040','Vaschette alluminio 4 porzioni CF100','ALLUMINIO','ALL','POOL PACK NORD OVEST SPA','CF',0.900,1.000),
 ('SACC-010','Sacchetti spesa bio compostabili 30X50','SACCHETTI','SAC','BRENTA SRL','CF',0.700,0.750);
GO

INSERT INTO vw_EGM_AI_disponibilita_articoli
    (codice_articolo, esistenza, ordinato_fornitori, impegnato_clienti) VALUES
 ('ROTO-028',13119,5000,1200),
 ('ROTO-029', 6210,   0, 800),
 ('ROTO-025', 5450,2000, 300),
 ('BIPP-049',20031,   0,1300),
 ('BICC-020', 8800,1000, 250),
 ('PELL-030', 1420, 500, 100),
 ('PELL-045',  340,   0, 400),   -- disponibile negativo (impegnato > esistenza)
 ('ALLU-100', 2600, 300,  90),
 ('ALLU-040',    0, 600,   0),   -- esaurito
 ('SACC-010', 4750,   0, 500);
GO

/* listini: 5 fasce per articolo, sempre valide (2020 -> 2999). PrezzoNetto 'N'. */
INSERT INTO vw_EGM_AI_listini
    (CodiceArticolo, NumeroListino, DescrizioneListino, Prezzo, PrezzoNetto, UnitaMisura, CodiceClienteSpecifico, QuantitaDa, DataInizioValidita, DataFineValidita)
SELECT a.CodArticolo, n.NumeroListino,
       CONCAT('Listino ', n.NumeroListino),
       CAST(a.PesoLordo * (1.0 - 0.06*(n.NumeroListino-1)) + 0.05 AS DECIMAL(18,6)),
       'N', a.UnitaMisura, NULL, 1, '2020-01-01', '2999-12-31'
FROM vw_EGM_AI_anagraficaarticoli a
CROSS JOIN (VALUES (1),(2),(3),(4),(5)) AS n(NumeroListino);
GO

/* anagrafiche: 8 clienti + 1 fornitore (per verificare il filtro TipoAnagrafica) */
INSERT INTO vw_EGM_AI_anagrafiche
    (CodiceConto, TipoAnagrafica, RagioneSociale, Indirizzo, CAP, Citta, Provincia, Telefono, Cellulare, Email, PartitaIVA, CodiceFiscale, CodiceAgente, DescrizioneZona, Stato, Bloccato, OrarioApertura, GiornoChiusura, DataUltimoDocumento, Note) VALUES
 ('1','Cliente','PROGETTO SAS DI ODELLO STEFANO','Via Roma 12','10086','Rivarolo Canavese','TO','0124-11111','335-1111111','ordini@progettosas.it','01111110019','01111110019',1,'Canavese','Attivo','N','8-12 / 15-19','Lunedì','2026-05-07','Cliente storico, paga puntuale'),
 ('2','Cliente','LA PIAZZA SOC. COOP','Piazza Marconi 3','10082','Cuorgnè','TO','0124-22222','335-2222222','info@lapiazza.coop','02222220028','02222220028',1,'Canavese','Attivo','N','7-13','Domenica','2026-05-06',NULL),
 ('3','Cliente','MACELLERIA LUCCO BORLERA','Via Ivrea 44','10086','Rivarolo Canavese','TO','0124-33333','335-3333333',NULL,'03333330037','03333330037',2,'Canavese','Attivo','N','7-12:30 / 16-19:30','Mercoledì pomeriggio','2026-04-30','Richiede consegna mattino'),
 ('4','Cliente','R.G.D SRL','Corso Francia 200','10093','Collegno','TO','011-4444444',NULL,'amm@rgdsrl.it','04444440046','04444440046',2,'Torino Ovest','Attivo','N',NULL,NULL,'2026-04-27',NULL),
 ('5','Cliente','ASSOCIAZIONE CNOS FAP REGIONE PIEMONTE','Via Le Chiuse 14','10144','Torino','TO','011-5555555',NULL,'sede@cnosfap.it','05555550055','05555550055',1,'Torino','Attivo','N',NULL,NULL,'2026-04-23',NULL),
 ('6','Cliente','PRO LOCO CUORGNE','Via Arduino 1','10082','Cuorgnè','TO','0124-66666','335-6666666',NULL,'06666660064','06666660064',1,'Canavese','Attivo','S',NULL,NULL,'2026-05-05','BLOCCATO: insoluti da saldare'),
 ('7','Cliente','GRUPPO STORICO BORGO SAN ROCCO','Via San Rocco 9','10015','Ivrea','TO',NULL,'335-7777777',NULL,'07777770073','07777770073',2,'Eporediese','Attivo','N',NULL,NULL,'2026-05-04',NULL),
 ('8','Cliente','BAR CENTRALE DI ROSSI','Via Torino 5','10086','Rivarolo Canavese','TO','0124-88888',NULL,'barcentrale@pec.it','08888880082','08888880082',2,'Canavese','Attivo','N','6-20','Lunedì','2026-03-15',NULL),
 ('900','Fornitore','BRENTA SRL','Via Industria 1','35010','Loreggia','PD','049-9999999',NULL,'vendite@brenta.it','09999990909','09999990909',NULL,'Veneto','Attivo','N',NULL,NULL,'2026-04-24',NULL);
GO

/* vendite: righe su 4 anni, più articoli/clienti/agenti/famiglie (per grafici e top) */
INSERT INTO vw_EGM_AI_vendite
    (CodiceArticolo, DescrizioneArticolo, Famiglia, CodiceCliente, RagioneSocialeCliente, DescrizioneAgente, Anno, DataMovimento, Quantita, ValoreTotale) VALUES
 ('ROTO-028','Rotolo termoretraibile omologato MM57X30MTX12AN','ROTOLI','1','PROGETTO SAS DI ODELLO STEFANO','Rossi Mario',2026,'2026-05-07',200,124.00),
 ('ROTO-028','Rotolo termoretraibile omologato MM57X30MTX12AN','ROTOLI','2','LA PIAZZA SOC. COOP','Rossi Mario',2026,'2026-05-06',1000,620.00),
 ('BIPP-049','Piatto rotondo in polpa di cellulosa 170 MM','PIATTI MONOUSO','1','PROGETTO SAS DI ODELLO STEFANO','Rossi Mario',2026,'2026-05-07',200,8.80),
 ('BIPP-049','Piatto rotondo in polpa di cellulosa 170 MM','PIATTI MONOUSO','5','ASSOCIAZIONE CNOS FAP REGIONE PIEMONTE','Bianchi Luigi',2026,'2026-04-23',250,10.31),
 ('PELL-030','Pellicola estensibile trasparente MM300','PELLICOLE','3','MACELLERIA LUCCO BORLERA','Bianchi Luigi',2026,'2026-04-20',80,152.00),
 ('ALLU-100','Alluminio in rotolo alimentare MT100','ALLUMINIO','4','R.G.D SRL','Bianchi Luigi',2026,'2026-03-18',40,220.00),
 ('ROTO-028','Rotolo termoretraibile omologato MM57X30MTX12AN','ROTOLI','2','LA PIAZZA SOC. COOP','Rossi Mario',2025,'2025-11-12',1500,930.00),
 ('ROTO-029','Rotolo termoretraibile N.V.C.S.F. MM57X30MTX12AN','ROTOLI','1','PROGETTO SAS DI ODELLO STEFANO','Rossi Mario',2025,'2025-09-03',900,558.00),
 ('BIPP-049','Piatto rotondo in polpa di cellulosa 170 MM','PIATTI MONOUSO','2','LA PIAZZA SOC. COOP','Rossi Mario',2025,'2025-07-22',3000,132.00),
 ('BICC-020','Bicchiere bio PLA 200 CC','PIATTI MONOUSO','5','ASSOCIAZIONE CNOS FAP REGIONE PIEMONTE','Bianchi Luigi',2025,'2025-06-10',2000,180.00),
 ('PELL-045','Pellicola alimentare in rotolo MM450','PELLICOLE','3','MACELLERIA LUCCO BORLERA','Bianchi Luigi',2025,'2025-05-05',120,342.00),
 ('ALLU-100','Alluminio in rotolo alimentare MT100','ALLUMINIO','4','R.G.D SRL','Bianchi Luigi',2025,'2025-03-30',60,330.00),
 ('SACC-010','Sacchetti spesa bio compostabili 30X50','SACCHETTI','8','BAR CENTRALE DI ROSSI','Rossi Mario',2025,'2025-02-18',300,210.00),
 ('ROTO-028','Rotolo termoretraibile omologato MM57X30MTX12AN','ROTOLI','1','PROGETTO SAS DI ODELLO STEFANO','Rossi Mario',2024,'2024-10-01',1200,744.00),
 ('ROTO-025','Rotoli POS termici bianchi MM57X15MTX12AN','ROTOLI CASSA','2','LA PIAZZA SOC. COOP','Rossi Mario',2024,'2024-08-14',800,320.00),
 ('BIPP-049','Piatto rotondo in polpa di cellulosa 170 MM','PIATTI MONOUSO','5','ASSOCIAZIONE CNOS FAP REGIONE PIEMONTE','Bianchi Luigi',2024,'2024-06-20',2500,110.00),
 ('PELL-030','Pellicola estensibile trasparente MM300','PELLICOLE','4','R.G.D SRL','Bianchi Luigi',2024,'2024-04-11',150,285.00),
 ('ALLU-040','Vaschette alluminio 4 porzioni CF100','ALLUMINIO','3','MACELLERIA LUCCO BORLERA','Bianchi Luigi',2024,'2024-03-02',90,171.00),
 ('SACC-010','Sacchetti spesa bio compostabili 30X50','SACCHETTI','8','BAR CENTRALE DI ROSSI','Rossi Mario',2024,'2024-01-25',500,350.00),
 ('ROTO-028','Rotolo termoretraibile omologato MM57X30MTX12AN','ROTOLI','2','LA PIAZZA SOC. COOP','Rossi Mario',2023,'2023-11-08',1000,600.00),
 ('BIPP-049','Piatto rotondo in polpa di cellulosa 170 MM','PIATTI MONOUSO','1','PROGETTO SAS DI ODELLO STEFANO','Rossi Mario',2023,'2023-09-17',2000,88.00),
 ('PELL-045','Pellicola alimentare in rotolo MM450','PELLICOLE','3','MACELLERIA LUCCO BORLERA','Bianchi Luigi',2023,'2023-05-29',200,570.00),
 ('ALLU-100','Alluminio in rotolo alimentare MT100','ALLUMINIO','4','R.G.D SRL','Bianchi Luigi',2023,'2023-03-14',80,440.00);
GO

/* ordini clienti */
INSERT INTO vw_EGM_AI_ordini_clienti
    (codice_articolo, descrizione_articolo, unita_misura, codice_conto, ragione_sociale, citta, anno, numero_ordine, data_ordine, data_consegna, quantita, quantita_evasa) VALUES
 ('ROTO-028','Rotolo termoretraibile omologato MM57X30MTX12AN','RT','1','PROGETTO SAS DI ODELLO STEFANO','Rivarolo Canavese',2026,101,'2026-05-06','2026-05-10',200,200),
 ('ROTO-028','Rotolo termoretraibile omologato MM57X30MTX12AN','RT','2','LA PIAZZA SOC. COOP','Cuorgnè',2026,102,'2026-05-06','2026-05-12',1000,1000),
 ('BIPP-049','Piatto rotondo in polpa di cellulosa 170 MM','PZ','6','PRO LOCO CUORGNE','Cuorgnè',2026,103,'2026-05-05','2026-05-15',600,0),
 ('BIPP-049','Piatto rotondo in polpa di cellulosa 170 MM','PZ','7','GRUPPO STORICO BORGO SAN ROCCO','Ivrea',2026,104,'2026-05-04','2026-05-14',700,0),
 ('PELL-030','Pellicola estensibile trasparente MM300','RT','3','MACELLERIA LUCCO BORLERA','Rivarolo Canavese',2026,105,'2026-04-28','2026-05-03',50,20),
 ('ALLU-040','Vaschette alluminio 4 porzioni CF100','CF','4','R.G.D SRL','Collegno',2026,106,'2026-04-27','2026-05-05',120,0),
 ('BICC-020','Bicchiere bio PLA 200 CC','PZ','5','ASSOCIAZIONE CNOS FAP REGIONE PIEMONTE','Torino',2026,107,'2026-04-23','2026-04-30',250,250),
 ('SACC-010','Sacchetti spesa bio compostabili 30X50','CF','8','BAR CENTRALE DI ROSSI','Rivarolo Canavese',2025,98,'2025-12-01','2025-12-06',300,300);
GO

/* ordini fornitori (in arrivo) */
INSERT INTO vw_EGM_AI_ordini_fornitori
    (codice_articolo, descrizione_articolo, unita_misura, codice_conto, ragione_sociale, citta, anno, numero_ordine, data_ordine, data_consegna, quantita, quantita_evasa) VALUES
 ('ROTO-028','Rotolo termoretraibile omologato MM57X30MTX12AN','RT','900','BRENTA SRL','Loreggia',2026,5001,'2026-04-24','2026-05-08',15000,15000),
 ('BIPP-049','Piatto rotondo in polpa di cellulosa 170 MM','PZ','900','BRENTA SRL','Loreggia',2026,5002,'2026-03-11','2026-03-25',9000,9000),
 ('ROTO-025','Rotoli POS termici bianchi MM57X15MTX12AN','NR','900','CRISTIANPACK','Torino',2026,5003,'2026-04-30','2026-05-20',2000,0),
 ('PELL-030','Pellicola estensibile trasparente MM300','RT','900','CRISTIANPACK','Torino',2026,5004,'2026-04-15','2026-05-02',500,500),
 ('ALLU-040','Vaschette alluminio 4 porzioni CF100','CF','900','POOL PACK NORD OVEST SPA','Torino',2026,5005,'2026-04-10','2026-05-01',600,0);
GO

/* scadenze aperte: cliente 1 (ok), 3 (scaduta), 6 (insoluto) */
INSERT INTO vw_EGM_AI_scadenze_aperte
    (codice_cliente, numero_documento, data_scadenza, importo_residuo, flag_insoluto) VALUES
 ('1',7001,'2026-08-31',744.00,'N'),
 ('1',7002,'2026-09-30',310.00,'N'),
 ('3',7010,'2026-05-15',342.00,'N'),
 ('3',7011,'2026-04-10',171.00,'N'),      -- scaduta (data < oggi 2026-07-01)
 ('6',7020,'2026-03-01',530.00,'S'),      -- insoluto
 ('6',7021,'2026-06-20',210.00,'N');
GO

/* tabelle editabili: allineate agli articoli/clienti (codditt = VITC) */
INSERT INTO artico (codditt, ar_codart, ar_descr, ar_note, ar_pesonet)
SELECT 'VITC', CodArticolo, DescrArticolo, NULL, PesoNetto FROM vw_EGM_AI_anagraficaarticoli;

INSERT INTO anagra (codditt, an_conto, an_telef, an_cell, an_email, an_note)
SELECT 'VITC', CodiceConto, Telefono, Cellulare, Email, Note FROM vw_EGM_AI_anagrafiche;
GO

PRINT '=== ERPTEST seed completato ===';
SELECT 'articoli' AS tab, COUNT(*) AS righe FROM vw_EGM_AI_anagraficaarticoli
UNION ALL SELECT 'vendite', COUNT(*) FROM vw_EGM_AI_vendite
UNION ALL SELECT 'clienti', COUNT(*) FROM vw_EGM_AI_anagrafiche
UNION ALL SELECT 'listini', COUNT(*) FROM vw_EGM_AI_listini;
GO
