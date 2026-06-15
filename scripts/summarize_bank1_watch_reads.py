#!/usr/bin/env python3
"""Summarize FCEUX Bank 1 read watcher TSV output."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "rom_analysis" / "fceux_bank1_watch"
DEFAULT_OUTPUT = ROOT / "rom_analysis" / "fceux_bank1_watch_summary.md"


@dataclass
class ReadHit:
    frame: int
    label: str
    category: str
    rom_hit: str
    cpu_addr: str
    value: str
    record_cpu_range: str
    expected_bytes: str
    context: str


def read_summary(input_dir: Path) -> dict[str, str]:
    path = input_dir / "summary.tsv"
    if not path.exists():
        return {}

    rows = list(csv.DictReader(path.open(encoding="utf-8"), delimiter="\t"))
    if not rows:
        return {}

    start = rows[0]
    final = rows[-1]
    return {
        "completed_frame": final.get("frame", ""),
        "final_reason": final.get("reason", ""),
        "registered": final.get("registered") or start.get("registered", ""),
        "hits": final.get("hits", ""),
        "callback_detail": start.get("detail", ""),
    }


def read_hits(input_dir: Path) -> list[ReadHit]:
    path = input_dir / "bank1_reads.tsv"
    if not path.exists():
        return []

    hits: list[ReadHit] = []
    for row in csv.DictReader(path.open(encoding="utf-8"), delimiter="\t"):
        try:
            frame = int(row["frame"])
        except (KeyError, ValueError):
            continue
        hits.append(
            ReadHit(
                frame=frame,
                label=row.get("label", ""),
                category=row.get("category", ""),
                rom_hit=row.get("rom_hit", ""),
                cpu_addr=row.get("cpu_addr", ""),
                value=row.get("value", ""),
                record_cpu_range=row.get("record_cpu_range", ""),
                expected_bytes=row.get("expected_bytes", ""),
                context=row.get("context", ""),
            )
        )
    return hits


def context_matches_expected(hit: ReadHit) -> bool:
    expected = hit.expected_bytes.strip()
    if not expected:
        return False
    return expected in hit.context


def summarize_hits(hits: list[ReadHit]) -> list[dict[str, object]]:
    by_label: dict[str, list[ReadHit]] = defaultdict(list)
    for hit in hits:
        by_label[hit.label].append(hit)

    rows: list[dict[str, object]] = []
    for label, label_hits in sorted(by_label.items()):
        frames = [hit.frame for hit in label_hits]
        first = label_hits[0]
        cpu_addrs = Counter(hit.cpu_addr for hit in label_hits)
        values = Counter(hit.value for hit in label_hits)
        evidence_hit = next((hit for hit in label_hits if context_matches_expected(hit)), first)
        rows.append(
            {
                "label": label,
                "category": first.category,
                "rom_hit": first.rom_hit,
                "record_cpu_range": first.record_cpu_range,
                "hits": len(label_hits),
                "first_frame": min(frames),
                "last_frame": max(frames),
                "unique_cpu_addrs": len(cpu_addrs),
                "top_cpu_addrs": ", ".join(f"`{addr}`:{count}" for addr, count in cpu_addrs.most_common(4)),
                "top_values": ", ".join(f"`{value}`:{count}" for value, count in values.most_common(4)),
                "expected_bytes": first.expected_bytes,
                "context": evidence_hit.context,
                "context_matches_expected": context_matches_expected(evidence_hit),
            }
        )

    rows.sort(key=lambda row: (-int(row["hits"]), str(row["label"])))
    return rows


def write_markdown(
    output: Path,
    input_dir: Path,
    summary: dict[str, str],
    rows: list[dict[str, object]],
    command: str,
) -> None:
    try:
        display_input_dir = input_dir.relative_to(ROOT)
    except ValueError:
        display_input_dir = input_dir

    lines = [
        "# FCEUX Bank 1 read-watch summary",
        "",
        f"Input directory: `{display_input_dir}`",
        "",
    ]
    if command:
        lines.extend(["Command:", "", "```powershell", command, "```", ""])

    if summary:
        lines.extend(
            [
                "## Run result",
                "",
                f"- Final frame: `{summary.get('completed_frame', '')}`",
                f"- Final reason: `{summary.get('final_reason', '')}`",
                f"- Registered watched CPU addresses: `{summary.get('registered', '')}`",
                f"- Total read hits: `{summary.get('hits', '')}`",
                f"- Callback detail: `{summary.get('callback_detail', '')}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Observed labels",
            "",
            "| label | category | ROM hit | CPU record range | hits | first frame | last frame | unique CPU addrs | expected bytes in context | evidence context |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
        ]
    )
    if rows:
        for row in rows:
            lines.append(
                f"| `{row['label']}` | {row['category']} | `{row['rom_hit']}` | "
                f"`{row['record_cpu_range']}` | {row['hits']} | {row['first_frame']} | "
                f"{row['last_frame']} | {row['unique_cpu_addrs']} | "
                f"{'yes' if row['context_matches_expected'] else 'no'} | "
                f"`{row['context']}` |"
            )
    else:
        lines.append("| _none_ |  |  |  | 0 |  |  |  |  |  |")

    lines.extend(
        [
            "",
            "## Details",
            "",
            "| label | top CPU addresses | top values | expected bytes |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['label']}` | {row['top_cpu_addrs']} | {row['top_values']} | `{row['expected_bytes']}` |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- A hit means the emulator read a watched CPU address while the Lua watcher was active.",
            "- A context match is stronger evidence because the surrounding bytes include the translation candidate's expected byte sequence.",
            "- This still needs to be paired with screen state/PPU writes before treating every candidate as final patch text.",
        ]
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT), help="Directory containing summary.tsv and bank1_reads.tsv.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Markdown file to write.")
    parser.add_argument("--command", default="", help="Command line to record in the generated summary.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input_dir).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    summary = read_summary(input_dir)
    hits = read_hits(input_dir)
    rows = summarize_hits(hits)
    write_markdown(output, input_dir, summary, rows, args.command)
    print(f"Wrote {output}")
    print(f"labels={len(rows)} hits={len(hits)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
