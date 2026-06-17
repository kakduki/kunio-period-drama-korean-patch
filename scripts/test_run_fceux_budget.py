#!/usr/bin/env python3
"""Test the non-GUI autoplay budget guard in run_fceux_lua_analysis.py."""

from __future__ import annotations

import tempfile
from pathlib import Path

from run_fceux_lua_analysis import (
    BLIND_AUTOPLAY_FRAME_CAP,
    BLIND_AUTOPLAY_TIMEOUT_CAP,
    apply_blind_autoplay_budget,
    mirror_staged_manual_outputs,
    parse_args,
)


def check_default_blind_autoplay_is_capped() -> None:
    args = parse_args([])
    apply_blind_autoplay_budget(args, Path("kunio_auto_dump.lua"))
    assert args.frames == BLIND_AUTOPLAY_FRAME_CAP
    assert args.timeout == BLIND_AUTOPLAY_TIMEOUT_CAP


def check_targeted_watch_is_not_capped() -> None:
    args = parse_args(["--target-lua", "lua/kunio_broad_scan_candidate_targets.lua"])
    original = (args.frames, args.timeout)
    apply_blind_autoplay_budget(args, Path("kunio_auto_dump.lua"))
    assert (args.frames, args.timeout) == original


def check_explicit_long_autoplay_is_not_capped() -> None:
    args = parse_args(["--allow-long-autoplay"])
    original = (args.frames, args.timeout)
    apply_blind_autoplay_budget(args, Path("kunio_auto_dump.lua"))
    assert (args.frames, args.timeout) == original


def check_staged_manual_outputs_are_mirrored() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        staged = tmp / "staged" / "rom_analysis" / "manual_screen_dump_v042"
        staged.mkdir(parents=True)
        (staged / "manual_frame_000123_target_records.tsv").write_text("frame\tlabel\n123\tkatana\n", encoding="utf-8")
        destination_root = tmp / "repo" / "rom_analysis"

        mirrored = mirror_staged_manual_outputs(tmp / "staged" / "rom_analysis", destination_root)

        expected = destination_root / "manual_screen_dump_v042" / "manual_frame_000123_target_records.tsv"
        assert mirrored == [destination_root / "manual_screen_dump_v042"]
        assert expected.read_text(encoding="utf-8") == "frame\tlabel\n123\tkatana\n"


def main() -> int:
    check_default_blind_autoplay_is_capped()
    check_targeted_watch_is_not_capped()
    check_explicit_long_autoplay_is_not_capped()
    check_staged_manual_outputs_are_mirrored()
    print("OK: run_fceux_lua_analysis autoplay budget guard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
