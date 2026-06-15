"""Summarize FCEUX Lua event and dump output.

The Lua automation records writes to $2006/$2007 in rom_analysis/fceux_lua.
This script groups those writes by frame and highlights frames that touch
nametable memory, which are the most useful candidates for text/UI rendering.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LUA_DIR = ROOT / "rom_analysis" / "fceux_lua"
OUT = ROOT / "rom_analysis" / "fceux_lua_event_summary.md"


@dataclass
class Event:
    frame: int
    kind: str
    cpu_addr: int
    value: int
    ppu_addr: int


def read_events(path: Path) -> list[Event]:
    events: list[Event] = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        header = next(f, None)
        if header is None:
            return events
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 5:
                continue
            frame, kind, cpu_addr, value, ppu_addr = parts
            events.append(
                Event(
                    frame=int(frame),
                    kind=kind,
                    cpu_addr=int(cpu_addr, 16),
                    value=int(value, 16),
                    ppu_addr=int(ppu_addr, 16),
                )
            )
    return events


def region(addr: int) -> str:
    addr %= 0x4000
    if 0x2000 <= addr <= 0x2FFF:
        if addr & 0x03FF >= 0x03C0:
            return "attribute"
        return "nametable"
    if 0x3F00 <= addr <= 0x3F1F:
        return "palette"
    if 0x0000 <= addr <= 0x1FFF:
        return "pattern"
    return "other"


def parse_summary(path: Path) -> dict[int, dict[str, str]]:
    rows: dict[int, dict[str, str]] = {}
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8", errors="replace") as f:
        header = next(f, "").rstrip("\n").split("\t")
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != len(header):
                continue
            row = dict(zip(header, parts))
            if row.get("frame", "").isdigit():
                rows[int(row["frame"])] = row
    return rows


def grouped_ppudata(events: list[Event]) -> list[tuple[int, int, list[int]]]:
    groups: list[tuple[int, int, list[int]]] = []
    start: int | None = None
    last: int | None = None
    values: list[int] = []

    for event in events:
        if event.kind != "PPUDATA":
            continue
        addr = event.ppu_addr
        if start is None:
            start = last = addr
            values = [event.value]
            continue
        assert last is not None
        if addr == last + 1:
            values.append(event.value)
            last = addr
        else:
            groups.append((start, last, values))
            start = last = addr
            values = [event.value]

    if start is not None and last is not None:
        groups.append((start, last, values))
    return groups


def hex_values(values: list[int], limit: int = 48) -> str:
    shown = " ".join(f"{v:02X}" for v in values[:limit])
    if len(values) > limit:
        shown += " ..."
    return shown


def main() -> int:
    events_path = LUA_DIR / "events.tsv"
    summary_path = LUA_DIR / "summary.tsv"
    if not events_path.exists():
        raise FileNotFoundError(f"Missing {events_path}")

    events = read_events(events_path)
    summary = parse_summary(summary_path)
    by_frame: dict[int, list[Event]] = defaultdict(list)
    for event in events:
        by_frame[event.frame].append(event)

    frame_rows: list[dict[str, object]] = []
    for frame, frame_events in sorted(by_frame.items()):
        data_events = [event for event in frame_events if event.kind == "PPUDATA"]
        if not data_events:
            continue
        counts = Counter(region(event.ppu_addr) for event in data_events)
        addrs = [event.ppu_addr for event in data_events]
        values = Counter(event.value for event in data_events)
        frame_rows.append(
            {
                "frame": frame,
                "total_events": len(frame_events),
                "ppudata": len(data_events),
                "regions": counts,
                "min_addr": min(addrs),
                "max_addr": max(addrs),
                "top_values": values.most_common(8),
                "summary_reason": summary.get(frame, {}).get("reason", ""),
                "summary_writes": summary.get(frame, {}).get("ppu_writes", ""),
            }
        )

    interesting = [
        row
        for row in frame_rows
        if row["regions"].get("nametable", 0) or row["regions"].get("attribute", 0)
    ]
    interesting.sort(
        key=lambda row: (
            row["regions"].get("nametable", 0) + row["regions"].get("attribute", 0),
            row["ppudata"],
        ),
        reverse=True,
    )

    lines: list[str] = []
    lines.append("# FCEUX Lua event summary")
    lines.append("")
    lines.append("Generated from `rom_analysis/fceux_lua/events.tsv`.")
    lines.append("")
    lines.append("## Frame overview")
    lines.append("")
    lines.append("| frame | reason | PPUDATA | address range | regions | top values |")
    lines.append("| ---: | --- | ---: | --- | --- | --- |")
    for row in frame_rows:
        regions = row["regions"]
        region_text = ", ".join(f"{name}:{count}" for name, count in sorted(regions.items()))
        values = ", ".join(f"{value:02X}x{count}" for value, count in row["top_values"])
        lines.append(
            "| {frame} | {reason} | {ppudata} | ${min_addr:04X}-${max_addr:04X} | {regions} | {values} |".format(
                frame=row["frame"],
                reason=row["summary_reason"] or "-",
                ppudata=row["ppudata"],
                min_addr=row["min_addr"],
                max_addr=row["max_addr"],
                regions=region_text,
                values=values,
            )
        )

    lines.append("")
    lines.append("## Strong nametable candidates")
    lines.append("")
    if not interesting:
        lines.append("No nametable/attribute PPUDATA writes were found.")
    else:
        for row in interesting[:12]:
            frame = int(row["frame"])
            frame_events = by_frame[frame]
            lines.append(
                f"### Frame {frame}: ${row['min_addr']:04X}-${row['max_addr']:04X}"
            )
            lines.append("")
            lines.append(
                "- Regions: "
                + ", ".join(
                    f"{name}:{count}" for name, count in sorted(row["regions"].items())
                )
            )
            lines.append(f"- PPUDATA writes: {row['ppudata']}")
            lines.append("- Consecutive write groups:")
            for start, end, values in grouped_ppudata(frame_events)[:16]:
                reg = region(start)
                if reg not in {"nametable", "attribute"}:
                    continue
                lines.append(
                    f"  - `${start:04X}-${end:04X}` ({reg}, {len(values)} bytes): `{hex_values(values)}`"
                )
            lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "- Palette-only frames such as `33`, `95`, `125`, and `284` are less useful for text extraction."
    )
    lines.append(
        "- Clear/fill frames such as `233` and `653` write zeroes into nametable rows and are useful for screen-transition timing."
    )
    lines.append(
        "- Frame `314` is the strongest current text/UI rendering candidate because it writes many non-zero tile values across `$2086-$23EB`."
    )
    lines.append(
        "- The next practical breakpoint target is the code path that writes these frame `314` PPUDATA values, then backtrack to the source text buffer/table."
    )

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
