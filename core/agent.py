"""Orchestrates the Generate → Validate → Self-Correct agentic loop. Used by both CLI and API."""

import json
from core.generator import generate
from core.validator import validate
from core.corrector import correct
from core.session import session_manager

INJECTION_PHRASES = [
    "ignore previous instructions",
    "disregard",
    "forget instructions",
    "system:",
    "```system",
    "jailbreak",
    "override instructions",
]


def sanitize_prompt(prompt: str) -> tuple[str, str | None]:
    """Strip whitespace, enforce length cap, reject injection phrases."""
    prompt = prompt.strip()
    if len(prompt) > 2000:
        return ("", "Prompt too long. Maximum 2000 characters.")
    for phrase in INJECTION_PHRASES:
        if phrase.lower() in prompt.lower():
            return ("", "Invalid prompt: potential injection attempt detected.")
    return (prompt, None)


def run_agent_loop(
    user_prompt: str,
    session_id: str,
    tokens: dict,
    client: object,
    model: str,
    max_retries: int = 2,
) -> tuple[str, str, list[str]]:
    """
    Run Generate → Validate → Self-Correct loop.
    Returns (final_code, status_string, final_error_list).
    """
    token_context = json.dumps(tokens, indent=2)
    prior = session_manager.get_last_component(session_id)

    print("[Generator] Calling LLM...")
    code = generate(user_prompt, token_context, prior, client, model)

    for attempt in range(max_retries):
        print(f"[Validator] Checking output (attempt {attempt + 1})...")
        errors = validate(code, tokens)
        if not errors:
            break
        error_log = "\n".join(errors)
        print(f"[Corrector] Retry {attempt + 1}/{max_retries}:\n{error_log}")
        code = correct(code, error_log, token_context, client, model)

    final_errors = validate(code, tokens)
    status = "VALID" if not final_errors else "WARNING: unresolved validation issues after retries"
    session_manager.push(session_id, user_prompt, code)
    return code, status, final_errors
