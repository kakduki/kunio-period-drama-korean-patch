#!/usr/bin/env python3
"""Analyze the local English IPS as a technical reference."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_MD5 = "0d406a85285b4de8468f0dab6aad5fe5"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, required=True)
    parser.add_argument("--ips", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "rom_analysis")
    args = parser.parse_args()
    rom = args.rom if args.rom.is_absolute() else ROOT / args.rom
    ips = args.ips if args.ips.is_absolute() else ROOT / args.ips
    if not rom.is_file() or not ips.is_file():
        raise SystemExit("ROM and IPS must both exist")
    digest = hashlib.md5(rom.read_bytes()).hexdigest()
    if digest != EXPECTED_MD5:
        raise SystemExit(f"unexpected base ROM MD5: {digest}")
    out = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "analyze_reference_ips.py"),
            str(rom),
            str(ips),
            "--json-output",
            str(out / "english_patch_reference.json"),
            "--markdown-output",
            str(out / "english_patch_reference.md"),
        ],
        cwd=ROOT,
        check=True,
    )
    print(f"English reference analysis: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
