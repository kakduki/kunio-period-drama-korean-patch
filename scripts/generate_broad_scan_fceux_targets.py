#!/usr/bin/env python3
"""Generate FCEUX read-watch targets for broad-scan promotion candidates.

These targets watch original bytes only. They are for proving whether the
candidate records are active on a manually reached screen before any v0.5 ROM
is built.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATCHABILITY = ROOT / "rom_analysis" / "broad_scan_patchability.json"
SLOT_PLAN = ROOT / "rom_analysis" / "korean_slot_allocation_plan.json"
EXPANSION_PLAN = ROOT / "rom_analysis" / "next_glyph_expansion_plan.json"
READABLE_REFERENCE = ROOT / "text_data" / "translation_readable_reference.json"
V042_EXTRA_GLYPHS = 32
OUT_LUA = ROOT / "lua" / "kunio_broad_scan_candidate_targets.lua"
OUT_JSON = ROOT / "rom_analysis" / "broad_scan_fceux_targets.json"
OUT_MD = ROOT / "rom_analysis" / "broad_scan_fceux_targets.md"


def parse_cpu_guess(raw: str) -> int:
    text = raw.strip()
    if text.startswith("$"):
        return int(text[1:], 16)
    if text.startswith("0x"):
        return int(text, 16)
    return int(text, 16)


def parse_hex_bytes(raw: str) -> list[int]:
    return [int(part, 16) for part in raw.split() if part]


def lua_quote(value: object) -> str:
    text = str(value)
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def normalize_label(row: dict[str, object]) -> str:
    rom = str(row["rom_offset"]).replace("0x", "").lower()
    romaji = str(row.get("romaji") or row.get("source") or "candidate")
    clean = "".join(ch.lower() if ch.isalnum() else "_" for ch in romaji)
    clean = "_".join(part for part in clean.split("_") if part)
    return f"broad_{rom}_{clean}"


def load_v042_prg_bytes() -> dict[str, str]:
    plan = json.loads(SLOT_PLAN.read_text(encoding="utf-8"))
    expansion = json.loads(EXPANSION_PLAN.read_text(encoding="utf-8"))
    slots = {
        str(slot["glyph"]): str(slot["prg_plus_0x7a_byte"])
        for slot in plan.get("slots", [])
    }
    for slot in expansion.get("next_slots", [])[:V042_EXTRA_GLYPHS]:
        slots[str(slot["glyph"])] = str(slot["prg_plus_0x7a_byte"])
    return slots


def load_readable_by_romaji() -> dict[str, dict[str, object]]:
    payload = json.loads(READABLE_REFERENCE.read_text(encoding="utf-8"))
    out: dict[str, dict[str, object]] = {}
    for row in payload.get("translation_data_joined", []):
        romaji = str(row.get("romaji", "")).strip()
        if romaji and romaji not in out:
            out[romaji] = row
    return out


def readable_text(row: dict[str, object], reference: dict[str, dict[str, object]]) -> dict[str, object]:
    ref = reference.get(str(row.get("romaji", "")).strip(), {})
    return {
        "source": ref.get("source") or row.get("source", ""),
        "korean": ref.get("korean") or row.get("korean", ""),
        "category": ref.get("category") or row.get("category", ""),
        "reference_context": ref.get("transcription_context") or ref.get("section") or "",
    }


def planned_bytes(
    row: dict[str, object],
    extension_by_glyph: dict[str, str],
    v042_by_glyph: dict[str, str],
) -> str:
    values = []
    for glyph in row.get("korean_glyphs", []):
        if glyph in v042_by_glyph:
            values.append(v042_by_glyph[glyph])
            continue
        if glyph in extension_by_glyph:
            values.append(extension_by_glyph[glyph])
            continue
        values.append("unknown")
    return " ".join(values)


def build_payload() -> dict[str, object]:
    data = json.loads(PATCHABILITY.read_text(encoding="utf-8"))
    readable_by_romaji = load_readable_by_romaji()
    extension_by_glyph = {
        str(slot["glyph"]): str(slot["planned_prg_byte"])
        for slot in data.get("glyph_extension_if_promoted", [])
    }
    v042_by_glyph = load_v042_prg_bytes()

    targets = []
    for row in data.get("promotion_candidates", []):
        readable = readable_text(row, readable_by_romaji)
        start = parse_cpu_guess(str(row["cpu_address_guess"]))
        expected_len = len(parse_hex_bytes(str(row["bytes"])))
        target = {
            "label": normalize_label(row),
            "source": readable["source"],
            "romaji": row.get("romaji", ""),
            "korean": readable["korean"],
            "category": readable["category"],
            "reference_context": readable["reference_context"],
            "confidence": row.get("confidence", ""),
            "rom_offset": row.get("rom_offset", ""),
            "bank16": row.get("bank16", ""),
            "start": start,
            "stop": start + expected_len - 1,
            "expected_original_bytes": row.get("bytes", ""),
            "old_bytes": row.get("bytes", ""),
            "future_patch_bytes_preview": planned_bytes(row, extension_by_glyph, v042_by_glyph),
            "new_glyphs": row.get("new_glyphs", []),
            "reason": row.get("reason", ""),
        }
        targets.append(target)

    targets.sort(key=lambda row: (int(str(row["rom_offset"]), 16), str(row["label"])))
    return {
        "source": str(PATCHABILITY.relative_to(ROOT)),
        "readable_reference": str(READABLE_REFERENCE.relative_to(ROOT)),
        "target_count": len(targets),
        "purpose": "manual read-watch proof for v0.4.2 font-ready promotion candidates; watches original bytes only",
        "preview_rule": f"future patch preview uses v0.4.2 font bytes: base compact slots plus first {V042_EXTRA_GLYPHS} planned extra glyphs",
        "targets": targets,
    }


def write_lua(payload: dict[str, object]) -> None:
    lines = [
        "-- Auto-generated by scripts/generate_broad_scan_fceux_targets.py.",
        "-- Targets expect original bytes for broad-scan promotion candidates.",
        "-- Use on the base ROM first; do not treat hits as patch approval without screen context.",
        "return {",
    ]
    for target in payload["targets"]:
        lines.append(
            "  { "
            f"label = {lua_quote(target['label'])}, "
            f"category = {lua_quote(target['category'])}, "
            f"rom = 0x{int(str(target['rom_offset']), 16):05X}, "
            f"start = 0x{target['start']:04X}, "
            f"stop = 0x{target['stop']:04X}, "
            f"bytes = {lua_quote(target['expected_original_bytes'])}, "
            f"old_bytes = {lua_quote(target['old_bytes'])}, "
            f"source = {lua_quote(target['source'])}, "
            f"romaji = {lua_quote(target['romaji'])}, "
            f"korean = {lua_quote(target['korean'])}, "
            f"confidence = {lua_quote(target['confidence'])} "
            "},"
        )
    lines.append("}")
    OUT_LUA.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_markdown(payload: dict[str, object]) -> None:
    lines = [
        "# Broad Scan FCEUX Targets",
        "",
        "These targets watch original bytes for broad-scan promotion candidates.",
        "They are for manual screen proof before promoting any new text into the v0.4.2 line.",
        "",
        f"- Source: `{payload['source']}`",
        f"- Readable reference: `{payload['readable_reference']}`",
        f"- Targets: **{payload['target_count']}**",
        f"- Preview rule: {payload['preview_rule']}",
        "",
        "Run after manually reaching the related screen:",
        "",
        "```powershell",
        "python scripts/run_fceux_lua_analysis.py --lua-script lua/kunio_bank1_watch.lua --target-lua lua/kunio_broad_scan_candidate_targets.lua --frames 900 --timeout 60 --final-output rom_analysis/fceux_broad_scan_candidates --clean-output --no-dump-hex --no-dump-bin",
        "```",
        "",
        "## Targets",
        "",
        "| ROM | CPU range | confidence | romaji | source | korean | context | original bytes | future patch preview | new glyphs |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for target in payload["targets"]:
        new_glyphs = "".join(target.get("new_glyphs", [])) or "-"
        lines.append(
            f"| `{target['rom_offset']}` | `${target['start']:04X}-${target['stop']:04X}` | "
            f"{target['confidence']} | {target['romaji']} | {target['source']} | {target['korean']} | "
            f"{target.get('reference_context', '') or '-'} | "
            f"`{target['expected_original_bytes']}` | `{target['future_patch_bytes_preview']}` | {new_glyphs} |"
        )

    lines += [
        "",
        "## Promotion Rule",
        "",
        "- A CPU read hit proves only that the record was read in that run.",
        "- Promote to a v0.5 patch candidate only when the screen context also matches the intended label/dialogue.",
        "- Under v0.4.2 these seven rows are font-ready, but visual/screen proof is still required before patching.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = build_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_lua(payload)
    write_markdown(payload)
    print(f"Wrote {OUT_LUA}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(f"targets={payload['target_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
