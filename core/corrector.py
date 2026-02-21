"""Calls the LLM with the original code and validation error log to produce a corrected component."""

import groq
from core.prompts import CORRECTION_PROMPT
from core.generator import strip_fences


def correct(original_code: str, error_log: str, token_context: str, client: object, model: str) -> str:
    """Call LLM with error context to produce corrected component. Returns raw code string."""
    prompt = CORRECTION_PROMPT.format(
        token_context=token_context,
        original_code=original_code,
        error_log=error_log
    )
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        raw = response.choices[0].message.content
        return strip_fences(raw)
    except groq.APIError as e:
        raise RuntimeError(f"[Corrector] LLM call failed: {e}") from e
