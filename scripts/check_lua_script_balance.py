#!/usr/bin/env python3
"""Lightweight balance check for hand-written FCEUX Lua scripts."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


OPENERS = {"function", "if", "do", "repeat"}
CLOSERS = {"end", "until"}
TOKEN_RE = re.compile(r"\b(function|if|do|repeat|end|until)\b|[(){}\[\]]")


def strip_comments_and_strings(text: str) -> str:
    out: list[str] = []
    i = 0
    quote: str | None = None
    line_comment = False
    block_comment = False
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""

        if line_comment:
            if ch == "\n":
                line_comment = False
                out.append(ch)
            else:
                out.append(" ")
            i += 1
            continue

        if block_comment:
            if text.startswith("]]", i):
                block_comment = False
                out.extend("  ")
                i += 2
            else:
                out.append("\n" if ch == "\n" else " ")
                i += 1
            continue

        if quote:
            if ch == "\\":
                out.extend("  ")
                i += 2
                continue
            if ch == quote:
                quote = None
            out.append("\n" if ch == "\n" else " ")
            i += 1
            continue

        if ch == "-" and nxt == "-":
            if text.startswith("--[[", i):
                block_comment = True
                out.extend("    ")
                i += 4
            else:
                line_comment = True
                out.extend("  ")
                i += 2
            continue

        if ch in {"'", '"'}:
            quote = ch
            out.append(" ")
            i += 1
            continue

        out.append(ch)
        i += 1

    return "".join(out)


def line_for(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def check_file(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8")
    text = strip_comments_and_strings(raw)
    errors: list[str] = []
    block_stack: list[tuple[str, int]] = []
    bracket_stack: list[tuple[str, int]] = []
    bracket_pairs = {")": "(", "}": "{", "]": "["}

    for match in TOKEN_RE.finditer(text):
        token = match.group(0)
        lineno = line_for(text, match.start())
        if token in OPENERS:
            block_stack.append((token, lineno))
            continue
        if token in CLOSERS:
            if not block_stack:
                errors.append(f"line {lineno}: unmatched `{token}`")
                continue
            opener, _ = block_stack.pop()
            if token == "until" and opener != "repeat":
                errors.append(f"line {lineno}: `until` closes `{opener}`")
            if token == "end" and opener == "repeat":
                errors.append(f"line {lineno}: `end` closes `repeat`; expected `until`")
            continue
        if token in {"(", "{", "["}:
            bracket_stack.append((token, lineno))
            continue
        if token in bracket_pairs:
            expected = bracket_pairs[token]
            if not bracket_stack:
                errors.append(f"line {lineno}: unmatched `{token}`")
                continue
            opener, opener_line = bracket_stack.pop()
            if opener != expected:
                errors.append(f"line {lineno}: `{token}` closes `{opener}` from line {opener_line}")

    for token, lineno in reversed(block_stack):
        errors.append(f"line {lineno}: unclosed `{token}`")
    for token, lineno in reversed(bracket_stack):
        errors.append(f"line {lineno}: unclosed `{token}`")
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
