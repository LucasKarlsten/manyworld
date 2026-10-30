#!/usr/bin/env python3
"""One real persona-to-LLM smoke test; NEVER executes economic transactions.

Uses Manyworld's OpenAI-compatible adapter to contact a local Ollama server.
Only the public decision summary is printed; no private chain of thought.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

from llm.adapters import OpenAICompatAdapter

PROFILES = Path(__file__).resolve().parents[1] / "scenarios/sweden-ubi/personas.v1.json"
ALLOWED = {"buy_essential", "save_cash", "search_job", "wait"}


def load_persona(persona_id: str) -> dict:
    personas = json.loads(PROFILES.read_text(encoding="utf-8"))["personas"]
    return next((p for p in personas if p["id"] == persona_id), None) or _unknown(persona_id)


def _unknown(persona_id: str):
    raise ValueError(f"unknown persona: {persona_id}")


def decode_decision(text: str) -> dict:
    data = json.loads(text)
    if not isinstance(data, dict) or set(data) != {"action", "explanation"}:
        raise ValueError("expected only action and explanation")
    if data["action"] not in ALLOWED:
        raise ValueError(f"unsupported action: {data['action']}")
    if not isinstance(data["explanation"], str) or not 1 <= len(data["explanation"]) <= 300:
        raise ValueError("explanation must be 1..300 characters")
    return data


async def run(args) -> dict:
    persona = load_persona(args.persona)
    # These are hypothetical smoke-test observations, NOT simulator readings.
    example_state = {
        "simulated_day": 5,
        "cash_model_usd": 250,
        "employment_status": "unemployed",
        "policy_announcement": (
            "The government has introduced universal basic income. "
            "This citizen is eligible for 15000 model-USD every 30 days, "
            "with a first scheduled payment on day 5."
        ),
        "note": "Synthetic fixture, not read from a Manyworld run",
    }
    prompt = (
        "/no_think\nYou are acting as a synthetic economic agent, not a chatbot. "
        "Choose one action grounded in your personality and observed situation. "
        "Do not assume actions already happened. "
        "Return JSON with exactly: action (one of buy_essential, save_cash, "
        "search_job, wait), explanation (one short first-person Swedish sentence). "
        "Do not include private reasoning or extra fields.\n"
        + json.dumps({"persona": persona, "observation": example_state}, ensure_ascii=False)
    )
    adapter = OpenAICompatAdapter({
        "base_url": args.base_url, "auth": "none", "timeout_s": args.timeout,
    })
    response = await adapter.complete(
        args.model,
        [{"role": "user", "content": prompt}],
        purpose="sweden_persona_smoke",
        max_tokens=args.max_tokens,
        temperature=0,
    )
    if not response.text.strip():
        choices = response.raw.get("choices") or [{}]
        reason = choices[0].get("finish_reason", "unknown")
        completion = (response.raw.get("usage") or {}).get("completion_tokens", "unknown")
        raise RuntimeError(
            f"Ollama returned empty message.content (finish_reason={reason}, "
            f"completion_tokens={completion}). Qwen3 may have spent its output "
            "budget in thinking mode. This smoke test sends /no_think and "
            "allows a larger token budget."
        )
    try:
        decision = decode_decision(response.text)
    except ValueError as exc:
        snippet = response.text.strip()[:160]
        raise RuntimeError(
            f"Model returned invalid decision JSON (characters={len(response.text)}, "
            f"preview={snippet!r}). No action was executed."
        ) from exc
    return {
        "status": "real_provider_reply_validated",
        "persona": persona["id"],
        "model": args.model,
        "source": "synthetic_fixture_NOT_live_simulation",
        "proposed_decision_only": decision,
        "executed_in_engine": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--persona", default="marcus")
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "qwen3:4b"))
    parser.add_argument("--base-url", default="http://127.0.0.1:11434/v1")
    parser.add_argument("--timeout", type=float, default=90)
    parser.add_argument("--max-tokens", type=int, default=1024)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(args)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
