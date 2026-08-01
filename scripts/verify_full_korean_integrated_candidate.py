#!/usr/bin/env python3
"""Summarize bounded runtime evidence for the integrated Korean candidate."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from rom_utils import REPO_ROOT


DEFAULT_ROM = REPO_ROOT / "output" / "full_korean_integrated_candidate" / "kunio_period_drama_korean_integrated_candidate.nes"
DEFAULT_PRE_POINTER = REPO_ROOT / "rom_analysis" / "full_pointer_high_pre_pointer_probe"
DEFAULT_STAGE = REPO_ROOT / "rom_analysis" / "stage_progression_probe_full_pointer_high_candidate"
DEFAULT_OUTPUT_JSON = REPO_ROOT / "rom_analysis" / "full_korean_integrated_runtime.json"
DEFAULT_OUTPUT_MARKDOWN = REPO_ROOT / "rom_analysis" / "full_korean_integrated_runtime.md"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, default=DEFAULT_ROM)
    parser.add_argument("--pre-pointer-dir", type=Path, default=DEFAULT_PRE_POINTER)
    parser.add_argument("--stage-dir", type=Path, default=DEFAULT_STAGE)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_OUTPUT_MARKDOWN)
    parser.add_argument("--expected-label-count", type=int, default=10)
    return parser.parse_args()


def verify(args: argparse.Namespace) -> dict[str, object]:
    rom = args.rom.read_bytes()
    matches = read_tsv(args.pre_pointer_dir / "matches.tsv")
    pre_summary = read_tsv(args.pre_pointer_dir / "summary.tsv")
    stage_summary = read_tsv(args.stage_dir / "summary.tsv")
    captures = read_tsv(args.stage_dir / "captures.tsv")

    matched_targets = sorted({row["target"] for row in matches})
    pre_done = next((row for row in reversed(pre_summary) if row["reason"] == "lua_done"), None)
    stage_done = next((row for row in reversed(stage_summary) if row["reason"] == "lua_done"), None)
    ppu_write_count = int(matches[0]["ppu_write_count"]) if matches and matches[0].get("ppu_write_count") else None
    combat_frames = [int(row["frame"]) for row in captures if row["reason"] == "combat_screen_change"]
    event_frames = [int(row["frame"]) for row in captures if int(row["frame"]) >= 1900]

    payload = {
        "candidate_md5": hashlib.md5(rom).hexdigest(),
        "candidate_size": len(rom),
        "candidate_chr_banks": rom[5] if len(rom) > 5 else None,
        "expected_label_count": args.expected_label_count,
        "pre_pointer": {
            "matched_rows": len(matched_targets),
            "target_ids": matched_targets,
            "lua_done": pre_done is not None,
            "terminal_frame": int(pre_done["frame"]) if pre_done else None,
            "ppu_write_count": ppu_write_count,
        },
        "stage_progression": {
            "lua_done": stage_done is not None,
            "terminal_frame": int(stage_done["frame"]) if stage_done else None,
            "unique_screens": int(stage_done["unique"]) if stage_done else None,
            "combat_frames": combat_frames,
            "event_frames": event_frames,
            "boss_proof": False,
        },
        "status": "PASS_INTEGRATED_BOOT_RUNTIME_NOT_READY"
        if len(matched_targets) == args.expected_label_count and pre_done and stage_done and combat_frames
        else "FAIL_INTEGRATED_RUNTIME_EVIDENCE",
        "release_status": "NOT_READY",
        "known_limits": [
            "The bounded route reaches combat and event screens but does not prove every boss route.",
            "Native pixel review for every translated record and remaining non-pointer families is incomplete.",
            f"The ROM contains {len(matched_targets)} runtime-mapped fixed labels; 190 inventory rows remain untranslated or blocked.",
        ],
        "evidence": {
            "pre_pointer_matches": str(args.pre_pointer_dir / "matches.tsv"),
            "pre_pointer_summary": str(args.pre_pointer_dir / "summary.tsv"),
            "stage_summary": str(args.stage_dir / "summary.tsv"),
            "stage_captures": str(args.stage_dir / "captures.tsv"),
        },
    }
    return payload


def render_markdown(payload: dict[str, object]) -> str:
    pre = payload["pre_pointer"]
    stage = payload["stage_progression"]
    return "\n".join(
        [
            "# Full Korean Integrated Runtime Evidence",
            "",
            f"- Candidate MD5: `{payload['candidate_md5']}`.",
            f"- Candidate size: `{payload['candidate_size']}` bytes; CHR banks: `{payload['candidate_chr_banks']}`.",
            f"- Status: **{payload['status']}**; release status: **{payload['release_status']}**.",
            "",
            "## Bounded Evidence",
            "",
            f"- Fixed Bank 1 labels: {pre['matched_rows']} exact CPU owners; lua_done={pre['lua_done']} at frame {pre['terminal_frame']}.",
            f"- Stage progression: `lua_done`={stage['lua_done']} at frame `{stage['terminal_frame']}`; unique screens `{stage['unique_screens']}`.",
            f"- Combat checkpoints: `{', '.join(str(frame) for frame in stage['combat_frames'])}`.",
            f"- Event checkpoints at or after frame 1900: `{', '.join(str(frame) for frame in stage['event_frames'])}`.",
            "- Boss proof: **NOT AVAILABLE** in this bounded route.",
            "",
            "## Limits",
            "",
            *[f"- {item}" for item in payload["known_limits"]],
            "",
            "Raw evidence paths are recorded in the machine-readable JSON report.",
            "",
        ]
    )


def main() -> int:
    args = parse_args()
    payload = verify(args)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.output_markdown.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("candidate_md5", "status", "release_status", "pre_pointer", "stage_progression")}, ensure_ascii=False))
    return 0 if payload["status"] == "PASS_INTEGRATED_BOOT_RUNTIME_NOT_READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
