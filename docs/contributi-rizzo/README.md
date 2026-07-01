# Contribuire al dataset rizzo-pii (senza Gemini)

Ricetta per contribuire **dati sintetici italiani** al dataset
[`rizzoaiacademy/anonimizzazione-testi-italiano`](https://huggingface.co/datasets/rizzoaiacademy/anonimizzazione-testi-italiano),
usando i **nostri template** (scritti a mano, non Gemini) + un generatore di **ditte
individuali** ORG-heavy. Rinforza il tag debole (**ORG / nomi-ditta MAIUSCOLO**), che è il
caso B2B del gestionale.

> Fatto una volta → 2 PR (~10.000 esempi): discussions/7 e /8.

## File di questa cartella
- `legal_templates.json` — 53 template commerciale/legale (ORG-heavy + ditte individuali).
- `patch-generatore-ditta.py` — il generatore `ditta_individuale` da innestare nel repo rizzo.

## Dove va il token HF
**Mai nel repo.** In ordine di preferenza:
1. `hf auth login` → salva in `~/.cache/huggingface` (fuori dal progetto). ✅ consigliato
2. Sessione: PowerShell `$env:HF_TOKEN="hf_..."` (non persiste).
3. `.env` gitignorato (sconsigliato: segreto su disco).

Serve un token **write** (huggingface.co/settings/tokens). Dopo l'uso, **revocalo** se l'hai
esposto.

## Procedura
```powershell
# 1. clona il repo rizzo-pii
git clone https://github.com/Rizzo-AI-Academy/rizzo-pii
cd rizzo-pii

# 2. porta i nostri template + la patch del generatore
copy ..\docs\contributi-rizzo\legal_templates.json dataset\synthetic\legal_templates.json
#    poi incolla i blocchi di patch-generatore-ditta.py in
#    src\data_pipeline\generate_synthetic_pii.py (vicino a org_piece / mixed_list / SLOTS)

# 3. ambiente (solo huggingface_hub: lo script NON usa torch né SDK Gemini)
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install huggingface_hub python-dotenv

# 4. autenticazione HF (una volta)
.\.venv\Scripts\hf.exe auth login        # oppure  $env:HF_TOKEN="hf_..."

# 5. DRY-RUN (niente upload): controlla la distribuzione dei tag
.\.venv\Scripts\python.exe src\data_pipeline\contribute_dataset.py `
    --offline --n 300 --handle IL_TUO_HANDLE --no-upload

# 6. BATCH VERO + apre la PR (rinforza ORG e ditte individuali)
.\.venv\Scripts\python.exe src\data_pipeline\contribute_dataset.py `
    --offline --n 5000 --handle IL_TUO_HANDLE `
    --boost ORG=6 DITTAIND=6 IBAN=3 CF=3 CATASTO=3
# -> stampa l'URL della Pull Request
```

## Regole
- **Solo dati sintetici.** Lo script inietta valori con checksum validi (CF/PIVA/IBAN);
  nessuna PII reale viene mai prodotta o caricata.
- `--offline` = nessun LLM esterno: la prosa nuova viene dai nostri template.
- La PR è **in attesa di revisione** del maintainer (Simone Rizzo), non merge automatico.
- Per più varietà: aggiungi altri template a `legal_templates.json` (stessi slot ammessi:
  FULLNAME, ORG, CF, PIVA, IBAN, ADDRESS, CITY, DATE, AMOUNT, DOCID, CATASTO, CONTO, PEC,
  PHONE, TARGA, DITTAIND, DITTALIST, NAMELIST, ORGLIST, MIXEDLIST, …).
