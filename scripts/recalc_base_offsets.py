#!/usr/bin/env python3
"""Reverse-calculate base offsets from autoplay runtime read bytes.

For each mismatched target in bank1_watch_targets.json:
  expected_byte = (HIRAGANA_LOW[char] + base) & 0xFF
  → base_candidate = (actual_byte - HIRAGANA_LOW[char]) & 0xFF

If all chars yield the same base_candidate → runtime bytes ARE encoding the text
with a different base.  If inconsistent → runtime bytes are unrelated (wrong bank).

Updates bank1_watch_targets.json:
  - adds "runtime_base_candidates" field with per-char analysis
  - if consistent base found: updates expected_bytes and base
  - if inconsistent: adds note, keeps existing expected_bytes
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HIRAGANA_LOW: dict[str, int] = {
    "あ": 0x01, "い": 0x02, "う": 0x03, "え": 0x04, "お": 0x05,
    "か": 0x06, "き": 0x07, "く": 0x08, "け": 0x09, "こ": 0x0A,
    "さ": 0x0B, "し": 0x0C, "す": 0x0D, "せ": 0x0E, "そ": 0x0F,
    "た": 0x10, "ち": 0x11, "つ": 0x12, "て": 0x13, "と": 0x14,
    "な": 0x15, "に": 0x16, "ぬ": 0x17, "ね": 0x18, "の": 0x19,
    "は": 0x1A, "ひ": 0x1B, "ふ": 0x1C, "へ": 0x1D, "ほ": 0x1E,
    "ま": 0x20, "み": 0x21, "む": 0x22, "め": 0x23, "も": 0x24,
    "や": 0x25, "ゆ": 0x26, "よ": 0x27,
    "ら": 0x28, "り": 0x29, "る": 0x2A, "れ": 0x2B, "ろ": 0x2C,
    "わ": 0x2D, "を": 0x2E, "ん": 0x2F,
}

VOICED_TO_BASE: dict[str, str] = {
    "が": "か", "ぎ": "き", "ぐ": "く", "げ": "け", "ご": "こ",
    "ざ": "さ", "じ": "し", "ず": "す", "ぜ": "せ", "ぞ": "そ",
    "だ": "た", "ぢ": "ち", "づ": "つ", "で": "て", "ど": "と",
    "ば": "は", "び": "ひ", "ぶ": "ふ", "べ": "へ", "ぼ": "ほ",
    "ぱ": "は", "ぴ": "ひ", "ぷ": "ふ", "ぺ": "へ", "ぽ": "ほ",
}

KATAKANA_OFFSET = ord("ァ") - ord("ぁ")


def to_hiragana(ch: str) -> str:
    code = ord(ch)
    if ord("ァ") <= code <= ord("ヶ"):
        return chr(code - KATAKANA_OFFSET)
    return ch


def fold_voiced(ch: str) -> str:
    return VOICED_TO_BASE.get(ch, ch)


def normalize(text: str) -> list[str]:
    chars = []
    for ch in text:
        h = to_hiragana(ch)
        f = fold_voiced(h)
        if f in HIRAGANA_LOW:
            chars.append(f)
    return chars


def encode(text: str, base: int) -> list[int]:
    return [(HIRAGANA_LOW[ch] + base) & 0xFF for ch in normalize(text)]


def calc_base_candidates(text: str, actual_bytes: list[int]) -> list[dict]:
    chars = normalize(text)
    results = []
    for i, (ch, actual) in enumerate(zip(chars, actual_bytes)):
        low = HIRAGANA_LOW[ch]
        candidate = (actual - low) & 0xFF
        results.append({
            "char": ch,
            "hiragana_low": f"0x{low:02X}",
            "actual_byte": f"0x{actual:02X}",
            "base_candidate": f"0x{candidate:02X}",
        })
    return results


def parse_byte_diff(byte_diff: str) -> list[int] | None:
    """Parse byte_diff string like '9C>53 90>70 A8>60' → [0x53, 0x70, 0x60]."""
    if not byte_diff or byte_diff == "no_expected":
        return None
    parts = byte_diff.split()
    result = []
    for p in parts:
        if ">" in p:
            _, actual = p.split(">")
            result.append(int(actual, 16))
        elif p.startswith("="):
            result.append(int(p[1:], 16))
    return result if result else None


def main() -> int:
    targets_path = ROOT / "rom_analysis" / "bank1_watch_targets.json"
    reads_path   = ROOT / "rom_analysis" / "fceux_bank1_watch_test" / "bank1_reads.tsv"

    targets_data = json.loads(targets_path.read_text(encoding="utf-8"))

    # Build label → top byte_diff from TSV
    byte_diff_by_label: dict[str, str] = {}
    if reads_path.exists():
        import csv
        from collections import Counter
        diffs_by_label: dict[str, Counter] = {}
        for row in csv.DictReader(reads_path.open(encoding="utf-8"), delimiter="\t"):
            label = row.get("label", "")
            bd = row.get("byte_diff", "")
            if label and bd:
                diffs_by_label.setdefault(label, Counter())[bd] += 1
        for label, cnt in diffs_by_label.items():
            byte_diff_by_label[label] = cnt.most_common(1)[0][0]

    print("=" * 70)
    print("Base offset recalculation from runtime read bytes")
    print("Formula: ROM_byte = (HIRAGANA_LOW[char] + base) & 0xFF")
    print("         base_candidate = (actual_byte - HIRAGANA_LOW[char]) & 0xFF")
    print("=" * 70)

    updated = 0
    for target in targets_data["targets"]:
        label   = target["label"]
        source  = target.get("source", "")
        base    = int(target.get("base", "0x00"), 16)
        exp_str = target.get("expected_bytes", "")
        bd      = byte_diff_by_label.get(label, "")

        if not bd:
            continue

        actual = parse_byte_diff(bd)
        if actual is None:
            continue

        chars = normalize(source)
        if not chars or len(actual) < len(chars):
            continue

        actual_trimmed = actual[:len(chars)]
        candidates = calc_base_candidates(source, actual_trimmed)
        bases_set = {int(c["base_candidate"], 16) for c in candidates}
        consistent = len(bases_set) == 1
        new_base = next(iter(bases_set)) if consistent else None

        # Report
        print(f"\n[{label}]  source={source!r}  declared_base=0x{base:02X}")
        print(f"  byte_diff  : {bd}")
        print(f"  expected   : {exp_str}")
        for c in candidates:
            print(f"    {c['char']} low={c['hiragana_low']}  actual={c['actual_byte']}  base_candidate={c['base_candidate']}")

        if consistent and new_base is not None and new_base != base:
            new_expected = encode(source, new_base)
            new_expected_str = " ".join(f"{b:02X}" for b in new_expected)
            print(f"  -> CONSISTENT base 0x{new_base:02X}! new expected_bytes: {new_expected_str}")
            target["base"] = f"0x{new_base:02X}"
            target["expected_bytes"] = new_expected_str
            target["runtime_base_note"] = (
                f"base updated 0x{base:02X}->0x{new_base:02X} from runtime bytes; "
                f"old expected_bytes were {exp_str}"
            )
            updated += 1
        else:
            bases_str = ", ".join(f"0x{b:02X}" for b in sorted(bases_set))
            print(f"  -> INCONSISTENT bases ({bases_str}) - runtime bytes NOT encoding {source!r}")
            print(f"     Likely cause: CPU address mapped to different ROM bank during test window")
            target.setdefault("runtime_base_note",
                f"runtime bytes {' '.join(f'{a:02X}' for a in actual_trimmed)} "
                f"don't encode with any consistent base "
                f"(candidates: {bases_str}); expected_bytes unchanged"
            )

    print(f"\n{'=' * 70}")
    print(f"Updated {updated} target(s) with new base offset.")
    if updated == 0:
        print("No consistent base found → expected_bytes unchanged.")
        print("Root cause: mismatched targets have CPU addresses read while a")
        print("different ROM bank is loaded (not the text bank).")

    targets_path.write_text(
        json.dumps(targets_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Written: {targets_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
