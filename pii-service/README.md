# pii-service — guardia PII locale (rizzo-pii-0.3B)

Microservizio HTTP che **anonimizza il testo utente** prima che raggiunga il LLM, e ne
permette il **ripristino** in locale. Così, anche tenendo l'API DeepSeek (cloud), i **dati
personali non lasciano l'azienda**: al modello vanno solo placeholder (`[FULLNAME_1]`…).

> Modello: [`rizzoaiacademy/rizzo-pii-0.3B`](https://huggingface.co/rizzoaiacademy/rizzo-pii-0.3B)
> (mmBERT fine-tuned, italiano, MIT). Logica di detection derivata da
> [rizzo-pii](https://github.com/Rizzo-AI-Academy/rizzo-pii) (`src/app/app.py`, MIT,
> © Simone Rizzo — Rizzo AI Academy): modello + rete regex/checksum (CF/PIVA/IBAN).

## Come gira
```
chat → backend Agno → [pre-hook] → POST pii-service /anonymize → "[FULLNAME_1] ..."
                                         ↓ mapping {ph: valore} in session_state
                       DeepSeek vede solo i placeholder
tool → ripristina(arg, mapping) in locale → SELECT con il valore vero
```
È **middleware** (pre-hook), non un tool che il LLM chiama: l'anonimizzazione avviene
PRIMA che il modello veda il messaggio. Quando rizzo pubblicherà un MCP, resterà comunque
un pre-hook lato backend (l'MCP serve ad altri usi, non a proteggere l'input).

## Avvio
```
avvia-pii.bat          # primo avvio: venv + deps + scarica il modello (~1GB), poi parte
```
Gira su `http://127.0.0.1:5005`. Override porta: env `PII_PORT`. Modello: env `PII_MODEL`.

## Attivare la guardia nel backend
Nel `backend/.env`:
```
PII_GUARD=on
PII_URL=http://127.0.0.1:5005
```
Con `PII_GUARD=off` (default) il backend ignora il servizio: demo invariata.
**Fail-closed:** se la guardia è `on` ma il servizio non risponde, la richiesta viene
bloccata (meglio fermarsi che far passare PII).

## API
- `GET /health` → `{ok, model, device}`
- `POST /anonymize` `{text}` → `{anonymized_text, mapping, n_entities, by_label}`

## Prova / eval
```
.venv\Scripts\python.exe prova.py   # frasi italiane realistiche -> entità + testo mascherato
```
⚠️ Onesto: il modello è ~0.989 F1 sui dati loro, **non sui tuoi**. Eyeball `prova.py` sui
nomi/CF/indirizzi reali Vittone prima di fidarti: ~1% può sfuggire (specie nomi propri).
