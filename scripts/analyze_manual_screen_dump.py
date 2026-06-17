#!/usr/bin/env python3
"""Summarize manual FCEUX screen dumps captured by kunio_manual_screen_dump.lua."""

from __future__ import annotations

import argparse
import csv
import json
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


def make_payload(records_path: Path, rows: list[dict[str, str]], related: list[Path]) -> dict[str, object]:
    matches = [row for row in rows if row.get("active_expected_match", "").lower() == "true"]
    frame = rows[0].get("frame", "?") if rows else "?"
    screenshot = next((path for path in related if path.name.endswith("_screen.gd")), None)
    meta = next((path for path in related if path.name.endswith("_meta.txt")), None)
    return {
        "input_records": rel(records_path),
        "frame": frame,
        "targets_checked": len(rows),
        "active_expected_matches": len(matches),
        "latest_screenshot": rel(screenshot) if screenshot else "",
        "latest_meta": rel(meta) if meta else "",
        "active_matches": matches,
        "captured_files": [
            {
                "path": rel(path),
                "bytes": path.stat().st_size,
                "kind": path.suffix.lower().lstrip(".") or "file",
            }
            for path in related
        ],
    }


def write_markdown(output: Path, payload: dict[str, object]) -> None:
    matches = payload["active_matches"]
    lines = [
        "# Manual Screen Dump Summary",
        "",
        f"- Input records: `{payload['input_records']}`",
        f"- Frame: **{payload['frame']}**",
        f"- Targets checked: **{payload['targets_checked']}**",
        f"- Active expected matches: **{payload['active_expected_matches']}**",
        f"- Screenshot: `{payload['latest_screenshot'] or '-'}`",
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
        "| file | bytes | kind |",
        "| --- | ---: | --- |",
    ]
    for path in payload["captured_files"]:
        lines.append(f"| `{path['path']}` | {path['bytes']} | `{path['kind']}` |")

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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT))
    parser.add_argument("--records", help="Specific *_target_records.tsv file to summarize.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--json-output", help="Machine-readable summary path. Defaults to output path with .json suffix.")
    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser().resolve()
    records_path = Path(args.records).expanduser().resolve() if args.records else latest_records(input_dir)
    output = Path(args.output).expanduser().resolve()
    json_output = Path(args.json_output).expanduser().resolve() if args.json_output else output.with_suffix(".json")
    if records_path is None or not records_path.exists():
        raise FileNotFoundError(f"No manual target records found under {input_dir}")

    rows = read_records(records_path)
    prefix = records_path.name.replace("_target_records.tsv", "")
    related = sorted(records_path.parent.glob(prefix + "*"))
    payload = make_payload(records_path, rows, related)
    write_markdown(output, payload)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output}")
    print(f"Wrote {json_output}")
    print(
        "records={targets_checked} matches={active_expected_matches} frame={frame}".format(
            **payload
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
