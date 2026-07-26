#!/usr/bin/env python3
"""Build a bounded 8x16 Korean-font proof for one real opening dialogue.

The verified dialogue renderer already queues two vertically adjacent tiles per
source byte. The original game sends a blank top tile and an 8x8 glyph below.
This proof changes that behavior only while the renderer reads pointer record
182, turning the existing pair into a top and bottom Korean glyph tile.

It is a renderer experiment, not a release patch. The code cave is a base-ROM
`0xFF` run in the same PRG page as the active dialogue record and is checked
before every build.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from analyze_reference_ips import parse_ines_layout
from build_patch import make_records, write_ips
from compile_korean_scene_batch import DEFAULT_CATALOG, compile_catalog
from build_opening_dialogue_proof import (
    BASE_MD5,
    CHR_BANK,
    KOREAN_GLYPH_CODES,
    ORIGINAL_RECORD,
    POINTER_INDEX,
    POINTER_ROM_OFFSET,
    PROOF_RECORD,
    RECORD_LENGTH,
    RECORD_ROM_OFFSET,
    physical_tile_for_code,
    resolve_base_rom,
    target_tile_offset,
    validate_english_reference_slots,
)
from korean_tile_font import find_korean_font, render_tall_tiles, write_tall_preview
from rom_utils import REPO_ROOT


RENDER_ENTRY_ROM_OFFSET = 0x0556F
RENDER_MARKER_ROM_OFFSET = 0x05586
RENDER_ENTRY_CPU = 0x955F
RENDER_MARKER_CPU = 0x9576
RENDER_ENTRY_ORIGINAL = bytes.fromhex("C9 00 F0")
RENDER_MARKER_ORIGINAL = bytes.fromhex("A9 00 F0")

CODE_CAVE_ROM_OFFSET = 0x07FB5
CODE_CAVE_CPU = 0xBFA5
CODE_CAVE_SIZE = 0x5B
MARKER_HELPER_CPU = 0xBFCE
BOTTOM_TILE_DELTA = 0x20

DEFAULT_OUTPUT_DIR = REPO_ROOT / "output"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "opening_dialogue_8x16_proof.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "opening_dialogue_8x16_proof.md"
DEFAULT_PREVIEW = REPO_ROOT / "rom_analysis" / "opening_dialogue_8x16_font_preview.png"
OUT_STEM = "kunio_period_drama_korean_opening_dialogue_8x16_proof"


def default_tall_font(candidate: str | Path | None) -> Path:
    if candidate is not None:
        return find_korean_font(candidate)
    bold = Path(r"C:\Windows\Fonts\malgunbd.ttf")
    if bold.is_file():
        return bold
    return find_korean_font()


def helper_code() -> bytes:
    """Return the target-record gate and top/bottom tile-pair helper.

    The entry hook replaces `CMP #$00` at `$955F`. Non-target records replay
    the original comparison/branch behavior. Target codes `0x81-0x93` save
    their top tile in `$1B`, push `code + 0x20` as the bottom tile, and resume
    the original queue writer. The marker hook then restores `$1B` and puts
    the saved top tile in the queue's first data slot.
    """

    entry = bytes.fromhex(
        "48 A5 1A C9 A6 D0 17 A5 1B C9 B1 D0 11 "
        "68 C9 81 90 0D C9 94 B0 09 85 1B 18 69 20 4C 6B 95 "
        "68 C9 00 D0 03 4C 6B 95 4C 63 95"
    )
    marker = bytes.fromhex(
        "A5 1B C9 81 90 0D C9 94 B0 09 48 A9 B1 85 1B 68 "
        "4C 8D 95 A9 00 4C 8D 95"
    )
    if len(entry) != MARKER_HELPER_CPU - CODE_CAVE_CPU:
        raise AssertionError("entry helper no longer reaches the marker helper")
    return entry + marker


HELPER_CODE = helper_code()
ENTRY_HOOK = bytes((0x4C, CODE_CAVE_CPU & 0xFF, CODE_CAVE_CPU >> 8))
MARKER_HOOK = bytes((0x4C, MARKER_HELPER_CPU & 0xFF, MARKER_HELPER_CPU >> 8))


def build_tall_glyph_tiles(font_path: str | Path | None) -> dict[int, tuple[bytes, bytes]]:
    return {
        code: render_tall_tiles(character, font_path=font_path, threshold=92)
        for character, code in KOREAN_GLYPH_CODES.items()
    }


def validate_opening_catalog(catalog_path: Path) -> dict[str, object]:
    """Make the proof builder consume the scene-owned compilation contract."""

    compiled = compile_catalog(catalog_path)
    records = compiled["records"]
    if not isinstance(records, list) or len(records) != 1:
        raise ValueError("opening proof catalog must contain exactly one record")
    record = records[0]
    if (
        record["id"] != "PTR-182"
        or record["pointer_index"] != POINTER_INDEX
        or record["pointer_rom_offset"] != f"0x{POINTER_ROM_OFFSET:05X}"
        or record["record_rom_offset"] != f"0x{RECORD_ROM_OFFSET:05X}"
    ):
        raise ValueError("opening proof catalog does not identify pointer entry 182")
    if record["encoded"] != PROOF_RECORD:
        raise ValueError("opening proof catalog bytes diverge from the verified proof record")
    if compiled["glyph_codes"] != KOREAN_GLYPH_CODES:
        raise ValueError("opening proof catalog glyph allocation diverges from the verified slots")
    return compiled


def add_target(
    targets: list[dict[str, object]],
    *,
    kind: str,
    rom_offset: int,
    length: int,
    **extra: object,
) -> None:
    targets.append({"kind": kind, "rom_offset": rom_offset, "length": length, **extra})


def apply_opening_8x16_proof(
    base: bytes,
    glyph_tiles: dict[int, tuple[bytes, bytes]],
) -> tuple[bytes, list[dict[str, object]]]:
    if len(ORIGINAL_RECORD) != RECORD_LENGTH or len(PROOF_RECORD) != RECORD_LENGTH:
        raise AssertionError("proof record length invariant failed")
    if base[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + RECORD_LENGTH] != ORIGINAL_RECORD:
        raise ValueError("opening source record does not match the verified base bytes")
    if base[RENDER_ENTRY_ROM_OFFSET:RENDER_ENTRY_ROM_OFFSET + len(RENDER_ENTRY_ORIGINAL)] != RENDER_ENTRY_ORIGINAL:
        raise ValueError("renderer entry bytes do not match the verified base ROM")
    if base[RENDER_MARKER_ROM_OFFSET:RENDER_MARKER_ROM_OFFSET + len(RENDER_MARKER_ORIGINAL)] != RENDER_MARKER_ORIGINAL:
        raise ValueError("renderer marker bytes do not match the verified base ROM")
    cave_end = CODE_CAVE_ROM_OFFSET + CODE_CAVE_SIZE
    if base[CODE_CAVE_ROM_OFFSET:cave_end] != b"\xff" * CODE_CAVE_SIZE:
        raise ValueError("the bounded renderer code cave is not an untouched 0xFF run")
    if len(HELPER_CODE) > CODE_CAVE_SIZE:
        raise AssertionError("renderer helper does not fit the approved code cave")

    layout = parse_ines_layout(base)
    patched = bytearray(base)
    targets: list[dict[str, object]] = []
    patched[RECORD_ROM_OFFSET:RECORD_ROM_OFFSET + RECORD_LENGTH] = PROOF_RECORD
    add_target(
        targets,
        kind="dialogue_record",
        rom_offset=RECORD_ROM_OFFSET,
        length=RECORD_LENGTH,
        pointer_rom_offset=POINTER_ROM_OFFSET,
    )

    for character, code in KOREAN_GLYPH_CODES.items():
        top, bottom = glyph_tiles.get(code, (None, None))
        if top is None or bottom is None or len(top) != 16 or len(bottom) != 16:
            raise ValueError(f"missing 8x16 tile pair for code 0x{code:02X}")
        top_offset = target_tile_offset(layout, code)
        bottom_code = code + BOTTOM_TILE_DELTA
        bottom_offset = target_tile_offset(layout, bottom_code)
        patched[top_offset:top_offset + 16] = top
        patched[bottom_offset:bottom_offset + 16] = bottom
        add_target(
            targets,
            kind="font_tile_top",
            rom_offset=top_offset,
            length=16,
            character=character,
            code=f"0x{code:02X}",
            physical_tile=f"0x{physical_tile_for_code(code):03X}",
        )
        add_target(
            targets,
            kind="font_tile_bottom",
            rom_offset=bottom_offset,
            length=16,
            character=character,
            code=f"0x{bottom_code:02X}",
            physical_tile=f"0x{physical_tile_for_code(bottom_code):03X}",
        )

    patched[RENDER_ENTRY_ROM_OFFSET:RENDER_ENTRY_ROM_OFFSET + len(ENTRY_HOOK)] = ENTRY_HOOK
    add_target(
        targets,
        kind="renderer_entry_hook",
        rom_offset=RENDER_ENTRY_ROM_OFFSET,
        length=len(ENTRY_HOOK),
        cpu_address=f"0x{RENDER_ENTRY_CPU:04X}",
    )
    patched[RENDER_MARKER_ROM_OFFSET:RENDER_MARKER_ROM_OFFSET + len(MARKER_HOOK)] = MARKER_HOOK
    add_target(
        targets,
        kind="renderer_marker_hook",
        rom_offset=RENDER_MARKER_ROM_OFFSET,
        length=len(MARKER_HOOK),
        cpu_address=f"0x{RENDER_MARKER_CPU:04X}",
    )
    patched[CODE_CAVE_ROM_OFFSET:CODE_CAVE_ROM_OFFSET + len(HELPER_CODE)] = HELPER_CODE
    add_target(
        targets,
        kind="renderer_helper",
        rom_offset=CODE_CAVE_ROM_OFFSET,
        length=len(HELPER_CODE),
        cpu_address=f"0x{CODE_CAVE_CPU:04X}",
    )

    allowed = [
        (int(target["rom_offset"]), int(target["rom_offset"]) + int(target["length"]))
        for target in targets
    ]
    escaped = [
        offset
        for offset, (old, new) in enumerate(zip(base, patched))
        if old != new and not any(start <= offset < end for start, end in allowed)
    ]
    if escaped:
        raise AssertionError(f"proof patch changed {len(escaped)} byte(s) outside its allowlist")
    return bytes(patched), targets


def changed_spans(original: bytes, patched: bytes) -> list[tuple[int, int]]:
    offsets = [index for index, pair in enumerate(zip(original, patched)) if pair[0] != pair[1]]
    if not offsets:
        return []
    spans: list[tuple[int, int]] = []
    start = previous = offsets[0]
    for offset in offsets[1:]:
        if offset != previous + 1:
            spans.append((start, previous + 1))
            start = offset
        previous = offset
    spans.append((start, previous + 1))
    return spans


def render_report(payload: dict[str, object]) -> str:
    source = payload["source"]
    candidate = payload["candidate"]
    return "\n".join(
        [
            "# Opening Dialogue 8x16 Korean Proof Candidate",
            "",
            "Status: **CANDIDATE_BUILT_NOT_VISUALLY_VERIFIED_FONT_8X16**",
            "",
            "This is a one-record renderer proof, not a release patch. It keeps the",
            "original pointer and record length, then uses the renderer's existing two",
            "vertical tile writes to display one Korean glyph as an 8x16 pair.",
            "",
            "## Source",
            "",
            f"- Pointer index: `{source['pointer_index']}`",
            f"- Pointer ROM offset: `{source['pointer_rom_offset']}` (unchanged)",
            f"- Record ROM offset: `{source['record_rom_offset']}`",
            f"- Korean proof: {source['korean_text']}",
            "",
            "## Bounded Renderer Change",
            "",
            f"- Renderer entry hook: `{source['renderer_entry_rom_offset']}` -> `{source['renderer_entry_cpu']}`",
            f"- Renderer marker hook: `{source['renderer_marker_rom_offset']}` -> `{source['renderer_marker_cpu']}`",
            f"- Same-page code cave: `{source['code_cave_rom_offset']}` -> `{source['code_cave_cpu']}`",
            "- Only record `$B1A6` and source codes `0x81-0x93` enter the 8x16 path.",
            "- All other renderer inputs replay the original control flow.",
            "",
            "## Result",
            "",
            f"- Base MD5: `{candidate['base_md5']}`",
            f"- Candidate MD5: `{candidate['patched_md5']}`",
            f"- Changed-byte spans: `{candidate['changed_span_count']}`; escaped bytes: `{candidate['escaped_byte_count']}`.",
            f"- IPS: `{candidate['ips_path']}`",
            f"- ROM: `{candidate['rom_path']}`",
            "",
            "The candidate must pass the bounded opening capture and a native-size",
            "readability review before it can replace the 8x8 baseline.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?", help="Base Japanese ROM")
    parser.add_argument("--reference-ips", required=True, help="English reference IPS")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--font", help="Korean TrueType font path")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_REPORT_MARKDOWN)
    parser.add_argument("--preview", type=Path, default=DEFAULT_PREVIEW)
    args = parser.parse_args()

    rom_path = resolve_base_rom(args.rom)
    base = rom_path.read_bytes()
    actual_md5 = hashlib.md5(base).hexdigest()
    if actual_md5 != BASE_MD5:
        raise ValueError(f"unsupported base ROM MD5: {actual_md5}")
    ips_path = Path(args.reference_ips).expanduser()
    if not ips_path.is_file():
        raise FileNotFoundError(f"reference IPS not found: {ips_path}")

    catalog = validate_opening_catalog(args.catalog)
    reference = validate_english_reference_slots(base, ips_path)
    font = default_tall_font(args.font)
    glyph_tiles = build_tall_glyph_tiles(font)
    patched, targets = apply_opening_8x16_proof(base, glyph_tiles)
    records = make_records(base, patched)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    ips_output = args.out_dir / f"{OUT_STEM}.ips"
    rom_output = args.out_dir / f"{OUT_STEM}.nes"
    write_ips(ips_output, records)
    rom_output.write_bytes(patched)
    write_tall_preview(list(KOREAN_GLYPH_CODES), args.preview, font_path=font, threshold=92)

    changed = changed_spans(base, patched)
    payload = {
        "status": "CANDIDATE_BUILT_NOT_VISUALLY_VERIFIED_FONT_8X16",
        "source": {
            "base_md5": BASE_MD5,
            "pointer_index": POINTER_INDEX,
            "pointer_rom_offset": f"0x{POINTER_ROM_OFFSET:05X}",
            "record_rom_offset": f"0x{RECORD_ROM_OFFSET:05X}",
            "record_length": RECORD_LENGTH,
            "catalog": str(args.catalog),
            "catalog_sha256": catalog["catalog_sha256"],
            "catalog_glyph_count": len(catalog["glyph_codes"]),
            "korean_text": catalog["records"][0]["korean_text"],
            "font": str(font),
            "font_preview": str(args.preview),
            "renderer_entry_rom_offset": f"0x{RENDER_ENTRY_ROM_OFFSET:05X}",
            "renderer_entry_cpu": f"0x{RENDER_ENTRY_CPU:04X}",
            "renderer_marker_rom_offset": f"0x{RENDER_MARKER_ROM_OFFSET:05X}",
            "renderer_marker_cpu": f"0x{RENDER_MARKER_CPU:04X}",
            "code_cave_rom_offset": f"0x{CODE_CAVE_ROM_OFFSET:05X}",
            "code_cave_cpu": f"0x{CODE_CAVE_CPU:04X}",
            "helper_length": len(HELPER_CODE),
            "chr_bank": CHR_BANK,
        },
        "english_reference_validation": reference,
        "candidate": {
            "base_md5": actual_md5,
            "patched_md5": hashlib.md5(patched).hexdigest(),
            "ips_path": str(ips_output),
            "rom_path": str(rom_output),
            "ips_record_count": len(records),
            "changed_span_count": len(changed),
            "changed_spans": [
                {"start": f"0x{start:05X}", "end_exclusive": f"0x{end:05X}"}
                for start, end in changed
            ],
            "escaped_byte_count": 0,
            "targets": targets,
        },
    }
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.report_markdown.write_text(render_report(payload), encoding="utf-8")
    print(f"ips={ips_output}")
    print(f"rom={rom_output}")
    print(f"report_json={args.report_json}")
    print(f"report_markdown={args.report_markdown}")
    print(f"base_md5={actual_md5}")
    print(f"patched_md5={payload['candidate']['patched_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
