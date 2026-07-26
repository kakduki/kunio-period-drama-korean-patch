#!/usr/bin/env python3
"""Analyze one bounded opening-route MMC3/PPU mapping trace."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path

from rom_utils import REPO_ROOT


DEFAULT_INPUT_DIR = REPO_ROOT / "rom_analysis" / "opening_mapper_trace_capture"
DEFAULT_JSON_OUTPUT = DEFAULT_INPUT_DIR / "analysis.json"
DEFAULT_MARKDOWN_OUTPUT = DEFAULT_INPUT_DIR / "analysis.md"
REFERENCE_CODES = (0x81, 0x9A)
MAPPER_CHR_REGISTER_COUNT = 6


def parse_hex_byte(value: str | None) -> int | None:
    token = (value or "").strip()
    if not token:
        return None
    return int(token, 16)


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"required trace file is missing: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def recurring_write_pcs(rows: list[dict[str, str]], kind: str) -> list[dict[str, object]]:
    counts: Counter[str] = Counter()
    for row in rows:
        if row.get("kind") != kind:
            continue
        pc = (row.get("pc") or "").strip()
        if pc:
            counts[pc] += 1
    return [
        {"pc": f"0x{pc}", "writes": count}
        for pc, count in counts.most_common(12)
    ]


def final_reason(rows: list[dict[str, str]]) -> str | None:
    for row in reversed(rows):
        reason = row.get("reason")
        if reason in {"lua_done", "frame_limit"}:
            return reason
    return None


def resolve_chr_windows(control: int, registers: list[int]) -> list[int]:
    """Return the eight mapped 1 KiB CHR banks for PPU 0000-1FFF."""

    if len(registers) != MAPPER_CHR_REGISTER_COUNT:
        raise ValueError("MMC3 CHR mapping needs registers r0-r5")
    r0, r1, r2, r3, r4, r5 = registers
    pair0 = (r0 & 0xFE, r0 | 0x01)
    pair1 = (r1 & 0xFE, r1 | 0x01)
    if control & 0x80:
        return [r2, r3, r4, r5, *pair0, *pair1]
    return [*pair0, *pair1, r2, r3, r4, r5]


def source_mapping(
    code: int,
    *,
    background_pattern_base: int,
    chr_windows: list[int],
) -> dict[str, object]:
    ppu_address = background_pattern_base + (code * 16)
    window_index = ppu_address // 0x400
    tile_in_window = (ppu_address % 0x400) // 16
    chr_1k_bank = chr_windows[window_index]
    physical_chr_bank = chr_1k_bank // 8
    local_tile = (chr_1k_bank % 8) * 0x40 + tile_in_window
    return {
        "code": f"0x{code:02X}",
        "ppu_pattern_address": f"0x{ppu_address:04X}",
        "ppu_window": f"0x{window_index * 0x400:04X}-0x{window_index * 0x400 + 0x3FF:04X}",
        "chr_1k_bank": chr_1k_bank,
        "physical_chr_8k_bank": physical_chr_bank,
        "physical_tile_in_bank": f"0x{local_tile:03X}",
    }


def analyze(
    input_dir: Path,
    *,
    expected_physical_chr_bank: int = 7,
) -> dict[str, object]:
    summary_rows = read_tsv(input_dir / "summary.tsv")
    snapshot_rows = read_tsv(input_dir / "mapper_snapshot.tsv")
    write_rows = read_tsv(input_dir / "mapper_writes.tsv")
    if not snapshot_rows:
        raise ValueError("mapper snapshot has no capture row")
    snapshot = snapshot_rows[-1]
    control = parse_hex_byte(snapshot.get("mapper_control"))
    ppu_control = parse_hex_byte(snapshot.get("ppu_control"))
    registers = [
        parse_hex_byte(snapshot.get(f"r{index}"))
        for index in range(MAPPER_CHR_REGISTER_COUNT)
    ]
    reason = final_reason(summary_rows)
    incomplete = control is None or ppu_control is None or any(value is None for value in registers)
    callback_counts = {
        "mapper_select": int(snapshot.get("mapper_select_callbacks") or 0),
        "mapper_data": int(snapshot.get("mapper_data_callbacks") or 0),
        "ppu_control": int(snapshot.get("ppu_control_callbacks") or 0),
    }
    recurring_pcs = {
        "mmc3_select": recurring_write_pcs(write_rows, "MMC3_SELECT"),
        "mmc3_data": recurring_write_pcs(write_rows, "MMC3_DATA"),
        "ppu_control": recurring_write_pcs(write_rows, "PPUCTRL"),
    }
    if incomplete:
        return {
            "overall_verdict": "UNKNOWN",
            "reason": reason,
            "capture_frame": int(snapshot["frame"]),
            "callback_counts": callback_counts,
            "missing": {
                "mapper_control": control is None,
                "ppu_control": ppu_control is None,
                "chr_registers": [
                    f"r{index}" for index, value in enumerate(registers) if value is None
                ],
            },
            "recurring_write_pcs": recurring_pcs,
        }

    concrete_registers = [int(value) for value in registers]
    chr_windows = resolve_chr_windows(int(control), concrete_registers)
    background_pattern_base = 0x1000 if int(ppu_control) & 0x10 else 0x0000
    mappings = [
        source_mapping(
            code,
            background_pattern_base=background_pattern_base,
            chr_windows=chr_windows,
        )
        for code in REFERENCE_CODES
    ]
    expected_reference_slots_match = all(
        row["physical_chr_8k_bank"] == expected_physical_chr_bank
        and row["physical_tile_in_bank"] == f"0x{0x100 + int(row['code'], 16):03X}"
        for row in mappings
    )
    verdict = "PASS" if reason == "lua_done" else "UNKNOWN"
    return {
        "overall_verdict": verdict,
        "reason": reason,
        "capture_frame": int(snapshot["frame"]),
        "callback_counts": callback_counts,
        "recurring_write_pcs": recurring_pcs,
        "mapper_control": f"0x{int(control):02X}",
        "chr_mode": 1 if int(control) & 0x80 else 0,
        "ppu_control": f"0x{int(ppu_control):02X}",
        "background_pattern_base": f"0x{background_pattern_base:04X}",
        "chr_registers": [f"0x{value:02X}" for value in concrete_registers],
        "chr_1k_windows": [
            {
                "ppu_window": f"0x{index * 0x400:04X}-0x{index * 0x400 + 0x3FF:04X}",
                "chr_1k_bank": bank,
                "physical_chr_8k_bank": bank // 8,
            }
            for index, bank in enumerate(chr_windows)
        ],
        "reference_code_mappings": mappings,
        "expected_physical_chr_8k_bank": expected_physical_chr_bank,
        "expected_reference_slots_match": expected_reference_slots_match,
    }


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Opening MMC3/PPU Mapping Trace",
        "",
        f"Status: {payload['overall_verdict']}",
        "",
        f"- Final Lua reason: {payload.get('reason')}",
        f"- Capture frame: {payload['capture_frame']}",
        f"- Callback counts: {payload['callback_counts']}",
    ]
    if payload["overall_verdict"] == "UNKNOWN":
        lines += [
            "",
            "The bounded route completed without enough mapper/PPU state to map the",
            "dialogue font. This does not authorize a CHR-page decision.",
            f"- Missing state: {payload['missing']}",
            "",
        ]
        return "\n".join(lines)

    lines += [
        "",
        "## Recurring Writer PCs",
        "",
        "These are CPU program-counter samples taken at register writes. They identify",
        "candidate mapper-update routines; they do not by themselves authorize a hook.",
        "",
        "| write kind | CPU PC | writes |",
        "| --- | --- | ---: |",
    ]
    for kind, rows in payload["recurring_write_pcs"].items():
        label = kind.replace("_", " ")
        if not rows:
            lines.append(f"| {label} | unavailable | 0 |")
            continue
        for row in rows:
            lines.append(f"| {label} | {row['pc']} | {row['writes']} |")

    lines += [
        f"- MMC3 control: {payload['mapper_control']}; CHR mode: {payload['chr_mode']}",
        f"- PPUCTRL: {payload['ppu_control']}; background pattern base: {payload['background_pattern_base']}",
        "- Reference slots 0x81 and 0x9A match expected Bank "
        f"{payload['expected_physical_chr_8k_bank']} physical tiles: "
        f"{payload['expected_reference_slots_match']}",
        "",
        "## CHR Windows",
        "",
        "| PPU window | 1 KiB CHR bank | physical 8 KiB CHR bank |",
        "| --- | ---: | ---: |",
    ]
    for row in payload["chr_1k_windows"]:
        lines.append(
            f"| {row['ppu_window']} | {row['chr_1k_bank']} | {row['physical_chr_8k_bank']} |"
        )
    lines += [
        "",
        "## Reference Dialogue Codes",
        "",
        "| code | PPU pattern address | PPU window | 1 KiB CHR bank | physical Bank/tile |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for row in payload["reference_code_mappings"]:
        lines.append(
            f"| {row['code']} | {row['ppu_pattern_address']} | {row['ppu_window']} | "
            f"{row['chr_1k_bank']} | Bank {row['physical_chr_8k_bank']}, tile {row['physical_tile_in_bank']} |"
        )
    lines += [
        "",
        "This proves the opening screen's mapped CHR state only. A different scene",
        "or a new font page still requires its own mapper-state evidence.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    parser.add_argument("--expected-physical-chr-bank", type=int, default=7)
    args = parser.parse_args()

    payload = analyze(
        args.input_dir,
        expected_physical_chr_bank=args.expected_physical_chr_bank,
    )
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")
    args.json_output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"overall_verdict={payload['overall_verdict']}")
    print(f"json={args.json_output}")
    print(f"markdown={args.markdown_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
