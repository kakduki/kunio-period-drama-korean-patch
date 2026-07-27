#!/usr/bin/env python3
"""Verify the bounded main-menu template against its visible nametable.

The reachable menu is not inferred from a blind string scan.  Its fixed Bank-7
template is copied to PPU $2700-$277F, which is nametable 1 rows 24-27.  This
tool compares the base and English-reference captures, records the eight
proven label locations, and describes a two-line 16x16 Korean layout.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from analyze_reference_ips import parse_ines_layout
from rom_utils import REPO_ROOT, find_rom_path


TEMPLATE_ROM_OFFSET = 0x1F2C1
TEMPLATE_LENGTH = 0x80
DISPLAY_NAMETABLE = 1
DISPLAY_TEMPLATE_OFFSET = DISPLAY_NAMETABLE * 0x400 + 24 * 32
MIRROR_TEMPLATE_OFFSET = 3 * 0x400 + 24 * 32
CHR_TILE_SIZE = 16

BASE_CAPTURE_DIR = REPO_ROOT / "rom_analysis" / "main_menu_base_context_capture"
REFERENCE_CAPTURE_DIR = REPO_ROOT / "rom_analysis" / "main_menu_english_context_capture"
DEFAULT_REFERENCE_ROM = REPO_ROOT / "output" / "technos_samurai_reference_menu_probe.nes"
DEFAULT_JSON_OUTPUT = REPO_ROOT / "rom_analysis" / "main_menu_context_report.json"
DEFAULT_MARKDOWN_OUTPUT = REPO_ROOT / "rom_analysis" / "main_menu_context_report.md"

# Each tuple is (stable id, source row, source column, legacy slot width).
LABEL_SLOTS = (
    ("items", 25, 2, 5),
    ("status", 25, 9, 6),
    ("growth", 25, 16, 6),
    ("tech", 25, 23, 7),
    ("record", 27, 2, 5),
    ("ally", 27, 9, 6),
    ("setting", 27, 16, 6),
    ("save", 27, 23, 7),
)
EXPECTED_ENGLISH_LABELS = ("ITEMS", "STATUS", "GROWTH", "TECH", "SAVE", "ALLY", "SETTNG", "SETUP")
KOREAN_MENU_LABELS = (
    "\ubb3c\uac74",
    "\uc0c1\ud0dc",
    "\uc131\uc7a5",
    "\uae30\uc220",
    "\uae30\ub85d",
    "\ub3d9\ub8cc",
    "\uc124\uc815",
    "\uc800\uc7a5",
)
DYNAMIC_TEMPLATE_OFFSETS = frozenset({0x21})


def hex_offset(value: int) -> str:
    return f"0x{value:05X}"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def latest_reason(rows: list[dict[str, str]]) -> str | None:
    for row in reversed(rows):
        reason = (row.get("reason") or "").strip()
        if reason:
            return reason
    return None


def find_capture_file(capture_dir: Path, suffix: str) -> Path:
    matches = sorted(capture_dir.glob(f"*{suffix}"))
    if len(matches) != 1:
        raise FileNotFoundError(
            f"expected exactly one {suffix!r} file in {capture_dir}, found {len(matches)}"
        )
    return matches[0]


def english_text(values: bytes) -> str:
    decoded: list[str] = []
    for value in values:
        if not 0x81 <= value <= 0x9A:
            raise ValueError(f"English menu value 0x{value:02X} is outside the verified A-Z slots")
        decoded.append(chr(ord("A") + value - 0x81))
    return "".join(decoded)


def label_slice(template: bytes, row: int, column: int, width: int) -> bytes:
    index = (row - 24) * 32 + column
    values = template[index : index + width]
    if len(values) != width:
        raise ValueError("label slot lies outside the 128-byte menu template")
    return values.split(b"\x00", 1)[0]


def matches_static_template(source: bytes, rendered: bytes) -> bool:
    if len(source) != TEMPLATE_LENGTH or len(rendered) != TEMPLATE_LENGTH:
        return False
    return all(
        source[index] == rendered[index]
        for index in range(TEMPLATE_LENGTH)
        if index not in DYNAMIC_TEMPLATE_OFFSETS
    )


def capture_info(capture_dir: Path) -> dict[str, Any]:
    summary_path = capture_dir / "summary.tsv"
    summary_rows = read_tsv(summary_path)
    nametables_path = find_capture_file(capture_dir, "_nametables_2000_2fff.bin")
    nametables = nametables_path.read_bytes()
    if len(nametables) != 0x1000:
        raise ValueError(f"unexpected nametable dump size {len(nametables)} in {nametables_path}")
    screenshot = next(iter(sorted(capture_dir.glob("*_screen.png"))), None)
    mapper_snapshot_path = capture_dir / "mapper_snapshot.tsv"
    return {
        "capture_dir": str(capture_dir),
        "summary_reason": latest_reason(summary_rows),
        "summary_rows": summary_rows,
        "nametables_path": nametables_path,
        "nametables": nametables,
        "template": nametables[
            DISPLAY_TEMPLATE_OFFSET : DISPLAY_TEMPLATE_OFFSET + TEMPLATE_LENGTH
        ],
        "mirror_template": nametables[
            MIRROR_TEMPLATE_OFFSET : MIRROR_TEMPLATE_OFFSET + TEMPLATE_LENGTH
        ],
        "screenshot": screenshot,
        "mapper_snapshot": read_tsv(mapper_snapshot_path)
        if mapper_snapshot_path.is_file()
        else [],
    }


def visible_label_mapper_mapping(capture: dict[str, Any]) -> dict[str, Any]:
    """Resolve the background $80-$BF page from the captured MMC3 state.

    At this menu frame PPUCTRL selects background pattern table 0 and MMC3
    CHR mode 0 maps table-0's $0800-$0BFF window through R1.  The template's
    English reference letters occupy tile codes $81-$9A, so R1's even page is
    the physical 1 KiB page that owns their font tiles.
    """

    snapshots = capture.get("mapper_snapshot")
    if not isinstance(snapshots, list) or not snapshots:
        return {"verdict": "UNKNOWN", "reason": "mapper snapshot is unavailable"}
    snapshot = snapshots[-1]
    try:
        mapper_control = int(str(snapshot["mapper_control"]), 16)
        ppu_control = int(str(snapshot["ppu_control"]), 16)
        r1 = int(str(snapshot["r1"]), 16)
    except (KeyError, TypeError, ValueError):
        return {"verdict": "UNKNOWN", "reason": "mapper snapshot is incomplete"}

    chr_mode = (mapper_control >> 7) & 1
    background_table = (ppu_control >> 4) & 1
    if chr_mode != 0 or background_table != 0:
        return {
            "verdict": "UNKNOWN",
            "reason": "captured mapper mode does not map background table 0 through R1",
            "mapper_control": f"0x{mapper_control:02X}",
            "ppu_control": f"0x{ppu_control:02X}",
            "r1": f"0x{r1:02X}",
        }
    page = r1 & 0xFE
    return {
        "verdict": "PASS",
        "reason": "background tile codes 0x80-0xBF map through the captured R1 page",
        "mapper_control": f"0x{mapper_control:02X}",
        "ppu_control": f"0x{ppu_control:02X}",
        "r1": f"0x{r1:02X}",
        "visible_chr_1k_page": f"0x{page:02X}",
        "physical_chr_8k_bank": page // 8,
        "tile_code_range": "0x80-0xBF",
    }


def screenshot_window2_candidates(
    screenshot: Path | None,
    *,
    base_rom: bytes,
    template: bytes,
) -> dict[str, Any]:
    """Infer the visible 1 KiB CHR page for tile codes 0x80-0xBF.

    This uses the literal captured pixels of visible Japanese glyphs.  It is
    deliberately advisory because an MMC3 split can change the mapper state
    within a frame, making an end-of-frame register snapshot insufficient.
    """

    if screenshot is None or not screenshot.is_file():
        return {"verdict": "UNKNOWN", "reason": "screenshot is unavailable"}
    try:
        from PIL import Image
    except ImportError:
        return {"verdict": "UNKNOWN", "reason": "Pillow is unavailable"}

    layout = parse_ines_layout(base_rom)
    image = Image.open(screenshot).convert("RGB")
    if image.width < 256 or image.height < 224:
        return {"verdict": "UNKNOWN", "reason": "unexpected screenshot dimensions"}

    def image_mask(x0: int, y0: int) -> tuple[int, ...]:
        return tuple(
            1 if image.getpixel((x0 + x, y0 + y)) == (255, 255, 255) else 0
            for y in range(8)
            for x in range(8)
        )

    def chr_mask(chr_1k_bank: int, code: int) -> tuple[int, ...]:
        local_tile = (chr_1k_bank % 8) * 0x40 + (code & 0x3F)
        offset = (
            layout.chr_start
            + (chr_1k_bank // 8) * 0x2000
            + local_tile * CHR_TILE_SIZE
        )
        tile = base_rom[offset : offset + CHR_TILE_SIZE]
        return tuple(
            ((tile[y] | tile[y + 8]) >> (7 - x)) & 1
            for y in range(8)
            for x in range(8)
        )

    observed: list[dict[str, int]] = []
    for _label, row, column, width in LABEL_SLOTS:
        for offset in range(width):
            code = template[(row - 24) * 32 + column + offset]
            if not 0x80 <= code < 0xC0:
                continue
            mask = image_mask((column + offset) * 8, row * 8)
            if not 0 < sum(mask) < 64:
                continue
            observed.append(
                {"row": row, "column": column + offset, "code": code, "ink_pixels": sum(mask)}
            )

    candidates: list[int] = []
    for chr_1k_bank in range(128):
        if all(
            chr_mask(chr_1k_bank, item["code"])
            == image_mask(item["column"] * 8, item["row"] * 8)
            for item in observed
        ):
            candidates.append(chr_1k_bank)

    if len(candidates) == 1:
        bank = candidates[0]
        verdict = "PASS"
        reason = "all visible 0x80-0xBF glyph masks match one physical 1 KiB CHR page"
    elif not candidates:
        verdict = "UNKNOWN"
        reason = "no single CHR page matches the captured glyph masks"
    else:
        verdict = "UNKNOWN"
        reason = "multiple physical CHR pages match the captured glyph masks"
    return {
        "verdict": verdict,
        "reason": reason,
        "observed_tiles": [
            {
                **item,
                "code": f"0x{item['code']:02X}",
            }
            for item in observed
        ],
        "matching_chr_1k_banks": candidates,
        "physical_chr_8k_banks": sorted({bank // 8 for bank in candidates}),
    }


def korean_layout() -> list[dict[str, Any]]:
    """Return the planned 2x2 tile cells within the copied 4-row template."""

    rows: list[dict[str, Any]] = []
    for index, ((label_id, _old_row, column, _width), text) in enumerate(
        zip(LABEL_SLOTS, KOREAN_MENU_LABELS, strict=True)
    ):
        upper_menu_row = index < 4
        top_row = 24 if upper_menu_row else 26
        bottom_row = top_row + 1
        rows.append(
            {
                "id": label_id,
                "korean": text,
                "column": column,
                "top_row": top_row,
                "bottom_row": bottom_row,
                "top_template_offsets": [
                    (top_row - 24) * 32 + column + delta for delta in range(4)
                ],
                "bottom_template_offsets": [
                    (bottom_row - 24) * 32 + column + delta for delta in range(4)
                ],
            }
        )
    return rows


def analyze(
    *,
    base_rom_path: Path,
    reference_rom_path: Path,
    base_capture_dir: Path,
    reference_capture_dir: Path,
) -> dict[str, Any]:
    base_rom = base_rom_path.read_bytes()
    reference_rom = reference_rom_path.read_bytes()
    if len(base_rom) != len(reference_rom):
        raise ValueError("base and reference ROM lengths differ")
    base_capture = capture_info(base_capture_dir)
    reference_capture = capture_info(reference_capture_dir)
    base_template = base_rom[TEMPLATE_ROM_OFFSET : TEMPLATE_ROM_OFFSET + TEMPLATE_LENGTH]
    reference_template = reference_rom[TEMPLATE_ROM_OFFSET : TEMPLATE_ROM_OFFSET + TEMPLATE_LENGTH]
    if len(base_template) != TEMPLATE_LENGTH or len(reference_template) != TEMPLATE_LENGTH:
        raise ValueError("menu template lies outside a supplied ROM")

    base_labels = [
        label_slice(base_template, row, column, width).hex(" ").upper()
        for _label, row, column, width in LABEL_SLOTS
    ]
    english_labels = [
        english_text(label_slice(reference_template, row, column, width))
        for _label, row, column, width in LABEL_SLOTS
    ]
    checks = {
        "base_lua_done": base_capture["summary_reason"] == "lua_done",
        "reference_lua_done": reference_capture["summary_reason"] == "lua_done",
        "base_template_matches_display": matches_static_template(base_template, base_capture["template"]),
        "base_mirror_matches_display": matches_static_template(base_template, base_capture["mirror_template"]),
        "reference_template_matches_display": matches_static_template(reference_template, reference_capture["template"]),
        "reference_mirror_matches_display": matches_static_template(reference_template, reference_capture["mirror_template"]),
        "english_labels_match_reference": tuple(english_labels) == EXPECTED_ENGLISH_LABELS,
    }
    mapper_mapping = visible_label_mapper_mapping(base_capture)
    checks["base_mapper_resolves_visible_label_page"] = mapper_mapping["verdict"] == "PASS"
    overall_verdict = "PASS" if all(checks.values()) else "FAIL"
    pixel_mapping = screenshot_window2_candidates(
        base_capture["screenshot"], base_rom=base_rom, template=base_template
    )
    label_rows = []
    for index, ((label_id, row, column, width), base_hex, english) in enumerate(
        zip(LABEL_SLOTS, base_labels, english_labels, strict=True)
    ):
        label_rows.append(
            {
                "id": label_id,
                "legacy_row": row,
                "legacy_column": column,
                "legacy_width": width,
                "rom_offset": hex_offset(TEMPLATE_ROM_OFFSET + (row - 24) * 32 + column),
                "base_bytes": base_hex,
                "english_reference": english,
                "korean_candidate": KOREAN_MENU_LABELS[index],
            }
        )
    return {
        "overall_verdict": overall_verdict,
        "checks": checks,
        "source": {
            "base_rom": str(base_rom_path),
            "reference_rom": str(reference_rom_path),
            "template_rom_offset": hex_offset(TEMPLATE_ROM_OFFSET),
            "template_length": TEMPLATE_LENGTH,
            "cpu_source": "0xF2B1-0xF330",
            "ppu_destination": "0x2700-0x277F",
            "display_nametable": DISPLAY_NAMETABLE,
            "display_rows": [24, 25, 26, 27],
        },
        "captures": {
            "base": {
                "dir": str(base_capture_dir),
                "reason": base_capture["summary_reason"],
                "screenshot": str(base_capture["screenshot"]) if base_capture["screenshot"] else None,
            },
            "reference": {
                "dir": str(reference_capture_dir),
                "reason": reference_capture["summary_reason"],
                "screenshot": str(reference_capture["screenshot"]) if reference_capture["screenshot"] else None,
            },
        },
        "labels": label_rows,
        "readability_layout": korean_layout(),
        "visible_label_mapper_mapping": mapper_mapping,
        "visible_window2_pixel_mapping": pixel_mapping,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    source = payload["source"]
    checks = payload["checks"]
    pixel = payload["visible_window2_pixel_mapping"]
    mapper = payload["visible_label_mapper_mapping"]
    lines = [
        "# Main Menu Context Evidence",
        "",
        f"Status: **{payload['overall_verdict']}**",
        "",
        "## Proven Context",
        "",
        f"- Base template: `{source['template_rom_offset']}`, {source['template_length']} bytes.",
        f"- CPU copy source: `{source['cpu_source']}`.",
        f"- PPU destination: `{source['ppu_destination']}` (nametable {source['display_nametable']}, rows 24-27).",
        "- Both captures use the fixed 1,906-frame menu route and finish with `lua_done`.",
        "",
        "## Label Map",
        "",
        "| id | base ROM offset | legacy tile row/column | English structural reference | Korean 16x16 candidate |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["labels"]:
        lines.append(
            f"| `{row['id']}` | `{row['rom_offset']}` | "
            f"{row['legacy_row']}/{row['legacy_column']} | {row['english_reference']} | {row['korean_candidate']} |"
        )
    lines += [
        "",
        "## Readability Layout",
        "",
        "Each Korean syllable uses a 2x2 set of 8x8 tiles. The first four labels",
        "move to rows 24-25 and the lower four to rows 26-27, so both menu lines",
        "remain fully inside the 240-pixel frame. The original selector stays in",
        "its existing row until its runtime movement is separately verified.",
        "",
        "| id | Korean | column | top row | bottom row |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in payload["readability_layout"]:
        lines.append(
            f"| `{row['id']}` | {row['korean']} | {row['column']} | "
            f"{row['top_row']} | {row['bottom_row']} |"
        )
    lines += [
        "",
        "## Runtime Font Mapping",
        "",
        f"- MMC3 mapper verdict: **{mapper['verdict']}**.",
        f"- {mapper['reason']}",
    ]
    if mapper["verdict"] == "PASS":
        lines += [
            f"- Captured R1: `{mapper['r1']}` -> visible CHR 1 KiB page `{mapper['visible_chr_1k_page']}` (Bank {mapper['physical_chr_8k_bank']}).",
        ]
    lines += [
        f"- Pixel-mask verdict: **{pixel['verdict']}**.",
        f"- {pixel['reason']}",
        f"- Matching 1 KiB CHR pages: `{pixel.get('matching_chr_1k_banks', [])}`.",
        "",
        "The mapper result identifies the live font page. The pixel-mask result stays",
        "advisory because a literal screenshot mask can include palette and raster effects.",
        "A menu candidate must still clone or otherwise isolate the live page before",
        "replacing declared Korean tile codes.",
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"- `{name}`: {'PASS' if value else 'FAIL'}" for name, value in checks.items())
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-rom", type=Path, default=find_rom_path())
    parser.add_argument("--reference-rom", type=Path, default=DEFAULT_REFERENCE_ROM)
    parser.add_argument("--base-capture", type=Path, default=BASE_CAPTURE_DIR)
    parser.add_argument("--reference-capture", type=Path, default=REFERENCE_CAPTURE_DIR)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    args = parser.parse_args()

    payload = analyze(
        base_rom_path=args.base_rom,
        reference_rom_path=args.reference_rom,
        base_capture_dir=args.base_capture,
        reference_capture_dir=args.reference_capture,
    )
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")
    print(f"overall_verdict={payload['overall_verdict']}")
    print(f"json={args.json_output}")
    print(f"markdown={args.markdown_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
