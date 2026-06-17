#!/usr/bin/env python3
"""Build an experimental CHR Bank 07 patch from korean_slot_allocation_plan."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from build_patch import (
    CHR_BANK7_END,
    CHR_BANK7_START,
    CHR_TILE_SIZE,
    glyph_8x16_to_8x8_tile,
    make_records,
    write_ips,
)
from rom_utils import REPO_ROOT, find_rom_path


DEFAULT_PLAN = REPO_ROOT / "rom_analysis" / "korean_slot_allocation_plan.json"
DEFAULT_OUT_DIR = REPO_ROOT / "output"
OUT_STEM = "kunio_period_drama_korean_plan_v0.2"


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def load_font() -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        r"C:\Windows\Fonts\malgun.ttf",
        r"C:\Windows\Fonts\malgunbd.ttf",
        r"C:\Windows\Fonts\gulim.ttc",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if not path.exists():
            continue
        try:
            return ImageFont.truetype(str(path), 14)
        except OSError:
            continue
    return ImageFont.load_default()


def render_glyph_8x16(glyph: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont) -> bytes:
    image = Image.new("1", (8, 16), 0)
    draw = ImageDraw.Draw(image)
    bbox = draw.textbbox((0, 0), glyph, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    x = (8 - width) // 2 - bbox[0]
    y = (16 - height) // 2 - bbox[1]
    draw.text((x, y), glyph, font=font, fill=255)

    out = bytearray(32)
    for row in range(16):
        plane0 = 0
        for col in range(8):
            if image.getpixel((col, row)):
                plane0 |= 1 << (7 - col)
        out[row] = plane0
        out[row + 16] = 0
    return bytes(out)


def build_from_plan(rom_path: Path, plan_path: Path, out_dir: Path) -> dict[str, object]:
    original = rom_path.read_bytes()
    patched = bytearray(original)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    font = load_font()

    changed_offsets: list[int] = []
    slot_reports: list[dict[str, object]] = []
    for slot in plan["slots"]:
        glyph = slot["glyph"]
        tile = int(slot["tile"], 16)
        target_offset = CHR_BANK7_START + tile * CHR_TILE_SIZE
        target_end = target_offset + CHR_TILE_SIZE
        if not CHR_BANK7_START <= target_offset < target_end <= CHR_BANK7_END:
            raise RuntimeError(f"Tile 0x{tile:03X} escaped CHR Bank 07")

        tile_data = glyph_8x16_to_8x8_tile(render_glyph_8x16(glyph, font))
        old = bytes(patched[target_offset:target_end])
        diff_count = sum(1 for a, b in zip(old, tile_data) if a != b)
        patched[target_offset:target_end] = tile_data
        changed_offsets.extend(
            offset for offset, (a, b) in enumerate(zip(old, tile_data), start=target_offset) if a != b
        )
        slot_reports.append(
            {
                "glyph": glyph,
                "tile": slot["tile"],
                "rom_offset": f"0x{target_offset:05X}",
                "planned_prg_byte": slot["prg_plus_0x7a_byte"],
                "changed_bytes": diff_count,
                "used_by_labels": slot["used_by_labels"],
            }
        )

    escaped = [offset for offset in changed_offsets if not CHR_BANK7_START <= offset < CHR_BANK7_END]
    if escaped:
        raise RuntimeError(f"{len(escaped)} changed byte(s) escaped CHR Bank 07")

    records = make_records(original, bytes(patched))
    out_dir.mkdir(parents=True, exist_ok=True)
    ips_path = out_dir / f"{OUT_STEM}.ips"
    patched_path = out_dir / f"{OUT_STEM}.nes"
    report_path = out_dir / f"{OUT_STEM}_build_report.json"

    write_ips(ips_path, records)
    patched_path.write_bytes(patched)

    report = {
        "plan": str(plan_path),
        "rom": str(rom_path),
        "original_md5": md5(original),
        "patched_md5": md5(bytes(patched)),
        "chr_bank7_range": [f"0x{CHR_BANK7_START:05X}", f"0x{CHR_BANK7_END - 1:05X}"],
        "glyphs_written": len(plan["slots"]),
        "changed_bytes": len(changed_offsets),
        "escaped_chr_bank7_bytes": len(escaped),
        "ips_records": len(records),
        "ips_path": str(ips_path),
        "patched_rom_path": str(patched_path),
        "slots": slot_reports,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?", help="Optional .nes path; defaults to rom/*.nes")
    parser.add_argument("--plan", default=str(DEFAULT_PLAN))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    rom_path = Path(args.rom).expanduser().resolve() if args.rom else find_rom_path()
    plan_path = Path(args.plan).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    report = build_from_plan(rom_path, plan_path, out_dir)
    print(f"patched ROM: {report['patched_rom_path']}")
    print(f"IPS: {report['ips_path']}")
    print(f"glyphs={report['glyphs_written']} changed_bytes={report['changed_bytes']} ips_records={report['ips_records']}")
    print(f"patched MD5: {report['patched_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
