#!/usr/bin/env python3
"""Render and compare 16x16 Korean dialogue-font candidates."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path

from korean_font_quality import evaluate_square_bitmaps
from korean_tile_font import SQUARE_TILE_HEIGHT, SQUARE_TILE_WIDTH, normalize_glyph_to_square_bitmap
from rom_utils import REPO_ROOT


DEFAULT_GLYPHS = tuple("쿠니마사어서움직여분조두목이큰일야:")
# The older proof catalog contains mojibake source labels. Use the exact
# Korean syllables that the readability candidate will serialize.
DEFAULT_GLYPHS = tuple(
    "\uCFE0\uB2C8\uC624\uC11C\uB458\uB7EC\uBD84\uC870\uB450\uBAA9\uC774\uC704\uD5D8\uD574:"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "rom_analysis" / "opening_font_profile_comparison"
RECOMMENDED_PROFILE = "malgun-bold-airy"


@dataclass(frozen=True)
class FontProfile:
    slug: str
    font_path: Path
    target_pixels: int
    threshold: int
    resample: str


DEFAULT_PROFILES = (
    FontProfile("malgun-bold-baseline", Path(r"C:\Windows\Fonts\malgunbd.ttf"), 15, 100, "lanczos"),
    FontProfile("malgun-bold-airy", Path(r"C:\Windows\Fonts\malgunbd.ttf"), 14, 145, "box"),
    FontProfile("nanum-extra-bold", Path(r"C:\Windows\Fonts\NanumGothicExtraBold.ttf"), 14, 135, "box"),
    FontProfile("kopub-dotum-bold", Path(r"C:\Windows\Fonts\KoPubDotumBold.ttf"), 14, 135, "box"),
    FontProfile("gulim-screen", Path(r"C:\Windows\Fonts\gulim.ttc"), 14, 135, "box"),
)


def evaluate_bitmaps(bitmaps: dict[str, list[list[int]]]) -> dict[str, object]:
    return evaluate_square_bitmaps(bitmaps)


def profile_bitmaps(profile: FontProfile, glyphs: tuple[str, ...]) -> dict[str, list[list[int]]]:
    return {
        glyph: normalize_glyph_to_square_bitmap(
            glyph,
            font_path=profile.font_path,
            target_pixels=profile.target_pixels,
            threshold=profile.threshold,
            resample=profile.resample,
        )
        for glyph in glyphs
    }


def render_comparison(
    profiles: list[FontProfile],
    bitmaps_by_profile: dict[str, dict[str, list[list[int]]]],
    glyphs: tuple[str, ...],
    output: Path,
) -> None:
    from PIL import Image, ImageDraw, ImageFont

    scale = 4
    label_width = 176
    row_height = SQUARE_TILE_HEIGHT * scale + 22
    cell_width = SQUARE_TILE_WIDTH * scale + 4
    image = Image.new("RGB", (label_width + cell_width * len(glyphs), row_height * len(profiles)), "white")
    draw = ImageDraw.Draw(image)
    label_font = ImageFont.load_default()
    for profile_index, profile in enumerate(profiles):
        top = profile_index * row_height
        draw.text((4, top + 4), profile.slug, fill="black", font=label_font)
        for glyph_index, glyph in enumerate(glyphs):
            bitmap = bitmaps_by_profile[profile.slug][glyph]
            left = label_width + glyph_index * cell_width
            for y, row in enumerate(bitmap):
                for x, pixel in enumerate(row):
                    if pixel:
                        draw.rectangle(
                            (left + x * scale, top + 18 + y * scale, left + (x + 1) * scale - 1, top + 18 + (y + 1) * scale - 1),
                            fill="black",
                        )
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def markdown_report(payload: dict[str, object]) -> str:
    lines = [
        "# Opening 16x16 Korean Font Profile Comparison",
        "",
        "These are literal one-bit NES tile pixels, not a high-resolution mockup.",
        "The triage result narrows candidates; native FCEUX capture remains decisive.",
        "",
        "| profile | target | threshold | resample | density | min distance | edge touches | triage |",
        "| --- | ---: | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for profile in payload["profiles"]:
        metrics = profile["metrics"]
        lines.append(
            f"| {profile['slug']} | {profile['target_pixels']} | {profile['threshold']} | "
            f"{profile['resample']} | {metrics['average_ink_density']:.4f} | "
            f"{metrics['minimum_pairwise_hamming']} | {metrics['edge_touching_glyph_count']} | "
            f"{'PASS' if metrics['triage_pass'] else 'REVIEW'} |"
        )
    lines += [
        "",
        f"- Glyph set: `{''.join(payload['glyphs'])}`",
        f"- Recommended prototype profile: `{payload['recommended_profile']}`",
        f"- Preview: `{payload['preview']}`",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--glyphs", default="".join(DEFAULT_GLYPHS))
    args = parser.parse_args()
    glyphs = tuple(dict.fromkeys(args.glyphs))
    profiles = [profile for profile in DEFAULT_PROFILES if profile.font_path.is_file()]
    if not profiles:
        raise FileNotFoundError("none of the Korean comparison fonts are installed")
    bitmaps_by_profile = {profile.slug: profile_bitmaps(profile, glyphs) for profile in profiles}
    preview = args.output_dir / "profiles.png"
    render_comparison(profiles, bitmaps_by_profile, glyphs, preview)
    payload = {
        "glyphs": list(glyphs),
        "preview": str(preview),
        "recommended_profile": RECOMMENDED_PROFILE,
        "profiles": [
            {**asdict(profile), "font_path": str(profile.font_path), "metrics": evaluate_bitmaps(bitmaps_by_profile[profile.slug])}
            for profile in profiles
        ],
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "report.json"
    markdown_path = args.output_dir / "report.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown_report(payload), encoding="utf-8")
    print(f"preview={preview}")
    print(f"json={json_path}")
    print(f"markdown={markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
