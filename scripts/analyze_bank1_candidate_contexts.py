#!/usr/bin/env python3
"""Build focused context tables around Bank 1 translation candidates."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import json
from pathlib import Path

from map_translation_offsets import (
    BANK1_ROM_END,
    BANK1_ROM_START,
    PRG_HEADER,
    PRG_SIZE,
    WATCH_ROM_END,
    WATCH_ROM_START,
    Hit,
    collect_hits,
    fmt_bytes,
    hit_sort_key,
    normalize,
    read_entries,
)
from rom_utils import find_rom_path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "rom_analysis" / "bank1_candidate_contexts.md"
OUT_TARGETS = ROOT / "rom_analysis" / "bank1_watch_targets.json"
OUT_LUA_TARGETS = ROOT / "lua" / "kunio_bank1_targets.lua"

DELIMITERS = {0x00, 0xFF}
FOCUSED_CATEGORIES = {"UI", "무기", "회복", "능력치", "보스", "스테이지", "메뉴"}
MAX_POINTER_REFS = 10
BEST_TARGET_CATEGORIES = {"UI", "무기", "회복", "능력치", "메뉴"}


@dataclass(frozen=True)
class Context:
    hit: Hit
    record_start: int
    record_end: int
    decoded_record: str
    pointer_refs: tuple[int, ...]

    @property
    def record_rom_start(self) -> int:
        return self.record_start + PRG_HEADER

    @property
    def record_rom_end(self) -> int:
        return self.record_end + PRG_HEADER

    @property
    def cpu_addr(self) -> int:
        return 0x8000 + (self.record_start % 0x4000)


def reverse_low_table() -> dict[int, str]:
    # Import lazily so this script keeps a single source of truth for the table.
    from map_translation_offsets import HIRAGANA_LOW

    return {low: kana for kana, low in HIRAGANA_LOW.items()}


def find_record_bounds(prg: bytes, prg_offset: int) -> tuple[int, int]:
    start = prg_offset
    while start > 0 and prg[start - 1] not in DELIMITERS:
        start -= 1

    end = prg_offset
    while end < len(prg) and prg[end] not in DELIMITERS:
        end += 1
    return start, end


def decode_shifted_record(data: bytes, base: int) -> str:
    rev = reverse_low_table()
    chars: list[str] = []
    for byte in data:
        low = (byte - base) & 0xFF
        chars.append(rev.get(low, f"<{byte:02X}>"))
    return "".join(chars)


def decode_plus_record(data: bytes) -> str:
    rev = reverse_low_table()
    chars: list[str] = []
    for byte in data:
        tile = byte + 0x7A
        if 0x101 <= tile <= 0x12F:
            chars.append(rev.get(tile - 0x100, f"<{byte:02X}>"))
        else:
            chars.append(f"<{byte:02X}>")
    return "".join(chars)


def decode_record(hit: Hit, data: bytes) -> str:
    if hit.mode == "plus-0x7A":
        return decode_plus_record(data)
    return decode_shifted_record(data, hit.base)


def find_pointer_refs(prg: bytes, cpu_addr: int) -> tuple[int, ...]:
    needle = bytes((cpu_addr & 0xFF, cpu_addr >> 8))
    refs: list[int] = []
    start = 0
    while True:
        idx = prg.find(needle, start)
        if idx == -1:
            break
        refs.append(idx + PRG_HEADER)
        start = idx + 1
    return tuple(refs[:MAX_POINTER_REFS])


def context_for_hit(prg: bytes, hit: Hit) -> Context:
    start, end = find_record_bounds(prg, hit.prg_offset)
    data = prg[start:end]
    decoded = decode_record(hit, data)
    refs = find_pointer_refs(prg, 0x8000 + (start % 0x4000))
    return Context(hit, start, end, decoded, refs)


def confidence_label(ctx: Context) -> str:
    hit = ctx.hit
    if hit.mode == "plus-0x7A":
        return "high"
    if ctx.record_rom_start <= hit.rom_offset and hit.rom_offset + len(hit.encoded) <= ctx.record_rom_end:
        return "medium"
    return "low"


def pointer_ref_text(refs: tuple[int, ...]) -> str:
    if not refs:
        return "-"
    text = ", ".join(f"`0x{ref:05X}`" for ref in refs)
    if len(refs) == MAX_POINTER_REFS:
        text += ", ..."
    return text


def strip_control_markers(text: str) -> str:
    out: list[str] = []
    in_marker = False
    for ch in text:
        if ch == "<":
            in_marker = True
            continue
        if ch == ">" and in_marker:
            in_marker = False
            continue
        if not in_marker:
            out.append(ch)
    return "".join(out)


def is_best_target(ctx: Context) -> bool:
    if ctx.hit.entry.category not in BEST_TARGET_CATEGORIES:
        return False
    if ctx.record_end - ctx.record_start > 0x18:
        return False
    source = normalize(ctx.hit.entry.source, fold_voiced=True)
    decoded = normalize(strip_control_markers(ctx.decoded_record), fold_voiced=True)
    return source in decoded


def section(lines: list[str], title: str, contexts: list[Context]) -> None:
    lines.append(f"## {title}")
    lines.append("")
    if not contexts:
        lines.append("No candidates.")
        lines.append("")
        return

    lines.append(
        "| confidence | ROM hit | record ROM range | CPU record addr | mode/base | Japanese | Korean | bytes | decoded record | pointer refs |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for ctx in contexts:
        hit = ctx.hit
        lines.append(
            f"| {confidence_label(ctx)} | `0x{hit.rom_offset:05X}` | "
            f"`0x{ctx.record_rom_start:05X}-0x{ctx.record_rom_end:05X}` | "
            f"`0x{ctx.cpu_addr:04X}` | {hit.mode}/`0x{hit.base:02X}` | "
            f"{hit.entry.source} | {hit.entry.korean} | `{fmt_bytes(hit.encoded)}` | "
            f"`{ctx.decoded_record}` | {pointer_ref_text(ctx.pointer_refs)} |"
        )
    lines.append("")


def unique_contexts(contexts: list[Context]) -> list[Context]:
    seen: set[tuple[int, str, int, str]] = set()
    out: list[Context] = []
    for ctx in sorted(contexts, key=lambda c: hit_sort_key(c.hit)):
        key = (ctx.hit.rom_offset, ctx.hit.mode, ctx.hit.base, ctx.hit.entry.source)
        if key in seen:
            continue
        seen.add(key)
        out.append(ctx)
    return out


def target_label(ctx: Context) -> str:
    return f"rom_{ctx.hit.rom_offset:05X}_candidate_{ctx.hit.base:02X}".lower()


def lua_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_targets(contexts: list[Context]) -> None:
    targets = []
    for ctx in sorted(contexts, key=lambda c: hit_sort_key(c.hit)):
        hit = ctx.hit
        targets.append(
            {
                "label": target_label(ctx),
                "category": hit.entry.category,
                "source": hit.entry.source,
                "korean": hit.entry.korean,
                "rom_hit": f"0x{hit.rom_offset:05X}",
                "prg_hit": f"0x{hit.prg_offset:05X}",
                "record_rom_range": [
                    f"0x{ctx.record_rom_start:05X}",
                    f"0x{ctx.record_rom_end:05X}",
                ],
                "record_cpu_range": [
                    f"0x{ctx.cpu_addr:04X}",
                    f"0x{ctx.cpu_addr + (ctx.record_end - ctx.record_start):04X}",
                ],
                "mode": hit.mode,
                "base": f"0x{hit.base:02X}",
                "expected_bytes": fmt_bytes(hit.encoded),
                "decoded_record": ctx.decoded_record,
                "confidence": confidence_label(ctx),
                "pointer_refs": [f"0x{ref:05X}" for ref in ctx.pointer_refs],
            }
        )

    payload = {
        "source": "rom_analysis/bank1_candidate_contexts.md",
        "description": "Breakpoint-ready Bank 1 item/menu/UI targets generated from translation-data candidate contexts.",
        "target_count": len(targets),
        "targets": targets,
    }
    OUT_TARGETS.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "-- Auto-generated by scripts/analyze_bank1_candidate_contexts.py.",
        "-- Do not edit by hand; edit the source analysis scripts/data instead.",
        "return {",
    ]
    for target in targets:
        start, stop = target["record_cpu_range"]
        lines.append(
            "  { "
            f"label = {lua_string(str(target['label']))}, "
            f"category = {lua_string(str(target['category']))}, "
            f"rom = {target['rom_hit']}, "
            f"start = {start}, "
            f"stop = {stop}, "
            f"bytes = {lua_string(str(target['expected_bytes']))} "
            "},"
        )
    lines.append("}")
    OUT_LUA_TARGETS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rom = Path(find_rom_path()).read_bytes()
    prg = rom[PRG_HEADER : PRG_HEADER + PRG_SIZE]
    hits = collect_hits(prg, read_entries())

    bank1_hits = [
        hit
        for hit in hits
        if BANK1_ROM_START <= hit.rom_offset < BANK1_ROM_END
        and (hit.entry.category in FOCUSED_CATEGORIES or hit.mode == "plus-0x7A")
    ]
    contexts = unique_contexts([context_for_hit(prg, hit) for hit in bank1_hits])
    watch_contexts = [
        ctx for ctx in contexts if WATCH_ROM_START <= ctx.hit.rom_offset < WATCH_ROM_END
    ]
    exact_contexts = [ctx for ctx in contexts if ctx.hit.mode == "plus-0x7A"]

    by_category: dict[str, list[Context]] = defaultdict(list)
    for ctx in contexts:
        by_category[ctx.hit.entry.category].append(ctx)

    lines: list[str] = [
        "# Bank 1 candidate contexts",
        "",
        "Generated from `translation_data.txt` matches in PRG Bank 1.",
        "",
        "Record ranges are provisional. They are bounded by `0x00` or `0xFF`, which matches the strongest visible table separators found so far, but FCEUX read traces still need to confirm runtime use.",
        "",
        f"Total focused Bank 1 candidates: `{len(contexts)}`",
        f"Candidates inside `ROM+0x05610-0x05810`: `{len(watch_contexts)}`",
        f"Exact `plus-0x7A` candidates: `{len(exact_contexts)}`",
        "",
    ]

    best_contexts = [ctx for ctx in contexts if is_best_target(ctx)]

    section(lines, "Watch range contexts", watch_contexts)
    section(lines, "Exact plus-0x7A contexts", exact_contexts)
    section(lines, "Best item/menu/UI breakpoint targets", best_contexts)

    for category in sorted(by_category):
        section(lines, f"Category: {category}", by_category[category])

    lines.append("## Notes")
    lines.append("")
    lines.append("- `high` means the current `plus-0x7A` hypothesis directly encoded the translation entry.")
    lines.append("- `medium` means the shifted-low pattern lands inside a delimiter-bounded record; it is a strong breakpoint target, not final proof.")
    lines.append("- Pointer refs are raw little-endian CPU-address references in PRG ROM and may include code/data false positives.")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_targets(best_contexts)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_TARGETS}")
    print(f"Wrote {OUT_LUA_TARGETS}")
    print(
        f"contexts={len(contexts)} watch={len(watch_contexts)} exact_plus={len(exact_contexts)} targets={len(best_contexts)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
