# Guided Component Architect

🚀 **Live Demo:** https://guided-component-architect-ten.vercel.app/
✨ Features:
- Agentic Generate → Validate → Correct Loop
- Multi-turn component editing
- Live preview rendering
- Export as TSX or Angular files
⚠️ Note: Backend API may take a few seconds to wake if hosted on a free tier.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Agentic%20API-green)
![LLM](https://img.shields.io/badge/LLM-Agentic%20Workflow-purple)
![License](https://img.shields.io/badge/Status-Assignment%20Project-orange)

## Overview

Guided Component Architect is a clean, modular agentic code generation pipeline that transforms natural language prompts into production-ready Angular components. The system enforces design system token compliance through automated validation and self-correction loops, ensuring generated components adhere to your design standards without manual intervention.

## Agentic Loop Architecture

The core generation process follows a deterministic agentic loop that validates and self-corrects output:

```
     User Prompt
         │
         ▼
   ┌─────────────┐
   │  Sanitizer  │ ← Injection check + length enforcement
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │  Generator  │ ← LLM call with design tokens + session context
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │  Validator  │ ← Token compliance + syntax check
   └──────┬──────┘
          │ errors?
     ┌────┴────┐
     │ Yes     │ No
     ▼         ▼
  Corrector  Output
     │         │
     └──retry──┘ (max 2 attempts)
          │
          ▼
   ┌─────────────────────────────┐
   │  Preview  │  Export  │  Done │
   └─────────────────────────────┘
```

**Sanitizer**: Validates user input for injection attempts and enforces a 2000-character length limit before prompt assembly.

**Generator**: Calls the LLM with the user prompt, design token context, and prior component state (for multi-turn editing).

**Validator**: Performs static analysis to ensure required design tokens appear in the generated code and verifies TypeScript brace balance and HTML tag closure.

**Corrector**: When validation fails, the system automatically calls the LLM again with the original code and a structured error log, requesting targeted fixes without modifying unrelated code.

**Output**: After validation passes (or max retries exhausted), the component is stored in session state and made available for preview, export, or further editing.

## Design System

The project uses a JSON-based design system (`design_system.json`) that defines visual tokens including colors, typography, spacing, and effects. These tokens are injected into every LLM prompt as strict requirements, ensuring generated components use exact hex values, font names, and spacing units from your design system.

Tokens flow through the pipeline as follows:
1. Tokens are loaded from `design_system.json` at application startup
2. The token dictionary is serialized to JSON and included in both generation and correction prompts
3. The validator checks that required tokens (primary-color, secondary-color, font) appear in the generated code
4. Export functions include a `design-tokens.md` reference document in ZIP exports

## Setup

```bash
git clone <repo>
cd guided-component-architect
pip install -r requirements.txt
Copy `.env.example` to a new file named `.env`.
# Add your GROQ_API_KEY to .env
```

Edit `.env` and set your OpenAI API key:
```
GROQ_API_KEY=gsk-your-key-here
MODEL_NAME=llama-3.3-70b-versatile
MAX_RETRIES=2
```

## Usage: CLI

Run the interactive CLI for local testing:

```bash
python main.py
```

The CLI provides an interactive loop where you can:
- Enter natural language prompts to generate components
- Use `reset` to clear the current session and start fresh
- Use `quit` to exit the application
- Export generated components as `.tsx` or `.zip` files

**Example multi-turn exchange:**

```
Describe your component: Create a login button with primary color
[Status] VALID
--- GENERATED COMPONENT ---
// component.ts
...
Export? (tsx / zip / no): no

Describe your component: Now make the button fully rounded
[Status] VALID
--- GENERATED COMPONENT ---
// component.ts (updated with rounded corners)
...
```

## Usage: API

Start the FastAPI server:

```bash
uvicorn api:app --reload
```

The API exposes five endpoints:

### POST /generate

Generate a new component or edit an existing one in a session.

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a card component with shadow",
    "session_id": "user-123"
  }'
```

Response includes `component_code`, `status`, `validation_errors`, and resource URLs for preview and export.

### GET /preview/{session_id}

Render a live HTML preview of the session's last generated component.

```bash
curl "http://localhost:8000/preview/user-123"
```

Returns an HTML page with Tailwind CDN and embedded component markup.

### GET /export/{session_id}?format=tsx

Export the session component as a single `.tsx` file.

```bash
curl "http://localhost:8000/export/user-123?format=tsx" -o component.tsx
```

### GET /export/{session_id}?format=zip

Export the session component as a ZIP archive containing separate `.ts`, `.html`, `.css` files plus `design-tokens.md`.

```bash
curl "http://localhost:8000/export/user-123?format=zip" -o component.zip
```

### GET /reset/{session_id}

Clear all state for a session, removing component history.

```bash
curl "http://localhost:8000/reset/user-123"
```

## Multi-Turn Editing

The system maintains in-memory session state that preserves component history across multiple requests. To edit a previously generated component, send a new `/generate` request with the same `session_id` and a follow-up prompt.

**Example:**

1. First request: `{"prompt": "Create a button", "session_id": "session-1"}`
2. Second request: `{"prompt": "Make it larger and add an icon", "session_id": "session-1"}`

The second request includes the first component's code in the LLM context, allowing the model to modify the existing component rather than generating a new one from scratch.

## Export Options

The system supports two export formats:

**`.tsx` (single file)**: All three sections (TypeScript, HTML template, CSS) are bundled into a single file with comment markers. This format is convenient for quick sharing or embedding in documentation.

**`.zip` (multi-file)**: The component is split into three separate Angular files (`component.ts`, `component.html`, `component.css`) plus a `design-tokens.md` reference document. This format matches standard Angular project structure and can be directly integrated into an Angular CLI project.

Export files are saved to the `./output/` directory when using the CLI, or returned as HTTP responses when using the API.

## Live Preview

The preview system renders generated components as standalone HTML pages using Tailwind CSS via CDN. This approach requires no Angular build pipeline, making it ideal for rapid iteration and evaluation.

**Important Note**: This is an evaluation/development preview only. It is not a compiled Angular application. Production use requires Angular CLI and a proper build pipeline.

The preview page includes:
- Tailwind CDN for utility classes
- Google Fonts integration for custom typography
- Inline CSS from the generated component
- Design token values injected into Tailwind config
- Responsive container with centered layout

## Assumptions

1. **Python 3.11+**: The project uses modern Python type hints (`str | None`, `dict[str, str]`) that require Python 3.11 or later.

2. **Groq API access (or OpenAI-compatible provider)**: The system requires a valid Groq API with access to the specified model (default: `llama-3.3-70b-versatile`).

3. **Design System Compliance**: Generated components are validated against required tokens (primary-color, secondary-color, font) but may not catch all design violations. Manual review is recommended for production use.

4. **Angular Component Structure**: The LLM is instructed to generate components following Angular `@Component` decorator patterns with separate template and styles blocks.

5. **Tailwind CSS**: Generated components use Tailwind utility classes. The preview system assumes Tailwind CDN availability.

6. **In-Memory Sessions**: Session state is stored in memory only. Restarting the server clears all sessions. No database or file persistence is implemented.

7. **Single Component Focus**: The system generates one component per request. Full-page applications require multiple sequential requests or manual composition.

8. **UTF-8 Encoding**: All file operations assume UTF-8 encoding. The system explicitly sets encoding on all reads and writes to prevent platform-dependent issues.

9. **Max Retries**: The self-correction loop attempts up to 2 retries (configurable via `MAX_RETRIES`). If validation still fails after retries, the component is returned with a warning status.

10. **Prompt Length Limit**: User prompts are capped at 2000 characters to prevent excessive API costs and ensure prompt quality.

## Prompt Injection Prevention

The system implements multiple layers of defense against prompt injection attacks that could subvert the LLM's instructions or extract sensitive information.

**Input Sanitization**: Before any prompt assembly, user input passes through `sanitize_prompt()` which performs three checks:
1. **Whitespace normalization**: Leading and trailing whitespace is stripped to prevent hidden control characters.
2. **Length enforcement**: Prompts exceeding 2000 characters are rejected with an error message, preventing resource exhaustion attacks.
3. **Injection phrase detection**: The system maintains a blocklist of common injection phrases including "ignore previous instructions", "disregard", "forget instructions", "system:", "```system", "jailbreak", and "override instructions". If any phrase appears (case-insensitive) in the user input, the request is rejected.

**Output Scope Enforcement**: The system never trusts LLM output as-is. Instead, it uses deterministic extraction functions (`extract_block()`) to locate specific code sections between labeled markers (`// component.ts`, `// component.html`, `// component.css`). This approach ensures that even if the LLM attempts to include explanatory text, system prompts, or malicious code outside the expected sections, only the content between markers is processed.

**Static Analysis**: The validator performs syntax checks (brace balance, tag closure) and token compliance verification before any code is stored or exported. This catches both accidental errors and potential injection attempts that produce malformed output.

**Scaling Considerations**: For production deployments handling untrusted user input, additional measures should be implemented:
- Rate limiting per session to prevent abuse
- Content Security Policy (CSP) headers on preview endpoints to prevent XSS
- Sandboxed execution environments for preview rendering
- Component contract schemas that validate generated code against expected Angular component structure before execution
- Output filtering to remove any non-component code that might have been injected

## Scaling to Full-Page Applications

While the current system focuses on single-component generation, it can be extended to generate full-page applications through several architectural enhancements:

**Component Contracts**: Define Pydantic schemas that specify required component interfaces (inputs, outputs, lifecycle hooks). The validator would check that generated components conform to these contracts before acceptance.

**Shared State Generation**: Extend the session manager to track multiple components per session and generate shared state management code (services, stores) when components need to communicate. The LLM prompt would include context about existing components in the session, enabling it to generate compatible interfaces.

**CSP-Sandboxed Preview**: For full-page previews, implement Content Security Policy headers that restrict script execution to Angular framework code only, preventing any injected malicious JavaScript from executing. The preview renderer would wrap generated components in an Angular application shell with strict CSP policies.

**Multi-Component Orchestration**: The agentic loop would be extended to generate multiple components in sequence, with each component's prompt including references to previously generated components. The validator would check cross-component compatibility (shared interfaces, consistent styling) in addition to single-component validation.

**Build Pipeline Integration**: For production use, add an export option that generates a complete Angular CLI project structure with `ng new`-compatible files, `angular.json` configuration, and dependency management. This would enable direct deployment of generated full-page applications.
