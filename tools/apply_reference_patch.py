#!/usr/bin/env python3
"""Apply a reference IPS to an external analysis copy, never the source ROM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _analysis_common import apply_ips, hashes, load  # noqa: E402


EXPECTED_BASE_MD5 = "0d406a85285b4de8468f0dab6aad5fe5"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path)
    parser.add_argument("patch", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    base = args.base.resolve()
    patch = args.patch.resolve()
    output = args.output.resolve()
    if base == output:
        raise SystemExit("refusing to overwrite the base ROM")
    if output.exists() and not args.force:
        raise SystemExit(f"output exists; use --force: {output}")
    before = load(base)
    patch_data = load(patch)
    before_hashes = hashes(before)
    if before_hashes["md5"] != EXPECTED_BASE_MD5:
        raise SystemExit(f"unexpected reference base MD5: {before_hashes['md5']}")
    after = apply_ips(before, patch_data)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(after)
    report_path = (args.report or output.with_suffix(".json")).resolve()
    report = {
        "base": {"path": str(base), **before_hashes},
        "ips": {"path": str(patch), **hashes(patch_data)},
        "analysis_copy": {"path": str(output), **hashes(after)},
        "source_rom_written": False,
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
