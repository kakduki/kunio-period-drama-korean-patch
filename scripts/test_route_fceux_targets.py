#!/usr/bin/env python3
"""Check generated route-specific FCEUX targets."""

from __future__ import annotations

import json

from rom_utils import REPO_ROOT


JSON_PATH = REPO_ROOT / "rom_analysis" / "route_fceux_targets.json"
MD_PATH = REPO_ROOT / "rom_analysis" / "route_fceux_targets.md"


def main() -> int:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert data["summary"]["route_count"] == 3
    assert data["summary"]["target_count"] == 7

    by_group = {route["group"]: route for route in data["routes"]}
    assert by_group["Kajiya"]["target_count"] == 1
    assert by_group["Tatsuji"]["target_count"] == 3
    assert by_group["Heishichi"]["target_count"] == 3
    assert by_group["Kajiya"]["targets"][0]["label"] == "broad_0440c_kajiya"
    assert {row["label"] for row in by_group["Tatsuji"]["targets"]} == {
        "broad_048f4_tatsuji",
        "broad_052a5_tatsuji",
        "broad_05be5_tatsuji",
    }

    for route in data["routes"]:
        target_lua = REPO_ROOT / route["target_lua"]
        watcher_lua = REPO_ROOT / route["watcher_lua"]
        assert target_lua.exists()
        assert watcher_lua.exists()
        assert "return {" in target_lua.read_text(encoding="utf-8")
        watcher_text = watcher_lua.read_text(encoding="utf-8")
        assert "KUNIO_TARGETS_LUA" in watcher_text
        assert "KUNIO_WATCHER_TITLE" in watcher_text
        assert "KUNIO_WATCHER_HINT" in watcher_text

    md = MD_PATH.read_text(encoding="utf-8")
    assert "Route FCEUX Targets" in md
    assert "kunio_manual_route_kajiya_capture_watch.lua" in md
    assert "if you only see the title/opening screen" in md

    print("OK: route-specific FCEUX targets are generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
