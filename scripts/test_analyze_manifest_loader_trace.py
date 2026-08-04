#!/usr/bin/env python3
"""Tests for the bounded native manifest loader trace analyzer."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_manifest_loader_trace import analyze_trace, render_markdown  # noqa: E402


def write_fixture(root: Path, status: str = "lua_done") -> None:
    (root / "summary.tsv").write_text(
        "frame\treason\thook_execs\tloader_reads\trecord_reads\tdialogue_id\tpage_state\n"
        f"1900\t{status}\t234\t91\t82\tBA\t00\n",
        encoding="utf-8",
    )
    ids = "\n".join(
        f"{frame}\tdialogue_id\t${value:04X}\t{value:02X}\t${value:04X}\t0000\t00\t00"
        for frame, value in ((646, 0xB7), (1015, 0xB8), (1317, 0xB9), (1623, 0xBA))
    )
    (root / "loader_reads.tsv").write_text(
        "frame\tlabel\taddress\tvalue\tdialogue_id\ttemp_high\ttemp_id\tpage_state\n"
        + ids
        + "\n",
        encoding="utf-8",
    )
    rows = []
    for start, length in ((0x9FB4, 26), (0x9FCE, 11)):
        rows.extend(f"1\tcandidate_record_window\t${address:04X}\t00\t00\t00\t00\t00" for address in range(start, start + length))
    (root / "record_reads.tsv").write_text(
        "frame\tlabel\taddress\tvalue\tdialogue_id\ttemp_high\ttemp_id\tpage_state\n"
        + "\n".join(rows)
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="manifest_trace_test_") as directory:
        root = Path(directory)
        write_fixture(root)
        payload = analyze_trace(root)
        assert payload["status"] == "PASS"
        assert payload["candidate_record_reads"] == 37
        assert "| 182 | `$9FB4` | 26 | 26 | PASS |" in render_markdown(payload)
        candidate = root / "candidate.nes"
        rom = bytearray(0x7000)
        for index, start, length in ((182, 0x9FB4, 26), (185, 0x9FCE, 11)):
            pointer_offset = 0x05DD4 + index * 2
            rom[pointer_offset:pointer_offset + 2] = start.to_bytes(2, "little")
            record_offset = 0x04010 + start - 0x8000
            rom[record_offset:record_offset + length] = bytes([0x81]) * (length - 1) + bytes([0xFF])
        candidate.write_bytes(rom)
        dynamic = analyze_trace(root, candidate, [182, 185])
        assert dynamic["status"] == "PASS"
        write_fixture(root, "target_not_seen")
        assert analyze_trace(root)["status"] == "UNKNOWN"
    print("OK: manifest loader trace analyzer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
