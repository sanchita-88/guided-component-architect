"""Calls the LLM to generate an Angular component from a user prompt and design token context."""

import os
import groq
from core.prompts import GENERATION_PROMPT


def strip_fences(text: str) -> str:
    """Remove markdown code fence lines from LLM output."""
    lines = text.splitlines()
    cleaned = [line for line in lines if not line.strip().startswith("```")]
    return "\n".join(cleaned).strip()


def generate(user_prompt: str, token_context: str, prior_component: str, client: object, model: str) -> str:
    """Call LLM to generate Angular component. Returns raw code string."""
    prompt = GENERATION_PROMPT.format(
        token_context=token_context,
        prior_component=prior_component or "(none — this is the first turn)",
        user_prompt=user_prompt
    )
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        raw = response.choices[0].message.content
        return strip_fences(raw)
    except groq.APIError as e:
        raise RuntimeError(f"[Generator] LLM call failed: {e}") from e
