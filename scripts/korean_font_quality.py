#!/usr/bin/env python3
"""Deterministic quality checks for native 16x16 Korean tile glyphs.

These checks are deliberately conservative. They keep a new screen candidate
from silently using the old compressed profile, an edge-clipped glyph set, or
an unapproved source font. Native FCEUX screenshots are still required for
screen promotion; this module only validates the glyph asset before ROM bytes
are generated.
"""

from __future__ import annotations

import itertools
from pathlib import Path

from korean_tile_font import (
    SQUARE_TILE_HEIGHT,
    SQUARE_TILE_WIDTH,
    normalize_glyph_to_square_bitmap,
    square_font_profile,
)


RELEASE_FONT_PROFILE = "readable"
RELEASE_FONT_BASENAME = "malgunbd.ttf"
MINIMUM_INK_DENSITY = 0.08
MAXIMUM_INK_DENSITY = 0.55
MINIMUM_PAIRWISE_HAMMING = 10


def _validate_bitmap(bitmap: list[list[int]]) -> None:
    if len(bitmap) != SQUARE_TILE_HEIGHT or any(
        len(row) != SQUARE_TILE_WIDTH for row in bitmap
    ):
        raise ValueError("expected a 16x16 Korean square bitmap")
    if any(pixel not in (0, 1) for row in bitmap for pixel in row):
        raise ValueError("Korean square bitmap pixels must be 0 or 1")


def bitmap_bounds(bitmap: list[list[int]]) -> tuple[int, int, int, int] | None:
    _validate_bitmap(bitmap)
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
    _validate_bitmap(bitmap)
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
    _validate_bitmap(left)
    _validate_bitmap(right)
    return sum(
        left_pixel != right_pixel
        for left_row, right_row in zip(left, right)
        for left_pixel, right_pixel in zip(left_row, right_row)
    )


def evaluate_square_bitmaps(bitmaps: dict[str, list[list[int]]]) -> dict[str, object]:
    """Return stable glyph metrics shared by audit and candidate builders."""

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
                "ink_density": round(
                    ink_pixels / (SQUARE_TILE_WIDTH * SQUARE_TILE_HEIGHT), 4
                ),
                "bounds": bounds,
                "components": connected_components(bitmap),
                "touches_edge": bool(
                    bounds
                    and (
                        0 in bounds
                        or SQUARE_TILE_WIDTH - 1 in bounds
                        or SQUARE_TILE_HEIGHT - 1 in bounds
                    )
                ),
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
        and min_distance >= MINIMUM_PAIRWISE_HAMMING
        # A colon is intentionally a light two-dot glyph at 16x16.
        and min(densities) >= MINIMUM_INK_DENSITY
        and max(densities) <= MAXIMUM_INK_DENSITY,
    }


def render_square_glyph_bitmaps(
    font_path: str | Path,
    glyphs: tuple[str, ...],
    *,
    font_profile: str,
) -> dict[str, list[list[int]]]:
    """Rasterize one screen candidate's unique glyphs using its profile."""

    if not glyphs or len(set(glyphs)) != len(glyphs):
        raise ValueError("glyph-quality rendering needs a non-empty unique glyph list")
    settings = square_font_profile(font_profile)
    return {
        glyph: normalize_glyph_to_square_bitmap(
            glyph,
            font_path=font_path,
            target_pixels=int(settings["target_pixels"]),
            threshold=int(settings["threshold"]),
            resample=str(settings["resample"]),
        )
        for glyph in glyphs
    }


def evaluate_release_square_font(
    *,
    font_path: str | Path,
    font_profile: str,
    bitmaps: dict[str, list[list[int]]],
) -> dict[str, object]:
    """Apply the standard developer gate used by new 16x16 screen builds."""

    metrics = evaluate_square_bitmaps(bitmaps)
    actual_basename = Path(font_path).name.lower()
    checks = {
        "profile_is_readable": font_profile == RELEASE_FONT_PROFILE,
        "font_is_malgun_bold": actual_basename == RELEASE_FONT_BASENAME,
        "no_duplicate_glyphs": not metrics["duplicate_pairs"],
        "no_edge_touching_glyphs": metrics["edge_touching_glyph_count"] == 0,
        "minimum_pairwise_hamming": (
            metrics["minimum_pairwise_hamming"] >= MINIMUM_PAIRWISE_HAMMING
        ),
        "minimum_ink_density": metrics["minimum_ink_density"] >= MINIMUM_INK_DENSITY,
        "maximum_ink_density": metrics["maximum_ink_density"] <= MAXIMUM_INK_DENSITY,
    }
    return {
        "verdict": "PASS" if all(checks.values()) else "FAIL",
        "font_path": str(font_path),
        "font_profile": font_profile,
        "requirements": {
            "font_basename": RELEASE_FONT_BASENAME,
            "font_profile": RELEASE_FONT_PROFILE,
            "minimum_ink_density": MINIMUM_INK_DENSITY,
            "maximum_ink_density": MAXIMUM_INK_DENSITY,
            "minimum_pairwise_hamming": MINIMUM_PAIRWISE_HAMMING,
            "edge_touching_glyph_count": 0,
        },
        "checks": checks,
        "metrics": metrics,
    }
