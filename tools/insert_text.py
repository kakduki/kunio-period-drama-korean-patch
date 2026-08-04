#!/usr/bin/env python3
"""Compile the current reviewed pointer-text candidate from the Japanese base."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def inside_root(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except ValueError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("build/pointer_candidate"))
    parser.add_argument("--font", type=Path)
    parser.add_argument("--draft", type=Path)
    parser.add_argument("--english", type=Path)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--segments", type=Path)
    args = parser.parse_args()
    rom = args.rom if args.rom.is_absolute() else ROOT / args.rom
    if not rom.is_file():
        raise SystemExit(f"base ROM not found: {rom}")
    out = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out = out.resolve()
    command_base = [
        sys.executable,
        str(ROOT / "scripts" / "build_full_pointer_korean_candidate.py"),
        str(rom.resolve()),
    ]
    values = {
        "--font": args.font,
        "--draft": args.draft,
        "--english": args.english,
        "--plan": args.plan,
        "--segments": args.segments,
    }

    # The existing compiler writes a report with repository-relative paths. Run it
    # inside the repository when the caller requests an external artifact folder.
    build_root = ROOT / "build"
    build_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pointer_candidate_", dir=build_root) as temp:
        compiler_out = out if inside_root(out) else Path(temp)
        command = command_base + ["--out-dir", str(compiler_out)]
        for flag, value in values.items():
            if value:
                command.extend([flag, str(value if value.is_absolute() else ROOT / value)])
        subprocess.run(command, cwd=ROOT, check=True)
        if compiler_out != out:
            out.mkdir(parents=True, exist_ok=True)
            for source in compiler_out.iterdir():
                destination = out / source.name
                if source.is_file():
                    shutil.copy2(source, destination)
    print(f"pointer candidate: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
