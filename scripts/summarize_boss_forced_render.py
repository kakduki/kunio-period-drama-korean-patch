#!/usr/bin/env python3
"""Summarize bounded forced boss-dialogue renderer captures."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from rom_utils import REPO_ROOT


DEFAULT_TARGETS = REPO_ROOT / "rom_analysis" / "boss_dialogue_targets.csv"
DEFAULT_CAPTURE_ROOT = Path(r"C:\tmp\kunio_boss_forced_render")
DEFAULT_JSON = REPO_ROOT / "rom_analysis" / "boss_dialogue_forced_render_report.json"
DEFAULT_MARKDOWN = REPO_ROOT / "rom_analysis" / "boss_dialogue_forced_render_report.md"


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_targets(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def capture_row(target: dict[str, str], capture_root: Path) -> dict[str, object]:
    index = target["pointer_index"]
    folder = capture_root / f"ptr{index}"
    forced = read_tsv(folder / "forced_pointer.tsv")
    source = read_tsv(folder / "source_reads.tsv")
    parser = read_tsv(folder / "parser_exec.tsv")
    ppu = read_tsv(folder / "ppu_writes.tsv")
    summary = read_tsv(folder / "summary.tsv")
    capture_summary = next((row for row in summary if row.get("reason") == "capture"), {})
    forced_cpu = source[0].get("address", "") if source else ""
    screen = folder / "frame_000392_screen.gd"
    source_bytes = [row.get("source_byte", "") for row in source[:32]]
    emit_count = sum(row.get("label") == "emit_dispatch" for row in parser)
    target_seen = capture_summary.get("target_seen") == "true"
    ppu_count = len(ppu)
    screen_bytes = screen.stat().st_size if screen.exists() else 0
    if target_seen and len(source) >= 2 and emit_count > 0 and ppu_count > 0 and screen_bytes > 0:
        forced_status = "PASS_FORCED_BOSS_DIALOGUE_RENDER"
        failure_class = "none"
    elif target_seen and screen_bytes > 0:
        forced_status = "UNKNOWN_FORCED_POINTER_ONLY"
        failure_class = "pointer_seen_but_parser_did_not_emit_text"
    else:
        forced_status = "FAIL_CAPTURE_INCOMPLETE"
        failure_class = "capture_missing_or_target_not_seen"
    return {
        "pointer_index": index,
        "forced_pointer_cpu": forced_cpu,
        "forced_pointer_write_rows": len(forced),
        "target_seen": target_seen,
        "source_read_rows": len(source),
        "source_bytes_sample": source_bytes,
        "emit_dispatch_rows": emit_count,
        "ppu_write_rows": ppu_count,
        "screen_dump_bytes": screen_bytes,
        "forced_render_status": forced_status,
        "natural_route_status": "UNKNOWN",
        "failure_class": failure_class,
        "evidence_scope": "Forced pointer renderer trace only; no natural boss-event proof.",
    }


def build_report(targets_path: Path, capture_root: Path) -> dict[str, object]:
    targets = read_targets(targets_path)
    rows = [capture_row(target, capture_root) for target in targets]
    return {
        "capture_root": capture_root.as_posix(),
        "target_count": len(rows),
        "forced_render_pass_count": sum(
            row["forced_render_status"] == "PASS_FORCED_BOSS_DIALOGUE_RENDER" for row in rows
        ),
        "natural_route_proof_count": 0,
        "rows": rows,
    }


def write_markdown(path: Path, report: dict[str, object]) -> None:
    rows = report["rows"]
    lines = [
        "# Boss Dialogue Forced Render Report",
        "",
        "This report summarizes bounded FCEUX captures that force one pointer record into the text loader.",
        "It is renderer evidence only and does not prove that the game naturally reaches a boss event.",
        "",
        f"- Target records: **{report['target_count']}**",
        f"- Forced renderer PASS: **{report['forced_render_pass_count']}**",
        "- Natural boss-route proof: **0**",
        "- Release status: **NOT_READY**",
        "",
        "| pointer | forced CPU | source reads | emits | PPU rows | forced status | natural status |",
        "| ---: | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['pointer_index']} | `{row['forced_pointer_cpu']}` | {row['source_read_rows']} | "
            f"{row['emit_dispatch_rows']} | {row['ppu_write_rows']} | {row['forced_render_status']} | "
            f"{row['natural_route_status']} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "A forced PASS means the selected candidate record was observed by the parser and produced emit/PPU activity within the bounded capture.",
        "UNKNOWN rows may begin with control bytes or require the event state that the forced pointer probe does not reproduce.",
        "The next release gate remains a naturally reached boss event with a human-readable screen capture.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--targets", type=Path, default=DEFAULT_TARGETS)
    parser.add_argument("--capture-root", type=Path, default=DEFAULT_CAPTURE_ROOT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    report = build_report(args.targets, args.capture_root)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    write_markdown(args.markdown_out, report)
    print(f"Wrote {args.json_out}")
    print(f"Wrote {args.markdown_out}")
    print(f"forced_render_pass={report['forced_render_pass_count']}/{report['target_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
