#!/usr/bin/env python3
"""Generate FCEUX targets for the v0.4.1 conflict-safe candidate."""

from __future__ import annotations

import generate_v04_fceux_targets as generator
from rom_utils import REPO_ROOT


generator.REPORT = REPO_ROOT / "output" / "kunio_period_drama_korean_prg_plan_v0.4.1_conflict_safe_build_report.json"
generator.OUT_LUA = REPO_ROOT / "lua" / "kunio_v041_conflict_safe_targets.lua"
generator.OUT_MD = REPO_ROOT / "rom_analysis" / "v041_conflict_safe_fceux_targets.md"
generator.OUT_JSON = REPO_ROOT / "rom_analysis" / "v041_conflict_safe_fceux_targets.json"
generator.TARGET_TITLE = "v0.4.1 Conflict-Safe FCEUX Targets"
generator.TARGET_DESCRIPTION = (
    "These targets watch for patched PRG bytes from the v0.4.1 conflict-safe candidate."
)
generator.RUN_COMMAND = (
    "python scripts/run_fceux_lua_analysis.py --rom output/kunio_period_drama_korean_prg_plan_v0.4.1_conflict_safe.nes "
    "--lua-script lua/kunio_bank1_watch.lua --target-lua lua/kunio_v041_conflict_safe_targets.lua "
    "--frames 10800 --timeout 240 --final-output rom_analysis/fceux_v041_conflict_safe_watch "
    "--clean-output --no-dump-hex --no-dump-bin"
)


if __name__ == "__main__":
    raise SystemExit(generator.main())
