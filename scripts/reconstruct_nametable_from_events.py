"""Reconstruct nametable tile grids from FCEUX Lua PPU events.

The FCEUX Lua dump records each $2007 write with a tracked PPU address. This
script applies those writes in order and emits 32x30 nametable grids for the
frames most likely to contain text/UI rendering.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LUA_DIR = ROOT / "rom_analysis" / "fceux_lua"
DEFAULT_OUT = ROOT / "rom_analysis" / "fceux_lua_nametable_reconstruction.md"
DEFAULT_FRAMES = [22, 23, 24, 25, 26, 27, 313, 314, 315, 316, 317, 318, 339, 341, 343, 345, 347, 349, 351, 353, 355, 357, 359, 361]


def read_events(path: Path) -> dict[int, list[tuple[str, int, int]]]:
    by_frame: dict[int, list[tuple[str, int, int]]] = defaultdict(list)
    with path.open("r", encoding="utf-8", errors="replace") as f:
        next(f, None)
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 5:
                continue
            frame_s, kind, _cpu_addr, value_s, ppu_addr_s = parts
            by_frame[int(frame_s)].append((kind, int(value_s, 16), int(ppu_addr_s, 16) % 0x4000))
    return by_frame


def is_tile_addr(addr: int) -> bool:
    return 0x2000 <= addr <= 0x23BF


def row_col(addr: int) -> tuple[int, int]:
    offset = addr - 0x2000
    return offset // 32, offset % 32


def format_grid(grid: list[int | None]) -> list[str]:
    rows = []
    for row in range(30):
        values = []
        for col in range(32):
            value = grid[row * 32 + col]
            values.append("__" if value is None else f"{value:02X}")
        rows.append(f"{row:02d}: " + " ".join(values))
    return rows


def format_overlay(changed: dict[int, int]) -> list[str]:
    rows = []
    for row in range(30):
        values = []
        any_changed = False
        for col in range(32):
            idx = row * 32 + col
            if idx in changed:
                values.append(f"{changed[idx]:02X}")
                any_changed = True
            else:
                values.append("..")
        if any_changed:
            rows.append(f"{row:02d}: " + " ".join(values))
    return rows


def frame_stats(changed: dict[int, int]) -> str:
    if not changed:
        return "no tile writes"
    rows = sorted({idx // 32 for idx in changed})
    cols = sorted({idx % 32 for idx in changed})
    nonzero = sum(1 for value in changed.values() if value != 0)
    return (
        f"{len(changed)} cells, {nonzero} non-zero, "
        f"rows {rows[0]}-{rows[-1]}, cols {cols[0]}-{cols[-1]}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, default=LUA_DIR / "events.tsv")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--frames",
        nargs="*",
        type=int,
        default=DEFAULT_FRAMES,
        help="Frames to snapshot after applying that frame's events.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    events = read_events(args.events)
    wanted = set(args.frames)
    max_frame = max(max(events), max(wanted))

    grid: list[int | None] = [None] * (32 * 30)
    snapshots: dict[int, tuple[list[int | None], dict[int, int]]] = {}

    for frame in range(max_frame + 1):
        changed: dict[int, int] = {}
        for kind, value, addr in events.get(frame, []):
            if kind != "PPUDATA" or not is_tile_addr(addr):
                continue
            row, col = row_col(addr)
            idx = row * 32 + col
            grid[idx] = value
            changed[idx] = value
        if frame in wanted:
            snapshots[frame] = (list(grid), dict(changed))

    lines: list[str] = []
    lines.append("# FCEUX Lua nametable reconstruction")
    lines.append("")
    try:
        rel_events = args.events.resolve().relative_to(ROOT)
    except ValueError:
        rel_events = args.events
    lines.append(f"Generated from `$2007` events in `{rel_events}`.")
    lines.append("Rows are NES nametable tile rows, 32 tiles wide. `__` means unknown/unwritten in the cumulative grid; `..` means unchanged in the per-frame overlay.")
    lines.append("")

    lines.append("## Snapshot index")
    lines.append("")
    lines.append("| frame | changed cells | note |")
    lines.append("| ---: | --- | --- |")
    for frame in args.frames:
        _grid, changed = snapshots.get(frame, ([None] * (32 * 30), {}))
        note = ""
        if 313 <= frame <= 318:
            note = "main text/UI composition cluster"
        elif 22 <= frame <= 27:
            note = "early screen composition cluster"
        elif 339 <= frame <= 361:
            note = "small rolling text/menu updates"
        lines.append(f"| {frame} | {frame_stats(changed)} | {note} |")

    for frame in args.frames:
        if frame not in snapshots:
            continue
        grid_snapshot, changed = snapshots[frame]
        lines.append("")
        lines.append(f"## Frame {frame}")
        lines.append("")
        lines.append(f"- Per-frame writes: {frame_stats(changed)}")
        lines.append("")
        lines.append("### Changed cells")
        lines.append("")
        overlay = format_overlay(changed)
        if overlay:
            lines.append("```text")
            lines.extend(overlay)
            lines.append("```")
        else:
            lines.append("_No nametable tile writes in this frame._")
        lines.append("")
        lines.append("### Cumulative nametable")
        lines.append("")
        lines.append("```text")
        lines.extend(format_grid(grid_snapshot))
        lines.append("```")

    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
