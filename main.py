"""Interactive CLI entry point for local testing of the agentic loop."""

import os
import json
import pathlib
from groq import Groq
from dotenv import load_dotenv
from core.agent import run_agent_loop, sanitize_prompt
from core.session import session_manager
from utils.export import export_tsx, export_zip
from utils.preview import render_preview


def setup_client() -> tuple[object, dict, str, int]:
    """Load environment, tokens file, and return initialized dependencies."""
    load_dotenv()
    # RULE 6: explicit UTF-8 encoding on all file reads
    tokens = json.loads(pathlib.Path("design_system.json").read_text(encoding="utf-8"))
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    model = os.getenv("MODEL_NAME", "llama-3.1-70b-versatile")
    retries = int(os.getenv("MAX_RETRIES", "2"))
    return client, tokens, model, retries


def handle_export(code: str, tokens: dict, session_id: str, choice: str) -> None:
    """Write export file and HTML preview to ./output/ directory."""
    out_dir = pathlib.Path("output")
    out_dir.mkdir(exist_ok=True)
    if choice == "tsx":
        path = out_dir / f"{session_id}.component.tsx"
        # export_tsx returns bytes (UTF-8 encoded) — write_bytes is correct here
        path.write_bytes(export_tsx(code))
        print(f"[Export] Saved: {path}")
    elif choice == "zip":
        path = out_dir / f"{session_id}.component.zip"
        path.write_bytes(export_zip(code, tokens))
        print(f"[Export] Saved: {path}")
    preview_path = out_dir / f"{session_id}.preview.html"
    # RULE 6: explicit UTF-8 encoding — render_preview returns str with possible unicode
    preview_path.write_text(render_preview(code, tokens), encoding="utf-8")
    print(f"[Preview] Saved: {preview_path} — open in any browser.")


def main() -> None:
    """Run interactive CLI session loop."""
    client, tokens, model, max_retries = setup_client()
    session_id = "cli-session"
    print("\n⚡ Guided Component Architect — CLI")
    print(f"   Model    : {model}")
    print(f"   Retries  : {max_retries}")
    print(f"   Tokens   : {list(tokens.keys())}")
    print("   Commands : 'reset' to clear session | 'quit' to exit\n")
    while True:
        user_input = input("Describe your component: ").strip()
        if user_input.lower() == "quit":
            print("Goodbye.")
            break
        if user_input.lower() == "reset":
            session_manager.reset(session_id)
            print("[Session] Reset complete.\n")
            continue
        clean, err = sanitize_prompt(user_input)
        if err:
            print(f"[Error] {err}\n")
            continue
        try:
            code, status, errors = run_agent_loop(
                clean, session_id, tokens, client, model, max_retries
            )
            print(f"\n[Status] {status}")
            if errors:
                print(f"[Warnings] {errors}")
            print("\n--- GENERATED COMPONENT ---")
            print(code)
            print("---------------------------\n")
            choice = input("Export? (tsx / zip / no): ").strip().lower()
            if choice in ("tsx", "zip"):
                handle_export(code, tokens, session_id, choice)
            print()
        except RuntimeError as e:
            print(f"[Error] {e}\n")


if __name__ == "__main__":
    main()
