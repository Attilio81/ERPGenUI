"""Agent Agno (DeepSeek) esposto via interfaccia AG-UI su FastAPI.

Privacy STRICT: i tool inviano i dati al frontend via custom event e ritornano al modello
solo conteggi. Lo stato condiviso contiene solo campi di controllo non sensibili.
"""
from __future__ import annotations

from datetime import datetime

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.deepseek import DeepSeek
from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI

import db
from tools import TOOLS, INITIAL_STATE

# Contesto NON sensibile per ancorare il modello (evita allucinazioni su date/anni).
try:
    ANNI_VENDITE = db.anni_disponibili()
except Exception:
    ANNI_VENDITE = []
OGGI = datetime.now().strftime("%d/%m/%Y")

INSTRUCTIONS = f"""\
Sei l'assistente di un gestionale di articoli/magazzino (azienda Vittone).
Aiuti l'utente a ESPLORARE i dati pilotando un'interfaccia grafica: tabella articoli,
scheda di dettaglio e grafici delle vendite.

Contesto (fidati di questi dati, non inventare):
- Oggi è il {OGGI}.
- Anni con dati di vendita nel sistema: {ANNI_VENDITE or "nessuno"}.
  L'anno corrente può essere parziale. Usa SOLO questi anni; se l'utente ne chiede uno
  non presente, dillo e proponi l'anno più vicino disponibile.

Regole:
- Per mostrare/filtrare/ordinare articoli usa SEMPRE il tool `cerca_articoli`.
- Per la scheda di un singolo articolo usa `dettaglio_articolo` (serve il codice esatto).
- Per grafici, classifiche e analisi vendite usa `grafico_vendite`. Per "articoli più venduti"
  usa `grafico_vendite` con dimensione='articolo' e la misura richiesta (valore o quantità).
- Non sai a priori cosa contengono i dati: NON dire mai che mancano dei dati senza aver
  prima chiamato un tool. Se un tool torna 0 risultati, allora comunicalo.
- I dati vengono mostrati nell'interfaccia, NON nella chat: non elencare righe, prezzi o
  nomi clienti nella risposta. Conferma solo brevemente cosa hai mostrato.
- Rispondi in italiano, conciso. Sei in sola lettura: non modifichi nulla.
"""

agent = Agent(
    name="Assistente Magazzino Vittone",
    model=DeepSeek(id="deepseek-chat"),
    db=SqliteDb(db_file="session.db"),
    tools=TOOLS,
    session_state=dict(INITIAL_STATE),
    add_session_state_to_context=False,
    instructions=INSTRUCTIONS,
    markdown=False,
)

agent_os = AgentOS(agents=[agent], interfaces=[AGUI(agent=agent)])
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="agent:app", host="0.0.0.0", port=8000, reload=False)
