#!/usr/bin/env python3
"""Generate a priority list for padding-rule visual verification."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


PIPELINE_DIR = REPO_ROOT / "rom_analysis" / "candidate_pipeline"
PADDING_MATRIX = PIPELINE_DIR / "padding_experiment_matrix.json"
OUT_JSON = PIPELINE_DIR / "padding_strategy_priority.json"
OUT_MD = PIPELINE_DIR / "padding_strategy_priority.md"

STRATEGY_RISK = {
    "preserve_tail": {
        "score": 10,
        "risk": "LOWEST_STRUCTURAL_RISK",
        "reason": "Keeps the original tail bytes after the shortened Korean byte, so it avoids introducing new padding/control bytes.",
    },
    "pad_00": {
        "score": 30,
        "risk": "LOW_PADDING_BYTE_RISK",
        "reason": "Uses zero padding, which may act as empty tile/control data and still needs strict visual proof.",
    },
    "pad_7a": {
        "score": 50,
        "risk": "MEDIUM_VISIBLE_BYTE_RISK",
        "reason": "Uses a nonzero padding byte that may render visibly depending on the active table.",
    },
    "pad_f8f9": {
        "score": 70,
        "risk": "HIGH_CONTROL_BYTE_RISK",
        "reason": "Uses high-byte padding that may behave like control or special glyph data.",
    },
    "pad_ff": {
        "score": 90,
        "risk": "HIGHEST_TERMINATOR_RISK",
        "reason": "Uses FF padding, which is commonly a terminator/sentinel in this text corpus.",
    },
}


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def rank_row(row: dict[str, object]) -> dict[str, object]:
    strategy = str(row.get("strategy", ""))
    risk = STRATEGY_RISK.get(
        strategy,
        {"score": 999, "risk": "UNKNOWN_STRATEGY_RISK", "reason": "No strategy-specific risk rule exists."},
    )
    score = int(risk["score"])
    if row.get("cpu_active_status") != "PASS":
        score += 1000
    if row.get("build_status") != "PASS":
        score += 2000
    if row.get("changes_original_tail") is True:
        score += 5
    if int(row.get("cpu_active_matches") or 0) == 0:
        score += 100
    return {
        "priority_score": score,
        "strategy": strategy,
        "risk_class": risk["risk"],
        "risk_reason": risk["reason"],
        "experiment_set": row.get("experiment_set", ""),
        "candidate_rom": str(row.get("candidate_rom", "")).replace("\\", "/"),
        "candidate_ips": str(row.get("candidate_ips", "")).replace("\\", "/"),
        "patched_bytes": row.get("patched_bytes", ""),
        "pad_bytes": row.get("pad_bytes", ""),
        "changes_original_tail": row.get("changes_original_tail", ""),
        "build_status": row.get("build_status", ""),
        "cpu_active_status": row.get("cpu_active_status", ""),
        "cpu_active_matches": row.get("cpu_active_matches", 0),
        "ppu_exact_status": row.get("ppu_exact_status", ""),
        "ppu_exact_vram_matches": row.get("ppu_exact_vram_matches", 0),
        "visual_status": row.get("visual_status", ""),
        "decision": row.get("decision", ""),
    }


def make_payload() -> dict[str, object]:
    matrix = load_json(PADDING_MATRIX)
    current_rows = [
        row for row in matrix.get("rows", [])
        if row.get("experiment_set") == "v05-current-font-base"
    ]
    ranked = sorted((rank_row(row) for row in current_rows), key=lambda row: (row["priority_score"], row["strategy"]))
    next_candidate = ranked[0] if ranked else {}
    return {
        "source": {
            "padding_experiment_matrix": rel(PADDING_MATRIX),
        },
        "summary": {
            "current_font_strategy_count": len(ranked),
            "recommended_strategy": next_candidate.get("strategy", ""),
            "recommended_candidate_rom": next_candidate.get("candidate_rom", ""),
            "recommended_risk_class": next_candidate.get("risk_class", ""),
            "release_gate_status": "UNKNOWN",
            "rule": "Rank only current-font padding experiments. This does not promote shortened replacements without PPU/visual proof.",
        },
        "rows": ranked,
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# Padding Strategy Priority",
        "",
        "This is the next-test priority list for the shortened padding-rule UNKNOWN gate.",
        "It does not approve any shortened replacement for release.",
        "",
        f"- Recommended strategy: `{summary['recommended_strategy']}`",
        f"- Recommended candidate ROM: `{summary['recommended_candidate_rom']}`",
        f"- Recommended risk class: `{summary['recommended_risk_class']}`",
        f"- Release gate status: `{summary['release_gate_status']}`",
        "",
        "| priority | strategy | risk | patched bytes | CPU | active matches | PPU | visual | candidate ROM |",
        "| ---: | --- | --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| {row['priority_score']} | `{row['strategy']}` | {row['risk_class']} | `{row['patched_bytes']}` | "
            f"{row['cpu_active_status']} | {row['cpu_active_matches']} | {row['ppu_exact_status']} | "
            f"{row['visual_status']} | `{row['candidate_rom']}` |"
        )
    lines += [
        "",
        "## Recommended Next Check",
        "",
        "Use the recommended candidate ROM only for a focused PPU/visual padding check.",
        "Do not merge shortened replacements into the normal dev or release candidate until the padding rule has strict PPU or visual acceptance.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"recommended={payload['summary']['recommended_strategy']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
