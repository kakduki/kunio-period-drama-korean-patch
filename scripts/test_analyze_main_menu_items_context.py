#!/usr/bin/env python3
"""Synthetic checks for the bounded Items-screen source-chain analyzer."""

from __future__ import annotations

import tempfile
from pathlib import Path

from analyze_main_menu_items_context import (
    ACTION_PPU_LENGTH,
    ACTION_PPU_START,
    ACTION_QUEUE_RAM_START,
    ACTION_SOURCE_CPU_START,
    ACTION_SOURCE_LENGTH,
    ACTION_SOURCE_ROM_OFFSET,
    ENGLISH_NONE_CODES,
    ENGLISH_TITLE_CODES,
    analyze,
    write_artifacts,
)


BASE_BLOCK = bytes.fromhex(
    "23 63 00 1B 92 86 83 00 00 00 00 00 9A 8D 8D 00 "
    "00 00 00 00 AC 90 8D 00 00 00 00 00 8D 93 A9 23 4C"
)
ENGLISH_BLOCK = bytes.fromhex(
    "23 63 00 1B 95 93 85 00 00 00 00 00 92 85 8D 8F "
    "96 85 00 00 87 89 96 85 00 00 00 00 84 92 90 23 4C"
)


def make_rom(path: Path, block: bytes) -> None:
    data = bytearray(0x40010)
    data[:4] = b"NES\x1a"
    data[4] = 8
    data[5] = 16
    data[ACTION_SOURCE_ROM_OFFSET : ACTION_SOURCE_ROM_OFFSET + ACTION_SOURCE_LENGTH] = block
    path.write_bytes(data)


def row(values: bytes) -> str:
    return " ".join(f"{value:02X}" for value in values)


def make_capture(path: Path, block: bytes, *, english: bool, r1: str = "3E") -> None:
    path.mkdir(parents=True)
    (path / "summary.tsv").write_text("frame\treason\n0\tlua_start\n1960\tlua_done\n", encoding="utf-8")
    (path / "mapper_snapshot.tsv").write_text(
        "frame\tmapper_control\tmapper_select\tppu_control\tr0\tr1\n"
        f"1960\t07\t7\t88\t3C\t{r1}\n",
        encoding="utf-8",
    )
    title = bytearray(32)
    empty = bytearray(32)
    if english:
        title[8 : 8 + len(ENGLISH_TITLE_CODES)] = ENGLISH_TITLE_CODES
        empty[6 : 6 + len(ENGLISH_NONE_CODES)] = ENGLISH_NONE_CODES
    (path / "ppu_rows.tsv").write_text(
        "nametable\trow\tvalues\n"
        f"0\t5\t{row(bytes(title))}\n"
        f"0\t8\t{row(bytes(empty))}\n",
        encoding="utf-8",
    )
    source_lines = ["frame\tcpu_address\tvalue\tpc\ta\tx\ty\tmapper_control\tr6\tr7"]
    queue_lines = ["frame\tcpu_address\tvalue\tpc\ta\tx\ty\tmapper_control\tr6\tr7"]
    for index, value in enumerate(block):
        source_lines.append(f"1912\t{ACTION_SOURCE_CPU_START + index:04X}\t{value:02X}\tB707\t00\t{index:02X}\t{index:02X}\t07\t08\t09")
        queue_lines.append(f"1912\t{ACTION_QUEUE_RAM_START + index:04X}\t{value:02X}\tB70D\t{value:02X}\t{index:02X}\t{index:02X}\t07\t08\t09")
    (path / "extra_source_reads.tsv").write_text("\n".join(source_lines) + "\n", encoding="utf-8")
    (path / "queue_writes.tsv").write_text("\n".join(queue_lines) + "\n", encoding="utf-8")
    ppu_lines = ["frame\tppu_address\tvalue\tpc"]
    for index, value in enumerate(block[4 : 4 + ACTION_PPU_LENGTH]):
        ppu_lines.append(f"1912\t{ACTION_PPU_START + index:04X}\t{value:02X}\tD728")
    (path / "ppu_writes.tsv").write_text("\n".join(ppu_lines) + "\n", encoding="utf-8")
    (path / "main_menu_frame_001960_screen.png").write_bytes(b"screen")


def main() -> int:
    with tempfile.TemporaryDirectory() as raw_tmp:
        root = Path(raw_tmp)
        base_rom = root / "base.nes"
        english_rom = root / "english.nes"
        make_rom(base_rom, BASE_BLOCK)
        make_rom(english_rom, ENGLISH_BLOCK)
        base_capture = root / "base"
        english_capture = root / "english"
        korean_capture = root / "korean"
        make_capture(base_capture, BASE_BLOCK, english=False)
        make_capture(english_capture, ENGLISH_BLOCK, english=True)
        make_capture(korean_capture, BASE_BLOCK, english=False, r1="46")

        payload = analyze(
            base_rom_path=base_rom,
            english_rom_path=english_rom,
            base_capture_dir=base_capture,
            english_capture_dir=english_capture,
            korean_capture_dir=korean_capture,
        )
        assert payload["context_verdict"] == "PASS"
        assert payload["candidate_page_verdict"] == "PASS"
        assert payload["candidate_translation"]["status"] == "MENU_POOL_ITEMS_SOFT_GATE_PASS"
        assert all(payload["checks"].values())
        assert payload["source_chain"]["rom_offset"] == "0x13727"
        paths = write_artifacts(root / "report", payload)
        assert len(paths) >= 5
        assert (root / "report" / "report.md").is_file()
        assert "ITEM-ACTIONS" in (root / "report" / "string_candidates.csv").read_text(encoding="utf-8")
    print("Main-menu Items context analyzer tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
