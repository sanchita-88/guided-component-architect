"""Validates generated component code for design token compliance and basic syntax correctness."""

import re
import json

REQUIRED_TOKENS = ["primary-color", "secondary-color"]
VOID_ELEMENTS = {
    "input", "br", "hr", "img", "link", "meta",
    "area", "base", "col", "embed", "param", "source", "track", "wbr"
}


def extract_block(code: str, start_marker: str, end_marker: str) -> str:
    """Extract text between two marker strings. Returns empty string if not found."""
    if start_marker not in code:
        return ""
    start = code.index(start_marker) + len(start_marker)
    if end_marker not in code[start:]:
        return code[start:].strip()
    end = code.index(end_marker, start)
    return code[start:end].strip()


def check_token_compliance(code: str, tokens: dict) -> list[str]:
    """Check that required design token values appear in generated code."""
    errors = []
    for key in REQUIRED_TOKENS:
        if key not in tokens:
            continue
        hex_val = tokens[key].lstrip("#").lower()
        if not re.search(hex_val, code, re.IGNORECASE):
            errors.append(
                f"MISSING TOKEN: '{key}' ({tokens[key]}) not found in generated code."
            )
    font = tokens.get("font", "").strip("'\"")
    if font and font.lower() not in code.lower():
        errors.append(f"MISSING TOKEN: font '{font}' not referenced in component.")
    return errors


def check_syntax(code: str) -> list[str]:
    """Check brace balance in TS block and tag balance in HTML block."""
    errors = []
    ts_block = extract_block(code, "// component.ts", "// component.html")
    if ts_block:
        opens = ts_block.count("{")
        closes = ts_block.count("}")
        if opens != closes:
            errors.append(
                f"SYNTAX ERROR: Mismatched curly braces in TypeScript block "
                f"({opens} open, {closes} close)."
            )
    html_block = extract_block(code, "// component.html", "// component.css")
    if html_block:
        open_tags = [
            t.lower()
            for t in re.findall(r"<([a-zA-Z][a-zA-Z0-9-]*)[\s>]", html_block)
            if t.lower() not in VOID_ELEMENTS
        ]
        close_tags = [
            t.lower()
            for t in re.findall(r"</([a-zA-Z][a-zA-Z0-9-]*)>", html_block)
        ]
        if sorted(open_tags) != sorted(close_tags):
            errors.append(
                f"SYNTAX ERROR: Unbalanced HTML tags. "
                f"Opened: {sorted(set(open_tags))}, Closed: {sorted(set(close_tags))}."
            )
    return errors


def validate(code: str, tokens: dict) -> list[str]:
    """Run all validation checks. Returns combined error list (empty = valid)."""
    return check_token_compliance(code, tokens) + check_syntax(code)
