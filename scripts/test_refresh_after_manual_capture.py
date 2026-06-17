#!/usr/bin/env python3
"""Check the manual capture refresh helper command lists."""

from __future__ import annotations

import refresh_after_manual_capture as refresh


def main() -> int:
    primary = [" ".join(command) for command in refresh.PRIMARY_COMMANDS]
    broad = [" ".join(command) for command in refresh.BROAD_COMMANDS]

    assert any("analyze_manual_screen_dump.py" in command for command in primary)
    assert any("generate_primary_visual_checklist.py" in command for command in primary)
    assert any("analyze_broad_scan_manual_dump.py" in command for command in broad)
    assert any("generate_route_proof_status.py" in command for command in broad)
    assert primary[-1] == "scripts/generate_next_manual_run.py"
    assert broad[-1] == "scripts/generate_next_manual_run.py"

    print("OK: manual capture refresh helper lists primary and broad refresh commands.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
