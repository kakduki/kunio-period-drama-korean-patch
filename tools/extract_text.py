#!/usr/bin/env python3
"""Run the project's conservative pointer-dialogue catalog extraction."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SIZE = 262_160
EXPECTED_MD5 = "0d406a85285b4de8468f0dab6aad5fe5"


def verify_base(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"base ROM not found: {path}")
    data = path.read_bytes()
    digest = hashlib.md5(data).hexdigest()
    if len(data) != EXPECTED_SIZE or digest != EXPECTED_MD5:
        raise SystemExit(
            f"unexpected base ROM: size={len(data)} md5={digest}; "
            f"expected size={EXPECTED_SIZE} md5={EXPECTED_MD5}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, required=True, help="verified Japanese base ROM")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "rom_analysis")
    args = parser.parse_args()

    rom = args.rom if args.rom.is_absolute() else ROOT / args.rom
    verify_base(rom)
    out = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(ROOT / "scripts" / "build_pointer_dialogue_catalog.py"),
        "--english-dump",
        str(ROOT / "rom_analysis" / "english_script_dump.tsv"),
        "--conservative-catalog",
        str(ROOT / "rom_analysis" / "pointer_dialogue_catalog.tsv"),
        "--output-tsv",
        str(out / "pointer_dialogue_catalog.tsv"),
        "--output-json",
        str(out / "pointer_dialogue_catalog.json"),
        "--output-markdown",
        str(out / "pointer_dialogue_catalog.md"),
    ]
    subprocess.run(command, cwd=ROOT, check=True)
    print(f"extracted structural catalog: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
