#!/usr/bin/env python3
"""Verify the bounded FCEUX byte path for the Items title and NONE rows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_items_title_none_korean_candidate import (
    NAME_BYTES,
    NAME_PPU_BYTES,
    NONE_BYTES,
    TITLE_BYTES,
)


def parse_hex(value: str) -> bytes:
    return bytes.fromhex(value.replace(" ", ""))


def load_rows(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if not lines:
        return []
    header = lines[0].split("\t")
    return [dict(zip(header, line.split("\t"), strict=False)) for line in lines[1:] if line.strip()]


def contiguous_values(rows: list[dict[str, str]], frame: int, start: int, length: int, pc: str | None = None) -> bytes:
    selected = {
        int(row["cpu_address"], 16): parse_hex(row["value"])
        for row in rows
        if int(row.get("frame", -1)) == frame
        and (pc is None or row.get("pc", "").upper() == pc)
        and start <= int(row["cpu_address"], 16) < start + length
    }
    values = []
    for address in range(start, start + length):
        if address not in selected or len(selected[address]) != 1:
            return b""
        values.append(selected[address][0])
    return bytes(values)


def first_frame_with(rows: list[dict[str, str]], start: int, expected: bytes, pc: str | None = None) -> int | None:
    frames = sorted({int(row.get("frame", -1)) for row in rows})
    for frame in frames:
        if contiguous_values(rows, frame, start, len(expected), pc) == expected:
            return frame
    return None


def verify(candidate: Path, capture_dir: Path) -> dict[str, object]:
    rom = candidate.read_bytes()
    source_checks = {
        "name_prg_seed": (0x00561B, NAME_BYTES),
        "name_ppu_seed": (0x3FB32, NAME_PPU_BYTES),
        "title_suffix": (0x136F4, TITLE_BYTES),
        "none": (0x0FC31, NONE_BYTES),
    }
    source_results = {
        owner: rom[offset : offset + len(expected)] == expected
        for owner, (offset, expected) in source_checks.items()
    }
    queue_path = capture_dir / "queue_writes.tsv"
    rows = load_rows(queue_path)
    name_frame = first_frame_with(rows, 0x60A8, bytes([0x20, 0x21, 0x22, 0x7A, 0x7A]))
    title_frame = first_frame_with(
        rows,
        0x60AD,
        bytes([0x36, 0x23, 0x7A, 0x24, 0x25, 0x7A, 0x7A, 0x7A, 0x7A, 0x7A, 0x7A, 0xFF]),
        "E888",
    )
    none_frame = first_frame_with(rows, 0x6506, NONE_BYTES, "BC16")
    summary_path = capture_dir / "summary.tsv"
    summary_text = summary_path.read_text(encoding="utf-8", errors="replace") if summary_path.is_file() else ""
    capture_completed = "	lua_done	" in summary_text
    payload = {
        "candidate": str(candidate),
        "capture_dir": str(capture_dir),
        "capture_completed": capture_completed,
        "source_checks": source_results,
        "source_bytes_pass": all(source_results.values()),
        "queue_frames": {
            "name": name_frame,
            "title_suffix": title_frame,
            "none": none_frame,
        },
        "queue_title_none_pass": title_frame is not None and none_frame is not None,
        "runtime_byte_gate": capture_completed and all(source_results.values()) and name_frame is not None and title_frame is not None and none_frame is not None,
        "visual_gate": "UNKNOWN_NATIVE_GDSCREENSHOT_TRANSPARENT",
        "status": "PASS_BYTE_PROOF_VISUAL_UNKNOWN" if capture_completed and all(source_results.values()) and name_frame is not None and title_frame is not None and none_frame is not None else "FAIL_OR_UNKNOWN",
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    payload = verify(args.candidate.resolve(), args.capture_dir.resolve())
    if args.report:
        args.report.resolve().write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["runtime_byte_gate"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
