#!/usr/bin/env python3
"""Render and compare 16x16 Korean dialogue-font candidates."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import itertools
import json
from pathlib import Path

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


def bitmap_bounds(bitmap: list[list[int]]) -> tuple[int, int, int, int] | None:
    points = [
        (x, y)
        for y, row in enumerate(bitmap)
        for x, pixel in enumerate(row)
        if pixel
    ]
    if not points:
        return None
    return (
        min(x for x, _ in points),
        min(y for _, y in points),
        max(x for x, _ in points),
        max(y for _, y in points),
    )


def connected_components(bitmap: list[list[int]]) -> int:
    pending = {
        (x, y)
        for y, row in enumerate(bitmap)
        for x, pixel in enumerate(row)
        if pixel
    }
    count = 0
    while pending:
        count += 1
        frontier = [pending.pop()]
        while frontier:
            x, y = frontier.pop()
            for next_y in range(max(0, y - 1), min(SQUARE_TILE_HEIGHT, y + 2)):
                for next_x in range(max(0, x - 1), min(SQUARE_TILE_WIDTH, x + 2)):
                    point = (next_x, next_y)
                    if point in pending:
                        pending.remove(point)
                        frontier.append(point)
    return count


def bitmap_hamming(left: list[list[int]], right: list[list[int]]) -> int:
    return sum(
        left_pixel != right_pixel
        for left_row, right_row in zip(left, right)
        for left_pixel, right_pixel in zip(left_row, right_row)
    )


def evaluate_bitmaps(bitmaps: dict[str, list[list[int]]]) -> dict[str, object]:
    if not bitmaps:
        raise ValueError("font comparison needs at least one glyph")
    glyph_rows = []
    for glyph, bitmap in bitmaps.items():
        bounds = bitmap_bounds(bitmap)
        ink_pixels = sum(sum(row) for row in bitmap)
        glyph_rows.append(
            {
                "glyph": glyph,
                "ink_pixels": ink_pixels,
                "ink_density": round(ink_pixels / (SQUARE_TILE_WIDTH * SQUARE_TILE_HEIGHT), 4),
                "bounds": bounds,
                "components": connected_components(bitmap),
                "touches_edge": bool(bounds and (0 in bounds or 15 in bounds)),
            }
        )
    pairs = list(itertools.combinations(bitmaps.items(), 2))
    distances = [bitmap_hamming(left, right) for (_, left), (_, right) in pairs]
    duplicate_pairs = [
        f"{left_name}/{right_name}"
        for (left_name, left), (right_name, right) in pairs
        if left == right
    ]
    densities = [float(row["ink_density"]) for row in glyph_rows]
    edge_count = sum(1 for row in glyph_rows if row["touches_edge"])
    min_distance = min(distances) if distances else 0
    return {
        "glyph_count": len(glyph_rows),
        "glyphs": glyph_rows,
        "average_ink_density": round(sum(densities) / len(densities), 4),
        "minimum_ink_density": min(densities),
        "maximum_ink_density": max(densities),
        "minimum_pairwise_hamming": min_distance,
        "duplicate_pairs": duplicate_pairs,
        "edge_touching_glyph_count": edge_count,
        "triage_pass": not duplicate_pairs
        and edge_count == 0
        and min_distance >= 10
        # The colon is intentionally a light two-dot glyph at 16x16.
        and min(densities) >= 0.08
        and max(densities) <= 0.55,
    }


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
