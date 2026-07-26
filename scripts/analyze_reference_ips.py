#!/usr/bin/env python3
"""Analyze a third-party IPS against a legally obtained base ROM without writing a ROM."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from rom_utils import REPO_ROOT


DEFAULT_JSON = REPO_ROOT / "rom_analysis" / "english_patch_reference.json"
DEFAULT_MARKDOWN = REPO_ROOT / "rom_analysis" / "english_patch_reference.md"
ASCII_RUN = re.compile(rb"[\x20-\x7e]{4,}")
ENGLISH_TILE_RUN = re.compile(rb"[\x00-\x1a]{4,}")
DIALOGUE_ENGLISH_TILE_RUN = re.compile(rb"[\x81-\x9a\xff]{4,}")


@dataclass(frozen=True)
class IpsRecord:
    offset: int
    data: bytes
    rle: bool


@dataclass(frozen=True)
class InesLayout:
    header_size: int
    prg_start: int
    prg_end: int
    chr_start: int
    chr_end: int
    prg_bank_size: int = 0x4000
    chr_bank_size: int = 0x2000


def digest(data: bytes, algorithm: str) -> str:
    return hashlib.new(algorithm, data).hexdigest()


def parse_ips(data: bytes) -> tuple[list[IpsRecord], int | None]:
    if not data.startswith(b"PATCH"):
        raise ValueError("IPS file does not start with PATCH")

    records: list[IpsRecord] = []
    position = 5
    while position < len(data):
        if data[position : position + 3] == b"EOF":
            position += 3
            remaining = len(data) - position
            if remaining == 0:
                return records, None
            if remaining == 3:
                return records, int.from_bytes(data[position : position + 3], "big")
            raise ValueError("unexpected bytes after IPS EOF")

        if position + 5 > len(data):
            raise ValueError("truncated IPS record header")
        offset = int.from_bytes(data[position : position + 3], "big")
        size = int.from_bytes(data[position + 3 : position + 5], "big")
        position += 5

        if size:
            end = position + size
            if end > len(data):
                raise ValueError("truncated IPS data record")
            records.append(IpsRecord(offset=offset, data=data[position:end], rle=False))
            position = end
            continue

        if position + 3 > len(data):
            raise ValueError("truncated IPS RLE record")
        rle_size = int.from_bytes(data[position : position + 2], "big")
        value = data[position + 2]
        position += 3
        records.append(IpsRecord(offset=offset, data=bytes([value]) * rle_size, rle=True))

    raise ValueError("IPS file has no EOF marker")


def apply_records(base: bytes, records: list[IpsRecord], truncate_size: int | None) -> bytes:
    patched = bytearray(base)
    for record in records:
        end = record.offset + len(record.data)
        if end > len(patched):
            patched.extend(b"\x00" * (end - len(patched)))
        patched[record.offset:end] = record.data
    if truncate_size is not None:
        del patched[truncate_size:]
    return bytes(patched)


def parse_ines_layout(rom: bytes) -> InesLayout:
    if len(rom) < 16 or rom[:4] != b"NES\x1a":
        raise ValueError("base ROM is not an iNES file")
    trainer_size = 512 if rom[6] & 0x04 else 0
    header_size = 16 + trainer_size
    prg_size = rom[4] * 0x4000
    chr_size = rom[5] * 0x2000
    prg_start = header_size
    prg_end = prg_start + prg_size
    chr_start = prg_end
    chr_end = chr_start + chr_size
    if chr_end > len(rom):
        raise ValueError("iNES header declares more PRG/CHR data than the ROM contains")
    return InesLayout(
        header_size=header_size,
        prg_start=prg_start,
        prg_end=prg_end,
        chr_start=chr_start,
        chr_end=chr_end,
    )


def region_for_offset(offset: int, layout: InesLayout) -> tuple[str, int | None]:
    if offset < layout.header_size:
        return "header", None
    if offset < layout.prg_end:
        return "PRG", (offset - layout.prg_start) // layout.prg_bank_size
    if offset < layout.chr_end:
        return "CHR", (offset - layout.chr_start) // layout.chr_bank_size
    return "trailing", None


def changed_offsets(base: bytes, patched: bytes) -> list[int]:
    common = min(len(base), len(patched))
    changed = [index for index in range(common) if base[index] != patched[index]]
    changed.extend(range(common, max(len(base), len(patched))))
    return changed


def group_spans(offsets: list[int], layout: InesLayout) -> list[dict[str, object]]:
    if not offsets:
        return []

    spans: list[dict[str, object]] = []
    start = offsets[0]
    previous = offsets[0]
    region, bank = region_for_offset(start, layout)
    for offset in offsets[1:]:
        next_region, next_bank = region_for_offset(offset, layout)
        if offset != previous + 1 or (next_region, next_bank) != (region, bank):
            spans.append(
                {
                    "start": start,
                    "end_exclusive": previous + 1,
                    "length": previous - start + 1,
                    "region": region,
                    "bank": bank,
                }
            )
            start = offset
            region, bank = next_region, next_bank
        previous = offset
    spans.append(
        {
            "start": start,
            "end_exclusive": previous + 1,
            "length": previous - start + 1,
            "region": region,
            "bank": bank,
        }
    )
    return spans


def summarize_banks(
    offsets: list[int], spans: list[dict[str, object]], layout: InesLayout
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for region, bank_count in (
        ("PRG", (layout.prg_end - layout.prg_start) // layout.prg_bank_size),
        ("CHR", (layout.chr_end - layout.chr_start) // layout.chr_bank_size),
    ):
        for bank in range(bank_count):
            bank_offsets = [
                offset
                for offset in offsets
                if region_for_offset(offset, layout) == (region, bank)
            ]
            if not bank_offsets:
                continue
            bank_spans = [
                span
                for span in spans
                if span["region"] == region and span["bank"] == bank
            ]
            rows.append(
                {
                    "region": region,
                    "bank": bank,
                    "changed_bytes": len(bank_offsets),
                    "changed_spans": len(bank_spans),
                    "first_offset": min(bank_offsets),
                    "last_offset": max(bank_offsets),
                }
            )
    return rows


def extract_new_ascii_runs(
    base: bytes, patched: bytes, layout: InesLayout, changed_set: set[int]
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    prg = patched[layout.prg_start : layout.prg_end]
    for match in ASCII_RUN.finditer(prg):
        rom_start = layout.prg_start + match.start()
        rom_end = layout.prg_start + match.end()
        if not any(offset in changed_set for offset in range(rom_start, rom_end)):
            continue
        base_bytes = base[rom_start:rom_end]
        if base_bytes == match.group():
            continue
        rows.append(
            {
                "rom_offset": rom_start,
                "prg_offset": rom_start - layout.prg_start,
                "prg_bank": (rom_start - layout.prg_start) // layout.prg_bank_size,
                "length": len(match.group()),
                "text": match.group().decode("ascii"),
            }
        )
    return rows


def extract_english_tile_runs(
    base: bytes, patched: bytes, layout: InesLayout, changed_set: set[int]
) -> list[dict[str, object]]:
    """Decode direct-low text bytes for CHR Bank 7 tiles 0x100-0x11A."""
    rows: list[dict[str, object]] = []
    prg = patched[layout.prg_start : layout.prg_end]
    for match in ENGLISH_TILE_RUN.finditer(prg):
        rom_start = layout.prg_start + match.start()
        rom_end = layout.prg_start + match.end()
        changed_count = sum(offset in changed_set for offset in range(rom_start, rom_end))
        if changed_count / len(match.group()) < 0.75:
            continue
        text = "".join(" " if byte == 0 else chr(ord("A") + byte - 1) for byte in match.group())
        text = " ".join(text.split())
        if sum(character.isalpha() for character in text) < 3:
            continue
        rows.append(
            {
                "rom_offset": rom_start,
                "prg_offset": rom_start - layout.prg_start,
                "prg_bank": (rom_start - layout.prg_start) // layout.prg_bank_size,
                "length": len(match.group()),
                "changed_ratio": round(changed_count / len(match.group()), 3),
                "text": text,
                "bytes": " ".join(f"{byte:02X}" for byte in match.group()),
            }
        )
    return rows


def extract_dialogue_english_tile_runs(
    base: bytes, patched: bytes, layout: InesLayout, changed_set: set[int]
) -> list[dict[str, object]]:
    """Decode the dialogue font path at CHR tiles 0x181-0x19A."""
    rows: list[dict[str, object]] = []
    prg = patched[layout.prg_start : layout.prg_end]
    for match in DIALOGUE_ENGLISH_TILE_RUN.finditer(prg):
        rom_start = layout.prg_start + match.start()
        rom_end = layout.prg_start + match.end()
        changed_count = sum(offset in changed_set for offset in range(rom_start, rom_end))
        if changed_count / len(match.group()) < 0.75:
            continue
        text = "".join(" " if byte == 0xFF else chr(ord("A") + byte - 0x81) for byte in match.group())
        text = " ".join(text.split())
        if sum(character.isalpha() for character in text) < 3:
            continue
        rows.append(
            {
                "rom_offset": rom_start,
                "prg_offset": rom_start - layout.prg_start,
                "prg_bank": (rom_start - layout.prg_start) // layout.prg_bank_size,
                "length": len(match.group()),
                "changed_ratio": round(changed_count / len(match.group()), 3),
                "text": text,
                "bytes": " ".join(f"{byte:02X}" for byte in match.group()),
            }
        )
    return rows


def render_chr_bank(
    rom: bytes,
    layout: InesLayout,
    bank: int,
    output: Path,
    scale: int = 3,
) -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise RuntimeError("Pillow is required only for optional CHR sheet rendering") from exc

    bank_count = (layout.chr_end - layout.chr_start) // layout.chr_bank_size
    if not 0 <= bank < bank_count:
        raise ValueError(f"CHR bank {bank} is outside 0-{bank_count - 1}")

    bank_start = layout.chr_start + bank * layout.chr_bank_size
    bank_data = rom[bank_start : bank_start + layout.chr_bank_size]
    columns = 32
    rows = 16
    label_height = 10
    cell_width = 8 * scale
    cell_height = 8 * scale + label_height
    colors = [(255, 255, 255), (180, 180, 180), (80, 80, 80), (0, 0, 0)]
    sheet = Image.new("RGB", (columns * cell_width, rows * cell_height), (235, 235, 235))
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.load_default()

    for tile in range(512):
        tile_start = tile * 16
        tile_data = bank_data[tile_start : tile_start + 16]
        cell_x = (tile % columns) * cell_width
        cell_y = (tile // columns) * cell_height
        draw.text((cell_x + 1, cell_y), f"{tile:03X}", fill=(170, 0, 0), font=label_font)
        for row in range(8):
            plane0 = tile_data[row]
            plane1 = tile_data[row + 8]
            for column in range(8):
                bit = 7 - column
                color = colors[((plane1 >> bit) & 1) * 2 + ((plane0 >> bit) & 1)]
                x0 = cell_x + column * scale
                y0 = cell_y + label_height + row * scale
                draw.rectangle(
                    (x0, y0, x0 + scale - 1, y0 + scale - 1),
                    fill=color,
                )

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def analyze(base: bytes, ips: bytes, base_name: str, patch_name: str) -> dict[str, object]:
    records, truncate_size = parse_ips(ips)
    patched = apply_records(base, records, truncate_size)
    layout = parse_ines_layout(base)
    offsets = changed_offsets(base, patched)
    spans = group_spans(offsets, layout)
    changed_set = set(offsets)
    ascii_runs = extract_new_ascii_runs(base, patched, layout, changed_set)
    english_tile_runs = extract_english_tile_runs(base, patched, layout, changed_set)
    dialogue_tile_runs = extract_dialogue_english_tile_runs(base, patched, layout, changed_set)
    bank_rows = summarize_banks(offsets, spans, layout)
    region_counts: dict[str, int] = {}
    for offset in offsets:
        region, _ = region_for_offset(offset, layout)
        region_counts[region] = region_counts.get(region, 0) + 1
    record_rows: list[dict[str, object]] = []
    for record in records:
        region, bank = region_for_offset(record.offset, layout)
        end = record.offset + len(record.data)
        actual_changed = sum(
            offset < len(base) and base[offset] != patched[offset]
            for offset in range(record.offset, min(end, len(patched)))
        )
        actual_changed += max(0, end - len(base))
        record_rows.append(
            {
                "offset": record.offset,
                "end_exclusive": end,
                "length": len(record.data),
                "region": region,
                "bank": bank,
                "rle": record.rle,
                "actual_changed_bytes": actual_changed,
            }
        )
    header_changes = [
        {
            "offset": offset,
            "base": base[offset],
            "patched": patched[offset],
        }
        for offset in offsets
        if offset < layout.header_size and offset < len(base) and offset < len(patched)
    ]

    return {
        "source": {
            "base_rom": base_name,
            "base_size": len(base),
            "base_md5": digest(base, "md5"),
            "base_sha1": digest(base, "sha1"),
            "base_payload_sha1": digest(base[layout.header_size :], "sha1"),
            "ips_patch": patch_name,
            "ips_size": len(ips),
            "ips_sha256": digest(ips, "sha256"),
        },
        "patched": {
            "size": len(patched),
            "md5": digest(patched, "md5"),
            "sha1": digest(patched, "sha1"),
            "payload_sha1": digest(patched[layout.header_size :], "sha1"),
        },
        "ines": {
            "header_size": layout.header_size,
            "prg_start": layout.prg_start,
            "prg_end": layout.prg_end,
            "prg_banks_16k": (layout.prg_end - layout.prg_start) // layout.prg_bank_size,
            "chr_start": layout.chr_start,
            "chr_end": layout.chr_end,
            "chr_banks_8k": (layout.chr_end - layout.chr_start) // layout.chr_bank_size,
        },
        "ips": {
            "record_count": len(records),
            "rle_record_count": sum(1 for record in records if record.rle),
            "truncate_size": truncate_size,
            "record_payload_bytes": sum(len(record.data) for record in records),
            "largest_records": sorted(
                record_rows,
                key=lambda row: int(row["length"]),
                reverse=True,
            )[:30],
            "prg_bank1_records": [
                row for row in record_rows if row["region"] == "PRG" and row["bank"] == 1
            ],
        },
        "changes": {
            "changed_byte_count": len(offsets),
            "changed_span_count": len(spans),
            "region_changed_bytes": region_counts,
            "bank_summary": bank_rows,
            "largest_spans": sorted(spans, key=lambda row: int(row["length"]), reverse=True)[:20],
            "header_changes": header_changes,
        },
        "new_ascii_runs": ascii_runs,
        "english_tile_alpha_runs": english_tile_runs,
        "english_dialogue_tile_alpha_runs": dialogue_tile_runs,
    }


def hex_offset(value: int) -> str:
    return f"0x{value:05X}"


def render_markdown(payload: dict[str, object]) -> str:
    source = payload["source"]
    patched = payload["patched"]
    ips = payload["ips"]
    changes = payload["changes"]
    ines = payload["ines"]
    bank_rows = changes["bank_summary"]
    ascii_runs = payload["new_ascii_runs"]
    english_tile_runs = payload["english_tile_alpha_runs"]
    dialogue_tile_runs = payload["english_dialogue_tile_alpha_runs"]

    lines = [
        "# English Patch Reference Analysis",
        "",
        "This report compares the public `Technos Samurai: Downtown Special v1.00` IPS",
        "with the verified Japanese base ROM. The third-party IPS and patched ROM are not stored in this repository.",
        "",
        "## Identity",
        "",
        f"- Base ROM: `{source['base_rom']}`",
        f"- Base size: `{source['base_size']}` bytes",
        f"- Base MD5: `{source['base_md5']}`",
        f"- Base SHA-1: `{source['base_sha1']}`",
        f"- Base payload SHA-1 (without iNES header): `{source['base_payload_sha1']}`",
        f"- Reference IPS: `{source['ips_patch']}`",
        f"- Reference IPS SHA-256: `{source['ips_sha256']}`",
        "- Official archive index: `https://www.dynamic-designs.us/downloads.shtml`",
        "- Patch database entry: `https://romhackplaza.org/translations/downtown-special-kunio-kun-no-jidaigeki-dayo-zenin-shuugou-english-translation-nes/`",
        f"- Patched size: `{patched['size']}` bytes",
        f"- Patched MD5: `{patched['md5']}`",
        f"- Patched SHA-1: `{patched['sha1']}`",
        f"- Patched payload SHA-1 (without iNES header): `{patched['payload_sha1']}`",
        "",
        "## Structural Result",
        "",
        f"- IPS records: `{ips['record_count']}` (`{ips['rle_record_count']}` RLE)",
        f"- IPS payload bytes: `{ips['record_payload_bytes']}`",
        f"- Actual changed bytes: `{changes['changed_byte_count']}`",
        f"- Contiguous changed spans: `{changes['changed_span_count']}`",
        f"- PRG changed bytes: `{changes['region_changed_bytes'].get('PRG', 0)}`",
        f"- CHR changed bytes: `{changes['region_changed_bytes'].get('CHR', 0)}`",
        f"- Header changed bytes: `{changes['region_changed_bytes'].get('header', 0)}`",
        f"- ROM size changed: `{'yes' if source['base_size'] != patched['size'] else 'no'}`",
        f"- New printable ASCII runs in changed PRG data: `{len(ascii_runs)}`",
        f"- English tile-code runs decoded from changed PRG data: `{len(english_tile_runs)}`",
        f"- English dialogue-code runs decoded from changed PRG data: `{len(dialogue_tile_runs)}`",
        "",
        "The English patch proves that this game can hold a complete translated script without",
        "expanding the ROM. Its own readme states that text was replaced and pointers were recalculated;",
        "the PRG changes below provide the map for recovering those text blocks and pointer tables.",
        "",
        "## Changed Banks",
        "",
        "| region | bank | changed bytes | spans | first ROM offset | last ROM offset |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in bank_rows:
        lines.append(
            f"| {row['region']} | {row['bank']} | {row['changed_bytes']} | {row['changed_spans']} | "
            f"`{hex_offset(row['first_offset'])}` | `{hex_offset(row['last_offset'])}` |"
        )

    lines.extend(
        [
            "",
            "## Bank 1 IPS Records",
            "",
            "These seven records are the primary script/pointer reverse-engineering targets.",
            "",
            "| ROM range | bytes | actual changed | working classification |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    classifications = {
        0x05288: "text/render support data",
        0x0561B: "dialogue/name table",
        0x056BC: "dialogue text block 1",
        0x05DD4: "pointer table plus dialogue text block 2",
        0x07894: "growth-rate UI text",
        0x07FB6: "inserted menu/label text",
        0x07FF7: "inserted menu/label text",
    }
    for row in ips["prg_bank1_records"]:
        lines.append(
            f"| `{hex_offset(row['offset'])}-{hex_offset(row['end_exclusive'] - 1)}` | "
            f"{row['length']} | {row['actual_changed_bytes']} | "
            f"{classifications.get(row['offset'], 'unclassified')} |"
        )

    lines.extend(
        [
            "",
            "## Header Difference",
            "",
        ]
    )
    if changes["header_changes"]:
        lines.append("| offset | base | patched | note |")
        lines.append("| --- | --- | --- | --- |")
        for row in changes["header_changes"]:
            note = (
                "iNES flags 6 changes mirroring bit; do not copy until its runtime need is understood"
                if row["offset"] == 6
                else "unclassified"
            )
            lines.append(
                f"| `{hex_offset(row['offset'])}` | `0x{row['base']:02X}` | "
                f"`0x{row['patched']:02X}` | {note} |"
            )
    else:
        lines.append("No iNES header bytes changed.")

    lines.extend(
        [
            "",
            "## Largest Changed Spans",
            "",
            "| region | bank | ROM range | bytes |",
            "| --- | ---: | --- | ---: |",
        ]
    )
    for row in changes["largest_spans"]:
        bank = "-" if row["bank"] is None else row["bank"]
        lines.append(
            f"| {row['region']} | {bank} | `{hex_offset(row['start'])}-"
            f"{hex_offset(row['end_exclusive'] - 1)}` | {row['length']} |"
        )

    lines.extend(
        [
            "",
            "## Decoded English Tile Runs",
            "",
            "The patched CHR Bank 7 sheet maps tile `0x100` to blank and tiles `0x101-0x11A`",
            "to `A-Z`. The reference ROM contains direct-low text bytes `0x00-0x1A`, including",
            "the verified anchors `BUNZO = 02 15 0E 1A 0F` and `SHOP = 13 08 0F 10`.",
            "These runs are therefore stronger text anchors than plain ASCII scans.",
            "",
            "| ROM offset | PRG bank | length | changed ratio | decoded text | bytes |",
            "| --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for row in english_tile_runs[:160]:
        lines.append(
            f"| `{hex_offset(row['rom_offset'])}` | {row['prg_bank']} | {row['length']} | "
            f"{row['changed_ratio']:.3f} | "
            f"`{row['text']}` | `{row['bytes']}` |"
        )

    lines.extend(
        [
            "",
            "## Decoded English Dialogue Runs",
            "",
            "The dialogue/name path uses CHR tiles `0x181-0x19A`, encoded as",
            "`A=0x81` through `Z=0x9A`, with `0xFF` acting as a separator/control byte.",
            "The first reference block at `0x0561B` includes the names `KUNIO`, `RIKI`, and `BUNZO`;",
            "sentence data begins at `0x056BC`.",
            "",
            "| ROM offset | PRG bank | length | changed ratio | decoded text | bytes |",
            "| --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for row in dialogue_tile_runs[:200]:
        lines.append(
            f"| `{hex_offset(row['rom_offset'])}` | {row['prg_bank']} | {row['length']} | "
            f"{row['changed_ratio']:.3f} | `{row['text']}` | `{row['bytes']}` |"
        )

    lines.extend(
        [
            "",
            "## New Printable PRG Runs",
            "",
        "These are discovery anchors, not a finished script dump. Short or encoded strings may not appear here.",
        "The current results are mostly non-language byte patterns, confirming that the English script uses",
        "the game's custom tile encoding rather than plain ASCII.",
            "",
            "| ROM offset | PRG bank | length | text |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    for row in ascii_runs[:120]:
        escaped = str(row["text"]).replace("|", "\\|")
        lines.append(
            f"| `{hex_offset(row['rom_offset'])}` | {row['prg_bank']} | {row['length']} | `{escaped}` |"
        )

    lines.extend(
        [
            "",
            "## How To Use This Reference",
            "",
            "1. Diff each changed PRG bank against the Japanese ROM and classify text, pointer, code, and palette spans.",
            "2. Recover the English pointer-table writes and map them back to Japanese source records.",
            "3. Build a deterministic script extractor/inserter from those records before translating more text.",
            "4. Reuse only structural knowledge. Do not reuse the English localization wording as the Korean translation source.",
            f"5. Treat CHR changes starting at `{hex_offset(ines['chr_start'])}` as font/icon reference material.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_rom", help="Path to the verified Japanese base ROM.")
    parser.add_argument("ips_patch", help="Path to the third-party IPS patch.")
    parser.add_argument("--json-output", default=str(DEFAULT_JSON))
    parser.add_argument("--markdown-output", default=str(DEFAULT_MARKDOWN))
    parser.add_argument(
        "--render-chr-bank",
        action="append",
        type=lambda value: int(value, 0),
        default=[],
        help="Render a patched 8x8 CHR bank sheet. May be supplied more than once.",
    )
    parser.add_argument(
        "--render-dir",
        help="Directory for optional CHR sheets. Defaults beside the JSON report.",
    )
    args = parser.parse_args()

    base_path = Path(args.base_rom).expanduser().resolve()
    patch_path = Path(args.ips_patch).expanduser().resolve()
    json_path = Path(args.json_output).expanduser().resolve()
    markdown_path = Path(args.markdown_output).expanduser().resolve()

    payload = analyze(
        base_path.read_bytes(),
        patch_path.read_bytes(),
        base_path.name,
        patch_path.name,
    )
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")

    if args.render_chr_bank:
        base = base_path.read_bytes()
        records, truncate_size = parse_ips(patch_path.read_bytes())
        patched = apply_records(base, records, truncate_size)
        layout = parse_ines_layout(base)
        render_dir = (
            Path(args.render_dir).expanduser().resolve()
            if args.render_dir
            else json_path.parent
        )
        for bank in args.render_chr_bank:
            output = render_dir / f"english_reference_chr_bank_{bank:02d}.png"
            render_chr_bank(patched, layout, bank, output)
            print(f"chr_sheet={output}")

    print(f"json={json_path}")
    print(f"markdown={markdown_path}")
    print(f"base_md5={payload['source']['base_md5']}")
    print(f"patched_sha1={payload['patched']['sha1']}")
    print(f"changed_bytes={payload['changes']['changed_byte_count']}")
    print(f"new_ascii_runs={len(payload['new_ascii_runs'])}")
    print(f"english_tile_alpha_runs={len(payload['english_tile_alpha_runs'])}")
    print(f"english_dialogue_tile_alpha_runs={len(payload['english_dialogue_tile_alpha_runs'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
