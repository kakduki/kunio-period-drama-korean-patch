#!/usr/bin/env python3
"""Map the physical CHR slots that the English reference patch changes.

The reference IPS is read and applied only in memory. This script never writes a
patched English ROM and never copies the third-party IPS into the repository.

The result is deliberately a *physical* CHR map: MMC3 can map each 1 KiB CHR
page differently at runtime, so an 8 KiB CHR-bank/tile coordinate is not by
itself proof of a visible screen context. It does establish the exact slots
the working English patch uses for its dialogue alphabet.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from analyze_reference_ips import apply_records, parse_ines_layout, parse_ips
from rom_utils import REPO_ROOT


DEFAULT_JSON = REPO_ROOT / "rom_analysis" / "english_font_slot_map.json"
DEFAULT_MARKDOWN = REPO_ROOT / "rom_analysis" / "english_font_slot_map.md"
LETTER_CODE_START = 0x81
LETTER_CODE_END = 0x9A
SPRITE_PATTERN_TABLE_1_TILE_BASE = 0x100
TILE_SIZE = 0x10
TILES_PER_CHR_BANK = 0x2000 // TILE_SIZE


def sha1_16(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()[:16]


def resolve_base_rom(candidate: str | None) -> Path:
    if candidate:
        path = Path(candidate).expanduser()
        if path.is_file():
            return path
        raise FileNotFoundError(f"base ROM not found: {path}")
    roms = sorted((REPO_ROOT / "rom").glob("*.nes"))
    if roms:
        return roms[0]
    raise FileNotFoundError("base ROM not found")


def code_label(code: int) -> str:
    if LETTER_CODE_START <= code <= LETTER_CODE_END:
        return chr(ord("A") + code - LETTER_CODE_START)
    return f"0x{code:02X}"


def physical_tile_for_dialogue_code(code: int) -> int:
    """Return the observed Bank 7 physical tile for an English dialogue byte.

    The raw English dialogue records use `0x81-0x9A` for `A-Z`. Their matching
    glyphs are visibly present at Bank 7 physical tiles `0x181-0x19A`, i.e.
    the 8x8 sprite pattern-table-1 half of the bank. This is an observed
    reference-patch relationship, not an assumption about every renderer.
    """

    return SPRITE_PATTERN_TABLE_1_TILE_BASE + code


def spans(values: list[int]) -> list[tuple[int, int]]:
    if not values:
        return []
    output: list[tuple[int, int]] = []
    start = previous = values[0]
    for value in values[1:]:
        if value != previous + 1:
            output.append((start, previous))
            start = value
        previous = value
    output.append((start, previous))
    return output


def format_spans(values: list[int]) -> list[str]:
    return [
        f"0x{start:03X}" if start == end else f"0x{start:03X}-0x{end:03X}"
        for start, end in spans(values)
    ]


def analyze_font_slots(base: bytes, reference: bytes) -> dict[str, object]:
    layout = parse_ines_layout(base)
    reference_layout = parse_ines_layout(reference)
    if layout != reference_layout:
        raise ValueError("reference patch changed the iNES PRG/CHR layout")

    bank_count = (layout.chr_end - layout.chr_start) // layout.chr_bank_size
    banks: list[dict[str, object]] = []
    code_coverage: dict[int, list[dict[str, object]]] = {
        code: [] for code in range(LETTER_CODE_START, LETTER_CODE_END + 1)
    }
    all_reference_tile_hashes: Counter[str] = Counter()

    for bank in range(bank_count):
        bank_start = layout.chr_start + bank * layout.chr_bank_size
        changed_tiles: list[int] = []
        changed_bytes_total = 0
        tile_rows: dict[int, dict[str, object]] = {}
        for tile in range(TILES_PER_CHR_BANK):
            start = bank_start + tile * TILE_SIZE
            end = start + TILE_SIZE
            base_tile = base[start:end]
            reference_tile = reference[start:end]
            changed_bytes = sum(old != new for old, new in zip(base_tile, reference_tile))
            if not changed_bytes:
                continue
            changed_tiles.append(tile)
            changed_bytes_total += changed_bytes
            row = {
                "tile": f"0x{tile:03X}",
                "rom_offset": f"0x{start:05X}",
                "changed_bytes": changed_bytes,
                "base_sha1_16": sha1_16(base_tile),
                "reference_sha1_16": sha1_16(reference_tile),
            }
            tile_rows[tile] = row
            all_reference_tile_hashes[str(row["reference_sha1_16"])] += 1

        letter_slots: list[dict[str, object]] = []
        for code in range(LETTER_CODE_START, LETTER_CODE_END + 1):
            physical_tile = physical_tile_for_dialogue_code(code)
            row = tile_rows.get(physical_tile)
            if row is None:
                continue
            slot = {
                "code": f"0x{code:02X}",
                "english_letter": code_label(code),
                "physical_tile": f"0x{physical_tile:03X}",
                **row,
            }
            letter_slots.append(slot)
            code_coverage[code].append(
                {
                    "chr_bank": bank,
                    "physical_tile": f"0x{physical_tile:03X}",
                    "rom_offset": row["rom_offset"],
                    "changed_bytes": row["changed_bytes"],
                    "reference_sha1_16": row["reference_sha1_16"],
                }
            )

        if changed_tiles:
            banks.append(
                {
                    "chr_bank": bank,
                    "rom_range": [
                        f"0x{bank_start:05X}",
                        f"0x{bank_start + layout.chr_bank_size - 1:05X}",
                    ],
                    "changed_tile_count": len(changed_tiles),
                    "changed_byte_count": changed_bytes_total,
                    "changed_tile_spans": format_spans(changed_tiles),
                    "english_letter_slots": letter_slots,
                }
            )

    coverage_rows = []
    for code, entries in code_coverage.items():
        hashes = sorted({str(entry["reference_sha1_16"]) for entry in entries})
        coverage_rows.append(
            {
                "code": f"0x{code:02X}",
                "english_letter": code_label(code),
                "physical_slot_count": len(entries),
                "chr_banks": [entry["chr_bank"] for entry in entries],
                "reference_glyph_variants": len(hashes),
                "slots": entries,
            }
        )

    return {
        "source": {
            "base_md5": hashlib.md5(base).hexdigest(),
            "reference_md5": hashlib.md5(reference).hexdigest(),
            "reference_ips_not_stored": True,
        },
        "scope": {
            "chr_bank_size": layout.chr_bank_size,
            "tile_size": TILE_SIZE,
            "tiles_per_chr_bank": TILES_PER_CHR_BANK,
            "english_letter_codes": [
                f"0x{LETTER_CODE_START:02X}",
                f"0x{LETTER_CODE_END:02X}",
            ],
            "observed_dialogue_physical_tile_formula": "0x100 + dialogue tile code",
            "mapping_warning": (
                "Physical 8 KiB CHR-bank coordinates; runtime MMC3 mapping still needs "
                "screen-context proof before a release patch."
            ),
        },
        "changed_chr_banks": banks,
        "english_letter_code_coverage": coverage_rows,
        "reference_changed_tile_glyph_hashes": {
            "unique_count": len(all_reference_tile_hashes),
            "reused_hash_count": sum(
                count > 1 for count in all_reference_tile_hashes.values()
            ),
        },
    }


def render_markdown(payload: dict[str, object]) -> str:
    scope = payload["scope"]
    lines = [
        "# English Reference Font Slot Map",
        "",
        "The English IPS is applied in memory only. This map records physical CHR slots",
            "whose tile bitmaps changed, with special focus on the verified dialogue alphabet",
            "codes `0x81-0x9A` (`A-Z`) at observed physical tiles `0x181-0x19A`.",
        "",
        "## Constraint",
        "",
        f"- {scope['mapping_warning']}",
        f"- CHR bank size: `{scope['chr_bank_size']}` bytes; tile size: `{scope['tile_size']}` bytes.",
        "",
        "## Letter-Code Coverage",
        "",
        "| code | English | physical slots | CHR banks | glyph variants |",
        "| --- | --- | ---: | --- | ---: |",
    ]
    for row in payload["english_letter_code_coverage"]:
        banks = ", ".join(str(value) for value in row["chr_banks"]) or "-"
        lines.append(
            f"| `{row['code']}` | {row['english_letter']} | "
            f"{row['physical_slot_count']} | {banks} | {row['reference_glyph_variants']} |"
        )

    lines.extend(
        [
            "",
            "## Changed CHR Banks",
            "",
            "| CHR bank | ROM range | changed tiles | changed bytes | tile spans | alphabet slots |",
            "| ---: | --- | ---: | ---: | --- | ---: |",
        ]
    )
    for bank in payload["changed_chr_banks"]:
        lines.append(
            f"| {bank['chr_bank']} | `{bank['rom_range'][0]}-{bank['rom_range'][1]}` | "
            f"{bank['changed_tile_count']} | {bank['changed_byte_count']} | "
            f"{', '.join(bank['changed_tile_spans'])} | {len(bank['english_letter_slots'])} |"
        )

    lines.extend(
        [
            "",
            "## Use In Korean Patch Work",
            "",
            "- The primary dialogue stream is verified on the opening scene as nametable tile codes;",
            "  the physical `0x100 + code` formula names the selected pattern-table-1 tile.",
            "- A Korean proof string may reuse an English letter-code slot only after every physical slot",
            "  required by its target screen has been replaced with the same Korean glyph.",
            "- This map does not authorize a broad CHR overwrite. It narrows the next trace and visual",
            "  check to the exact slots already proven relevant by the working English patch.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?", help="Base Japanese ROM")
    parser.add_argument("--reference-ips", required=True, help="English reference IPS")
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()

    base = resolve_base_rom(args.rom).read_bytes()
    ips_path = Path(args.reference_ips).expanduser()
    if not ips_path.is_file():
        raise FileNotFoundError(f"reference IPS not found: {ips_path}")
    records, truncate_size = parse_ips(ips_path.read_bytes())
    reference = apply_records(base, records, truncate_size)
    payload = analyze_font_slots(base, reference)

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")
    coverage = payload["english_letter_code_coverage"]
    print(f"json={args.json_output}")
    print(f"markdown={args.markdown_output}")
    print(
        "alphabet_slots="
        + ",".join(
            f"{row['code']}:{row['physical_slot_count']}" for row in coverage
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
