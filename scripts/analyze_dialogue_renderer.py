#!/usr/bin/env python3
"""Record static evidence for the Bank 1 dialogue renderer before decoding text."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from analyze_reference_ips import parse_ines_layout
from rom_utils import REPO_ROOT


DEFAULT_OUTPUT_JSON = REPO_ROOT / "rom_analysis" / "dialogue_renderer_evidence.json"
DEFAULT_OUTPUT_MARKDOWN = REPO_ROOT / "rom_analysis" / "dialogue_renderer_evidence.md"

PARSER_SIGNATURE = bytes.fromhex("A5 20 85 10 A9 00 85 22 B1 05 29 0F C9 0E 90 06")
CONTROL_PREFIX = bytes.fromhex("B1 05 C9")
MASK_LOOKUP_PREFIX = bytes.fromhex("A6 48 BD")
CPU_BANK_START = 0x8000


def hex_offset(value: int) -> str:
    return f"0x{value:05X}"


def hex_cpu(value: int) -> str:
    return f"0x{value:04X}"


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


def find_unique(data: bytes, signature: bytes, label: str) -> int:
    first = data.find(signature)
    if first == -1:
        raise ValueError(f"{label} signature was not found")
    if data.find(signature, first + 1) != -1:
        raise ValueError(f"{label} signature is not unique")
    return first


def extract_control_codes(data: bytes, start: int, limit: int) -> tuple[int, list[int]]:
    """Read the consecutive CMP immediate / BEQ control-byte branch chain."""

    offset = data.find(CONTROL_PREFIX, start, limit)
    if offset == -1:
        raise ValueError("dialogue control-byte chain was not found")
    cursor = offset + 2
    codes: list[int] = []
    while cursor + 3 < len(data):
        if data[cursor] != 0xC9 or data[cursor + 2] != 0xF0:
            break
        codes.append(data[cursor + 1])
        cursor += 4
    if not codes:
        raise ValueError("dialogue control-byte chain has no entries")
    return offset, codes


def cpu_address_to_bank_file_offset(
    cpu_address: int, bank_start: int, bank_end: int
) -> int:
    offset = bank_start + (cpu_address - CPU_BANK_START)
    if not bank_start <= offset < bank_end:
        raise ValueError(f"CPU address {hex_cpu(cpu_address)} is outside the parser bank")
    return offset


def analyze(rom: bytes) -> dict[str, object]:
    layout = parse_ines_layout(rom)
    parser_offset = find_unique(rom, PARSER_SIGNATURE, "dialogue parser")
    parser_bank = (parser_offset - layout.prg_start) // layout.prg_bank_size
    bank_start = layout.prg_start + parser_bank * layout.prg_bank_size
    bank_end = bank_start + layout.prg_bank_size
    if not bank_start <= parser_offset < bank_end:
        raise ValueError("dialogue parser is not inside a PRG bank")

    control_offset, control_codes = extract_control_codes(
        rom,
        parser_offset,
        min(bank_end, parser_offset + 0x80),
    )
    lookup_offset = rom.find(MASK_LOOKUP_PREFIX, control_offset, bank_end)
    if lookup_offset == -1:
        raise ValueError("dialogue mask lookup was not found")
    cpu_lookup_address = int.from_bytes(rom[lookup_offset + 3 : lookup_offset + 5], "little")
    lookup_file_offset = cpu_address_to_bank_file_offset(
        cpu_lookup_address,
        bank_start,
        bank_end,
    )
    mask_table = list(rom[lookup_file_offset : lookup_file_offset + 4])
    if len(mask_table) != 4:
        raise ValueError("dialogue mask table is truncated")

    return {
        "source": {
            "base_md5": hashlib.md5(rom).hexdigest(),
            "base_sha256": hashlib.sha256(rom).hexdigest(),
        },
        "parser": {
            "rom_offset": hex_offset(parser_offset),
            "prg_bank": parser_bank,
            "control_compare_offset": hex_offset(control_offset),
            "primary_stream_zero_page": "0x05",
            "secondary_stream_zero_page": "0x07",
            "low_nibble_branch": {
                "mask": "0x0F",
                "threshold": "0x0E",
            },
            "special_control_bytes": [f"0x{value:02X}" for value in control_codes],
            "mask_lookup_cpu_address": hex_cpu(cpu_lookup_address),
            "mask_lookup_rom_offset": hex_offset(lookup_file_offset),
            "mask_table": [f"0x{value:02X}" for value in mask_table],
        },
        "decoder_status": "UNRESOLVED",
        "safe_direct_glyph_decode": False,
        "next_requirement": (
            "Trace the initialization of zero-page streams 0x05 and 0x07, "
            "then verify the emitted tile byte for one known dialogue record."
        ),
    }


def render_markdown(payload: dict[str, object]) -> str:
    parser = payload["parser"]
    controls = ", ".join(parser["special_control_bytes"])
    masks = ", ".join(parser["mask_table"])
    return "\n".join(
        (
            "# Dialogue Renderer Evidence",
            "",
            "This is a static code-path record, not a decoded dialogue script.",
            "",
            "## Verified",
            "",
            f"- Parser ROM offset: {parser['rom_offset']}",
            f"- Parser PRG bank: {parser['prg_bank']}",
            f"- Primary input stream: zero-page {parser['primary_stream_zero_page']}",
            f"- Secondary input stream: zero-page {parser['secondary_stream_zero_page']}",
            f"- Low-nibble branch: mask {parser['low_nibble_branch']['mask']}, threshold {parser['low_nibble_branch']['threshold']}",
            f"- Explicit special bytes: {controls}",
            f"- Per-mode mask lookup: CPU {parser['mask_lookup_cpu_address']}, ROM {parser['mask_lookup_rom_offset']}",
            f"- Mask values: {masks}",
            "",
            "## Consequence",
            "",
            "A Bank 1 dialogue byte is processed with a second stream and control branches.",
            "Do not treat it as a universal direct tile index or decode it with the menu-only glyph hypothesis.",
            "The Japanese columns in script_catalog.tsv must remain tokenized until one known",
            "dialogue record has a traced source byte to emitted-tile proof.",
            "",
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?", help="Base Japanese ROM")
    parser.add_argument("--json-output", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_OUTPUT_MARKDOWN)
    args = parser.parse_args()

    rom = resolve_base_rom(args.rom).read_bytes()
    payload = analyze(rom)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")
    print(f"json={args.json_output}")
    print(f"markdown={args.markdown_output}")
    print(f"controls={','.join(payload['parser']['special_control_bytes'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
