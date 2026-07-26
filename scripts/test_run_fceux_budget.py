#!/usr/bin/env python3
"""Test the non-GUI autoplay budget guard in run_fceux_lua_analysis.py."""

from __future__ import annotations

import tempfile
from pathlib import Path

from run_fceux_lua_analysis import (
    BLIND_AUTOPLAY_FRAME_CAP,
    BLIND_AUTOPLAY_TIMEOUT_CAP,
    apply_blind_autoplay_budget,
    find_lua_script,
    latest_manual_dump_record,
    mirror_staged_manual_outputs,
    parse_args,
    summary_final_reason,
    validate_run_intent,
)


def expect_value_error(callback) -> None:
    try:
        callback()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def check_default_blind_autoplay_is_refused() -> None:
    args = parse_args([])
    expect_value_error(lambda: validate_run_intent(args, Path("kunio_auto_dump.lua")))


def check_missing_lua_script_is_refused_before_gui_setup() -> None:
    expect_value_error(lambda: find_lua_script(None))


def check_target_table_does_not_legitimize_legacy_autoplay() -> None:
    args = parse_args(["--target-lua", "lua/kunio_opening_dialogue_proof_target.lua"])
    expect_value_error(lambda: validate_run_intent(args, Path("kunio_auto_dump.lua")))


def check_explicit_blind_autoplay_is_hard_capped() -> None:
    args = parse_args(["--allow-blind-autoplay", "--frames", "99999", "--timeout", "9999"])
    validate_run_intent(args, Path("kunio_auto_dump.lua"))
    apply_blind_autoplay_budget(args, Path("kunio_auto_dump.lua"))
    assert args.frames == BLIND_AUTOPLAY_FRAME_CAP
    assert args.timeout == BLIND_AUTOPLAY_TIMEOUT_CAP


def check_targeted_watch_is_not_capped() -> None:
    args = parse_args(["--frames", "2400", "--timeout", "180"])
    original = (args.frames, args.timeout)
    validate_run_intent(args, Path("kunio_opening_dialogue_proof.lua"))
    apply_blind_autoplay_budget(args, Path("kunio_opening_dialogue_proof.lua"))
    assert (args.frames, args.timeout) == original


def check_retired_long_autoplay_option_is_refused() -> None:
    args = parse_args(["--allow-long-autoplay"])
    expect_value_error(lambda: validate_run_intent(args, Path("kunio_auto_dump.lua")))


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


def check_latest_manual_dump_record() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        root = Path(raw_tmp) / "rom_analysis"
        assert latest_manual_dump_record(root) is None
        first = root / "manual_screen_dump_v042" / "manual_frame_000001_target_records.tsv"
        second = root / "manual_screen_dump_v042" / "manual_frame_000222_target_records.tsv"
        second.parent.mkdir(parents=True)
        first.write_text("first\n", encoding="utf-8")
        second.write_text("second\n", encoding="utf-8")
        assert latest_manual_dump_record(root) == second


def check_bounded_target_miss_is_a_terminal_reason() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        summary = Path(raw_tmp) / "summary.tsv"
        summary.write_text("frame\\treason\\n1430\\ttarget_not_seen\\n", encoding="utf-8")
        assert summary_final_reason(summary) == "target_not_seen"


def main() -> int:
    check_default_blind_autoplay_is_refused()
    check_missing_lua_script_is_refused_before_gui_setup()
    check_target_table_does_not_legitimize_legacy_autoplay()
    check_explicit_blind_autoplay_is_hard_capped()
    check_targeted_watch_is_not_capped()
    check_retired_long_autoplay_option_is_refused()
    check_staged_manual_outputs_are_mirrored()
    check_latest_manual_dump_record()
    check_bounded_target_miss_is_a_terminal_reason()
    print("OK: run_fceux_lua_analysis autoplay budget guard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
