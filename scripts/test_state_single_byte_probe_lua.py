#!/usr/bin/env python3
"""Static checks for the state single-byte FCEUX probe."""

from __future__ import annotations

from rom_utils import REPO_ROOT


LUA = REPO_ROOT / "lua" / "kunio_state_single_byte_probe.lua"


def main() -> int:
    text = LUA.read_text(encoding="utf-8")
    required = [
        "KUNIO_STATE_ADDR",
        "KUNIO_STATE_VALUE",
        "KUNIO_STATE_WRITES",
        "only explicitly listed bytes",
        "state_single_byte_probe_summary.tsv",
        "state_single_byte_probe_watch.tsv",
        "kunio_broad_scan_candidate_targets.lua",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    if missing:
        raise SystemExit(f"state probe Lua missing: {', '.join(missing)}")
    print("OK: state single-byte probe Lua is guarded and configurable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
