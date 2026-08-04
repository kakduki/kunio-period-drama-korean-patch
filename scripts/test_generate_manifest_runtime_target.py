"""Tests for relocated manifest-candidate FCEUX target generation."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from generate_manifest_runtime_target import read_target, render_lua  # noqa: E402


def main() -> int:
    rom = bytearray(0x7000)
    pointer_index = 185
    pointer_offset = 0x05DD4 + pointer_index * 2
    record_offset = 0x05FDE
    cpu_address = 0x9FCE
    rom[pointer_offset:pointer_offset + 2] = cpu_address.to_bytes(2, "little")
    payload = bytes.fromhex("83 86 87 BB 85 00 82 81 84 CB FF")
    rom[record_offset:record_offset + len(payload)] = payload

    target = read_target(bytes(rom), pointer_index, 0x200)
    assert target["cpu_address"] == cpu_address
    assert target["record_rom_offset"] == record_offset
    assert target["prg_bank"] == 2
    assert target["bytes"] == payload
    with tempfile.TemporaryDirectory(prefix="manifest_target_test_") as directory:
        output = render_lua(Path(directory) / "candidate.nes", "abc123", [target])
    assert "manifest_ptr_185_candidate" in output
    assert "0x9FCE" in output
    assert "prg_bank = 2" in output
    assert "83 86 87 BB 85 00 82 81 84 CB FF" in output
    print("OK: relocated manifest runtime target generation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
