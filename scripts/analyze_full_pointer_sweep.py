#!/usr/bin/env python3
"""Audit bounded forced renders for every full-pointer Korean record."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from PIL import Image

from rom_utils import REPO_ROOT


POINTER_COUNT = 248
PAGE_STATE_ADDRESS = 0x07FF
POINTER_TABLE_ROM_OFFSET = 0x05DD4
PRG_BANK1_ROM_START = 0x04010
DEFAULT_SWEEP_ROOT = Path(r"C:\tmp\kunio_full_pointer_sweep")
DEFAULT_ROM = REPO_ROOT / "output" / "full_korean_candidate" / "kunio_period_drama_korean_full_candidate.nes"
DEFAULT_PLAN = REPO_ROOT / "rom_analysis" / "pointer_font_page_plan.json"
DEFAULT_ENGLISH = REPO_ROOT / "rom_analysis" / "english_script_dump.tsv"
DEFAULT_JSON = REPO_ROOT / "rom_analysis" / "full_pointer_sweep_runtime.json"
DEFAULT_MARKDOWN = REPO_ROOT / "rom_analysis" / "full_pointer_sweep_runtime.md"


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def image_metrics(path: Path | None) -> dict[str, int | bool]:
    if path is None or not path.exists():
        return {
            "field_unique_colors": 0,
            "field_nonblack_pixels": 0,
            "bottom_nonblack_pixels": 0,
            "text_pixels_present": False,
            "field_background_present": False,
        }
    with Image.open(path).convert("RGB") as image:
        bottom = image.crop((0, image.height * 3 // 4, image.width, image.height))
        field = image.crop((0, 24, image.width, image.height * 3 // 4))
        field_colors = field.getcolors(maxcolors=field.width * field.height) or []
        bottom_nonblack = sum(
            max(pixel) > 24 for pixel in bottom.getdata()
        )
        field_nonblack = sum(
            max(pixel) > 24 for pixel in field.getdata()
        )
    return {
        "field_unique_colors": len(field_colors),
        "field_nonblack_pixels": field_nonblack,
        "bottom_nonblack_pixels": bottom_nonblack,
        "text_pixels_present": bottom_nonblack >= 20,
        "field_background_present": (
            len(field_colors) >= 8 and field_nonblack >= 1000
        ),
    }


def pointer_cpu(rom: bytes, index: int) -> int:
    offset = POINTER_TABLE_ROM_OFFSET + index * 2
    return int.from_bytes(rom[offset : offset + 2], "little")


def candidate_has_terminator(rom: bytes, cpu: int, limit: int = 0x0400) -> bool:
    if not 0x8000 <= cpu <= 0xBFFF:
        return False
    offset = PRG_BANK1_ROM_START + cpu - 0x8000
    return 0xFF in rom[offset : min(offset + limit, len(rom))]


def expected_record_terminated(english_rows: dict[int, dict[str, str]], index: int) -> bool:
    raw = english_rows.get(index, {}).get("en_raw_bytes", "")
    return bool(raw) and raw.split()[-1].upper() == "FF"


def source_mode(source_rows: list[dict[str, str]], static_terminated: bool, excluded: bool) -> str:
    if excluded:
        return "EXCLUDED_NON_DIALOGUE"
    values = {int(row["value"], 16) for row in source_rows if row.get("value")}
    if 0xFF in values:
        return "DIRECT_TRACE_TERMINATOR"
    if static_terminated:
        if values & {0xF0, 0xF1, 0xF8, 0xF9, 0xFA, 0xFB}:
            return "CONTROL_STREAM_STATIC_TERMINATOR"
        return "STATIC_TERMINATOR_NOT_REACHED_BY_WATCH"
    return "UNKNOWN_SOURCE_END"


def audit_pointer(
    index: int,
    rom: bytes,
    assignments: list[int | None],
    english_rows: dict[int, dict[str, str]],
    root: Path,
) -> dict[str, object]:
    directory = root / f"ptr{index:03d}"
    summary = read_tsv(directory / "summary.tsv")
    forced = read_tsv(directory / "forced_pointer.tsv")
    source = read_tsv(directory / "source_reads.tsv")
    mapper = read_tsv(directory / "mapper_state.tsv")
    ram_files = sorted(directory.glob("*_cpu_ram.bin"))
    screen_files = sorted(directory.glob("*_screen.png"))
    ram = ram_files[-1].read_bytes() if ram_files else b""
    final = summary[-1] if summary else {}
    capture = next((row for row in summary if row.get("reason") == "capture"), {})
    cpu = pointer_cpu(rom, index)
    page = assignments[index]
    excluded = page is None
    static_terminated = candidate_has_terminator(rom, cpu)
    expected_terminated = expected_record_terminated(english_rows, index)
    page_state = ram[PAGE_STATE_ADDRESS] if len(ram) > PAGE_STATE_ADDRESS else None
    forced_id = any(
        int(row.get("pointer_index", "-1")) == index
        and int(row.get("dialogue_id", "-1"), 16) == index + 1
        for row in forced
    )
    source_addresses = {row.get("address") for row in source}
    metrics = image_metrics(screen_files[-1] if screen_files else None)
    checks = {
        "lua_done": final.get("reason") == "lua_done",
        "target_seen": final.get("target_seen") == "true",
        "capture_screenshot": capture.get("screenshot") == "true",
        "forced_id_written": forced_id,
        "source_progress_or_control": bool(source),
        "page_state": page is None or page_state == page + 1,
        "text_pixels_present": metrics["text_pixels_present"],
        "field_background_present": metrics["field_background_present"],
        "static_terminator": (not expected_terminated) or static_terminated,
    }
    if excluded:
        status = "PASS_EXCLUDED_ROUTER" if all(checks.values()) else "FAIL_EXCLUDED_ROUTER"
    else:
        status = "PASS_ACTIVE_RENDERER" if all(checks.values()) else "FAIL_ACTIVE_RENDERER"
    return {
        "pointer_index": index,
        "target_cpu": f"0x{cpu:04X}",
        "page_index": page,
        "excluded": excluded,
        "page_state": None if page_state is None else f"0x{page_state:02X}",
        "mapper_r1_at_capture": mapper[-1].get("r1") if mapper else None,
        "source_mode": source_mode(source, static_terminated, excluded),
        "source_address_count": len(source_addresses),
        "source_row_count": len(source),
        "expected_static_terminator": expected_terminated,
        "static_terminator_found": static_terminated,
        "image": metrics,
        "checks": checks,
        "status": status,
        "directory": str(directory),
    }


def build_report(
    root: Path,
    rom_path: Path,
    plan_path: Path,
    english_path: Path,
) -> dict[str, object]:
    rom = rom_path.read_bytes()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    assignments = plan["pointer_page_assignments"]
    english_rows = {
        int(row["pointer_index"]): row
        for row in read_tsv(english_path)
        if row.get("record_kind") == "pointer_pair"
    }
    if len(assignments) != POINTER_COUNT:
        raise ValueError(f"expected {POINTER_COUNT} page assignments")
    rows = [audit_pointer(i, rom, assignments, english_rows, root) for i in range(POINTER_COUNT)]
    active = [row for row in rows if not row["excluded"]]
    excluded = [row for row in rows if row["excluded"]]
    return {
        "status": "PASS" if all(row["status"].startswith("PASS") for row in rows) else "FAIL",
        "release_status": "NOT_READY",
        "sweep_root": str(root),
        "rom": str(rom_path),
        "pointer_count": POINTER_COUNT,
        "active_count": len(active),
        "excluded_count": len(excluded),
        "active_pass_count": sum(row["status"] == "PASS_ACTIVE_RENDERER" for row in active),
        "excluded_pass_count": sum(row["status"] == "PASS_EXCLUDED_ROUTER" for row in excluded),
        "source_modes": dict(Counter(str(row["source_mode"]) for row in rows)),
        "capture_r1_values": sorted({row["mapper_r1_at_capture"] for row in rows if row["mapper_r1_at_capture"]}),
        "notes": [
            "Active rows are forced renderer checks, not natural event-control proof.",
            "Control-stream rows may not reach FF through the watched source address even when their static record is terminated.",
            "The last mapper R1 capture is diagnostic because the renderer can restore the normal R1 after drawing.",
            "Release remains NOT_READY until non-pointer contexts and natural boss/event routes are verified.",
        ],
        "rows": rows,
    }


def render_markdown(payload: dict[str, object]) -> str:
    rows = payload["rows"]
    lines = [
        "# Full Pointer Sweep Runtime Audit",
        "",
        f"- Soft-gate status: **{payload['status']}**.",
        f"- Active pointer rows: `{payload['active_pass_count']}/{payload['active_count']}`.",
        f"- Excluded non-dialogue rows: `{payload['excluded_pass_count']}/{payload['excluded_count']}`.",
        f"- Release status: **{payload['release_status']}**.",
        "",
        "This audit uses one bounded forced-render run per pointer. It proves the compiled record, page state, source/control handling, and representative screen capture without requiring a full enemy-clear or boss route.",
        "",
        "## Source Modes",
        "",
        "| mode | count | meaning |",
        "| --- | ---: | --- |",
    ]
    meanings = {
        "DIRECT_TRACE_TERMINATOR": "The watched source trace reached FF.",
        "CONTROL_STREAM_STATIC_TERMINATOR": "Control bytes split the watched reads; the candidate record is statically terminated.",
        "EXCLUDED_NON_DIALOGUE": "Excluded by the page plan and retained from Japanese/control data.",
        "STATIC_TERMINATOR_NOT_REACHED_BY_WATCH": "Static terminator exists but the bounded watch did not reach it.",
        "UNKNOWN_SOURCE_END": "Needs investigation.",
    }
    for mode, count in sorted(payload["source_modes"].items()):
        lines.append(f"| {mode} | {count} | {meanings.get(mode, '')} |")
    lines += [
        "",
        "## Pointer Rows",
        "",
        "| pointer | CPU | page | state | source mode | source rows | pixels | field | result |",
        "| ---: | ---: | ---: | ---: | --- | ---: | --- | --- | --- |",
    ]
    for row in rows:
        image = row["image"]
        lines.append(
            f"| {row['pointer_index']} | {row['target_cpu']} | {row['page_index'] if row['page_index'] is not None else '-'} | "
            f"{row['page_state'] or '-'} | {row['source_mode']} | {row['source_row_count']} | "
            f"{image['text_pixels_present']} | {image['field_background_present']} | {row['status']} |"
        )
    lines += ["", "## Interpretation", ""]
    lines.extend(f"- {note}" for note in payload["notes"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_SWEEP_ROOT)
    parser.add_argument("--rom", type=Path, default=DEFAULT_ROM)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--english", type=Path, default=DEFAULT_ENGLISH)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    payload = build_report(args.root, args.rom, args.plan, args.english)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps({key: value for key, value in payload.items() if key != "rows"}, ensure_ascii=False))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
