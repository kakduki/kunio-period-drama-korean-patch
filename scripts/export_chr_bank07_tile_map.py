#!/usr/bin/env python3
"""Export the current CHR bank 07 glyph/tile map as data files."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from map_translation_offsets import HIRAGANA_LOW
from rom_utils import find_rom_path


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "rom_analysis" / "chr_bank07_tile_map.json"
OUT_MD = ROOT / "rom_analysis" / "chr_bank07_tile_map.md"

INES_HEADER = 0x10
PRG_SIZE = 0x20000
CHR_START = INES_HEADER + PRG_SIZE
CHR_BANK_SIZE = 0x2000
CHR_BANK = 7
CHR_BANK_ROM_START = CHR_START + CHR_BANK * CHR_BANK_SIZE
TILE_SIZE = 16

def tile_bytes(rom: bytes, tile: int) -> bytes:
    start = CHR_BANK_ROM_START + tile * TILE_SIZE
    return rom[start : start + TILE_SIZE]


def tile_entry(rom: bytes, tile: int, glyph: str, group: str) -> dict[str, object]:
    data = tile_bytes(rom, tile)
    return {
        "chr_bank": CHR_BANK,
        "tile": f"0x{tile:03X}",
        "glyph": glyph,
        "group": group,
        "bank_relative_offset": f"0x{tile * TILE_SIZE:04X}",
        "rom_offset": f"0x{CHR_BANK_ROM_START + tile * TILE_SIZE:05X}",
        "prg_plus_0x7a_byte": f"0x{((tile - 0x7A) & 0xFF):02X}",
        "nonzero_bytes": sum(1 for byte in data if byte),
        "sha1_16": hashlib.sha1(data).hexdigest()[:16],
    }


def build_entries(rom: bytes) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []

    for glyph, low in sorted(HIRAGANA_LOW.items(), key=lambda item: item[1]):
        entries.append(tile_entry(rom, 0x100 + low, glyph, "hiragana"))

    for digit in range(10):
        entries.append(tile_entry(rom, 0x1C0 + digit, str(digit), "digit"))

    for idx, code in enumerate(range(ord("A"), ord("Z") + 1), start=0x1E1):
        entries.append(tile_entry(rom, idx, chr(code), "latin_upper"))

    return entries


def write_markdown(entries: list[dict[str, object]]) -> None:
    lines = [
        "# CHR bank 07 tile map",
        "",
        "This is a structured export of the current visually identified font map.",
        "",
        f"- CHR ROM starts at `ROM+0x{CHR_START:05X}`.",
        f"- Rendered CHR bank `{CHR_BANK:02d}` covers `ROM+0x{CHR_BANK_ROM_START:05X}-0x{CHR_BANK_ROM_START + CHR_BANK_SIZE - 1:05X}`.",
        "- Tile offsets below are bank-relative 8x8 CHR tile indexes.",
        "- `prg_plus_0x7a_byte` is the byte expected by the current hypothesis: `PRG byte + 0x7A = CHR tile low byte`.",
        "",
    ]

    for group in ("hiragana", "digit", "latin_upper"):
        lines.append(f"## {group}")
        lines.append("")
        lines.append("| tile | glyph | PRG byte (+0x7A) | bank offset | ROM offset | nonzero | sha1_16 |")
        lines.append("| --- | --- | --- | --- | --- | ---: | --- |")
        for entry in entries:
            if entry["group"] != group:
                continue
            lines.append(
                f"| `{entry['tile']}` | {entry['glyph']} | `{entry['prg_plus_0x7a_byte']}` | "
                f"`{entry['bank_relative_offset']}` | `{entry['rom_offset']}` | "
                f"{entry['nonzero_bytes']} | `{entry['sha1_16']}` |"
            )
        lines.append("")

    lines.extend(
        [
            "## Notes",
            "",
            "- This export does not prove every glyph is used by the text renderer; it records the current CHR-bank visual mapping used by the ROM text scans.",
            "- Runtime FCEUX traces still need to connect PRG reads to PPU tile writes for final patch confidence.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rom = Path(find_rom_path()).read_bytes()
    entries = build_entries(rom)
    payload = {
        "chr_start_rom_offset": f"0x{CHR_START:05X}",
        "chr_bank": CHR_BANK,
        "chr_bank_rom_range": [
            f"0x{CHR_BANK_ROM_START:05X}",
            f"0x{CHR_BANK_ROM_START + CHR_BANK_SIZE - 1:05X}",
        ],
        "tile_size_bytes": TILE_SIZE,
        "entries": entries,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(entries)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"entries={len(entries)} bank_range=0x{CHR_BANK_ROM_START:05X}-0x{CHR_BANK_ROM_START + CHR_BANK_SIZE - 1:05X}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
