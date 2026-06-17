#!/usr/bin/env python3
"""Summarize manual FCEUX screen dumps captured by kunio_manual_screen_dump.lua."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "rom_analysis" / "manual_screen_dump"
DEFAULT_OUTPUT = DEFAULT_INPUT / "summary.md"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_records(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def latest_records(input_dir: Path) -> Path | None:
    files = sorted(input_dir.glob("manual_frame_*_target_records.tsv"))
    return files[-1] if files else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT))
    parser.add_argument("--records", help="Specific *_target_records.tsv file to summarize.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser().resolve()
    records_path = Path(args.records).expanduser().resolve() if args.records else latest_records(input_dir)
    output = Path(args.output).expanduser().resolve()
    if records_path is None or not records_path.exists():
        raise FileNotFoundError(f"No manual target records found under {input_dir}")

    rows = read_records(records_path)
    matches = [row for row in rows if row.get("active_expected_match", "").lower() == "true"]
    frame = rows[0].get("frame", "?") if rows else "?"
    prefix = records_path.name.replace("_target_records.tsv", "")
    related = sorted(records_path.parent.glob(prefix + "*"))

    lines = [
        "# Manual Screen Dump Summary",
        "",
        f"- Input records: `{rel(records_path)}`",
        f"- Frame: **{frame}**",
        f"- Targets checked: **{len(rows)}**",
        f"- Active expected matches: **{len(matches)}**",
        "",
        "## Active Matches",
        "",
    ]
    if matches:
        lines += [
            "| label | category | ROM hit | CPU range | expected bytes | record snapshot |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for row in matches:
            lines.append(
                f"| `{row.get('label', '')}` | {row.get('category', '')} | "
                f"`{row.get('rom_hit', '')}` | `{row.get('cpu_range', '')}` | "
                f"`{row.get('expected_bytes', '')}` | `{row.get('record_snapshot', '')}` |"
            )
    else:
        lines.append("_No generated Bank 1 target currently matches this screen's CPU record snapshots._")

    lines += [
        "",
        "## Captured Files",
        "",
        "| file | bytes |",
        "| --- | ---: |",
    ]
    for path in related:
        lines.append(f"| `{rel(path)}` | {path.stat().st_size} |")

    lines += [
        "",
        "## Interpretation",
        "",
        "- A match here means the manually reached screen has the expected candidate bytes mapped in CPU memory at the generated watch range.",
        "- A non-match is still useful: it tells us this screen is not covered by the current Bank 1 target list and needs broader static matching or a new breakpoint target.",
        "- The `.gd` screenshot is FCEUX/GD image data from `gui.gdscreenshot()`; keep it as evidence even if it is not directly viewable in every image viewer.",
    ]

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output}")
    print(f"records={len(rows)} matches={len(matches)} frame={frame}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
