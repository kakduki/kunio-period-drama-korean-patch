#!/usr/bin/env python3
"""Generate a category-oriented Bank 1 text offset inventory.

This report is intentionally conservative: it separates runtime-confirmed
targets from static translation-data matches so the patch work does not mistake
good breakpoint candidates for final proof.
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from analyze_bank1_candidate_contexts import confidence_label, context_for_hit
from map_translation_offsets import collect_hits, fmt_bytes, read_entries
from rom_utils import find_rom_path


ROOT = Path(__file__).resolve().parents[1]
TARGETS_PATH = ROOT / "rom_analysis" / "bank1_watch_targets.json"
WATCH_SUMMARY_PATH = ROOT / "rom_analysis" / "fceux_bank1_watch_test" / "bank1_reads.tsv"
OUT_MD = ROOT / "rom_analysis" / "bank1_offset_inventory.md"
OUT_JSON = ROOT / "rom_analysis" / "bank1_offset_inventory.json"
READABLE_REFERENCE = ROOT / "text_data" / "translation_readable_reference.json"

WATCH_ROM_START = 0x05610
WATCH_ROM_END = 0x05810

CATEGORY_GROUPS = {
    "UI/status": {"UI", "능력치", "캐릭터명"},
    "items/equipment": {"무기", "회복", "방어구", "특수"},
    "menu": {"타이틀", "메뉴", "모드"},
    "event/dialogue-related": {"대사", "이벤트", "보스", "스테이지", "엔딩", "기술"},
}


@dataclass
class RuntimeEvidence:
    hits: int = 0
    active_expected_matches: int = 0
    first_frame: int | None = None
    last_frame: int | None = None
    snapshots: set[str] = field(default_factory=set)

    @property
    def has_active_match(self) -> bool:
        return self.active_expected_matches > 0


@dataclass
class InventoryRow:
    label: str
    category: str
    source: str
    source_romaji: str
    source_context: str
    korean: str
    rom_hit: int
    prg_hit: int
    record_rom_range: tuple[int, int]
    record_cpu_range: tuple[int, int]
    mode: str
    base: str
    expected_bytes: str
    decoded_record: str
    confidence: str
    confidence_evidence: str
    runtime_base_note: str
    pointer_refs: list[str]
    runtime: RuntimeEvidence

    @property
    def evidence_level(self) -> str:
        if self.runtime.has_active_match or self.confidence == "high" and self.confidence_evidence:
            return "runtime-confirmed"
        if self.confidence == "high":
            return "encoding-exact"
        if self.pointer_refs:
            return "static-candidate+pointer"
        return "static-candidate"

    @property
    def in_watch_range(self) -> bool:
        return WATCH_ROM_START <= self.rom_hit < WATCH_ROM_END


def parse_hex(value: str) -> int:
    return int(value, 16)


def load_runtime_evidence() -> dict[str, RuntimeEvidence]:
    if not WATCH_SUMMARY_PATH.exists():
        return {}
    by_label: dict[str, RuntimeEvidence] = defaultdict(RuntimeEvidence)
    for row in csv.DictReader(WATCH_SUMMARY_PATH.open(encoding="utf-8"), delimiter="\t"):
        label = row.get("label", "")
        if not label:
            continue
        evidence = by_label[label]
        try:
            frame = int(row.get("frame", ""))
        except ValueError:
            frame = None
        evidence.hits += 1
        if row.get("active_expected_match", "").lower() == "true":
            evidence.active_expected_matches += 1
        if frame is not None:
            evidence.first_frame = frame if evidence.first_frame is None else min(evidence.first_frame, frame)
            evidence.last_frame = frame if evidence.last_frame is None else max(evidence.last_frame, frame)
        snapshot = row.get("record_snapshot", "").strip()
        if snapshot:
            evidence.snapshots.add(snapshot)
    return dict(by_label)


def load_readable_reference() -> dict[str, dict[str, str]]:
    if not READABLE_REFERENCE.exists():
        return {}
    data = json.loads(READABLE_REFERENCE.read_text(encoding="utf-8"))
    return {
        str(row["source"]): row
        for row in data.get("translation_data_joined", [])
    }


def readable_for(source: str, readable_by_source: dict[str, dict[str, str]]) -> tuple[str, str]:
    readable = readable_by_source.get(source, {})
    return (
        str(readable.get("romaji", "")),
        str(readable.get("subsection") or readable.get("section", "")),
    )


def load_rows() -> list[InventoryRow]:
    runtime_by_label = load_runtime_evidence()
    readable_by_source = load_readable_reference()
    data = json.loads(TARGETS_PATH.read_text(encoding="utf-8"))
    rows: list[InventoryRow] = []
    for target in data.get("targets", []):
        label = str(target["label"])
        source = str(target.get("source", ""))
        source_romaji, source_context = readable_for(source, readable_by_source)
        record_rom = tuple(parse_hex(value) for value in target["record_rom_range"])
        record_cpu = tuple(parse_hex(value) for value in target["record_cpu_range"])
        rows.append(
            InventoryRow(
                label=label,
                category=str(target.get("category", "")),
                source=source,
                source_romaji=source_romaji,
                source_context=source_context,
                korean=str(target.get("korean", "")),
                rom_hit=parse_hex(str(target["rom_hit"])),
                prg_hit=parse_hex(str(target["prg_hit"])),
                record_rom_range=(record_rom[0], record_rom[1]),
                record_cpu_range=(record_cpu[0], record_cpu[1]),
                mode=str(target.get("mode", "")),
                base=str(target.get("base", "")),
                expected_bytes=str(target.get("expected_bytes", "")),
                decoded_record=str(target.get("decoded_record", "")),
                confidence=str(target.get("confidence", "")),
                confidence_evidence=str(target.get("confidence_evidence", "")),
                runtime_base_note=str(target.get("runtime_base_note", "")),
                pointer_refs=list(target.get("pointer_refs", [])),
                runtime=runtime_by_label.get(label, RuntimeEvidence()),
            )
        )

    labels = {row.label for row in rows}
    candidate_keys = {
        (row.rom_hit, row.source, row.expected_bytes)
        for row in rows
    }
    rom = Path(find_rom_path()).read_bytes()
    prg = rom[0x10:0x10 + 0x20000]
    for hit in collect_hits(prg, read_entries()):
        if not WATCH_ROM_START <= hit.rom_offset < WATCH_ROM_END:
            continue
        ctx = context_for_hit(prg, hit)
        key = (hit.rom_offset, hit.entry.source, fmt_bytes(hit.encoded))
        if key in candidate_keys:
            continue
        candidate_keys.add(key)
        label = f"watch_rom_{hit.rom_offset:05X}_{hit.entry.category}_{hit.base:02X}".lower()
        if label in labels:
            continue
        labels.add(label)
        source_romaji, source_context = readable_for(hit.entry.source, readable_by_source)
        rows.append(
            InventoryRow(
                label=label,
                category=hit.entry.category,
                source=hit.entry.source,
                source_romaji=source_romaji,
                source_context=source_context,
                korean=hit.entry.korean,
                rom_hit=hit.rom_offset,
                prg_hit=hit.prg_offset,
                record_rom_range=(ctx.record_rom_start, ctx.record_rom_end),
                record_cpu_range=(ctx.cpu_addr, ctx.cpu_addr + (ctx.record_end - ctx.record_start)),
                mode=hit.mode,
                base=f"0x{hit.base:02X}",
                expected_bytes=fmt_bytes(hit.encoded),
                decoded_record=ctx.decoded_record,
                confidence=confidence_label(ctx),
                confidence_evidence="",
                runtime_base_note="watch-range supplemental candidate; not in bank1_watch_targets.json",
                pointer_refs=[f"0x{ref:05X}" for ref in ctx.pointer_refs],
                runtime=runtime_by_label.get(label, RuntimeEvidence()),
            )
        )
    return rows


def group_for_category(category: str) -> str:
    for group, categories in CATEGORY_GROUPS.items():
        if category in categories:
            return group
    return "other"


def fmt_rom(value: int) -> str:
    return f"0x{value:05X}"


def fmt_cpu(value: int) -> str:
    return f"${value:04X}"


def clean_record(value: str, max_len: int = 64) -> str:
    compact = re.sub(r"\s+", "", value)
    if len(compact) <= max_len:
        return compact
    return compact[:max_len - 3] + "..."


def runtime_text(evidence: RuntimeEvidence) -> str:
    if evidence.hits == 0:
        return "-"
    frames = ""
    if evidence.first_frame is not None and evidence.last_frame is not None:
        frames = f", frames {evidence.first_frame}-{evidence.last_frame}"
    return f"{evidence.hits} hits, active {evidence.active_expected_matches}{frames}"


def evidence_text(row: InventoryRow) -> str:
    pieces = [row.evidence_level]
    if row.confidence_evidence:
        pieces.append(row.confidence_evidence)
    elif row.runtime.has_active_match:
        pieces.append(runtime_text(row.runtime))
    elif row.runtime.hits:
        pieces.append("read hit without expected-byte context")
    elif row.pointer_refs:
        pieces.append(f"{len(row.pointer_refs)} pointer ref(s)")
    return "; ".join(pieces)


def write_json(rows: list[InventoryRow]) -> None:
    payload = {
        "source": [
            "rom_analysis/bank1_watch_targets.json",
            "rom_analysis/bank1_text_block_map.md watch-range supplemental candidates",
            "text_data/translation_readable_reference.json",
        ],
        "watch_range": [fmt_rom(WATCH_ROM_START), fmt_rom(WATCH_ROM_END)],
        "target_count": len(rows),
        "targets": [
            {
                "label": row.label,
                "category_group": group_for_category(row.category),
                "category": row.category,
                "source": row.source,
                "source_romaji": row.source_romaji,
                "source_context": row.source_context,
                "korean": row.korean,
                "rom_hit": fmt_rom(row.rom_hit),
                "prg_hit": fmt_rom(row.prg_hit),
                "record_rom_range": [fmt_rom(row.record_rom_range[0]), fmt_rom(row.record_rom_range[1])],
                "record_cpu_range": [fmt_cpu(row.record_cpu_range[0]), fmt_cpu(row.record_cpu_range[1])],
                "mode": row.mode,
                "base": row.base,
                "expected_bytes": row.expected_bytes,
                "decoded_record": row.decoded_record,
                "evidence_level": row.evidence_level,
                "evidence": evidence_text(row),
                "runtime_hits": row.runtime.hits,
                "runtime_active_expected_matches": row.runtime.active_expected_matches,
                "in_watch_range": row.in_watch_range,
            }
            for row in rows
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_table(lines: list[str], rows: list[InventoryRow]) -> None:
    if not rows:
        lines.append("_No targets in this group yet._")
        lines.append("")
        return
    lines.append("| evidence | ROM hit | record ROM | CPU range | category | Japanese | Korean | mode/base | bytes | decoded record | runtime |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for row in sorted(rows, key=lambda item: (item.evidence_level != "runtime-confirmed", item.rom_hit, item.category, item.source)):
        lines.append(
            f"| {row.evidence_level} | `{fmt_rom(row.rom_hit)}` | "
            f"`{fmt_rom(row.record_rom_range[0])}-{fmt_rom(row.record_rom_range[1])}` | "
            f"`{fmt_cpu(row.record_cpu_range[0])}-{fmt_cpu(row.record_cpu_range[1])}` | "
            f"{row.category} | {format_source(row)} | {row.korean} | {row.mode}/`{row.base}` | "
            f"`{row.expected_bytes}` | `{clean_record(row.decoded_record)}` | {runtime_text(row.runtime)} |"
        )
    lines.append("")


def format_source(row: InventoryRow) -> str:
    if row.source_romaji:
        return f"{row.source} ({row.source_romaji})"
    return row.source


def write_markdown(rows: list[InventoryRow]) -> None:
    by_group: dict[str, list[InventoryRow]] = defaultdict(list)
    for row in rows:
        by_group[group_for_category(row.category)].append(row)

    confirmed = [row for row in rows if row.evidence_level == "runtime-confirmed"]
    watch_rows = [row for row in rows if row.in_watch_range]

    lines = [
        "# Bank 1 Text Offset Inventory",
        "",
        "This inventory consolidates the current Bank 1 translation candidates with runtime read-watch evidence.",
        "",
        f"- Source targets: `{TARGETS_PATH.relative_to(ROOT)}`",
        "- Supplemental watch-range candidates: generated from `translation_data.txt` hits inside `ROM+0x05610-0x05810`",
        f"- Watch range: `ROM+{fmt_rom(WATCH_ROM_START)}-ROM+{fmt_rom(WATCH_ROM_END)}`",
        f"- Total targets: **{len(rows)}**",
        f"- Runtime-confirmed targets: **{len(confirmed)}**",
        f"- Targets inside watch range: **{len(watch_rows)}**",
        "",
        "Evidence levels:",
        "",
        "- `runtime-confirmed`: FCEUX read-watch or preserved runtime evidence saw the expected bytes active in memory.",
        "- `encoding-exact`: exact `plus-0x7A` encoding match, but without active runtime read evidence yet.",
        "- `static-candidate+pointer`: translation-data match plus at least one raw pointer reference.",
        "- `static-candidate`: translation-data match only; use as breakpoint/search target.",
        "",
        "## Runtime-confirmed offsets",
        "",
    ]
    add_table(lines, confirmed)

    lines.extend(["## Watch range: ROM+0x05610-0x05810", ""])
    add_table(lines, watch_rows)

    for group in ("UI/status", "items/equipment", "menu", "event/dialogue-related", "other"):
        lines.extend([f"## {group}", ""])
        add_table(lines, by_group.get(group, []))

    lines.extend(
        [
            "## Gaps",
            "",
            "- No menu-category target is currently present in `bank1_watch_targets.json`; menu labels still need broader capture or refined translation matching.",
            "- Event/dialogue evidence is still static candidate evidence only. The current watch range contains boss/stage/name-like strings, but no fully runtime-confirmed event dialogue block yet.",
            "- Several read hits without active expected-byte matches (`rom_05bba_candidate_7a`, `rom_06fa1_candidate_8d`) are deliberately not promoted to confirmed offsets.",
        ]
    )

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = load_rows()
    write_json(rows)
    write_markdown(rows)
    confirmed = sum(1 for row in rows if row.evidence_level == "runtime-confirmed")
    watch = sum(1 for row in rows if row.in_watch_range)
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(f"targets={len(rows)} runtime_confirmed={confirmed} watch_range={watch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
