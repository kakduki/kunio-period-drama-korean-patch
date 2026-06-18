#!/usr/bin/env python3
"""Generate focused PNG crops from the v0.4.2 auto-input FCEUX screenshots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from convert_fceux_gd_to_png import gd_pixels_to_png_rgb, parse_gd_truecolor
from rom_utils import REPO_ROOT


AUTO_DIR = REPO_ROOT / "rom_analysis" / "fceux_input_explorer_v042"
OUT_JSON = AUTO_DIR / "review_crops.json"
OUT_MD = AUTO_DIR / "review_crops.md"

DEFAULT_CROPS = [
    ("dialogue_box", 0, 184, 256, 56),
    ("top_overlay", 0, 0, 256, 24),
]


def crop_pixels(pixel_data: bytes, width: int, x: int, y: int, crop_width: int, crop_height: int) -> bytes:
    stride = width * 4
    output = bytearray()
    for row in range(crop_height):
        start = ((y + row) * stride) + (x * 4)
        end = start + (crop_width * 4)
        output.extend(pixel_data[start:end])
    return bytes(output)


def make_crops(input_dir: Path = AUTO_DIR) -> dict[str, object]:
    crops = []
    for gd_file in sorted(input_dir.glob("*_screen.gd")):
        width, height, pixels = parse_gd_truecolor(gd_file.read_bytes())
        for name, x, y, crop_width, crop_height in DEFAULT_CROPS:
            if x < 0 or y < 0 or x + crop_width > width or y + crop_height > height:
                raise ValueError(f"crop {name} exceeds screenshot bounds for {gd_file}")
            cropped_pixels = crop_pixels(pixels, width, x, y, crop_width, crop_height)
            out_path = gd_file.with_name(f"{gd_file.stem}_{name}.png")
            out_path.write_bytes(gd_pixels_to_png_rgb(crop_width, crop_height, cropped_pixels))
            crops.append(
                {
                    "source": str(gd_file.relative_to(REPO_ROOT)).replace("\\", "/"),
                    "crop": name,
                    "path": str(out_path.relative_to(REPO_ROOT)).replace("\\", "/"),
                    "x": x,
                    "y": y,
                    "width": crop_width,
                    "height": crop_height,
                    "bytes": out_path.stat().st_size,
                }
            )
    return {
        "source_dir": str(input_dir.relative_to(REPO_ROOT)).replace("\\", "/"),
        "crop_count": len(crops),
        "crops": crops,
    }


def write_report(payload: dict[str, object]) -> None:
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Auto-Input Review Crops",
        "",
        "Focused crops generated from the checked-in FCEUX `gui.gdscreenshot()` captures.",
        "",
        f"- Source directory: `{payload['source_dir']}`",
        f"- Crop images: **{payload['crop_count']}**",
        "",
        "| source | crop | image | region | bytes |",
        "| --- | --- | --- | --- | ---: |",
    ]
    for row in payload["crops"]:
        lines.append(
            f"| `{row['source']}` | `{row['crop']}` | `{row['path']}` | "
            f"{row['x']},{row['y']} {row['width']}x{row['height']} | {row['bytes']} |"
        )
    lines += [
        "",
        "## Use",
        "",
        "- `dialogue_box` crops isolate the bottom text area for quicker visual review.",
        "- `top_overlay` crops preserve the scripted route/frame marker without opening the full screenshot.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=AUTO_DIR)
    args = parser.parse_args()

    input_dir = args.input_dir
    if not input_dir.is_absolute():
        input_dir = REPO_ROOT / input_dir
    payload = make_crops(input_dir)
    write_report(payload)
    print(f"Wrote {OUT_JSON.relative_to(REPO_ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(REPO_ROOT)}")
    print(f"crop_count={payload['crop_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
