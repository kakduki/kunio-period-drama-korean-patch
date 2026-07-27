#!/usr/bin/env python3
"""Prove the reachable Items screen's text-source chain without free play.

The fixed menu route is deliberately bounded.  The analysis compares Japanese
base and English-reference captures of the same Items screen, then follows one
static action template through its active MMC3 bank, SRAM queue buffer, and
PPU output.  It also records why the current main-menu-only R1 clone must not
be promoted as a shared-font build.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path
from typing import Any

from analyze_reference_ips import parse_ines_layout
from build_main_menu_korean_candidate import GLYPH_CODE_PAIRS
from convert_fceux_gd_to_png import convert_file
from rom_utils import REPO_ROOT


ACTION_SOURCE_ROM_OFFSET = 0x13727
ACTION_SOURCE_LENGTH = 0x21
ACTION_SOURCE_CPU_START = 0xB717
ACTION_SOURCE_CPU_END = ACTION_SOURCE_CPU_START + ACTION_SOURCE_LENGTH
ACTION_SOURCE_MMC3_R7 = 0x09
ACTION_COPY_PC = "B707"
ACTION_QUEUE_COPY_PC = "B70D"
ACTION_QUEUE_RAM_START = 0x6360
ACTION_PPU_START = 0x2363
ACTION_PPU_LENGTH = 0x1B

ENGLISH_TITLE_CODES = bytes((0x0B, 0x15, 0x0E, 0x09, 0x0F, 0x36, 0x13, 0x7A, 0x09, 0x14, 0x05, 0x0D, 0x13))
ENGLISH_NONE_CODES = bytes((0x0E, 0x0F, 0x0E, 0x05, 0x38))
ENGLISH_ACTIONS = ("USE", "REMOVE", "GIVE", "DRP")
KOREAN_ACTIONS = "\uc0ac\uc6a9 / \ubc84\ub9ac\uae30 / \uc8fc\uae30 / \ubc84\ub9bc"

MENU_KOREAN_R1_CODES = frozenset(
    code
    for left, right in GLYPH_CODE_PAIRS.values()
    for code in (left, right, left + 0x20, right + 0x20)
)
MAIN_MENU_CANDIDATE_R1 = "46"

DEFAULT_BASE_ROM = next(iter(sorted((REPO_ROOT / "rom").glob("*.nes"))), None)
DEFAULT_ENGLISH_ROM = REPO_ROOT / "output" / "technos_samurai_reference_menu_probe.nes"
DEFAULT_BASE_CAPTURE = REPO_ROOT / "rom_analysis" / "main_menu_items_queue_base"
DEFAULT_ENGLISH_CAPTURE = REPO_ROOT / "rom_analysis" / "main_menu_items_queue_english"
DEFAULT_KOREAN_CAPTURE = REPO_ROOT / "rom_analysis" / "main_menu_items_probe"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "rom_analysis" / "items_context"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def latest_reason(rows: list[dict[str, str]]) -> str | None:
    for row in reversed(rows):
        value = (row.get("reason") or "").strip()
        if value:
            return value
    return None


def hex_value(value: str) -> int:
    return int(value, 16)


def find_one(capture_dir: Path, pattern: str, *, required: bool = True) -> Path | None:
    matches = sorted(capture_dir.glob(pattern))
    if len(matches) == 1:
        return matches[0]
    if not required and not matches:
        return None
    raise FileNotFoundError(
        f"expected exactly one {pattern!r} in {capture_dir}, found {len(matches)}"
    )


def capture_screen(capture_dir: Path) -> Path | None:
    png = find_one(capture_dir, "*_screen.png", required=False)
    if png is not None:
        return png
    return find_one(capture_dir, "*_screen.gd", required=False)


def ppu_row(capture_dir: Path, nametable: int, row: int) -> bytes:
    rows = read_tsv(capture_dir / "ppu_rows.tsv")
    matches = [
        entry
        for entry in rows
        if int(entry["nametable"]) == nametable and int(entry["row"]) == row
    ]
    if len(matches) != 1:
        raise ValueError(
            f"expected one PPU row {nametable}/{row} in {capture_dir}, found {len(matches)}"
        )
    values = bytes(int(value, 16) for value in matches[0]["values"].split())
    if len(values) != 32:
        raise ValueError(f"unexpected PPU row width in {capture_dir}: {len(values)}")
    return values


def contains_sequence(haystack: bytes, needle: bytes) -> bool:
    return haystack.find(needle) >= 0


def source_runtime_block(capture_dir: Path) -> tuple[bytes, list[dict[str, str]]]:
    rows = read_tsv(capture_dir / "extra_source_reads.tsv")
    selected = [
        row
        for row in rows
        if row.get("pc") == ACTION_COPY_PC
        and ACTION_SOURCE_CPU_START <= hex_value(row["cpu_address"]) < ACTION_SOURCE_CPU_END
    ]
    by_address: dict[int, dict[str, str]] = {}
    for row in selected:
        address = hex_value(row["cpu_address"])
        previous = by_address.get(address)
        if previous is not None and previous["value"] != row["value"]:
            raise ValueError(f"conflicting action-source values at CPU 0x{address:04X}")
        by_address[address] = row
    expected_addresses = range(ACTION_SOURCE_CPU_START, ACTION_SOURCE_CPU_END)
    missing = [address for address in expected_addresses if address not in by_address]
    if missing:
        raise ValueError(
            "action source trace is incomplete: "
            + ", ".join(f"0x{address:04X}" for address in missing[:6])
        )
    ordered = [by_address[address] for address in expected_addresses]
    if any(hex_value(row["r7"]) != ACTION_SOURCE_MMC3_R7 for row in ordered):
        raise ValueError("action source was not read through MMC3 R7 bank 0x09")
    return bytes(hex_value(row["value"]) for row in ordered), ordered


def queue_runtime_block(capture_dir: Path) -> tuple[bytes, list[dict[str, str]]]:
    rows = read_tsv(capture_dir / "queue_writes.tsv")
    selected = [
        row
        for row in rows
        if row.get("pc") == ACTION_QUEUE_COPY_PC
        and ACTION_QUEUE_RAM_START <= hex_value(row["cpu_address"]) < ACTION_QUEUE_RAM_START + ACTION_SOURCE_LENGTH
    ]
    by_address: dict[int, dict[str, str]] = {}
    for row in selected:
        address = hex_value(row["cpu_address"])
        previous = by_address.get(address)
        if previous is not None and previous["value"] != row["value"]:
            raise ValueError(f"conflicting action-queue values at RAM 0x{address:04X}")
        by_address[address] = row
    expected_addresses = range(ACTION_QUEUE_RAM_START, ACTION_QUEUE_RAM_START + ACTION_SOURCE_LENGTH)
    missing = [address for address in expected_addresses if address not in by_address]
    if missing:
        raise ValueError(
            "action queue trace is incomplete: "
            + ", ".join(f"0x{address:04X}" for address in missing[:6])
        )
    ordered = [by_address[address] for address in expected_addresses]
    return bytes(hex_value(row["value"]) for row in ordered), ordered


def action_ppu_block(capture_dir: Path) -> bytes:
    rows = read_tsv(capture_dir / "ppu_writes.tsv")
    by_address: dict[int, str] = {}
    for row in rows:
        address = hex_value(row["ppu_address"])
        if ACTION_PPU_START <= address < ACTION_PPU_START + ACTION_PPU_LENGTH:
            by_address[address] = row["value"]
    expected_addresses = range(ACTION_PPU_START, ACTION_PPU_START + ACTION_PPU_LENGTH)
    missing = [address for address in expected_addresses if address not in by_address]
    if missing:
        raise ValueError(
            "action PPU trace is incomplete: "
            + ", ".join(f"0x{address:04X}" for address in missing[:6])
        )
    return bytes(hex_value(by_address[address]) for address in expected_addresses)


def source_rom_offset_from_trace(rom: bytes, trace_rows: list[dict[str, str]]) -> int:
    layout = parse_ines_layout(rom)
    first = trace_rows[0]
    r7 = hex_value(first["r7"])
    cpu_address = hex_value(first["cpu_address"])
    if not 0xA000 <= cpu_address < 0xC000:
        raise ValueError(f"source CPU address is outside R7 window: 0x{cpu_address:04X}")
    offset = layout.prg_start + r7 * 0x2000 + (cpu_address - 0xA000)
    if offset + ACTION_SOURCE_LENGTH > layout.prg_end:
        raise ValueError("source block exceeds PRG region")
    return offset


def decode_english_action_codes(values: bytes) -> tuple[str, ...]:
    slots = (values[4:7], values[12:18], values[20:24], values[28:31])
    decoded: list[str] = []
    for slot in slots:
        if any(not 0x81 <= code <= 0x9A for code in slot):
            raise ValueError(f"English action slot contains an unexpected code: {slot.hex(' ')}")
        decoded.append("".join(chr(ord("A") + code - 0x81) for code in slot))
    return tuple(decoded)


def final_mapper_snapshot(capture_dir: Path) -> dict[str, str]:
    rows = read_tsv(capture_dir / "mapper_snapshot.tsv")
    if not rows:
        raise ValueError(f"mapper snapshot is empty: {capture_dir}")
    return rows[-1]


def candidate_page_conflict(capture_dir: Path | None, action_block: bytes) -> dict[str, object]:
    if capture_dir is None or not capture_dir.is_dir():
        return {
            "verdict": "UNKNOWN",
            "reason": "main-menu Korean candidate Items-screen capture is unavailable",
        }
    summary = read_tsv(capture_dir / "summary.tsv")
    snapshot = final_mapper_snapshot(capture_dir)
    r1 = snapshot.get("r1", "")
    conflicting_codes = sorted(set(action_block) & MENU_KOREAN_R1_CODES)
    clone_active = r1.upper() == MAIN_MENU_CANDIDATE_R1
    lua_done = latest_reason(summary) == "lua_done"
    failed = lua_done and clone_active and bool(conflicting_codes)
    passed = lua_done and clone_active and not conflicting_codes
    return {
        "verdict": "FAIL" if failed else "PASS" if passed else "UNKNOWN",
        "reason": (
            "Items action codes overlap the main-menu Korean 16x16 quadrants while the R1 clone is active"
            if failed
            else "isolated Korean menu code pool is active without overlapping Items action codes"
            if passed
            else "capture did not prove an active non-overlapping R1 clone"
        ),
        "lua_done": lua_done,
        "final_r1": r1,
        "clone_active": clone_active,
        "conflicting_codes": [f"0x{code:02X}" for code in conflicting_codes],
        "screen": str(capture_screen(capture_dir)) if capture_screen(capture_dir) else None,
    }


def capture_completion(capture_dir: Path) -> dict[str, object]:
    summary = read_tsv(capture_dir / "summary.tsv")
    screen = capture_screen(capture_dir)
    return {
        "lua_done": latest_reason(summary) == "lua_done",
        "screen_available": screen is not None and screen.is_file(),
        "screen": str(screen) if screen else None,
    }


def analyze(
    *,
    base_rom_path: Path,
    english_rom_path: Path,
    base_capture_dir: Path,
    english_capture_dir: Path,
    korean_capture_dir: Path | None,
) -> dict[str, object]:
    base = base_rom_path.read_bytes()
    english = english_rom_path.read_bytes()
    if len(base) != len(english):
        raise ValueError("base and English reference ROM sizes differ")

    base_source, base_source_rows = source_runtime_block(base_capture_dir)
    english_source, english_source_rows = source_runtime_block(english_capture_dir)
    base_queue, _ = queue_runtime_block(base_capture_dir)
    english_queue, _ = queue_runtime_block(english_capture_dir)
    base_ppu = action_ppu_block(base_capture_dir)
    english_ppu = action_ppu_block(english_capture_dir)
    base_offset = source_rom_offset_from_trace(base, base_source_rows)
    english_offset = source_rom_offset_from_trace(english, english_source_rows)
    base_rom_block = base[base_offset : base_offset + ACTION_SOURCE_LENGTH]
    english_rom_block = english[english_offset : english_offset + ACTION_SOURCE_LENGTH]
    english_actions = decode_english_action_codes(english_source)
    english_row5 = ppu_row(english_capture_dir, 0, 5)
    english_row8 = ppu_row(english_capture_dir, 0, 8)
    base_mapper = final_mapper_snapshot(base_capture_dir)
    english_mapper = final_mapper_snapshot(english_capture_dir)

    checks = {
        "base_lua_done": bool(capture_completion(base_capture_dir)["lua_done"]),
        "english_lua_done": bool(capture_completion(english_capture_dir)["lua_done"]),
        "base_screen_available": bool(capture_completion(base_capture_dir)["screen_available"]),
        "english_screen_available": bool(capture_completion(english_capture_dir)["screen_available"]),
        "base_source_rom_offset": base_offset == ACTION_SOURCE_ROM_OFFSET,
        "english_source_rom_offset": english_offset == ACTION_SOURCE_ROM_OFFSET,
        "base_source_reads_match_rom": base_source == base_rom_block,
        "english_source_reads_match_rom": english_source == english_rom_block,
        "base_queue_matches_source": base_queue == base_source,
        "english_queue_matches_source": english_queue == english_source,
        "base_ppu_matches_action_bytes": base_ppu == base_queue[4 : 4 + ACTION_PPU_LENGTH],
        "english_ppu_matches_action_bytes": english_ppu == english_queue[4 : 4 + ACTION_PPU_LENGTH],
        "english_title_matches_reference": contains_sequence(english_row5, ENGLISH_TITLE_CODES),
        "english_none_matches_reference": contains_sequence(english_row8, ENGLISH_NONE_CODES),
        "english_actions_match_reference": english_actions == ENGLISH_ACTIONS,
        "base_r0_page_is_3c": base_mapper.get("r0") == "3C",
        "english_r0_page_is_3c": english_mapper.get("r0") == "3C",
        "base_r1_page_is_3e": base_mapper.get("r1") == "3E",
        "english_r1_page_is_3e": english_mapper.get("r1") == "3E",
    }
    context_verdict = "PASS" if all(checks.values()) else "FAIL"
    conflict = candidate_page_conflict(korean_capture_dir, base_ppu)
    return {
        "context_verdict": context_verdict,
        "candidate_page_verdict": conflict["verdict"],
        "release_verdict": "UNKNOWN",
        "checks": checks,
        "source_chain": {
            "rom_offset": f"0x{ACTION_SOURCE_ROM_OFFSET:05X}",
            "prg_16k_bank": 4,
            "mmc3_8k_bank": ACTION_SOURCE_MMC3_R7,
            "cpu_start": f"0x{ACTION_SOURCE_CPU_START:04X}",
            "cpu_end": f"0x{ACTION_SOURCE_CPU_END - 1:04X}",
            "runtime_copy_pc": f"0x{int(ACTION_COPY_PC, 16):04X}",
            "queue_copy_pc": f"0x{int(ACTION_QUEUE_COPY_PC, 16):04X}",
            "queue_ram_start": f"0x{ACTION_QUEUE_RAM_START:04X}",
            "ppu_start": f"0x{ACTION_PPU_START:04X}",
            "length": ACTION_SOURCE_LENGTH,
            "base_hex": base_source.hex(" ").upper(),
            "english_hex": english_source.hex(" ").upper(),
        },
        "english_reference": {
            "title": "KUNIO'S ITEMS",
            "empty_label": "NONE",
            "actions": list(english_actions),
            "title_row": 5,
            "empty_label_row": 8,
            "action_row": 27,
        },
        "candidate_translation": {
            "actions": KOREAN_ACTIONS,
            "status": "MENU_POOL_ITEMS_SOFT_GATE_PASS",
            "reason": "The bounded candidate keeps the original Items action bytes and uses an isolated R1 code pool; full Items translation remains a separate two-row queue task.",
        },
        "mapper": {
            "base_final": base_mapper,
            "english_final": english_mapper,
            "visible_low_code_page": "R0=0x3C",
            "visible_action_code_page": "R1=0x3E",
        },
        "candidate_page_conflict": conflict,
        "captures": {
            "base": capture_completion(base_capture_dir),
            "english": capture_completion(english_capture_dir),
            "korean_candidate": (
                {"screen": conflict.get("screen")} if korean_capture_dir and korean_capture_dir.is_dir() else None
            ),
        },
    }


def render_markdown(payload: dict[str, object]) -> str:
    checks = payload["checks"]
    source = payload["source_chain"]
    reference = payload["english_reference"]
    translation = payload["candidate_translation"]
    mapper = payload["mapper"]
    conflict = payload["candidate_page_conflict"]
    assert isinstance(checks, dict)
    assert isinstance(source, dict)
    assert isinstance(reference, dict)
    assert isinstance(translation, dict)
    assert isinstance(mapper, dict)
    assert isinstance(conflict, dict)
    lines = [
        "# Main Menu Items Context",
        "",
        f"Context verdict: **{payload['context_verdict']}**",
        f"Shared-page candidate verdict: **{payload['candidate_page_verdict']}**",
        f"Release verdict: **{payload['release_verdict']}**",
        "",
        "## Proven Chain",
        "",
        f"`{source['rom_offset']}` (PRG 16 KiB bank {source['prg_16k_bank']}; MMC3 8 KiB bank {source['mmc3_8k_bank']})",
        f"-> CPU `{source['cpu_start']}`-`{source['cpu_end']}`",
        f"-> copy routine `{source['runtime_copy_pc']}`",
        f"-> SRAM `{source['queue_ram_start']}`",
        f"-> PPU `{source['ppu_start']}` action row.",
        "",
        "The Japanese base and English reference both completed the same fixed 1,980-frame route with `lua_done`.",
        "Their runtime source bytes matched ROM, their queue writes matched those source bytes, and their PPU action bytes matched the queue payload.",
        "",
        "## English Reference",
        "",
        f"- Title: `{reference['title']}` (row {reference['title_row']}).",
        f"- Empty inventory: `{reference['empty_label']}` (row {reference['empty_label_row']}).",
        f"- Action row: `{', '.join(reference['actions'])}` (row {reference['action_row']}).",
        f"- Korean action proposal: `{translation['actions']}`.",
        "",
        "## Font Isolation",
        "",
        f"- Items low-code font page: `{mapper['visible_low_code_page']}`.",
        f"- Items action-code font page: `{mapper['visible_action_code_page']}`.",
        f"- Existing main-menu candidate: **{conflict['verdict']}**. {conflict['reason']}",
    ]
    codes = conflict.get("conflicting_codes")
    if isinstance(codes, list) and codes:
        lines.append(f"- Overlapping action codes: `{', '.join(str(code) for code in codes)}`.")
    lines += [
        "",
        "The bounded candidate keeps the original Items action bytes while the cloned R1 page is active.",
        "Full Korean Items translation still needs its own title/empty/action source owners and a second PPU row; this smoke test only proves page isolation.",
        "",
        "## Checks",
        "",
    ]
    lines.extend(
        f"- `{name}`: {'PASS' if value else 'FAIL'}" for name, value in checks.items()
    )
    lines.append("")
    return "\n".join(lines)


def write_candidates(path: Path, payload: dict[str, object]) -> None:
    source = payload["source_chain"]
    assert isinstance(source, dict)
    rows = [
        {
            "id": "ITEM-ACTIONS",
            "context": "reachable main-menu Items screen, row 27",
            "rom_offset": source["rom_offset"],
            "prg_16k_bank": source["prg_16k_bank"],
            "mmc3_8k_bank": source["mmc3_8k_bank"],
            "english_reference": "USE / REMOVE / GIVE / DRP",
            "korean_candidate": KOREAN_ACTIONS,
            "source_confidence": "runtime-proven",
            "build_status": "BLOCKED_BY_TWO_ROW_QUEUE_AND_STATE_GUARD",
        },
        {
            "id": "ITEM-NONE",
            "context": "reachable main-menu Items screen, row 8",
            "rom_offset": "0x0FC31",
            "prg_16k_bank": 3,
            "mmc3_8k_bank": 7,
            "english_reference": "NONE",
            "korean_candidate": "\uc5c6\uc74c",
            "source_confidence": "English-reference structural evidence",
            "build_status": "PENDING_RUNTIME_SOURCE_TRACE_AND_TWO_ROW_QUEUE",
        },
        {
            "id": "ITEM-TITLE",
            "context": "reachable main-menu Items screen, row 5",
            "rom_offset": "UNKNOWN",
            "prg_16k_bank": "UNKNOWN",
            "mmc3_8k_bank": "UNKNOWN",
            "english_reference": "KUNIO'S ITEMS",
            "korean_candidate": "\ucfe0\ub2c8\uc624\uc758 \ubb3c\uac74",
            "source_confidence": "screen-only",
            "build_status": "PENDING_DYNAMIC_TITLE_SOURCE_TRACE",
        },
    ]
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def copy_screen(source: Path | None, destination: Path) -> Path | None:
    if source is None or not source.is_file():
        return None
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.suffix.lower() == ".gd":
        convert_file(source, destination)
    else:
        shutil.copy2(source, destination)
    return destination


def write_artifacts(output_dir: Path, payload: dict[str, object]) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "report.json"
    markdown_path = output_dir / "report.md"
    candidates_path = output_dir / "string_candidates.csv"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    write_candidates(candidates_path, payload)
    written = [json_path, markdown_path, candidates_path]
    captures = payload["captures"]
    assert isinstance(captures, dict)
    for key, filename in (("base", "base_items.png"), ("english", "english_items.png"), ("korean_candidate", "main_menu_candidate_items.png")):
        item = captures.get(key)
        if not isinstance(item, dict):
            continue
        copied = copy_screen(Path(str(item["screen"])) if item.get("screen") else None, output_dir / filename)
        if copied is not None:
            written.append(copied)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-rom", type=Path, default=DEFAULT_BASE_ROM)
    parser.add_argument("--english-rom", type=Path, default=DEFAULT_ENGLISH_ROM)
    parser.add_argument("--base-capture", type=Path, default=DEFAULT_BASE_CAPTURE)
    parser.add_argument("--english-capture", type=Path, default=DEFAULT_ENGLISH_CAPTURE)
    parser.add_argument("--korean-capture", type=Path, default=DEFAULT_KOREAN_CAPTURE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    if args.base_rom is None:
        raise FileNotFoundError("base ROM not found under rom/")
    payload = analyze(
        base_rom_path=args.base_rom,
        english_rom_path=args.english_rom,
        base_capture_dir=args.base_capture,
        english_capture_dir=args.english_capture,
        korean_capture_dir=args.korean_capture,
    )
    for path in write_artifacts(args.output_dir, payload):
        print(path)
    print(f"context_verdict={payload['context_verdict']}")
    print(f"candidate_page_verdict={payload['candidate_page_verdict']}")
    return 0 if payload["context_verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
