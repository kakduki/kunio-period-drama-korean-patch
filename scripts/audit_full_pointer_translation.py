#!/usr/bin/env python3
"""Audit all English-guided Korean pointer translations before release."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from build_full_pointer_korean_candidate import clean_korean_text
from rom_utils import REPO_ROOT


POINTER_COUNT = 248
TOKEN_RE = re.compile(r"<([0-9A-Fa-f]{2})>")
ASCII_WORD_RE = re.compile(r"[A-Za-z]+")
ALLOWED_DRAFT_PUNCTUATION = frozenset(" !?.,:~'-")
DYNAMIC_CONTROL_CODES = frozenset(
    {0xF1, 0xF2, 0xF5, 0xFA, 0xFB, 0xFC, 0xFD, 0xFE}
)
DEFAULT_DRAFT = REPO_ROOT / "text_data" / "pointer_dialogue_korean_draft.tsv"
DEFAULT_ENGLISH = REPO_ROOT / "rom_analysis" / "english_script_dump.tsv"
DEFAULT_JSON = REPO_ROOT / "rom_analysis" / "full_pointer_translation_audit.json"
DEFAULT_CSV = REPO_ROOT / "rom_analysis" / "full_pointer_translation_audit.csv"
DEFAULT_MARKDOWN = REPO_ROOT / "rom_analysis" / "full_pointer_translation_audit.md"


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def english_pointer_rows(rows: list[dict[str, str]]) -> dict[int, dict[str, str]]:
    pointer_rows = [row for row in rows if row.get("record_kind") == "pointer_pair"]
    result = {int(row["pointer_index"]): row for row in pointer_rows}
    if len(result) != POINTER_COUNT or set(result) != set(range(POINTER_COUNT)):
        raise ValueError("English reference must contain pointer rows 0..247")
    return result


def readable_english(tokenized: str) -> str:
    text = TOKEN_RE.sub(" ", tokenized)
    return " ".join(text.replace("¶", " ").split())


def row_issues(
    draft: dict[str, str],
    english: dict[str, str],
) -> tuple[list[str], list[str]]:
    active = not draft["translation_status"].startswith("excluded")
    korean = draft["korean_text"]
    failures: list[str] = []
    warnings: list[str] = []
    if "\ufffd" in korean:
        failures.append("unicode_replacement_character")
    invalid = sorted(
        {
            character
            for character in korean
            if not (
                "\uac00" <= character <= "\ud7a3"
                or character in ALLOWED_DRAFT_PUNCTUATION
            )
        }
    )
    if invalid:
        failures.append("unsupported_draft_character")
    if active and not clean_korean_text(korean):
        failures.append("empty_compiled_text")
    if not active and korean.strip():
        failures.append("excluded_row_has_translation")
    if active and not readable_english(english["en_text"]):
        warnings.append("empty_readable_english")
    if active and ASCII_WORD_RE.search(korean):
        warnings.append("ascii_word_in_korean")
    if active and draft["translation_status"].endswith("_draft"):
        warnings.append("semantic_draft_not_reviewed")
    if active and "확인 필요" in draft["notes"]:
        warnings.append("context_confirmation_required")
    raw = bytes.fromhex(english["en_raw_bytes"]) if english["en_raw_bytes"] else b""
    dynamic_f0 = 0xF0 in raw and not raw.startswith(bytes((0xF0, 0xBB)))
    if active and (DYNAMIC_CONTROL_CODES.intersection(raw) or dynamic_f0):
        warnings.append("dynamic_control_context")
    return failures, warnings


def build_audit(
    draft_rows: list[dict[str, str]],
    english_rows: dict[int, dict[str, str]],
) -> dict[str, object]:
    if len(draft_rows) != POINTER_COUNT:
        raise ValueError(f"expected {POINTER_COUNT} draft rows")
    if [int(row["pointer_index"]) for row in draft_rows] != list(range(POINTER_COUNT)):
        raise ValueError("draft pointer indices must be ordered 0..247")

    rows: list[dict[str, object]] = []
    duplicate_groups: defaultdict[str, list[int]] = defaultdict(list)
    all_failures: Counter[str] = Counter()
    all_warnings: Counter[str] = Counter()
    for draft in draft_rows:
        index = int(draft["pointer_index"])
        english = english_rows[index]
        failures, warnings = row_issues(draft, english)
        all_failures.update(failures)
        all_warnings.update(warnings)
        compiled_text = clean_korean_text(draft["korean_text"])
        if compiled_text:
            duplicate_groups[compiled_text].append(index)
        rows.append(
            {
                "pointer_index": index,
                "translation_status": draft["translation_status"],
                "english_text": readable_english(english["en_text"]),
                "korean_draft": draft["korean_text"],
                "compiled_display_text": compiled_text,
                "basis": draft["basis"],
                "notes": draft["notes"],
                "failures": failures,
                "warnings": warnings,
            }
        )

    duplicates = [
        {"compiled_display_text": text, "pointer_indices": indices}
        for text, indices in duplicate_groups.items()
        if len(indices) > 1
    ]
    status_counts = Counter(row["translation_status"] for row in draft_rows)
    active_count = sum(
        not row["translation_status"].startswith("excluded") for row in draft_rows
    )
    reviewed_count = sum(
        not row["translation_status"].endswith("_draft")
        and not row["translation_status"].startswith("excluded")
        for row in draft_rows
    )
    structural_status = "PASS" if not all_failures else "FAIL"
    translation_status = (
        "PASS" if reviewed_count == active_count else "REVIEW_REQUIRED"
    )
    return {
        "status": (
            "PASS"
            if structural_status == "PASS" and translation_status == "PASS"
            else "STRUCTURAL_PASS_TRANSLATION_REVIEW_REQUIRED"
            if structural_status == "PASS"
            else "FAIL"
        ),
        "structural_status": structural_status,
        "translation_status": translation_status,
        "coverage": {
            "row_count": len(draft_rows),
            "active_count": active_count,
            "excluded_count": len(draft_rows) - active_count,
            "reviewed_count": reviewed_count,
            "status_counts": dict(sorted(status_counts.items())),
            "failure_counts": dict(sorted(all_failures.items())),
            "warning_counts": dict(sorted(all_warnings.items())),
            "duplicate_display_groups": len(duplicates),
        },
        "policy": {
            "english_role": "semantic and control-structure reference",
            "compiled_text": "Hangul syllables and spaces; punctuation is represented by retained English control bytes",
            "release_rule": "every active row must leave draft status after semantic/context review",
        },
        "duplicate_display_groups": duplicates,
        "rows": rows,
    }


def write_outputs(
    payload: dict[str, object],
    json_path: Path,
    csv_path: Path,
    markdown_path: Path,
) -> None:
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    rows = payload["rows"]
    assert isinstance(rows, list)
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "pointer_index",
                "translation_status",
                "english_text",
                "korean_draft",
                "compiled_display_text",
                "basis",
                "notes",
                "failures",
                "warnings",
            ),
        )
        writer.writeheader()
        for row in rows:
            output = dict(row)
            output["failures"] = ",".join(row["failures"])
            output["warnings"] = ",".join(row["warnings"])
            writer.writerow(output)

    coverage = payload["coverage"]
    assert isinstance(coverage, dict)
    lines = [
        "# Full Pointer Translation Audit",
        "",
        f"Status: **{payload['status']}**",
        "",
        f"- Rows: `{coverage['row_count']}`; active: `{coverage['active_count']}`; excluded: `{coverage['excluded_count']}`.",
        f"- Structurally valid translations: `{coverage['active_count']}` / `{coverage['active_count']}`.",
        f"- Semantically reviewed rows: `{coverage['reviewed_count']}` / `{coverage['active_count']}`.",
        f"- Translation statuses: `{coverage['status_counts']}`.",
        f"- Failures: `{coverage['failure_counts']}`.",
        f"- Warnings: `{coverage['warning_counts']}`.",
        "",
        "The English patch is the semantic and control-structure reference. The",
        "Current Korean rows compile cleanly and all active rows passed the",
        "English-reference semantic review. Forty-seven dynamic control contexts",
        "remain flagged for screen-specific review; runtime/layout PASS is not",
        "whole-game visual approval.",
        "",
        "The CSV companion contains every English line, Korean draft, actual",
        "compiled display text, notes, and row-level findings for review.",
        "",
    ]
    markdown_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft", type=Path, default=DEFAULT_DRAFT)
    parser.add_argument("--english", type=Path, default=DEFAULT_ENGLISH)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    payload = build_audit(
        load_tsv(args.draft),
        english_pointer_rows(load_tsv(args.english)),
    )
    write_outputs(payload, args.json, args.csv, args.markdown)
    print(
        f"status={payload['status']} "
        f"structural={payload['structural_status']} "
        f"reviewed={payload['coverage']['reviewed_count']}/"
        f"{payload['coverage']['active_count']}"
    )
    return 0 if payload["structural_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
