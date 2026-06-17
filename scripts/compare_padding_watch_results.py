#!/usr/bin/env python3
"""Compare FCEUX read-watch results across PRG padding experiment strategies."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "rom_analysis" / "prg_padding_fceux_targets.json"
OUT_MD = ROOT / "rom_analysis" / "fceux_padding_exp_watch_comparison.md"
OUT_JSON = ROOT / "rom_analysis" / "fceux_padding_exp_watch_comparison.json"


def read_summary(input_dir: Path) -> dict[str, str]:
    path = input_dir / "summary.tsv"
    if not path.exists():
        return {}
    rows = list(csv.DictReader(path.open(encoding="utf-8"), delimiter="\t"))
    if not rows:
        return {}
    return rows[-1]


def read_hits(input_dir: Path) -> list[dict[str, str]]:
    path = input_dir / "bank1_reads.tsv"
    if not path.exists():
        return []
    return list(csv.DictReader(path.open(encoding="utf-8"), delimiter="\t"))


def watch_dir_for(strategy: str) -> Path:
    return ROOT / "rom_analysis" / f"fceux_padding_exp_{strategy}_watch"


def main() -> int:
    targets = json.loads(TARGETS.read_text(encoding="utf-8"))
    rows = []
    for strategy, target_rows in targets["targets_by_strategy"].items():
        target = target_rows[0]
        input_dir = watch_dir_for(strategy)
        summary = read_summary(input_dir)
        hits = read_hits(input_dir)
        active_hits = [
            row for row in hits
            if row.get("active_expected_match", "").lower() == "true"
        ]
        snapshots = sorted({row.get("record_snapshot", "") for row in active_hits if row.get("record_snapshot")})
        rows.append(
            {
                "strategy": strategy,
                "input_dir": str(input_dir.relative_to(ROOT)),
                "expected_bytes": target["expected_patched_bytes"],
                "hits": len(hits),
                "active_expected_matches": len(active_hits),
                "final_frame": summary.get("frame", ""),
                "final_reason": summary.get("reason", ""),
                "registered": summary.get("registered", ""),
                "record_snapshots": snapshots,
                "screen_verdict": "not-checked",
            }
        )

    payload = {
        "source": str(TARGETS.relative_to(ROOT)),
        "summary": {
            "strategy_count": len(rows),
            "all_have_active_matches": all(row["active_expected_matches"] > 0 for row in rows),
            "screen_verdict": "not-checked",
        },
        "results": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# FCEUX Padding Experiment Watch Comparison",
        "",
        "This compares CPU read-watch results for the five `ROM+0x071A4` padding experiment ROMs.",
        "",
        "Important: this validates that each strategy's bytes become active in the watched CPU record. It does not validate visible rendering.",
        "",
        "| strategy | expected bytes | hits | active expected matches | final frame | final reason | record snapshot | screen verdict |",
        "| --- | --- | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in rows:
        snapshot = "<br>".join(f"`{value}`" for value in row["record_snapshots"]) or "-"
        lines.append(
            f"| {row['strategy']} | `{row['expected_bytes']}` | {row['hits']} | "
            f"{row['active_expected_matches']} | {row['final_frame']} | {row['final_reason']} | "
            f"{snapshot} | {row['screen_verdict']} |"
        )
    lines += [
        "",
        "## Notes",
        "",
        "- All strategies need a separate visual/PPU check before any padding rule is promoted.",
        "- Differing hit counts can happen when a padding byte changes control flow or terminator behavior; treat this as a signal to inspect the status screen carefully.",
        "- `preserve_tail` is only a baseline because it keeps old tail bytes after the new first glyph.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(f"strategies={len(rows)} all_active={payload['summary']['all_have_active_matches']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
