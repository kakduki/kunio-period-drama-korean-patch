#!/usr/bin/env python3
"""Lightweight syntax sanity check for generated FCEUX Lua target tables."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


FIELD_RE = re.compile(r"\b(label|category|bytes|old_bytes|source|korean)\s*=\s*\"(?:\\.|[^\"])*\"")


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    if "return {" not in text:
        errors.append("missing `return {`")
    if not text.rstrip().endswith("}"):
        errors.append("file does not end with `}`")
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("{") and not stripped.startswith("--") and stripped not in {"return {", "}"}:
            continue
        if stripped.startswith("{"):
            quote_count = 0
            escaped = False
            for char in line:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quote_count += 1
            if quote_count % 2:
                errors.append(f"line {lineno}: odd number of string quotes")
            if not stripped.endswith("},"):
                errors.append(f"line {lineno}: target row should end with `}},`")
            fields = {match.group(1) for match in FIELD_RE.finditer(line)}
            missing = {"label", "category", "bytes", "old_bytes", "source", "korean"} - fields
            if missing:
                errors.append(f"line {lineno}: missing quoted field(s): {', '.join(sorted(missing))}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()
    failed = False
    for raw in args.files:
        path = Path(raw).expanduser().resolve()
        errors = check_file(path)
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
