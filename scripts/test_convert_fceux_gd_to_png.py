#!/usr/bin/env python3
"""Tests for the FCEUX GD to PNG converter."""

from __future__ import annotations

from convert_fceux_gd_to_png import PNG_SIGNATURE, gd_pixels_to_png_rgb, parse_gd_truecolor


def test_parse_truecolor_header() -> None:
    gd = b"\xff\xfe" + b"\x00\x02\x00\x01\x01" + b"\xff\xff\xff\xff"
    gd += bytes([0, 1, 2, 3, 0, 4, 5, 6])
    width, height, pixels = parse_gd_truecolor(gd)

    assert width == 2
    assert height == 1
    assert pixels == bytes([0, 1, 2, 3, 0, 4, 5, 6])


def test_png_dimensions_are_written() -> None:
    png = gd_pixels_to_png_rgb(2, 1, bytes([0, 1, 2, 3, 0, 4, 5, 6]))

    assert png.startswith(PNG_SIGNATURE)
    assert png[16:24] == b"\x00\x00\x00\x02\x00\x00\x00\x01"


if __name__ == "__main__":
    test_parse_truecolor_header()
    test_png_dimensions_are_written()
