#!/usr/bin/env python3
"""Check the generated route proof status report."""

from __future__ import annotations

import json

from rom_utils import REPO_ROOT


JSON_PATH = REPO_ROOT / "rom_analysis" / "route_proof_status.json"
MD_PATH = REPO_ROOT / "rom_analysis" / "route_proof_status.md"


def main() -> int:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    summary = data["summary"]
    routes = data["routes"]

    assert summary["route_count"] == 3
    assert summary["target_count"] == 7
    assert summary["broad_dump_status"] == "no_manual_broad_scan_dump_records"
    assert summary["status_counts"] == {"no_dump_records": 3}

    by_group = {route["group"]: route for route in routes}
    assert by_group["Kajiya"]["watch_lua"] == "lua/kunio_manual_route_kajiya_capture_watch.lua"
    assert by_group["Tatsuji"]["target_count"] == 3
    assert by_group["Heishichi"]["target_count"] == 3
    assert by_group["Heishichi"]["targets"][0]["label"] == "broad_06294_heishichi"

    md = MD_PATH.read_text(encoding="utf-8")
    assert "Route Proof Status" in md
    assert "Do not keep blind autoplay running" in md
    assert "Route 2: Tatsuji" in md

    print("OK: route proof status reports the current no-dump route bottleneck.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
