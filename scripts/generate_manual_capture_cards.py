#!/usr/bin/env python3
"""Generate short FCEUX manual capture task cards from the decision matrix."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


DECISION_MATRIX = REPO_ROOT / "rom_analysis" / "patch_decision_matrix.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "manual_capture_cards.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "manual_capture_cards.md"

BASE_ROM_NAME = "rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes"
V041_ROM_NAME = "output/kunio_period_drama_korean_prg_plan_v0.4.1_conflict_safe.nes"


def capture_mode(row: dict[str, object]) -> dict[str, str]:
    kind = str(row.get("kind", ""))
    if kind in {"conflict_needs_manual_screen", "broad_non_overlapping"}:
        return {
            "rom_to_open": BASE_ROM_NAME,
            "lua_script": "lua/kunio_manual_broad_scan_dump.lua",
            "summary_command": "python scripts/analyze_broad_scan_manual_dump.py",
            "why": "Confirm original-byte broad-scan evidence before building a new patch candidate.",
        }
    if kind == "runtime_padding_rule_blocker":
        return {
            "rom_to_open": "output/kunio_period_drama_korean_prg_padding_exp_rom_071a4_candidate_82_pad_00.nes first, then compare other padding experiment ROMs",
            "lua_script": "lua/kunio_manual_screen_dump.lua",
            "summary_command": "python scripts/analyze_manual_screen_dump.py",
            "why": "Decide which padding strategy renders cleanly before shortening this text.",
        }
    return {
        "rom_to_open": V041_ROM_NAME,
        "lua_script": "lua/kunio_manual_v041_screen_dump.lua",
        "summary_command": "python scripts/analyze_manual_screen_dump.py --input-dir rom_analysis/manual_screen_dump_v041 --output rom_analysis/manual_screen_dump_v041/summary.md",
        "why": "Verify the current conflict-safe candidate on the manually reached screen.",
    }


def make_cards(limit: int = 12) -> dict[str, object]:
    matrix = json.loads(DECISION_MATRIX.read_text(encoding="utf-8"))
    rows = matrix.get("high_value_next_checks", [])[:limit]
    cards = []
    for index, row in enumerate(rows, start=1):
        mode = capture_mode(row)
        cards.append(
            {
                "task": index,
                "priority": row.get("priority", ""),
                "kind": row.get("kind", ""),
                "label": row.get("label", ""),
                "rom_hit": row.get("rom_hit", ""),
                "source": row.get("source", ""),
                "korean": row.get("korean", ""),
                "evidence_risk": f"{row.get('evidence_level', '')} / {row.get('risk', '')}",
                "rom_to_open": mode["rom_to_open"],
                "lua_script": mode["lua_script"],
                "summary_command": mode["summary_command"],
                "purpose": mode["why"],
                "decision_after_capture": row.get("next_action", ""),
            }
        )
    return {
        "source": str(DECISION_MATRIX.relative_to(REPO_ROOT)),
        "summary": {
            "card_count": len(cards),
            "rule": "Stop blind autoplay when stagnant_screen appears; use these cards for manually reached screens.",
        },
        "cards": cards,
    }


def write_markdown(payload: dict[str, object]) -> None:
    lines = [
        "# Manual Capture Cards",
        "",
        "Use these short cards at the FCEUX window. They are intentionally smaller than the full decision matrix.",
        "",
        "- Stop blind autoplay when `stagnant_screen` appears.",
        "- Pause on the exact text/menu/status screen before running Lua.",
        "- Keep the generated dumps as evidence even when there is no active match.",
        "",
    ]

    for card in payload["cards"]:
        lines += [
            f"## Task {card['task']}: `{card['rom_hit']}`",
            "",
            f"- Kind: `{card['kind']}`",
            f"- Source/Korean: {card['source']} -> {card['korean']}",
            f"- Evidence/Risk: {card['evidence_risk']}",
            f"- Open ROM: `{card['rom_to_open']}`",
            f"- Run Lua: `{card['lua_script']}`",
            f"- Summarize: `{card['summary_command']}`",
            f"- Purpose: {card['purpose']}",
            f"- Decision after capture: {card['decision_after_capture']}",
            "",
        ]

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    payload = make_cards()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"cards={payload['summary']['card_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
