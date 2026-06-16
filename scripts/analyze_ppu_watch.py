#!/usr/bin/env python3
"""Analyze FCEUX PPU write watch output (ppu_writes.tsv).

Looks for repeated byte sequences in nametable area writes during phase 2
(menu navigation). These sequences likely correspond to menu text tiles.

Cross-references against known expected_bytes from bank1_watch_targets.json
to see if any tile writes match the text encoding bytes we expect.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT  = ROOT / "rom_analysis" / "fceux_ppu_watch"
DEFAULT_OUTPUT = ROOT / "rom_analysis" / "fceux_ppu_watch" / "analysis.md"
TARGETS_PATH   = ROOT / "rom_analysis" / "bank1_watch_targets.json"


@dataclass
class PpuWrite:
    frame: int
    vram_addr: str
    byte: int
    phase: int
    nt: int
    tile_row: int
    tile_col: int


def load_writes(input_dir: Path) -> list[PpuWrite]:
    path = input_dir / "ppu_writes.tsv"
    if not path.exists():
        return []
    writes: list[PpuWrite] = []
    for row in csv.DictReader(path.open(encoding="utf-8"), delimiter="\t"):
        try:
            writes.append(PpuWrite(
                frame=int(row["frame"]),
                vram_addr=row["vram_addr"],
                byte=int(row["byte"], 16),
                phase=int(row["phase"]),
                nt=int(row["nt"]),
                tile_row=int(row["tile_row"]),
                tile_col=int(row["tile_col"]),
            ))
        except (KeyError, ValueError):
            continue
    return writes


def load_expected_bytes(targets_path: Path) -> dict[str, list[int]]:
    """label → list of expected byte values."""
    if not targets_path.exists():
        return {}
    data = json.loads(targets_path.read_text(encoding="utf-8"))
    result: dict[str, list[int]] = {}
    for t in data.get("targets", []):
        label = t.get("label", "")
        eb    = t.get("expected_bytes", "")
        if eb:
            result[label] = [int(x, 16) for x in eb.split()]
    return result


def find_runs(writes: list[PpuWrite]) -> list[tuple[int, int, list[int]]]:
    """Find consecutive same-address runs: (start_frame, vram_base, bytes)."""
    if not writes:
        return []
    runs: list[tuple[int, int, list[int]]] = []
    cur_base = int(writes[0].vram_addr.lstrip("$"), 16)
    cur_frame = writes[0].frame
    cur_bytes: list[int] = [writes[0].byte]

    for w in writes[1:]:
        addr = int(w.vram_addr.lstrip("$"), 16)
        expected_next = (cur_base + len(cur_bytes)) % 0x4000
        if addr == expected_next and w.frame == cur_frame:
            cur_bytes.append(w.byte)
        else:
            if len(cur_bytes) >= 2:
                runs.append((cur_frame, cur_base, cur_bytes))
            cur_base  = addr
            cur_frame = w.frame
            cur_bytes = [w.byte]

    if len(cur_bytes) >= 2:
        runs.append((cur_frame, cur_base, cur_bytes))
    return runs


def bytes_as_hex(b: list[int]) -> str:
    return " ".join(f"{x:02X}" for x in b)


def check_pattern_match(run_bytes: list[int], expected: list[int]) -> bool:
    if len(expected) == 0 or len(run_bytes) < len(expected):
        return False
    for i in range(len(run_bytes) - len(expected) + 1):
        if run_bytes[i:i+len(expected)] == expected:
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT))
    parser.add_argument("--output",    default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser().resolve()
    output    = Path(args.output).expanduser().resolve()

    writes = load_writes(input_dir)
    if not writes:
        print(f"No ppu_writes.tsv found in {input_dir}")
        return 1

    expected_map = load_expected_bytes(TARGETS_PATH)
    # flat list of all expected byte sequences (deduplicated)
    all_expected: list[tuple[str, list[int]]] = [
        (lbl, eb) for lbl, eb in expected_map.items()
    ]

    # Split by phase
    by_phase: dict[int, list[PpuWrite]] = defaultdict(list)
    for w in writes:
        by_phase[w.phase].append(w)

    # Per-address byte frequency (phase 2 only — menu)
    phase2_writes = by_phase.get(2, [])
    addr_bytes: dict[str, Counter] = defaultdict(Counter)
    for w in phase2_writes:
        addr_bytes[w.vram_addr][w.byte] += 1

    # Top written addresses in phase 2
    addr_total = {addr: sum(cnt.values()) for addr, cnt in addr_bytes.items()}
    top_addrs = sorted(addr_total, key=lambda a: -addr_total[a])[:30]

    # Consecutive run analysis (all phases)
    all_runs = find_runs(writes)
    phase2_runs = [(f, b, bs) for f, b, bs in all_runs
                   if any(w.frame == f and w.phase == 2 for w in phase2_writes)]

    # Check runs against expected bytes
    matched_runs: list[tuple[int, int, list[int], str]] = []
    for (frame, base, run_bytes) in all_runs:
        for lbl, eb in all_expected:
            if check_pattern_match(run_bytes, eb):
                matched_runs.append((frame, base, run_bytes, lbl))

    # Unique byte sequence frequency in phase 2
    seq_counter: Counter = Counter()
    for _, _, run_bytes in all_runs:
        seq_counter[bytes_as_hex(run_bytes)] += 1
    top_seqs = seq_counter.most_common(20)

    # Write markdown
    lines = [
        "# PPU Write Watch Analysis",
        "",
        f"Input: `{input_dir.relative_to(ROOT) if input_dir.is_relative_to(ROOT) else input_dir}`",
        "",
        f"- Total nametable writes: **{len(writes)}**",
        f"- Phase 1 writes: {len(by_phase.get(1, []))}",
        f"- Phase 2 writes (menu): **{len(phase2_writes)}**",
        f"- Phase 3 writes: {len(by_phase.get(3, []))}",
        "",
        "## Matched runs (expected text bytes found in PPU writes)",
        "",
    ]
    if matched_runs:
        lines += [
            "| frame | vram_addr | run_bytes | matched_label |",
            "| --- | --- | --- | --- |",
        ]
        for frame, base, run_bytes, lbl in matched_runs[:50]:
            lines.append(
                f"| {frame} | `${base:04X}` | `{bytes_as_hex(run_bytes)}` | `{lbl}` |"
            )
    else:
        lines.append("_No exact matches found between PPU writes and expected text bytes._")

    lines += [
        "",
        "## Top nametable addresses written (phase 2 — menu)",
        "",
        "| vram_addr | total_writes | top_bytes |",
        "| --- | ---: | --- |",
    ]
    for addr in top_addrs:
        cnt = addr_bytes[addr]
        top_b = ", ".join(f"`{b:02X}`×{n}" for b, n in cnt.most_common(5))
        lines.append(f"| `{addr}` | {addr_total[addr]} | {top_b} |")

    lines += [
        "",
        "## Top repeated byte sequences (all phases, min length 2)",
        "",
        "| sequence | count |",
        "| --- | ---: |",
    ]
    for seq, cnt in top_seqs:
        lines.append(f"| `{seq}` | {cnt} |")

    lines += [
        "",
        "## Phase 2 consecutive write runs (first 40)",
        "",
        "| frame | vram_base | length | bytes |",
        "| --- | --- | ---: | --- |",
    ]
    shown = 0
    for frame, base, run_bytes in all_runs:
        phase = next((w.phase for w in writes if w.frame == frame), 0)
        if phase != 2:
            continue
        lines.append(
            f"| {frame} | `${base:04X}` | {len(run_bytes)} | `{bytes_as_hex(run_bytes[:16])}"
            f"{'...' if len(run_bytes) > 16 else ''}` |"
        )
        shown += 1
        if shown >= 40:
            break

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Written: {output}")
    print(f"total_writes={len(writes)}  phase2={len(phase2_writes)}  matched_runs={len(matched_runs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
