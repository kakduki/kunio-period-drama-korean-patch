#!/usr/bin/env python3
"""Test the dependency-free Korean 16x16 font-comparison metrics."""

from __future__ import annotations

from audit_korean_square_font import evaluate_bitmaps


def glyph(points: tuple[tuple[int, int], ...]) -> list[list[int]]:
    bitmap = [[0] * 16 for _ in range(16)]
    for x, y in points:
        bitmap[y][x] = 1
    return bitmap


def main() -> int:
    metrics = evaluate_bitmaps(
        {
            "가": glyph(((2, 2), (3, 3), (4, 4))),
            "나": glyph(((10, 10), (11, 11), (12, 12))),
        }
    )
    assert metrics["glyph_count"] == 2
    assert metrics["duplicate_pairs"] == []
    assert metrics["edge_touching_glyph_count"] == 0
    assert metrics["minimum_pairwise_hamming"] == 6
    duplicate = evaluate_bitmaps({"가": glyph(((2, 2),)), "나": glyph(((2, 2),))})
    assert duplicate["duplicate_pairs"] == ["가/나"]
    print("Korean 16x16 font comparison tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
