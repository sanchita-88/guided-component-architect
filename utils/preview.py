"""Renders a standalone HTML preview of a generated component using Tailwind CDN. No Angular build required."""

from core.validator import extract_block


def render_preview(component_code: str, tokens: dict) -> str:
    """
    Build a standalone HTML page embedding the component with Tailwind CDN.
    Caller must write output with encoding='utf-8' if saving to disk.
    """
    html_block = extract_block(component_code, "// component.html", "// component.css")
    print("HTML BLOCK DEBUG:")
    print(html_block)
    css_marker = "// component.css"
    css_start = component_code.find(css_marker)
    css_block = component_code[css_start + len(css_marker):].strip() if css_start != -1 else ""
    primary = tokens.get("primary-color", "#6366f1")
    bg = tokens.get("background-color", "#0f172a")
    font = tokens.get("font", "Inter")
    font_url = font.replace(" ", "+")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Component Preview — Guided Component Architect</title>
  <link href="https://fonts.googleapis.com/css2?family={font_url}:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          colors: {{ primary: '{primary}' }},
          fontFamily: {{ sans: ['{font}', 'sans-serif'] }}
        }}
      }}
    }}
  </script>
  <style>
    body {{
      background-color: {bg};
      font-family: '{font}', sans-serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem;
    }}
    {css_block}
  </style>
</head>
<body>
  <div class="w-full max-w-2xl">
    {html_block}
  </div>
  <p style="position:fixed;bottom:8px;right:12px;color:#475569;font-size:11px;">
    ⚡ Guided Component Architect — Dev Preview (Tailwind CDN)
  </p>
</body>
</html>"""
