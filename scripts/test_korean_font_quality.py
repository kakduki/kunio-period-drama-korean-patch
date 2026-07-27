#!/usr/bin/env python3
"""Focused checks for the reusable Korean 16x16 font-quality gate."""

from __future__ import annotations

from korean_font_quality import evaluate_release_square_font, evaluate_square_bitmaps


def block(left: int, top: int) -> list[list[int]]:
    bitmap = [[0] * 16 for _ in range(16)]
    for y in range(top, top + 5):
        for x in range(left, left + 5):
            bitmap[y][x] = 1
    return bitmap


def main() -> int:
    left = block(2, 2)
    right = block(9, 9)
    metrics = evaluate_square_bitmaps({"left": left, "right": right})
    assert metrics["triage_pass"] is True
    assert metrics["minimum_pairwise_hamming"] == 50

    passed = evaluate_release_square_font(
        font_path=r"C:\Windows\Fonts\malgunbd.ttf",
        font_profile="readable",
        bitmaps={"left": left, "right": right},
    )
    assert passed["verdict"] == "PASS"

    wrong_font = evaluate_release_square_font(
        font_path=r"C:\Windows\Fonts\gulim.ttc",
        font_profile="readable",
        bitmaps={"left": left, "right": right},
    )
    assert wrong_font["verdict"] == "FAIL"
    assert wrong_font["checks"]["font_is_malgun_bold"] is False

    duplicate = evaluate_square_bitmaps({"left": left, "copy": left})
    assert duplicate["triage_pass"] is False
    assert duplicate["duplicate_pairs"] == ["left/copy"]
    print("Korean 16x16 font-quality gate tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
