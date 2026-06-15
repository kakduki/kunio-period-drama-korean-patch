#!/usr/bin/env python3
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]


def find_rom_path() -> Path:
    if len(sys.argv) > 1:
        rom_path = Path(sys.argv[1]).expanduser()
        if rom_path.exists():
            return rom_path
        raise FileNotFoundError(f"ROM not found: {rom_path}")

    rom_dir = REPO_ROOT / "rom"
    roms = sorted(rom_dir.glob("*.nes"))
    if roms:
        return roms[0]

    raise FileNotFoundError(
        "ROM not found. Put a .nes file in the rom/ folder, "
        "or pass the ROM path as the first argument."
    )


def analysis_dir(name: str | None = None) -> Path:
    path = REPO_ROOT / "rom_analysis"
    if name:
        path = path / name
    path.mkdir(parents=True, exist_ok=True)
    return path
