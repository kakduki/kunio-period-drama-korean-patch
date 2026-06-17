#!/usr/bin/env python3
"""Plan Korean glyph slot allocation for the current Bank 1 offset inventory."""

from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "rom_analysis" / "bank1_offset_inventory.json"
CHAR_MAP = ROOT / "font" / "char_map.json"
OUT_JSON = ROOT / "rom_analysis" / "korean_slot_allocation_plan.json"
OUT_MD = ROOT / "rom_analysis" / "korean_slot_allocation_plan.md"

PATCH_TILE_START = 0x101
PATCH_TILE_END = 0x1B5
TILE_SIZE = 0x10
CHR_BANK7_ROM_START = 0x2E010

PRIORITY_LEVELS = {
    "runtime-confirmed": 0,
    "encoding-exact": 1,
    "static-candidate+pointer": 2,
    "static-candidate": 3,
}


def load_inventory() -> list[dict[str, object]]:
    data = json.loads(INVENTORY.read_text(encoding="utf-8"))
    return list(data["targets"])


def korean_chars(text: str) -> list[str]:
    return [ch for ch in text if "\uac00" <= ch <= "\ud7a3"]


def target_sort_key(target: dict[str, object]) -> tuple[int, bool, str, str]:
    evidence = str(target.get("evidence_level", ""))
    return (
        PRIORITY_LEVELS.get(evidence, 9),
        not bool(target.get("in_watch_range")),
        str(target.get("rom_hit")),
        str(target.get("source")),
    )


def load_current_chars() -> list[str]:
    data = json.loads(CHAR_MAP.read_text(encoding="utf-8"))
    return list(data["sorted"])


def build_plan() -> dict[str, object]:
    targets = sorted(load_inventory(), key=target_sort_key)
    current_chars = load_current_chars()
    required: "OrderedDict[str, list[str]]" = OrderedDict()
    for target in targets:
        korean = str(target.get("korean", ""))
        for ch in korean_chars(korean):
            required.setdefault(ch, []).append(str(target.get("label")))

    slots = []
    for index, ch in enumerate(required):
        tile = PATCH_TILE_START + index
        if tile > PATCH_TILE_END:
            raise RuntimeError("Required Korean glyphs exceed available patch tile slots")
        rom_offset = CHR_BANK7_ROM_START + tile * TILE_SIZE
        slots.append(
            {
                "slot_index": index,
                "glyph": ch,
                "tile": f"0x{tile:03X}",
                "rom_offset": f"0x{rom_offset:05X}",
                "prg_plus_0x7a_byte": f"0x{((tile - 0x7A) & 0xFF):02X}",
                "used_by_labels": required[ch],
                "currently_at_char_map_index": current_chars.index(ch) if ch in current_chars else None,
                "currently_at_tile": (
                    f"0x{PATCH_TILE_START + current_chars.index(ch):03X}"
                    if ch in current_chars and PATCH_TILE_START + current_chars.index(ch) <= PATCH_TILE_END
                    else None
                ),
            }
        )

    encoded_targets = []
    slot_by_glyph = {slot["glyph"]: slot for slot in slots}
    for target in targets:
        korean = str(target.get("korean", ""))
        chars = korean_chars(korean)
        prg_bytes = [
            str(slot_by_glyph[ch]["prg_plus_0x7a_byte"])
            for ch in chars
            if ch in slot_by_glyph
        ]
        encoded_targets.append(
            {
                "label": target.get("label"),
                "evidence_level": target.get("evidence_level"),
                "category_group": target.get("category_group"),
                "category": target.get("category"),
                "rom_hit": target.get("rom_hit"),
                "source": target.get("source"),
                "korean": korean,
                "required_glyphs": chars,
                "planned_prg_bytes": prg_bytes,
                "original_expected_bytes": target.get("expected_bytes"),
            }
        )

    return {
        "source": str(INVENTORY.relative_to(ROOT)),
        "patch_tile_range": [f"0x{PATCH_TILE_START:03X}", f"0x{PATCH_TILE_END:03X}"],
        "available_slots": PATCH_TILE_END - PATCH_TILE_START + 1,
        "required_glyph_count": len(slots),
        "slots": slots,
        "targets": encoded_targets,
    }


def write_markdown(plan: dict[str, object]) -> None:
    slots = plan["slots"]
    targets = plan["targets"]
    lines = [
        "# Korean Slot Allocation Plan",
        "",
        "This is a planning artifact for assigning Korean glyphs to CHR Bank 07 patch slots before PRG text bytes are rewritten.",
        "",
        f"- Source inventory: `{plan['source']}`",
        f"- Patch tile range: `{plan['patch_tile_range'][0]}-{plan['patch_tile_range'][1]}`",
        f"- Available slots: **{plan['available_slots']}**",
        f"- Required Korean glyphs for current inventory: **{plan['required_glyph_count']}**",
        "- `current char_map tile` is `-` when the glyph exists only beyond the current 181-slot v0.1 patch range or is absent from `font/char_map.json`.",
        "",
        "## Required Glyph Slots",
        "",
        "| # | glyph | tile | ROM offset | planned PRG byte (+0x7A) | current char_map tile | used by count |",
        "| ---: | --- | --- | --- | --- | --- | ---: |",
    ]
    for slot in slots:
        current = slot["currently_at_tile"] or "-"
        lines.append(
            f"| {slot['slot_index']} | {slot['glyph']} | `{slot['tile']}` | `{slot['rom_offset']}` | "
            f"`{slot['prg_plus_0x7a_byte']}` | `{current}` | {len(slot['used_by_labels'])} |"
        )

    lines.extend(
        [
            "",
            "## Target Encoding Preview",
            "",
            "| evidence | ROM hit | category | Japanese | Korean | glyphs | planned PRG bytes | original candidate bytes |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for target in targets:
        glyphs = "".join(target["required_glyphs"]) or "-"
        planned = " ".join(str(byte) for byte in target["planned_prg_bytes"]) or "-"
        lines.append(
            f"| {target['evidence_level']} | `{target['rom_hit']}` | {target['category']} | "
            f"{target['source']} | {target['korean']} | {glyphs} | `{planned}` | "
            f"`{target['original_expected_bytes']}` |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This does not patch PRG text yet. It defines a compact Korean glyph slot plan for the currently known Bank 1 targets.",
            "- Planned PRG bytes assume the same `CHR tile = PRG byte + 0x7A` renderer path. Shifted-low tables still need runtime confirmation before direct PRG replacement.",
            "- Current `char_map.json` places punctuation/digits/Latin before Hangul, so many required Korean glyphs currently live at later slots than this compact plan.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    plan = build_plan()
    OUT_JSON.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(plan)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"required_glyphs={plan['required_glyph_count']} available={plan['available_slots']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
