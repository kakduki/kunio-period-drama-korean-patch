#!/usr/bin/env python3
"""Analyze FCEUX PPU write logs by reconstructing frame nametables.

The original PPU watch analyzer grouped only same-frame +1-address runs, which
misses text that is written across frames, interleaved with other writes, or
using vertical VRAM increments. This version rebuilds each frame's final
nametable writes and scans fill-stripped, address-ordered streams.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "rom_analysis" / "fceux_ppu_watch"
DEFAULT_OUTPUT = ROOT / "rom_analysis" / "fceux_ppu_watch" / "analysis_v2.md"
TILEMAP_PATH = ROOT / "rom_analysis" / "chr_bank07_tile_map.json"
TARGETS_PATH = ROOT / "rom_analysis" / "bank1_watch_targets.json"

DEFAULT_FILL_TILES = {0x00, 0x7A}


def load_decode(path: Path) -> dict[int, str]:
    if not path.exists():
        return {}
    tilemap = json.loads(path.read_text(encoding="utf-8"))
    decoded: dict[int, str] = {}
    for entry in tilemap.get("entries", []):
        prg_value = entry.get("prg_plus_0x7a_byte")
        glyph = entry.get("glyph")
        if prg_value is not None and glyph is not None:
            decoded[int(prg_value, 16)] = glyph
    return decoded


def parse_bytes(text: str) -> list[int]:
    return [int(byte, 16) for byte in text.split() if byte]


def load_targets(path: Path) -> list[tuple[str, list[int]]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    targets: list[tuple[str, list[int]]] = []
    target_rows = list(data.get("targets", []))
    for strategy, rows in data.get("targets_by_strategy", {}).items():
        for row in rows:
            target = dict(row)
            target.setdefault("strategy", strategy)
            target_rows.append(target)

    for target in target_rows:
        expected = (
            target.get("expected_bytes")
            or target.get("expected_patched_bytes")
            or target.get("patched_bytes")
            or ""
        )
        if expected:
            strategy = target.get("strategy")
            label = target.get("label", "?")
            if strategy and not str(label).startswith(f"{strategy}:"):
                label = f"{strategy}:{label}"
            targets.append((
                label,
                parse_bytes(expected),
            ))
    return targets


def load_frames(input_dir: Path) -> tuple[dict[int, dict[int, int]], dict[int, int]]:
    path = input_dir / "ppu_writes.tsv"
    frames: dict[int, dict[int, int]] = defaultdict(dict)
    phases: dict[int, int] = {}
    for row in csv.DictReader(path.open(encoding="utf-8"), delimiter="\t"):
        try:
            frame = int(row["frame"])
            vram_addr = int(row["vram_addr"].lstrip("$"), 16)
            byte = int(row["byte"], 16)
            phase = int(row["phase"])
        except (KeyError, ValueError):
            continue
        if not 0x2000 <= vram_addr < 0x3000:
            continue
        if (vram_addr & 0x3FF) >= 0x3C0:
            continue
        frames[frame][vram_addr] = byte
        phases[frame] = phase
    return frames, phases


def parse_fill_tiles(text: str) -> set[int]:
    if not text.strip():
        return set()
    return {int(byte.strip(), 16) for byte in text.split(",") if byte.strip()}


def runs_from_nametable(nametable: dict[int, int], fill_tiles: set[int]) -> list[list[int]]:
    runs: list[list[int]] = []
    run: list[int] = []
    for addr in sorted(nametable):
        if nametable[addr] in fill_tiles:
            if run:
                runs.append(run)
                run = []
            continue
        if run and addr == run[-1] + 1:
            run.append(addr)
        else:
            if run:
                runs.append(run)
            run = [addr]
    if run:
        runs.append(run)
    return [run for run in runs if len(run) >= 2]


def contains(stream: list[int], sequence: list[int]) -> bool:
    if not sequence or len(stream) < len(sequence):
        return False
    seq_len = len(sequence)
    for index in range(len(stream) - seq_len + 1):
        if stream[index:index + seq_len] == sequence:
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--targets", default=str(TARGETS_PATH), help="JSON target file; supports bank1_watch_targets or v04 target JSON.")
    parser.add_argument(
        "--fill-tiles",
        default="00,7A",
        help="Comma-separated byte values to strip from reconstructed streams. Use an empty string with --no-strip-fill.",
    )
    parser.add_argument(
        "--no-strip-fill",
        action="store_true",
        help="Do not strip fill/padding bytes before matching. Useful for padding strategy experiments.",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    targets_path = Path(args.targets).expanduser()
    if not targets_path.is_absolute():
        targets_path = ROOT / targets_path
    targets_path = targets_path.resolve()

    decoded = load_decode(TILEMAP_PATH)
    targets = load_targets(targets_path)
    frames, phases = load_frames(input_dir)
    fill_tiles = set() if args.no_strip_fill else parse_fill_tiles(args.fill_tiles)

    phase_streams: dict[int, list[int]] = defaultdict(list)
    for frame in sorted(frames):
        phase = phases.get(frame, 0)
        for addr in sorted(frames[frame]):
            byte = frames[frame][addr]
            if byte not in fill_tiles:
                phase_streams[phase].append(byte)

    matches: list[tuple[int, str, list[int]]] = []
    seen: set[tuple[int, str, tuple[int, ...]]] = set()
    sequence_counts = Counter(tuple(expected) for _, expected in targets)
    for phase, stream in phase_streams.items():
        for label, expected in targets:
            key = (phase, label, tuple(expected))
            if key not in seen and contains(stream, expected):
                matches.append((phase, label, expected))
                seen.add(key)

    best_frame = max(
        frames,
        key=lambda frame: sum(1 for byte in frames[frame].values() if byte not in fill_tiles),
        default=None,
    )

    lines = [
        "# PPU Write Watch Analysis v2",
        "",
        f"Input: `{input_dir.relative_to(ROOT) if input_dir.is_relative_to(ROOT) else input_dir}`",
        f"Targets: `{targets_path.relative_to(ROOT) if targets_path.is_relative_to(ROOT) else targets_path}`",
        "",
        f"- Frames captured: **{len(frames)}**",
        f"- Targets loaded: **{len(targets)}**",
        f"- Unique target byte sequences: **{len(sequence_counts)}**",
        f"- Decode glyphs: **{len(decoded)}**",
        f"- Fill tiles stripped: **{', '.join(f'0x{byte:02X}' for byte in sorted(fill_tiles)) if fill_tiles else 'none'}**",
        "",
        "## Matched Targets",
        "",
    ]
    if matches:
        lines += ["| phase | label | expected_bytes |", "| ---: | --- | --- |"]
        for phase, label, expected in matches:
            bytes_hex = " ".join(f"{byte:02X}" for byte in expected)
            lines.append(f"| {phase} | `{label}` | `{bytes_hex}` |")
    else:
        lines.append("_No expected byte sequences found in the reconstructed streams._")
    lines += ["", f"**Matched: {len(matches)} / {len(targets)}**", ""]

    duplicate_matches = [
        (phase, label, expected)
        for phase, label, expected in matches
        if sequence_counts[tuple(expected)] > 1
    ]
    if duplicate_matches:
        lines += [
            "## Ambiguity Notes",
            "",
            "- Some matched targets share the same byte sequence. A PPU stream match proves that byte sequence was written, but does not by itself distinguish which ROM offset produced it.",
            "",
            "| byte sequence | matched labels |",
            "| --- | --- |",
        ]
        by_sequence: dict[tuple[int, ...], list[str]] = defaultdict(list)
        for _, label, expected in duplicate_matches:
            by_sequence[tuple(expected)].append(label)
        for sequence, labels in sorted(by_sequence.items()):
            bytes_hex = " ".join(f"{byte:02X}" for byte in sequence)
            label_text = ", ".join(f"`{label}`" for label in sorted(labels))
            lines.append(f"| `{bytes_hex}` | {label_text} |")
        lines.append("")

    if best_frame is not None:
        lines += [
            f"## Representative Screen: Frame {best_frame}",
            "",
            "| vram_base | len | decoded |",
            "| --- | ---: | --- |",
        ]
        nametable = frames[best_frame]
        for run in runs_from_nametable(nametable, fill_tiles):
            text = "".join(decoded.get(nametable[addr], f"<{nametable[addr]:02X}>") for addr in run)
            lines.append(f"| `${run[0]:04X}` | {len(run)} | {text} |")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Written: {output}")
    print(f"frames={len(frames)} matched={len(matches)}/{len(targets)} best_frame={best_frame}")
    for phase, label, expected in matches:
        print(f"  MATCH phase{phase} {label}: {' '.join(f'{byte:02X}' for byte in expected)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
