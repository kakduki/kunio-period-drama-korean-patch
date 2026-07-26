#!/usr/bin/env python3
"""Test runtime CHR mapping audit decisions without launching FCEUX."""

from __future__ import annotations

from analyze_reference_ips import parse_ines_layout
from audit_opening_font_runtime_mapping import audit_emitted_tiles


def synthetic_rom() -> bytes:
    data = bytearray(16 + 8 * 0x4000 + 16 * 0x2000)
    data[:4] = b"NES\x1a"
    data[4] = 8
    data[5] = 16
    data[6] = 0x40
    return bytes(data)


def emitted_row(*, source: str, value: str, role: str = "top") -> dict[str, str]:
    return {
        "frame": "650",
        "role": role,
        "address": "7139",
        "value": value,
        "pc": "95AE",
        "y": "00",
        "source_byte": source,
        "mapper_control": "07",
        "mapper_select": "7",
        "ppu_control": "8C",
        "r0": "3C",
        "r1": "3E",
        "r2": "30",
        "r3": "31",
        "r4": "32",
        "r5": "33",
        "r6": "02",
        "r7": "03",
    }


def main() -> int:
    base = synthetic_rom()
    candidate = bytearray(base)
    layout = parse_ines_layout(base)
    bank7_code81 = layout.chr_start + 7 * 0x2000 + 0x181 * 16
    runtime_bank7_codec0 = layout.chr_start + 7 * 0x2000 + 0x1C0 * 16
    wrong_bank7_codec0 = runtime_bank7_codec0 + 16
    candidate[bank7_code81 : bank7_code81 + 16] = b"\xAA" * 16
    candidate[wrong_bank7_codec0 : wrong_bank7_codec0 + 16] = b"\xBB" * 16

    payload = audit_emitted_tiles(
        [
            emitted_row(source="81", value="81"),
            emitted_row(source="C0", value="C0"),
        ],
        source_codes={0x81, 0xC0},
        font_targets={0x81: bank7_code81, 0xC0: wrong_bank7_codec0},
        layout=layout,
        base=base,
        candidate=bytes(candidate),
    )
    assert payload["overall_verdict"] == "FAIL"
    assert payload["pass_count"] == 1
    assert payload["fail_count"] == 1
    failed = next(row for row in payload["audits"] if row["emitted_tile_code"] == "0xC0")
    assert failed["runtime_physical_chr_bank"] == 7
    assert failed["runtime_physical_tile"] == "0x1C0"
    assert failed["target_matches_runtime_slot"] is False
    print("Opening font runtime mapping audit tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
