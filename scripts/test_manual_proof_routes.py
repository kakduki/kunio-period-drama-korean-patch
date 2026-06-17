#!/usr/bin/env python3
"""Check the generated manual proof route grouping."""

from __future__ import annotations

import json

from rom_utils import REPO_ROOT


JSON_PATH = REPO_ROOT / "rom_analysis" / "manual_proof_routes.json"
MD_PATH = REPO_ROOT / "rom_analysis" / "manual_proof_routes.md"


def main() -> int:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    summary = data["summary"]
    routes = data["routes"]

    assert summary["candidate_count"] == 7
    assert summary["route_count"] == 3
    assert summary["groups"] == ["Kajiya", "Tatsuji", "Heishichi"]

    by_group = {route["group"]: route for route in routes}
    assert by_group["Kajiya"]["rom_offsets"] == ["0x0440C"]
    assert by_group["Tatsuji"]["rom_offsets"] == ["0x048F4", "0x052A5", "0x05BE5"]
    assert by_group["Heishichi"]["rom_offsets"] == ["0x06294", "0x0631B", "0x06359"]

    md = MD_PATH.read_text(encoding="utf-8")
    assert "Manual Proof Routes" in md
    assert "Manual route groups: **3**" in md
    assert "Route 1: Kajiya" in md

    print("OK: manual proof routes group the seven candidates into three contexts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
