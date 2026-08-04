#!/usr/bin/env python3
"""Check that candidate reports support both repository and temp outputs."""

from __future__ import annotations

from pathlib import Path

from build_full_pointer_korean_candidate import display_path
from rom_utils import REPO_ROOT


def main() -> int:
    inside = REPO_ROOT / "output" / "candidate.nes"
    outside = Path("C:/tmp/kunio_source_rebuild/candidate.nes")
    assert display_path(inside) == "output/candidate.nes"
    assert display_path(outside).replace("\\", "/") == "C:/tmp/kunio_source_rebuild/candidate.nes"
    print("OK: candidate report paths handle repository and external outputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
