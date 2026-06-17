#!/usr/bin/env python3
"""Generate a CHR Bank 07 slot inventory for the current Korean font patch."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from rom_utils import REPO_ROOT, find_rom_path


INES_HEADER_SIZE = 0x10
PRG_ROM_SIZE = 0x20000
CHR_START = INES_HEADER_SIZE + PRG_ROM_SIZE
CHR_BANK_SIZE = 0x2000
CHR_BANK = 7
CHR_BANK7_START = CHR_START + CHR_BANK * CHR_BANK_SIZE
CHR_BANK7_END = CHR_BANK7_START + CHR_BANK_SIZE
CHR_TILE_SIZE = 0x10
PATCH_TILE_START = 0x101
PATCH_TILE_END = 0x1B5

CHAR_MAP = REPO_ROOT / "font" / "char_map.json"
TILE_MAP = REPO_ROOT / "rom_analysis" / "chr_bank07_tile_map.json"
PATCHED_ROM = REPO_ROOT / "output" / "kunio_period_drama_korean_v0.1.nes"
OUT_MD = REPO_ROOT / "rom_analysis" / "chr_bank07_patch_inventory.md"
OUT_JSON = REPO_ROOT / "rom_analysis" / "chr_bank07_patch_inventory.json"


def sha1_16(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()[:16]


def load_characters() -> list[str]:
    data = json.loads(CHAR_MAP.read_text(encoding="utf-8"))
    return list(data["sorted"])


def load_original_map() -> dict[int, dict[str, object]]:
    if not TILE_MAP.exists():
        return {}
    data = json.loads(TILE_MAP.read_text(encoding="utf-8"))
    result: dict[int, dict[str, object]] = {}
    for entry in data.get("entries", []):
        result[int(str(entry["tile"]), 16)] = entry
    return result


def tile_bytes(rom: bytes, tile: int) -> bytes:
    offset = CHR_BANK7_START + tile * CHR_TILE_SIZE
    return rom[offset:offset + CHR_TILE_SIZE]


def tile_kind(tile: int, original: dict[str, object] | None) -> str:
    if original:
        return str(original.get("group", "mapped"))
    if PATCH_TILE_START <= tile <= PATCH_TILE_END:
        return "patch-slot-unmapped-original"
    if 0x1C0 <= tile <= 0x1C9:
        return "digit"
    if 0x1E1 <= tile <= 0x1FA:
        return "latin_upper"
    return "other"


def build_inventory() -> dict[str, object]:
    base_rom = Path(find_rom_path()).read_bytes()
    patched_rom = PATCHED_ROM.read_bytes() if PATCHED_ROM.exists() else b""
    characters = load_characters()
    original_map = load_original_map()

    slots = []
    changed_slots = 0
    changed_bytes = 0
    for index, tile in enumerate(range(PATCH_TILE_START, PATCH_TILE_END + 1)):
        rom_offset = CHR_BANK7_START + tile * CHR_TILE_SIZE
        base_tile = tile_bytes(base_rom, tile)
        patched_tile = (
            patched_rom[rom_offset:rom_offset + CHR_TILE_SIZE]
            if patched_rom
            else b""
        )
        byte_diffs = (
            sum(1 for old, new in zip(base_tile, patched_tile) if old != new)
            if patched_tile
            else None
        )
        if byte_diffs:
            changed_slots += 1
            changed_bytes += byte_diffs
        original = original_map.get(tile)
        slots.append(
            {
                "slot_index": index,
                "tile": f"0x{tile:03X}",
                "rom_offset": f"0x{rom_offset:05X}",
                "bank_relative_offset": f"0x{tile * CHR_TILE_SIZE:04X}",
                "prg_plus_0x7a_byte": f"0x{((tile - 0x7A) & 0xFF):02X}",
                "original_glyph": original.get("glyph") if original else None,
                "original_group": tile_kind(tile, original),
                "patched_glyph": characters[index] if index < len(characters) else None,
                "base_sha1_16": sha1_16(base_tile),
                "patched_sha1_16": sha1_16(patched_tile) if patched_tile else None,
                "changed_bytes": byte_diffs,
            }
        )

    protected_tiles = []
    for tile in list(range(0x1C0, 0x1CA)) + list(range(0x1E1, 0x1FB)):
        rom_offset = CHR_BANK7_START + tile * CHR_TILE_SIZE
        base_tile = tile_bytes(base_rom, tile)
        patched_tile = patched_rom[rom_offset:rom_offset + CHR_TILE_SIZE] if patched_rom else b""
        original = original_map.get(tile)
        protected_tiles.append(
            {
                "tile": f"0x{tile:03X}",
                "rom_offset": f"0x{rom_offset:05X}",
                "glyph": original.get("glyph") if original else None,
                "group": tile_kind(tile, original),
                "changed_bytes": (
                    sum(1 for old, new in zip(base_tile, patched_tile) if old != new)
                    if patched_tile
                    else None
                ),
            }
        )

    return {
        "chr_start_rom_offset": f"0x{CHR_START:05X}",
        "chr_bank": CHR_BANK,
        "chr_bank_rom_range": [
            f"0x{CHR_BANK7_START:05X}",
            f"0x{CHR_BANK7_END - 1:05X}",
        ],
        "tile_size_bytes": CHR_TILE_SIZE,
        "patch_tile_range": [f"0x{PATCH_TILE_START:03X}", f"0x{PATCH_TILE_END:03X}"],
        "patch_slot_count": len(slots),
        "changed_patch_slots": changed_slots,
        "changed_patch_bytes": changed_bytes,
        "patched_rom_available": bool(patched_rom),
        "slots": slots,
        "protected_reference_tiles": protected_tiles,
    }


def write_markdown(payload: dict[str, object]) -> None:
    slots = payload["slots"]
    protected = payload["protected_reference_tiles"]
    lines = [
        "# CHR Bank 07 Patch Inventory",
        "",
        "This maps the current Korean font patch slots onto the original CHR Bank 07 tile space.",
        "",
        f"- CHR ROM starts at `{payload['chr_start_rom_offset']}`.",
        f"- CHR Bank 07 range: `{payload['chr_bank_rom_range'][0]}-{payload['chr_bank_rom_range'][1]}`.",
        f"- Patch tile range: `{payload['patch_tile_range'][0]}-{payload['patch_tile_range'][1]}`.",
        f"- Patch slots: **{payload['patch_slot_count']}**",
        f"- Changed patch slots in generated v0.1 ROM: **{payload['changed_patch_slots']}**",
        f"- Changed patch bytes in generated v0.1 ROM: **{payload['changed_patch_bytes']}**",
        "",
        "## Patch Slots",
        "",
        "| # | tile | ROM offset | PRG byte (+0x7A) | original | patched glyph | changed bytes |",
        "| ---: | --- | --- | --- | --- | --- | ---: |",
    ]
    for slot in slots:
        original = slot["original_glyph"] or slot["original_group"]
        lines.append(
            f"| {slot['slot_index']} | `{slot['tile']}` | `{slot['rom_offset']}` | "
            f"`{slot['prg_plus_0x7a_byte']}` | {original} | {slot['patched_glyph']} | "
            f"{slot['changed_bytes'] if slot['changed_bytes'] is not None else '-'} |"
        )

    lines.extend(
        [
            "",
            "## Reference Tiles Outside Patch Range",
            "",
            "Digits and uppercase Latin tiles are tracked here because they are useful for decoding and should not be accidentally overwritten by the current Bank7 font patch.",
            "",
            "| tile | ROM offset | glyph | group | changed bytes |",
            "| --- | --- | --- | --- | ---: |",
        ]
    )
    for tile in protected:
        lines.append(
            f"| `{tile['tile']}` | `{tile['rom_offset']}` | {tile['glyph']} | "
            f"{tile['group']} | {tile['changed_bytes'] if tile['changed_bytes'] is not None else '-'} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- The patch slots are 8x8 CHR tiles, 16 bytes each. They are not 8x16 tile indexes.",
            "- The generated v0.1 ROM currently writes inside `0x101-0x1B5`; digits `0x1C0-0x1C9` and uppercase Latin `0x1E1-0x1FA` are left unchanged.",
            "- PRG text bytes still need per-string encoding rules before these patched glyph slots can be used for a final translation patch.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = build_inventory()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(
        "slots={patch_slot_count} changed_slots={changed_patch_slots} "
        "changed_bytes={changed_patch_bytes}".format(**payload)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
