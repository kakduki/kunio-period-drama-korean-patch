#!/usr/bin/env python3
"""Check the generated next manual run report."""

from __future__ import annotations

import json

import generate_next_manual_run as next_manual
from rom_utils import REPO_ROOT


JSON_PATH = REPO_ROOT / "rom_analysis" / "next_manual_run.json"
MD_PATH = REPO_ROOT / "rom_analysis" / "next_manual_run.md"


def main() -> int:
    payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    summary = payload["summary"]
    action = payload["next_action"]

    assert summary["action_count"] == 12
    assert summary["primary_visual_pending"] == 9
    assert summary["route_proof_pending"] == 3
    assert summary["recommended_phase"] == "primary_v042_visual_review"
    assert action["target"] == "0x0569D"
    assert action["watcher_lua"] == "lua/kunio_manual_v042_capture_watch.lua"
    assert action["record_visual_review"].startswith("python scripts/record_primary_visual_review.py 0x0569D --confirm")
    assert action["after_capture"] == ["python scripts/refresh_after_manual_capture.py --phase primary"]

    md = MD_PATH.read_text(encoding="utf-8")
    assert "Next Manual Run" in md
    assert "Recommended Next Action" in md
    assert "0x0569D" in md
    assert "a new dump triggers the after-capture refresh automatically" in md
    assert "if you ran FCEUX/Lua directly instead of the launcher" in md
    assert "refresh_after_manual_capture.py --phase primary" in md
    assert "record_primary_visual_review.py 0x0569D --confirm" in md
    assert "kunio_manual_route_heishichi_capture_watch.lua" in md

    simulated_primary = {
        "rows": [
            {
                "priority": 10,
                "rom_hit": "0x07227",
                "romaji": "Katana",
                "screen_hint": "look for a katana/weapon item label",
                "visual_context_confirmed": True,
                "review_status": "visual_confirmed",
                "matches": 0,
                "capture_status": "not_in_manual_capture_cards",
                "rom_to_open": "output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes",
                "watcher_lua": "lua/kunio_manual_v042_capture_watch.lua",
            },
            {
                "priority": 20,
                "rom_hit": "0x0569D",
                "romaji": "Hashi",
                "screen_hint": "look for a bridge/stage/location label",
                "visual_context_confirmed": False,
                "review_status": "auto_input_match_needs_visual",
                "matches": 0,
                "capture_status": "not_in_manual_capture_cards",
                "rom_to_open": "output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes",
                "watcher_lua": "lua/kunio_manual_v042_capture_watch.lua",
            },
        ]
    }
    simulated_actions = next_manual.primary_actions(simulated_primary)
    assert len(simulated_actions) == 1
    assert simulated_actions[0]["target"] == "0x0569D"
    assert "0x0569D --confirm" in simulated_actions[0]["record_visual_review"]

    simulated_blocked = {
        "rows": [
            {
                "priority": 10,
                "rom_hit": "0x07227",
                "romaji": "Katana",
                "screen_hint": "blocked",
                "visual_context_confirmed": False,
                "review_status": "blocked_wrong_context_needs_inventory",
                "matches": 0,
                "capture_status": "not_in_manual_capture_cards",
                "rom_to_open": "output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes",
                "watcher_lua": "lua/kunio_manual_v042_capture_watch.lua",
            }
        ]
    }
    assert next_manual.primary_actions(simulated_blocked) == []

    print("OK: next manual run report combines primary visual and route proof queues.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
