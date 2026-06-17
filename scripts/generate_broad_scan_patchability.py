#!/usr/bin/env python3
"""Classify broad-scan capture candidates by PRG patchability.

This report does not approve new patches. It identifies which broad-scan hits
are even worth considering for a future v0.5 test ROM after screen proof.
"""

from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE_JSON = ROOT / "rom_analysis" / "translation_scan_capture_queue.json"
SLOT_PLAN_JSON = ROOT / "rom_analysis" / "korean_slot_allocation_plan.json"
OUT_JSON = ROOT / "rom_analysis" / "broad_scan_patchability.json"
OUT_MD = ROOT / "rom_analysis" / "broad_scan_patchability.md"

CONTROL_LIKE = {0x00, 0xFF, 0xF0, 0xF8, 0xF9, 0xFA, 0xFB, 0xFC, 0xFD, 0xFE}
PATCH_TILE_START = 0x101
PATCH_TILE_END = 0x1B5


def korean_chars(text: str) -> list[str]:
    return [ch for ch in text if "\uac00" <= ch <= "\ud7a3"]


def parse_hex_bytes(raw: str) -> list[int]:
    return [int(part, 16) for part in raw.split() if part]


def load_existing_slots() -> dict[str, dict[str, object]]:
    plan = json.loads(SLOT_PLAN_JSON.read_text(encoding="utf-8"))
    return {str(slot["glyph"]): slot for slot in plan.get("slots", [])}


def planned_prg_byte_for_new_slot(slot_index: int) -> str:
    tile = PATCH_TILE_START + slot_index
    return f"0x{((tile - 0x7A) & 0xFF):02X}"


def classify(row: dict[str, object], existing_slots: dict[str, dict[str, object]]) -> dict[str, object]:
    source_bytes = parse_hex_bytes(str(row["bytes"]))
    glyphs = korean_chars(str(row["korean"]))
    new_glyphs = [glyph for glyph in glyphs if glyph not in existing_slots]
    has_control = any(byte in CONTROL_LIKE for byte in source_bytes)
    length_equal = len(source_bytes) == len(glyphs)
    bank1 = int(row["bank16"]) == 1
    confidence = str(row["confidence"])
    priority = int(row["priority"])

    reasons = []
    if not bank1:
        reasons.append("not Bank 1")
    if has_control:
        reasons.append("source bytes contain control-like values")
    if not length_equal:
        reasons.append(f"length mismatch source_bytes={len(source_bytes)} korean_glyphs={len(glyphs)}")
    if priority > 15:
        reasons.append(f"capture priority {priority} is not high enough for promotion")
    if confidence not in {"high", "medium"}:
        reasons.append(f"confidence {confidence!r} is not high/medium")

    promotable_after_screen_proof = not reasons
    return {
        **row,
        "source_byte_len": len(source_bytes),
        "korean_glyphs": glyphs,
        "korean_glyph_len": len(glyphs),
        "new_glyphs": new_glyphs,
        "existing_glyphs": [glyph for glyph in glyphs if glyph in existing_slots],
        "contains_control_like_bytes": has_control,
        "length_equal": length_equal,
        "promotable_after_screen_proof": promotable_after_screen_proof,
        "blockers": reasons,
    }


def build_extended_slots(rows: list[dict[str, object]], existing_slots: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    required: "OrderedDict[str, list[str]]" = OrderedDict()
    for row in rows:
        if not row["promotable_after_screen_proof"]:
            continue
        for glyph in row["korean_glyphs"]:
            required.setdefault(glyph, []).append(str(row["rom_offset"]))

    existing_count = len(existing_slots)
    extension = []
    for glyph, users in required.items():
        if glyph in existing_slots:
            continue
        slot_index = existing_count + len(extension)
        tile = PATCH_TILE_START + slot_index
        if tile > PATCH_TILE_END:
            raise RuntimeError("Broad-scan glyph extension exceeds available CHR patch slots")
        extension.append(
            {
                "slot_index": slot_index,
                "glyph": glyph,
                "tile": f"0x{tile:03X}",
                "planned_prg_byte": planned_prg_byte_for_new_slot(slot_index),
                "used_by_rom_offsets": users,
            }
        )
    return extension


def main() -> int:
    queue = json.loads(QUEUE_JSON.read_text(encoding="utf-8"))
    existing_slots = load_existing_slots()
    rows = [classify(row, existing_slots) for row in queue["queue"]]
    promotion_candidates = [row for row in rows if row["promotable_after_screen_proof"]]
    glyph_extension = build_extended_slots(rows, existing_slots)

    payload = {
        "source": {
            "queue": str(QUEUE_JSON.relative_to(ROOT)),
            "slot_plan": str(SLOT_PLAN_JSON.relative_to(ROOT)),
        },
        "summary": {
            "queued_hits": len(rows),
            "promotion_candidates_after_screen_proof": len(promotion_candidates),
            "existing_required_glyphs": len(existing_slots),
            "additional_glyphs_if_promoted": len(glyph_extension),
            "available_slots": PATCH_TILE_END - PATCH_TILE_START + 1,
        },
        "promotion_candidates": promotion_candidates,
        "glyph_extension_if_promoted": glyph_extension,
        "classified_queue": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Broad Scan Patchability",
        "",
        "This report filters broad-scan hits into future v0.5 candidates.",
        "A row here still needs real screen proof before it should be patched.",
        "",
        "## Summary",
        "",
        f"- Queued broad-scan hits: **{payload['summary']['queued_hits']}**",
        f"- Promotion candidates after screen proof: **{payload['summary']['promotion_candidates_after_screen_proof']}**",
        f"- Existing required glyphs: **{payload['summary']['existing_required_glyphs']}**",
        f"- Additional glyphs if promoted: **{payload['summary']['additional_glyphs_if_promoted']}**",
        f"- Available CHR patch slots: **{payload['summary']['available_slots']}**",
        "",
        "## Promotion Candidates After Screen Proof",
        "",
        "| confidence | source | korean | ROM | bank | bytes | glyphs | new glyphs |",
        "| --- | --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for row in promotion_candidates:
        lines.append(
            f"| {row['confidence']} | {row['source']} | {row['korean']} | `{row['rom_offset']}` | "
            f"{row['bank16']} | `{row['bytes']}` | {''.join(row['korean_glyphs']) or '-'} | "
            f"{''.join(row['new_glyphs']) or '-'} |"
        )

    lines += [
        "",
        "## Additional Glyph Slots If Promoted",
        "",
        "| slot | glyph | tile | planned PRG byte | used by ROM offsets |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for slot in glyph_extension:
        users = ", ".join(slot["used_by_rom_offsets"])
        lines.append(
            f"| {slot['slot_index']} | {slot['glyph']} | `{slot['tile']}` | "
            f"`{slot['planned_prg_byte']}` | {users} |"
        )

    lines += [
        "",
        "## Blocked Examples",
        "",
        "| source | korean | ROM | bytes | blockers |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        if row["promotable_after_screen_proof"]:
            continue
        blockers = "; ".join(row["blockers"])
        lines.append(
            f"| {row['source']} | {row['korean']} | `{row['rom_offset']}` | `{row['bytes']}` | {blockers} |"
        )
        if len(lines) > 80:
            break

    lines += [
        "",
        "## Rule",
        "",
        "- Do not build a v0.5 ROM from these rows until the corresponding screen dump confirms active bytes.",
        "- Length mismatches and control-like source bytes remain non-promotable from static evidence.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(
        "queued={queued_hits} promotable={promotion_candidates_after_screen_proof} additional_glyphs={additional_glyphs_if_promoted}".format(
            **payload["summary"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
