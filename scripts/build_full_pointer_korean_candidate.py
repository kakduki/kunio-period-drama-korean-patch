#!/usr/bin/env python3
"""Compile all pointer-owned dialogue using the English patch control model."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from analyze_reference_ips import parse_ines_layout
from apply_ips_standalone import apply_ips
from build_opening_dialogue_8x16_proof import (
    CODE_CAVE_CPU,
    CODE_CAVE_ROM_OFFSET,
    CODE_CAVE_SIZE,
    RENDER_ENTRY_ORIGINAL,
    RENDER_ENTRY_ROM_OFFSET,
    RENDER_MARKER_ORIGINAL,
    RENDER_MARKER_ROM_OFFSET,
    default_tall_font,
)
from build_patch import make_records, write_ips
from build_ptr181_bank8_page_probe import BASE_MD5, CHR_BANK_SIZE, resolve_base_rom
from build_ptr181_conditional_mapper_probe import (
    MAPPER_SELECT_CAVE_ROM_OFFSET,
    MAPPER_STORE_CAVE_ROM_OFFSET,
    MAPPER_WRAPPER_ORIGINAL,
    MAPPER_WRAPPER_ROM_OFFSET,
)
from korean_tile_font import render_tall_tiles
from pointer_page_loader import (
    LOADER_CAVE_ROM_OFFSET,
    LOADER_HOOK_ORIGINAL,
    LOADER_HOOK_ROM_OFFSET,
    PAGE_TABLE_ROM_OFFSET,
    RENDER_SOURCE_RANGES,
    build_generic_mapper_helpers,
    build_loader_helper,
    build_page_scoped_renderer,
    encode_page_table,
    loader_hook,
)
from rom_utils import REPO_ROOT


POINTER_COUNT = 248
POINTER_TABLE_ROM_OFFSET = 0x05DD4
RECORD_PACK_START = 0x05FC4
ORIGINAL_CHR_BANKS = 16
OUTPUT_CHR_BANKS = 29
PAGE_SIZE = 0x0800
PAGE_CAPACITY = (OUTPUT_CHR_BANKS - ORIGINAL_CHR_BANKS) * 4
SOURCE_PAGE_OFFSET_IN_CHR = 0x0F800
SOURCE_CODES = tuple(range(0x81, 0x9B)) + tuple(range(0xC0, 0xC8))
BOTTOM_TILE_DELTA = 0x20
DEFAULT_DRAFT = REPO_ROOT / "text_data" / "pointer_dialogue_korean_draft.tsv"
DEFAULT_SEGMENTS = REPO_ROOT / "text_data" / "pointer_dialogue_korean_segments.json"
DEFAULT_ENGLISH = REPO_ROOT / "rom_analysis" / "english_script_dump.tsv"
DEFAULT_PLAN = REPO_ROOT / "rom_analysis" / "pointer_font_page_plan.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "full_pointer_korean_candidate"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "full_pointer_korean_candidate.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "full_pointer_korean_candidate.md"
OUT_STEM = "kunio_period_drama_korean_full_pointer_candidate"


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def clean_korean_text(text: str) -> str:
    kept = [character if character == " " or "\uac00" <= character <= "\ud7a3" else " " for character in text]
    return " ".join("".join(kept).split())


def is_replaceable(value: int) -> bool:
    return value == 0x00 or 0x81 <= value <= 0x9A


def replaceable_runs(template: bytes) -> list[tuple[int, int, int]]:
    runs: list[tuple[int, int, int]] = []
    cursor = 0
    while cursor < len(template):
        if not is_replaceable(template[cursor]):
            cursor += 1
            continue
        end = cursor + 1
        while end < len(template) and is_replaceable(template[end]):
            end += 1
        letter_count = sum(0x81 <= value <= 0x9A for value in template[cursor:end])
        runs.append((cursor, end, letter_count))
        cursor = end
    return runs


def split_text_by_weights(text: str, weights: list[int]) -> list[str]:
    if not weights:
        if text:
            raise ValueError("Korean text has no replaceable English run")
        return []
    if len(weights) == 1:
        return [text]
    total_weight = sum(weights)
    cuts: list[int] = []
    cumulative = 0
    previous = 0
    for weight in weights[:-1]:
        cumulative += weight
        ideal = round(len(text) * cumulative / total_weight)
        candidates = [
            position
            for position, character in enumerate(text)
            if character == " " and previous <= position
        ]
        cut = min(candidates, key=lambda value: abs(value - ideal), default=ideal)
        cut = max(previous, min(cut, len(text)))
        cuts.append(cut)
        previous = cut + (1 if cut < len(text) and text[cut:cut + 1] == " " else 0)
    pieces: list[str] = []
    start = 0
    for cut in cuts:
        pieces.append(text[start:cut].strip())
        start = cut
        while start < len(text) and text[start] == " ":
            start += 1
    pieces.append(text[start:].strip())
    return pieces


def control_skeleton(data: bytes, *, korean_codes: bool = False) -> bytes:
    def is_text(value: int) -> bool:
        if value == 0x00 or 0x81 <= value <= 0x9A:
            return True
        return korean_codes and 0xC0 <= value <= 0xC7

    return bytes(value for value in data if not is_text(value))


def encode_control_preserving_record(
    template: bytes,
    korean_text: str,
    glyph_codes: dict[str, int],
    explicit_segments: list[str] | None = None,
) -> bytes:
    runs = replaceable_runs(template)
    active_runs = [run for run in runs if run[2] > 0]
    if explicit_segments is None:
        pieces = split_text_by_weights(
            clean_korean_text(korean_text), [run[2] for run in active_runs]
        )
    else:
        pieces = [clean_korean_text(segment) for segment in explicit_segments]
        if len(pieces) != len(active_runs):
            raise ValueError(
                f"explicit segment count {len(pieces)} does not match "
                f"{len(active_runs)} replaceable runs"
            )
    replacements: dict[int, bytes] = {}
    for run, piece in zip(active_runs, pieces, strict=True):
        encoded = bytearray()
        for character in piece:
            if character == " ":
                encoded.append(0)
            else:
                try:
                    encoded.append(glyph_codes[character])
                except KeyError as exc:
                    raise ValueError(f"unallocated page glyph {character!r}") from exc
        replacements[run[0]] = bytes(encoded)

    output = bytearray()
    cursor = 0
    for start, end, letter_count in runs:
        output.extend(template[cursor:start])
        if letter_count > 0:
            output.extend(replacements[start])
        else:
            output.extend(template[start:end])
        cursor = end
    output.extend(template[cursor:])
    result = bytes(output)
    if control_skeleton(result, korean_codes=True) != control_skeleton(template):
        raise AssertionError("compiled record changed the English control skeleton")
    return result


def build_config(
    base: bytes,
    draft_path: Path = DEFAULT_DRAFT,
    english_path: Path = DEFAULT_ENGLISH,
    plan_path: Path = DEFAULT_PLAN,
    segments_path: Path = DEFAULT_SEGMENTS,
) -> dict[str, object]:
    draft = load_tsv(draft_path)
    english = [row for row in load_tsv(english_path) if row["record_kind"] == "pointer_pair"]
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    segment_overrides = json.loads(segments_path.read_text(encoding="utf-8"))
    if len(draft) != POINTER_COUNT or len(english) != POINTER_COUNT:
        raise ValueError("full pointer inputs must each contain 248 rows")
    pages = plan["optimized_pages"]
    assignments = plan["pointer_page_assignments"]
    if not pages or len(pages) > PAGE_CAPACITY or len(assignments) != POINTER_COUNT:
        raise ValueError(
            f"font page plan must contain 1-{PAGE_CAPACITY} pages and {POINTER_COUNT} assignments"
        )

    page_maps: list[dict[str, int]] = []
    for page in pages:
        syllables = list(page["syllables"])
        if len(syllables) > len(SOURCE_CODES):
            raise ValueError(f"page {page['page_index']} exceeds the 34-code pool")
        page_maps.append(dict(zip(syllables, SOURCE_CODES, strict=False)))

    records: list[dict[str, object]] = []
    cursor = RECORD_PACK_START
    for index, (draft_row, english_row) in enumerate(zip(draft, english, strict=True)):
        excluded = draft_row["translation_status"].startswith("excluded")
        page_index = assignments[index]
        if excluded:
            raw = bytes.fromhex(english_row["jp_raw_bytes"]) if english_row["jp_raw_bytes"] else b""
        else:
            if page_index is None:
                raise ValueError(f"active pointer {index} has no font page")
            template = bytes.fromhex(english_row["en_raw_bytes"])
            raw = encode_control_preserving_record(
                template,
                draft_row["korean_text"],
                page_maps[page_index],
                segment_overrides.get(str(index)),
            )
        record_offset = cursor if raw else None
        if raw:
            cursor += len(raw)
        records.append(
            {
                "pointer_index": index,
                "page_index": page_index,
                "excluded": excluded,
                "record_offset": record_offset,
                "record": raw,
                "korean_text": draft_row["korean_text"],
                "english_control_skeleton": control_skeleton(
                    bytes.fromhex(english_row["en_raw_bytes"])
                ).hex(" ").upper()
                if english_row["en_raw_bytes"]
                else "",
            }
        )
    if cursor > LOADER_CAVE_ROM_OFFSET:
        raise ValueError(
            f"compiled records end at 0x{cursor:05X}, past loader at 0x{LOADER_CAVE_ROM_OFFSET:05X}"
        )
    return {
        "records": records,
        "pages": pages,
        "page_maps": page_maps,
        "segment_override_count": len(segment_overrides),
        "assignments": assignments,
        "record_start": RECORD_PACK_START,
        "record_end": cursor,
        "record_bytes": cursor - RECORD_PACK_START,
        "record_loader_gap": LOADER_CAVE_ROM_OFFSET - cursor,
    }


def apply_full_candidate(
    base: bytes,
    config: dict[str, object],
    font_path: Path,
) -> tuple[bytes, list[dict[str, object]]]:
    if hashlib.md5(base).hexdigest() != BASE_MD5:
        raise ValueError("unsupported base ROM")
    if base[5] != ORIGINAL_CHR_BANKS:
        raise ValueError("base ROM CHR count is not 16")
    for offset, expected, label in (
        (LOADER_HOOK_ROM_OFFSET, LOADER_HOOK_ORIGINAL, "dialogue loader"),
        (RENDER_ENTRY_ROM_OFFSET, RENDER_ENTRY_ORIGINAL, "renderer entry"),
        (RENDER_MARKER_ROM_OFFSET, RENDER_MARKER_ORIGINAL, "renderer marker"),
        (MAPPER_WRAPPER_ROM_OFFSET, MAPPER_WRAPPER_ORIGINAL, "mapper wrapper"),
    ):
        if base[offset:offset + len(expected)] != expected:
            raise ValueError(f"{label} bytes do not match the base ROM")

    layout = parse_ines_layout(base)
    result = bytearray(base)
    targets: list[dict[str, object]] = []
    records = config["records"]
    assignments = config["assignments"]
    page_maps = config["page_maps"]
    assert isinstance(records, list) and isinstance(assignments, list) and isinstance(page_maps, list)

    for record in records:
        raw = record["record"]
        offset = record["record_offset"]
        assert isinstance(raw, bytes)
        if not raw:
            continue
        assert isinstance(offset, int)
        result[offset:offset + len(raw)] = raw
        pointer_cpu = offset - 0x04010 + 0x8000
        pointer_offset = POINTER_TABLE_ROM_OFFSET + int(record["pointer_index"]) * 2
        result[pointer_offset:pointer_offset + 2] = pointer_cpu.to_bytes(2, "little")
    targets.append(
        {
            "kind": "full_dialogue_records",
            "rom_offset": config["record_start"],
            "length": config["record_bytes"],
        }
    )
    targets.append(
        {
            "kind": "full_dialogue_pointer_table",
            "rom_offset": POINTER_TABLE_ROM_OFFSET,
            "length": POINTER_COUNT * 2,
        }
    )

    loader = build_loader_helper()
    page_table = encode_page_table(assignments)
    renderer, marker_cpu = build_page_scoped_renderer(CODE_CAVE_CPU, CODE_CAVE_SIZE)
    wrapper, select, store = build_generic_mapper_helpers(MAPPER_WRAPPER_ORIGINAL)
    writes = (
        ("pointer_page_loader_hook", LOADER_HOOK_ROM_OFFSET, loader_hook()),
        ("pointer_page_loader", LOADER_CAVE_ROM_OFFSET, loader),
        ("pointer_page_table", PAGE_TABLE_ROM_OFFSET, page_table),
        (
            "renderer_entry_hook",
            RENDER_ENTRY_ROM_OFFSET,
            bytes((0x4C, CODE_CAVE_CPU & 0xFF, CODE_CAVE_CPU >> 8)),
        ),
        (
            "renderer_marker_hook",
            RENDER_MARKER_ROM_OFFSET,
            bytes((0x4C, marker_cpu & 0xFF, marker_cpu >> 8)),
        ),
        ("page_scoped_renderer", CODE_CAVE_ROM_OFFSET, renderer),
        ("generic_mapper_wrapper", MAPPER_WRAPPER_ROM_OFFSET, wrapper),
        ("generic_mapper_select", MAPPER_SELECT_CAVE_ROM_OFFSET, select),
        ("generic_mapper_store", MAPPER_STORE_CAVE_ROM_OFFSET, store),
    )
    for kind, offset, data in writes:
        result[offset:offset + len(data)] = data
        targets.append({"kind": kind, "rom_offset": offset, "length": len(data)})

    source_page_start = layout.chr_start + SOURCE_PAGE_OFFSET_IN_CHR
    source_page = base[source_page_start:source_page_start + PAGE_SIZE]
    if len(source_page) != PAGE_SIZE:
        raise AssertionError("source CHR page is incomplete")
    appended = bytearray()
    page_count = len(page_maps)
    for page_index in range(PAGE_CAPACITY):
        page = bytearray(source_page)
        if page_index < page_count:
            for glyph, code in page_maps[page_index].items():
                top, bottom = render_tall_tiles(glyph, font_path=font_path, threshold=92)
                top_offset = ((code - 0x80) % 0x80) * 16
                bottom_offset = ((code + BOTTOM_TILE_DELTA - 0x80) % 0x80) * 16
                page[top_offset:top_offset + 16] = top
                page[bottom_offset:bottom_offset + 16] = bottom
        appended.extend(page)
    result[5] = OUTPUT_CHR_BANKS
    result.extend(appended)
    targets.append(
        {
            "kind": "expanded_korean_chr_pages",
            "rom_offset": len(base),
            "length": len(appended),
            "page_count": page_count,
        }
    )
    return bytes(result), targets


def render_report(payload: dict[str, object]) -> str:
    return "\n".join(
        (
            "# Full Pointer Korean Candidate",
            "",
            f"Status: **{payload['status']}**",
            "",
            "- English reference role: pointer ownership and non-letter control-byte order.",
            "- Korean replacement scope: English `0x81-0x9A`/space runs only.",
            f"- Compiled records: `{payload['compiled_records']}`; bytes: `{payload['record_bytes']}`.",
            f"- Record range: `{payload['record_start']}` to `{payload['record_end']}`.",
            f"- Gap before loader: `{payload['record_loader_gap']}` bytes.",
            f"- Korean CHR pages: `{payload['font_pages']}`; CHR banks: `16 -> 29`.",
            "- Excluded non-dialogue records retain their Japanese bytes.",
            "- English-reference review covers all 244 active rows; no translation drafts remain.",
            "- Forty-seven dynamic name/item-control rows remain context-flagged; broad visual coverage is still open.",
            "",
            f"- Base MD5: `{payload['base_md5']}`.",
            f"- Candidate MD5: `{payload['candidate_md5']}`.",
            "",
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?")
    parser.add_argument("--draft", type=Path, default=DEFAULT_DRAFT)
    parser.add_argument("--english", type=Path, default=DEFAULT_ENGLISH)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--segments", type=Path, default=DEFAULT_SEGMENTS)
    parser.add_argument("--font")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    base = resolve_base_rom(args.rom).read_bytes()
    config = build_config(base, args.draft, args.english, args.plan, args.segments)
    patched, targets = apply_full_candidate(base, config, default_tall_font(args.font))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rom_path = args.out_dir / f"{OUT_STEM}.nes"
    ips_path = args.out_dir / f"{OUT_STEM}.ips"
    rom_path.write_bytes(patched)
    write_ips(ips_path, make_records(base, patched))
    if apply_ips(base, ips_path) != patched:
        raise AssertionError("full pointer candidate IPS round trip failed")
    payload = {
        "status": "WHOLE_SCRIPT_CANDIDATE_BUILT_RUNTIME_UNKNOWN",
        "base_md5": hashlib.md5(base).hexdigest(),
        "candidate_md5": hashlib.md5(patched).hexdigest(),
        "rom_path": str(rom_path.relative_to(REPO_ROOT)),
        "ips_path": str(ips_path.relative_to(REPO_ROOT)),
        "compiled_records": sum(bool(record["record"]) for record in config["records"]),
        "record_bytes": config["record_bytes"],
        "record_start": f"0x{config['record_start']:05X}",
        "record_end": f"0x{config['record_end']:05X}",
        "record_loader_gap": config["record_loader_gap"],
        "font_pages": len(config["pages"]),
        "segment_overrides": config["segment_override_count"],
        "chr_banks": OUTPUT_CHR_BANKS,
        "targets": targets,
    }
    DEFAULT_REPORT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    DEFAULT_REPORT_MARKDOWN.write_text(render_report(payload), encoding="utf-8")
    print(f"rom={rom_path}")
    print(f"record_end={payload['record_end']}")
    print(f"candidate_md5={payload['candidate_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
