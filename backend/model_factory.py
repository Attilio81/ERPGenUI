"""Selezione del modello LLM via env `AI_PROVIDER` — il resto del codice è model-agnostic.

  mistral  : Mistral La Plateforme (Parigi, UE) — DPA diretto, dati in UE → **GDPR-compliant**.
             Consigliato in produzione. Serve `pip install mistralai` + MISTRAL_API_KEY.
  deepseek : DeepSeek cloud (api.deepseek.com) — economico ma server in Cina → NON compliant.
             Ok per sviluppo/costo. DEEPSEEK_API_KEY.
  local    : endpoint OpenAI-compatibile self-host (Ollama / LM Studio / vLLM) — zero terzi.

Cambi provider dal `.env`, senza toccare agent.py. La compliance GDPR viene dalla scelta
del provider (Mistral UE), non dall'app: vedi README, sezione Privacy & GDPR.
"""
from __future__ import annotations

import os


def build_model():
    provider = os.environ.get("AI_PROVIDER", "deepseek").lower()
    temp = float(os.environ.get("LLM_TEMPERATURE", "0.3"))

    if provider == "mistral":
        from agno.models.mistral import MistralChat  # richiede: pip install mistralai
        model = MistralChat(id=os.environ.get("MISTRAL_MODEL", "mistral-small-latest"),
                            temperature=temp)
    elif provider == "local":
        from agno.models.openai import OpenAILike
        model = OpenAILike(
            id=os.environ.get("LOCAL_MODEL", "qwen2.5"),
            base_url=os.environ.get("LOCAL_BASE_URL", "http://127.0.0.1:11434/v1"),
            api_key=os.environ.get("LOCAL_API_KEY", "not-needed"),
            temperature=temp,
        )
    else:  # deepseek (default)
        from agno.models.deepseek import DeepSeek
        model = DeepSeek(id=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"), temperature=temp)

    print(f"[LLM] provider={provider} model={getattr(model, 'id', '?')}")
    return model
