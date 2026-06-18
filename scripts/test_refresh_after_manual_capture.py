#!/usr/bin/env python3
"""Check the manual capture refresh helper command lists."""

from __future__ import annotations

import io
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

import refresh_after_manual_capture as refresh


def check_next_queue_summary() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        refresh.print_next_queue_summary()
    out = buffer.getvalue()
    assert "next_manual_queue=actions=12 primary=9 routes=3" in out
    assert "next_manual_action=phase=primary_v042_visual_review target=0x0569D group=Hashi" in out


def check_no_record_skip() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        missing_dir = Path(raw_tmp) / "manual_screen_dump_v042"
        command = [
            "scripts/analyze_manual_screen_dump.py",
            "--input-dir",
            str(missing_dir),
            "--output",
            str(missing_dir / "summary.md"),
        ]
        assert refresh.command_has_manual_records(command) is False
        missing_dir.mkdir()
        (missing_dir / "manual_frame_000001_target_records.tsv").write_text("frame\tlabel\n1\ttest\n", encoding="utf-8")
        assert refresh.command_has_manual_records(command) is True


def main() -> int:
    primary = [" ".join(command) for command in refresh.PRIMARY_COMMANDS]
    broad = [" ".join(command) for command in refresh.BROAD_COMMANDS]

    assert any("analyze_manual_screen_dump.py" in command for command in primary)
    assert any("generate_manual_dump_inventory.py" in command for command in primary)
    assert any("generate_primary_visual_checklist.py" in command for command in primary)
    assert any("generate_patch_progress_dashboard.py" in command for command in primary)
    assert any("analyze_broad_scan_manual_dump.py" in command for command in broad)
    assert any("generate_route_proof_status.py" in command for command in broad)
    assert any("generate_manual_dump_inventory.py" in command for command in broad)
    assert any("generate_patch_progress_dashboard.py" in command for command in broad)
    assert primary[-2] == "scripts/generate_next_manual_run.py"
    assert broad[-2] == "scripts/generate_next_manual_run.py"
    assert primary[-1] == "scripts/generate_patch_progress_dashboard.py"
    assert broad[-1] == "scripts/generate_patch_progress_dashboard.py"
    check_no_record_skip()
    check_next_queue_summary()

    print("OK: manual capture refresh helper lists commands and prints the next queue summary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
