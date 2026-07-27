#!/usr/bin/env python3
"""Build a scoped 16x16 Korean main-menu candidate from the verified base ROM.

The reachable menu's 128-byte template is copied to PPU $2700-$277F.  Its
background text tiles are selected by a fixed raster split that temporarily
maps MMC3 R1 to CHR page pair $3E/$3F.  This builder clones that pair into
Bank 8 ($46/$47), replaces only declared Korean glyph tiles in an isolated
code pool, and changes the raster split's immediate page value from $3E to
$46.  The pool was selected against the captured Japanese/English menu and
Items nametables so the first cross-screen candidate does not overwrite the
Items action row.

The source Bank 7 CHR pages remain byte-for-byte intact.  This is a bounded
candidate for one known menu screen, not a release patch for all contexts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from analyze_reference_ips import parse_ines_layout
from build_opening_dialogue_16x16_proof import (
    build_square_glyph_tiles,
    default_square_font,
)
from build_opening_dialogue_proof import BASE_MD5, resolve_base_rom
from build_patch import make_records, write_ips
from korean_font_quality import evaluate_release_square_font, render_square_glyph_bitmaps
from korean_tile_font import square_font_profile, write_square_preview
from rom_utils import REPO_ROOT


TEMPLATE_ROM_OFFSET = 0x1F2C1
TEMPLATE_LENGTH = 0x80
TEMPLATE_CPU_SOURCE = 0xF2B1
PPU_DESTINATION = 0x2700

# Fixed PRG Bank 7 raster setup.  It saves the current R0/R1 source values,
# temporarily selects $3C/$3E, applies them, and restores the saved values.
RASTER_R1_VALUE_ROM_OFFSET = 0x1EE5D
RASTER_R1_VALUE_CPU = 0xEE4D
RASTER_R1_VALUE_ORIGINAL = 0x3E
RASTER_R1_VALUE_CLONE = 0x46

CHR_1K_SIZE = 0x400
CHR_TILE_SIZE = 16
SOURCE_CHR_1K_PAIR = 0x3E
CLONE_CHR_1K_PAIR = 0x46
CHR_PAIR_SIZE = CHR_1K_SIZE * 2
FONT_PROFILE = "readable"

OUT_STEM = "kunio_period_drama_korean_main_menu_16x16_candidate"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "main_menu_korean_candidate"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "main_menu_korean_candidate.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "main_menu_korean_candidate.md"
DEFAULT_PREVIEW = REPO_ROOT / "rom_analysis" / "main_menu_korean_candidate_font_preview.png"

# (stable id, legacy row, column, legacy width).  The 16x16 layout uses rows
# 24-25 for the first four labels and rows 26-27 for the lower four labels.
MENU_SLOTS = (
    ("items", 25, 2, 5),
    ("status", 25, 9, 6),
    ("growth", 25, 16, 6),
    ("tech", 25, 23, 7),
    ("record", 27, 2, 5),
    ("ally", 27, 9, 6),
    ("setting", 27, 16, 6),
    ("save", 27, 23, 7),
)
MENU_LABELS = {
    "items": "\ubb3c\uac74",
    "status": "\uc0c1\ud0dc",
    "growth": "\uc131\uc7a5",
    "tech": "\uae30\uc220",
    "record": "\uae30\ub85d",
    "ally": "\ub3d9\ub8cc",
    "setting": "\uc124\uc815",
    "save": "\uc800\uc7a5",
}
GLYPH_ORDER = (
    "\ubb3c",
    "\uac74",
    "\uc0c1",
    "\ud0dc",
    "\uc131",
    "\uc7a5",
    "\uae30",
    "\uc220",
    "\ub85d",
    "\ub3d9",
    "\ub8cc",
    "\uc124",
    "\uc815",
    "\uc800",
)
# These are deliberately non-contiguous pairs.  The old 0x80-$9B allocation
# overlapped the verified Items action bytes (0x83, 0x86, 0x8D, 0x90, ...).
# Every selected code and its 0x20 lower-half partner is absent from the
# bounded Japanese/English menu and Items nametables captured in this repo.
ISOLATED_GLYPH_CODE_PAIRS = (
    (0x80, 0x81),
    (0xC1, 0x82),
    (0x84, 0xC4),
    (0x85, 0xC5),
    (0xA6, 0x87),
    (0xC7, 0xA8),
    (0xC9, 0x8A),
    (0xCA, 0xAB),
    (0xCC, 0xAD),
    (0x8E, 0x8F),
    (0xB0, 0x91),
    (0xD1, 0x94),
    (0xD4, 0x95),
    (0xB6, 0x97),
)
GLYPH_CODE_PAIRS = dict(zip(GLYPH_ORDER, ISOLATED_GLYPH_CODE_PAIRS))

# The union is the runtime-visible high-code set from the bounded base and
# English menu plus the base/English Items screen.  It is an evidence gate,
# not a claim that the whole game has been audited.
KNOWN_ACTIVE_HIGH_CODES = frozenset(
    {
        0x83,
        0x86,
        0x88,
        0x8B,
        0x8D,
        0x90,
        0x92,
        0x93,
        0x96,
        0x9A,
        0x9D,
        0x9F,
        0xA9,
        0xAC,
        0xB8,
        0xC2,
        0xC3,
        0xCF,
        0xD2,
        0xD3,
        0xD5,
        0xD8,
        0xDF,
        0xE0,
        0xE2,
        0xE3,
        0xED,
        0xEE,
        0xEF,
        0xF0,
        0xF2,
        0xF3,
        0xFD,
        0xFE,
        0xFF,
    }
)


def add_target(
    targets: list[dict[str, object]],
    *,
    kind: str,
    rom_offset: int,
    length: int,
    **extra: object,
) -> None:
    targets.append({"kind": kind, "rom_offset": rom_offset, "length": length, **extra})


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


def chr_page_offset(layout, page: int) -> int:
    page_count = (layout.chr_end - layout.chr_start) // CHR_1K_SIZE
    if not 0 <= page < page_count:
        raise ValueError(f"CHR 1 KiB page out of range: 0x{page:02X}")
    return layout.chr_start + page * CHR_1K_SIZE


def clone_tile_offset(layout, code: int) -> int:
    if not 0x80 <= code < 0x100:
        raise ValueError(f"menu glyph code must use clone page $80-$FF: 0x{code:02X}")
    return chr_page_offset(layout, CLONE_CHR_1K_PAIR) + (code & 0x7F) * CHR_TILE_SIZE


def validate_code_pool() -> None:
    allocated = {
        code
        for left, right in GLYPH_CODE_PAIRS.values()
        for code in (left, right, left + 0x20, right + 0x20)
    }
    if len(allocated) != len(GLYPH_CODE_PAIRS) * 4:
        raise AssertionError("Korean menu glyph code pool contains duplicate tiles")
    if allocated & KNOWN_ACTIVE_HIGH_CODES:
        overlap = ", ".join(f"0x{code:02X}" for code in sorted(allocated & KNOWN_ACTIVE_HIGH_CODES))
        raise AssertionError(f"Korean menu pool overlaps bounded active codes: {overlap}")
    if any(code >= 0x100 for code in allocated):
        raise AssertionError("Korean menu lower-half code exceeds one-byte tile range")


def label_tile_rows(label: str) -> tuple[bytes, bytes]:
    if len(label) != 2:
        raise ValueError(f"menu label must contain two Korean syllables: {label!r}")
    top = bytearray()
    bottom = bytearray()
    for glyph in label:
        try:
            left, right = GLYPH_CODE_PAIRS[glyph]
        except KeyError as exc:
            raise ValueError(f"menu label glyph has no CHR allocation: {glyph!r}") from exc
        top.extend((left, right))
        bottom.extend((left + 0x20, right + 0x20))
    return bytes(top), bytes(bottom)


def build_menu_template(base: bytes) -> bytes:
    original = base[TEMPLATE_ROM_OFFSET : TEMPLATE_ROM_OFFSET + TEMPLATE_LENGTH]
    if len(original) != TEMPLATE_LENGTH:
        raise ValueError("main-menu template lies outside the supplied ROM")
    template = bytearray(original)

    for _label_id, legacy_row, column, width in MENU_SLOTS:
        offset = (legacy_row - 24) * 32 + column
        template[offset : offset + width] = b"\x00" * width

    for index, (label_id, _legacy_row, column, _width) in enumerate(MENU_SLOTS):
        top_row = 24 if index < 4 else 26
        bottom_row = top_row + 1
        top, bottom = label_tile_rows(MENU_LABELS[label_id])
        top_offset = (top_row - 24) * 32 + column
        bottom_offset = (bottom_row - 24) * 32 + column
        template[top_offset : top_offset + len(top)] = top
        template[bottom_offset : bottom_offset + len(bottom)] = bottom

    return bytes(template)


def _assert_declared_scope(
    base: bytes,
    patched: bytes,
    targets: list[dict[str, object]],
) -> None:
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
        raise AssertionError(f"candidate changed bytes outside its declared targets: {escaped[:8]}")


def apply_main_menu_candidate(
    base: bytes,
    glyph_tiles: dict[str, tuple[bytes, bytes, bytes, bytes]],
    *,
    clone_source: bytes | None = None,
) -> tuple[bytes, list[dict[str, object]]]:
    validate_code_pool()
    if clone_source is not None and len(clone_source) != len(base):
        raise ValueError("menu clone-source ROM length differs from the target ROM")
    if base[RASTER_R1_VALUE_ROM_OFFSET] != RASTER_R1_VALUE_ORIGINAL:
        actual = base[RASTER_R1_VALUE_ROM_OFFSET]
        raise ValueError(
            "main-menu raster R1 immediate does not match the verified base byte: "
            f"0x{actual:02X}"
        )
    if SOURCE_CHR_1K_PAIR % 2 or CLONE_CHR_1K_PAIR % 2:
        raise AssertionError("MMC3 R1 pair values must be even")

    layout = parse_ines_layout(base)
    source_start = chr_page_offset(layout, SOURCE_CHR_1K_PAIR)
    clone_start = chr_page_offset(layout, CLONE_CHR_1K_PAIR)
    source_end = source_start + CHR_PAIR_SIZE
    clone_end = clone_start + CHR_PAIR_SIZE
    if clone_end > layout.chr_end:
        raise ValueError("clone CHR pair lies outside the ROM")

    patched = bytearray(base)
    targets: list[dict[str, object]] = []
    template = build_menu_template(base)
    patched[TEMPLATE_ROM_OFFSET : TEMPLATE_ROM_OFFSET + TEMPLATE_LENGTH] = template
    add_target(
        targets,
        kind="main_menu_template",
        rom_offset=TEMPLATE_ROM_OFFSET,
        length=TEMPLATE_LENGTH,
        cpu_source=f"0x{TEMPLATE_CPU_SOURCE:04X}",
        ppu_destination=f"0x{PPU_DESTINATION:04X}",
    )

    clone_bytes = (clone_source or base)[source_start:source_end]
    patched[clone_start:clone_end] = clone_bytes
    add_target(
        targets,
        kind="chr_pair_clone",
        rom_offset=clone_start,
        length=CHR_PAIR_SIZE,
        source_chr_1k_pair=f"0x{SOURCE_CHR_1K_PAIR:02X}",
        clone_chr_1k_pair=f"0x{CLONE_CHR_1K_PAIR:02X}",
        clone_source="external_base_rom" if clone_source is not None else "target_rom",
    )

    for glyph, (left_code, right_code) in GLYPH_CODE_PAIRS.items():
        tiles = glyph_tiles.get(glyph)
        if tiles is None or len(tiles) != 4 or any(len(tile) != CHR_TILE_SIZE for tile in tiles):
            raise ValueError(f"missing four 8x8 glyph tiles for {glyph!r}")
        placements = (
            ("font_tile_top_left", left_code, tiles[0]),
            ("font_tile_top_right", right_code, tiles[1]),
            ("font_tile_bottom_left", left_code + 0x20, tiles[2]),
            ("font_tile_bottom_right", right_code + 0x20, tiles[3]),
        )
        for kind, code, tile in placements:
            offset = clone_tile_offset(layout, code)
            patched[offset : offset + CHR_TILE_SIZE] = tile
            add_target(
                targets,
                kind=kind,
                rom_offset=offset,
                length=CHR_TILE_SIZE,
                glyph=glyph,
                code=f"0x{code:02X}",
                clone_chr_1k_page=f"0x{CLONE_CHR_1K_PAIR:02X}",
            )

    patched[RASTER_R1_VALUE_ROM_OFFSET] = RASTER_R1_VALUE_CLONE
    add_target(
        targets,
        kind="fixed_raster_r1_clone_page",
        rom_offset=RASTER_R1_VALUE_ROM_OFFSET,
        length=1,
        cpu_address=f"0x{RASTER_R1_VALUE_CPU:04X}",
        original=f"0x{RASTER_R1_VALUE_ORIGINAL:02X}",
        replacement=f"0x{RASTER_R1_VALUE_CLONE:02X}",
    )

    _assert_declared_scope(base, bytes(patched), targets)
    if clone_source is None and patched[source_start:source_end] != base[source_start:source_end]:
        raise AssertionError("source Bank 7 CHR pair was modified")
    return bytes(patched), targets


def build_report(
    *,
    base: bytes,
    patched: bytes,
    targets: list[dict[str, object]],
    out_dir: Path,
    ips_path: Path,
    rom_path: Path,
    font_path: Path,
    font_quality: dict[str, object],
) -> dict[str, object]:
    layout = parse_ines_layout(base)
    source_start = chr_page_offset(layout, SOURCE_CHR_1K_PAIR)
    clone_start = chr_page_offset(layout, CLONE_CHR_1K_PAIR)
    spans = changed_spans(base, patched)
    return {
        "status": "CANDIDATE_BUILT_PENDING_BOUNDED_CROSS_SCREEN_SMOKE",
        "source": {
            "base_md5": hashlib.md5(base).hexdigest(),
            "template_rom_offset": f"0x{TEMPLATE_ROM_OFFSET:05X}",
            "template_length": TEMPLATE_LENGTH,
            "template_cpu_source": f"0x{TEMPLATE_CPU_SOURCE:04X}",
            "ppu_destination": f"0x{PPU_DESTINATION:04X}",
            "english_reference_use": "menu slot layout and Bank 7 tile-page evidence only",
            "raster_r1_cpu_address": f"0x{RASTER_R1_VALUE_CPU:04X}",
            "raster_r1_rom_offset": f"0x{RASTER_R1_VALUE_ROM_OFFSET:05X}",
            "raster_r1_original": f"0x{RASTER_R1_VALUE_ORIGINAL:02X}",
            "raster_r1_clone": f"0x{RASTER_R1_VALUE_CLONE:02X}",
            "source_chr_1k_pair": f"0x{SOURCE_CHR_1K_PAIR:02X}",
            "clone_chr_1k_pair": f"0x{CLONE_CHR_1K_PAIR:02X}",
            "glyph_code_pool": "isolated_noncontiguous_0x80_to_0xD4",
            "known_active_high_codes_excluded": [
                f"0x{code:02X}" for code in sorted(KNOWN_ACTIVE_HIGH_CODES)
            ],
            "source_chr_rom_range": [
                f"0x{source_start:05X}",
                f"0x{source_start + CHR_PAIR_SIZE - 1:05X}",
            ],
            "clone_chr_rom_range": [
                f"0x{clone_start:05X}",
                f"0x{clone_start + CHR_PAIR_SIZE - 1:05X}",
            ],
            "source_bank7_pair_unchanged": True,
            "font_profile": FONT_PROFILE,
            "font_path": str(font_path),
            "font_quality": font_quality,
            "labels": [
                {
                    "id": label_id,
                    "korean": MENU_LABELS[label_id],
                    "column": column,
                    "top_row": 24 if index < 4 else 26,
                    "bottom_row": 25 if index < 4 else 27,
                }
                for index, (label_id, _row, column, _width) in enumerate(MENU_SLOTS)
            ],
            "glyph_code_pairs": {
                glyph: [f"0x{left:02X}", f"0x{right:02X}"]
                for glyph, (left, right) in GLYPH_CODE_PAIRS.items()
            },
        },
        "candidate": {
            "patched_md5": hashlib.md5(patched).hexdigest(),
            "out_dir": str(out_dir),
            "ips_path": str(ips_path),
            "rom_path": str(rom_path),
            "changed_span_count": len(spans),
            "changed_spans": [
                {"start": f"0x{start:05X}", "end_exclusive": f"0x{end:05X}"}
                for start, end in spans
            ],
            "targets": targets,
        },
        "known_limits": [
            "The isolated pool is proven only against the bounded Japanese/English menu and Items nametables.",
            "The fixed R1 clone remains a soft-gated shared renderer change; dialogue, status, and gameplay contexts are not audited.",
            "This ROM is a bounded candidate until both menu and Items captures pass with lua_done.",
        ],
    }


def render_markdown(payload: dict[str, object]) -> str:
    source = payload["source"]
    candidate = payload["candidate"]
    assert isinstance(source, dict)
    assert isinstance(candidate, dict)
    lines = [
        "# Korean Main Menu 16x16 Candidate",
        "",
        f"Status: **{payload['status']}**",
        "",
        "## Scoped Change",
        "",
        f"- Base MD5: `{source['base_md5']}`.",
        f"- Menu template: `{source['template_rom_offset']}` -> PPU `{source['ppu_destination']}`.",
        f"- Fixed raster R1: `{source['raster_r1_original']}` -> `{source['raster_r1_clone']}` at `{source['raster_r1_cpu_address']}`.",
        f"- CHR pair clone: `{source['source_chr_1k_pair']}` -> `{source['clone_chr_1k_pair']}`.",
        "- The original Bank 7 CHR pair is preserved; only the cloned Bank 8 pair receives Korean tiles.",
        "- Korean tiles use an isolated non-contiguous code pool; the bounded Items high-code set is excluded.",
        "- English patch use: structural menu-slot and font-page evidence, not text or artwork reuse.",
        f"- Korean font quality gate: **{source['font_quality']['verdict']}**.",
        "",
        "## Labels",
        "",
        "| id | Korean | column | tile rows |",
        "| --- | --- | ---: | --- |",
    ]
    labels = source["labels"]
    assert isinstance(labels, list)
    for label in labels:
        assert isinstance(label, dict)
        lines.append(
            f"| `{label['id']}` | {label['korean']} | {label['column']} | "
            f"{label['top_row']}-{label['bottom_row']} |"
        )
    lines += [
        "",
        "## Candidate",
        "",
        f"- Candidate MD5: `{candidate['patched_md5']}`.",
        f"- Declared changed spans: `{candidate['changed_span_count']}`.",
        "",
        "## Limits",
        "",
    ]
    limits = payload["known_limits"]
    assert isinstance(limits, list)
    lines.extend(f"- {limit}" for limit in limits)
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?", help="Base Japanese ROM")
    parser.add_argument("--font", default=None, help="Optional Korean TrueType font")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_REPORT_MARKDOWN)
    parser.add_argument("--preview", type=Path, default=DEFAULT_PREVIEW)
    args = parser.parse_args()

    base_path = resolve_base_rom(args.rom)
    base = base_path.read_bytes()
    actual_md5 = hashlib.md5(base).hexdigest()
    if actual_md5 != BASE_MD5:
        raise ValueError(f"unsupported base ROM MD5: {actual_md5}")

    font_path = default_square_font(args.font)
    glyph_bitmaps = render_square_glyph_bitmaps(
        font_path,
        GLYPH_ORDER,
        font_profile=FONT_PROFILE,
    )
    font_quality = evaluate_release_square_font(
        font_path=font_path,
        font_profile=FONT_PROFILE,
        bitmaps=glyph_bitmaps,
    )
    if font_quality["verdict"] != "PASS":
        raise ValueError(f"Korean font quality gate failed: {font_quality['checks']}")
    glyph_tiles = build_square_glyph_tiles(
        font_path,
        GLYPH_CODE_PAIRS,
        font_profile=FONT_PROFILE,
    )
    patched, targets = apply_main_menu_candidate(base, glyph_tiles)
    records = make_records(base, patched)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    ips_path = args.out_dir / f"{OUT_STEM}.ips"
    rom_path = args.out_dir / f"{OUT_STEM}.nes"
    write_ips(ips_path, records)
    rom_path.write_bytes(patched)

    profile = square_font_profile(FONT_PROFILE)
    write_square_preview(
        list(GLYPH_ORDER),
        args.preview,
        font_path=font_path,
        target_pixels=int(profile["target_pixels"]),
        threshold=int(profile["threshold"]),
        resample=str(profile["resample"]),
    )
    payload = build_report(
        base=base,
        patched=patched,
        targets=targets,
        out_dir=args.out_dir,
        ips_path=ips_path,
        rom_path=rom_path,
        font_path=font_path,
        font_quality=font_quality,
    )
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    args.report_markdown.write_text(render_markdown(payload), encoding="utf-8")
    print(f"ips={ips_path}")
    print(f"rom={rom_path}")
    print(f"report_json={args.report_json}")
    print(f"report_markdown={args.report_markdown}")
    print(f"preview={args.preview}")
    print(f"base_md5={actual_md5}")
    print(f"patched_md5={payload['candidate']['patched_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
