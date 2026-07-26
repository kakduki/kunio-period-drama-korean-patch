#!/usr/bin/env python3
"""Unit checks for the third-party IPS reference analyzer."""

from __future__ import annotations

from analyze_reference_ips import analyze, apply_records, parse_ips


def make_test_rom() -> bytes:
    header = bytearray(b"NES\x1a" + bytes(12))
    header[4] = 1
    header[5] = 1
    return bytes(header) + bytes(0x4000) + bytes(0x2000)


def main() -> int:
    base = bytearray(make_test_rom())
    text_offset = 16 + 0x20
    chr_offset = 16 + 0x4000 + 0x10
    tile_text_offset = 16 + 0x40
    dialogue_text_offset = 16 + 0x80
    base[tile_text_offset - 1] = 0xFF
    base[tile_text_offset + 5] = 0xFF
    base[dialogue_text_offset - 1] = 0x7F
    base[dialogue_text_offset + 11] = 0x7F
    ips = (
        b"PATCH"
        + text_offset.to_bytes(3, "big")
        + (5).to_bytes(2, "big")
        + b"HELLO"
        + chr_offset.to_bytes(3, "big")
        + b"\x00\x00"
        + (3).to_bytes(2, "big")
        + b"\x7f"
        + tile_text_offset.to_bytes(3, "big")
        + (5).to_bytes(2, "big")
        + bytes([0x08, 0x05, 0x0C, 0x0C, 0x0F])
        + dialogue_text_offset.to_bytes(3, "big")
        + (11).to_bytes(2, "big")
        + bytes([0x88, 0x85, 0x8C, 0x8C, 0x8F, 0xFF, 0x97, 0x8F, 0x92, 0x8C, 0x84])
        + b"EOF"
    )

    records, truncate_size = parse_ips(ips)
    if len(records) != 4 or truncate_size is not None:
        print("ERROR: expected four IPS records with no truncation")
        return 1
    if not records[1].rle or records[1].data != b"\x7f\x7f\x7f":
        print("ERROR: RLE record was not decoded")
        return 1

    patched = apply_records(bytes(base), records, truncate_size)
    if patched[text_offset : text_offset + 5] != b"HELLO":
        print("ERROR: text record did not apply")
        return 1

    payload = analyze(bytes(base), ips, "base.nes", "reference.ips")
    changes = payload["changes"]
    if changes["region_changed_bytes"] != {"PRG": 21, "CHR": 3}:
        print(f"ERROR: unexpected region counts {changes['region_changed_bytes']!r}")
        return 1
    runs = payload["new_ascii_runs"]
    if len(runs) != 1 or runs[0]["text"] != "HELLO" or runs[0]["prg_bank"] != 0:
        print(f"ERROR: unexpected ASCII extraction {runs!r}")
        return 1
    tile_runs = payload["english_tile_alpha_runs"]
    if len(tile_runs) != 1 or tile_runs[0]["text"] != "HELLO":
        print(f"ERROR: unexpected English tile-code extraction {tile_runs!r}")
        return 1
    dialogue_runs = payload["english_dialogue_tile_alpha_runs"]
    if len(dialogue_runs) != 1 or dialogue_runs[0]["text"] != "HELLO WORLD":
        print(f"ERROR: unexpected dialogue English tile-code extraction {dialogue_runs!r}")
        return 1

    print("OK: reference IPS parser classifies PRG/CHR changes and extracts new text anchors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
