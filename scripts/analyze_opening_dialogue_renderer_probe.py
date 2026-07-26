#!/usr/bin/env python3
"""Summarize the bounded opening-dialogue renderer trace."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from rom_utils import REPO_ROOT


DEFAULT_INPUT = REPO_ROOT / "rom_analysis" / "opening_dialogue_renderer_probe"
DEFAULT_JSON = DEFAULT_INPUT / "analysis.json"
DEFAULT_MARKDOWN = DEFAULT_INPUT / "analysis.md"


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def classify(input_dir: Path) -> dict[str, object]:
    summary = read_tsv(input_dir / "summary.tsv")
    parser_rows = read_tsv(input_dir / "parser_exec.tsv")
    source_reads = read_tsv(input_dir / "source_reads.tsv")
    buffer_rows = read_tsv(input_dir / "buffer_writes.tsv")
    queue_rows = read_tsv(input_dir / "queue_writes.tsv")
    dma_rows = read_tsv(input_dir / "dma.tsv")
    oam_rows = read_tsv(input_dir / "oam_writes.tsv")
    ppu_writes = read_tsv(input_dir / "ppu_writes.tsv")
    ppu_rows = read_tsv(input_dir / "ppu_rows.tsv")
    final_reason = summary[-1].get("reason", "") if summary else ""
    labels = Counter(row.get("label", "") for row in parser_rows)
    source_bytes = Counter(row.get("source_byte", "") for row in parser_rows)
    pcs = Counter(row.get("pc", "") for row in parser_rows)
    screenshot = any(input_dir.glob("renderer_probe_frame_*_screen.gd"))
    return {
        "status": "ROUTINE_TRACE_CAPTURED" if final_reason == "lua_done" and source_reads else "TRACE_INCOMPLETE",
        "checks": {
            "bounded_lua_completion": "PASS" if final_reason == "lua_done" else "FAIL",
            "screen_capture": "PASS" if screenshot else "FAIL",
            "target_parser_execution": "PASS" if labels.get("parser", 0) else "UNKNOWN",
            "target_source_reads": "PASS" if source_reads else "FAIL",
            "target_emit_prep_execution": "PASS" if labels.get("emit_prep", 0) else "UNKNOWN",
            "target_emit_dispatch_execution": "PASS" if labels.get("emit_dispatch", 0) else "UNKNOWN",
            "renderer_buffer_writes": "PASS" if buffer_rows else "UNKNOWN",
            "renderer_queue_writes": "PASS" if queue_rows else "UNKNOWN",
            "unrelated_oam_activity": "OBSERVED" if oam_rows or dma_rows else "UNKNOWN",
            "dialogue_nametable_writes": "PASS" if ppu_writes else "UNKNOWN",
            "ppu_rows_captured": "PASS" if len(ppu_rows) == 30 else "FAIL",
        },
        "evidence": {
            "final_reason": final_reason or "MISSING",
            "parser_hits_by_label": dict(sorted(labels.items())),
            "parser_source_bytes": dict(sorted(source_bytes.items())),
            "parser_pcs": dict(sorted(pcs.items())),
            "source_read_pcs": dict(sorted(Counter(row.get("pc", "") for row in source_reads).items())),
            "source_read_count": len(source_reads),
            "buffer_write_count": len(buffer_rows),
            "queue_write_count": len(queue_rows),
            "oam_write_count": len(oam_rows),
            "dma_write_count": len(dma_rows),
            "dialogue_nametable_write_count": len(ppu_writes),
            "ppu_row_count": len(ppu_rows),
        },
    }


def render_markdown(payload: dict[str, object]) -> str:
    checks = payload["checks"]
    evidence = payload["evidence"]
    lines = [
        "# Opening Dialogue Renderer Probe",
        "",
        f"Status: **{payload['status']}**",
        "",
        "| check | result |",
        "| --- | --- |",
    ]
    for label, result in checks.items():
        lines.append(f"| {label} | {result} |")
    lines.extend(
        [
            "",
            f"- Final Lua reason: `{evidence['final_reason']}`",
            f"- Parser hits by label: `{evidence['parser_hits_by_label']}`",
            f"- Parser source bytes: `{evidence['parser_source_bytes']}`",
            f"- Parser PCs: `{evidence['parser_pcs']}`",
            f"- Source-read PCs: `{evidence['source_read_pcs']}`",
            f"- Target source reads: `{evidence['source_read_count']}`",
            f"- Renderer-buffer writes: `{evidence['buffer_write_count']}`",
            f"- Renderer-queue writes: `{evidence['queue_write_count']}`",
            f"- Unrelated OAM tile-code writes: `{evidence['oam_write_count']}`",
            f"- Unrelated OAM DMA writes: `{evidence['dma_write_count']}`",
            f"- Dialogue-nametable writes: `{evidence['dialogue_nametable_write_count']}`",
            "",
            "The OAM activity above belongs to gameplay sprites, not this dialogue path.",
            "The relevant evidence is the source-read, queue, and nametable path. The",
            "8x16 candidate must still pass a bounded native-screen readability review.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    payload = classify(args.input_dir)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")
    print(f"status={payload['status']}")
    print(f"json={args.json_output}")
    print(f"markdown={args.markdown_output}")
    return 0 if payload["checks"]["bounded_lua_completion"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
