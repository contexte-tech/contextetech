"""Validation des formats de ressources (miroir de web/src/lib/format.js)."""
import json
import re

VAR_RE = re.compile(r"\{\{\s*([\w-]+)\s*\}\}")


def vars_of(template: str) -> list[str]:
    seen: list[str] = []
    for m in VAR_RE.finditer(template or ""):
        if m.group(1) not in seen:
            seen.append(m.group(1))
    return seen


def detect_format(row) -> str | None:
    if not isinstance(row, dict):
        return None
    if isinstance(row.get("messages"), list):
        return "chat"
    if "instruction" in row or ("input" in row and "output" in row):
        return "instruction"
    if "prompt" in row and "completion" in row:
        return "completion"
    return None


class DatasetError(ValueError):
    pass


def scan_jsonl(lines, keep_preview: int = 20):
    """Valide un flux de lignes JSONL. Renvoie (nb_lignes, format, aperçu)."""
    count, fmt, preview = 0, None, []
    for i, raw in enumerate(lines, start=1):
        line = raw.strip() if isinstance(raw, str) else raw.decode("utf-8").strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            raise DatasetError(f"invalid_json_line:{i}") from None
        f = detect_format(row)
        if f is None:
            raise DatasetError(f"unknown_format_line:{i}")
        fmt = fmt or f
        count += 1
        if len(preview) < keep_preview:
            preview.append(row)
    if count == 0:
        raise DatasetError("empty_dataset")
    return count, fmt, preview
