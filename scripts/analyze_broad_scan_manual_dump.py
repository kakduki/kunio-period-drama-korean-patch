#!/usr/bin/env python3
"""Summarize manual broad-scan screen dumps for v0.5 promotion decisions."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "rom_analysis" / "manual_screen_dump_broad_scan"
DEFAULT_OUTPUT = DEFAULT_INPUT / "summary.md"
TARGETS_JSON = ROOT / "rom_analysis" / "broad_scan_fceux_targets.json"
PATCHABILITY_JSON = ROOT / "rom_analysis" / "broad_scan_patchability.json"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def latest_records(input_dir: Path) -> Path | None:
    files = sorted(input_dir.glob("manual_frame_*_target_records.tsv"))
    return files[-1] if files else None


def read_records(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_targets() -> dict[str, dict[str, object]]:
    payload = json.loads(TARGETS_JSON.read_text(encoding="utf-8"))
    return {str(row["label"]): row for row in payload["targets"]}


def load_patchability() -> dict[str, dict[str, object]]:
    payload = json.loads(PATCHABILITY_JSON.read_text(encoding="utf-8"))
    out = {}
    for row in payload["promotion_candidates"]:
        out[str(row["rom_offset"]).upper()] = row
    return out


def normalize_rom_hit(raw: str) -> str:
    text = raw.replace("ROM+", "").strip()
    if text.lower().startswith("0x"):
        return f"0x{int(text, 16):05X}"
    return text


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
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            "\n".join(
                [
                    "# Broad Scan Manual Dump Summary",
                    "",
                    f"- Input directory: `{rel(input_dir)}`",
                    "- Status: **no manual broad-scan dump records found yet**",
                    "",
                    "Run `lua/kunio_manual_broad_scan_dump.lua` in FCEUX after manually reaching a candidate screen, then run this script again.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {output}")
        print("records=0 matches=0 frame=?")
        return 0

    rows = read_records(records_path)
    targets = load_targets()
    patchability = load_patchability()
    matches = [row for row in rows if row.get("active_expected_match", "").lower() == "true"]
    frame = rows[0].get("frame", "?") if rows else "?"

    promotable_matches = []
    for row in matches:
        label = row.get("label", "")
        target = targets.get(label, {})
        rom_hit = normalize_rom_hit(row.get("rom_hit", ""))
        patch_row = patchability.get(rom_hit.upper(), {})
        promotable_matches.append(
            {
                "record": row,
                "target": target,
                "patchability": patch_row,
            }
        )

    lines = [
        "# Broad Scan Manual Dump Summary",
        "",
        f"- Input records: `{rel(records_path)}`",
        f"- Frame: **{frame}**",
        f"- Targets checked: **{len(rows)}**",
        f"- Active original-byte matches: **{len(matches)}**",
        "",
        "## Promotion Evidence",
        "",
    ]
    if promotable_matches:
        lines += [
            "| label | confidence | ROM | source | korean | expected bytes | future patch preview | new glyphs | decision |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for item in promotable_matches:
            record = item["record"]
            target = item["target"]
            patch_row = item["patchability"]
            new_glyphs = "".join(patch_row.get("new_glyphs", [])) or "-"
            decision = "screen-context-needed"
            lines.append(
                f"| `{record.get('label', '')}` | {target.get('confidence', '')} | "
                f"`{record.get('rom_hit', '')}` | {target.get('source', '')} | "
                f"{target.get('korean', '')} | `{record.get('expected_bytes', '')}` | "
                f"`{target.get('future_patch_bytes_preview', '')}` | {new_glyphs} | {decision} |"
            )
    else:
        lines.append("_No broad-scan promotion candidate matched this manual screen._")

    lines += [
        "",
        "## All Target Snapshots",
        "",
        "| label | ROM | CPU range | match | snapshot |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row.get('label', '')}` | `{row.get('rom_hit', '')}` | "
            f"`{row.get('cpu_range', '')}` | {row.get('active_expected_match', '')} | "
            f"`{row.get('record_snapshot', '')}` |"
        )

    lines += [
        "",
        "## Rule",
        "",
        "- `active_original-byte_match=true` proves the candidate record was mapped in CPU memory on this manual screen.",
        "- It is still not sufficient alone: visually confirm the screenshot corresponds to the intended label/dialogue before building v0.5.",
        "- Medium-confidence matches with `new glyphs` require extending the CHR slot plan before patching.",
    ]

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output}")
    print(f"records={len(rows)} matches={len(matches)} frame={frame}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
