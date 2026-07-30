#!/usr/bin/env python3
"""Build PTR-181 using the common dialogue-ID to CHR-page runtime path."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_opening_dialogue_16x16_proof import changed_spans
from build_opening_dialogue_8x16_proof import (
    CODE_CAVE_CPU,
    CODE_CAVE_ROM_OFFSET,
    CODE_CAVE_SIZE,
    RENDER_MARKER_ROM_OFFSET,
    default_tall_font,
)
from build_patch import make_records, write_ips
from build_ptr181_conditional_mapper_probe import (
    MAPPER_SELECT_CAVE_ROM_OFFSET,
    MAPPER_STORE_CAVE_ROM_OFFSET,
    MAPPER_WRAPPER_ORIGINAL,
    MAPPER_WRAPPER_ROM_OFFSET,
)
from build_ptr181_korean_8x16_candidate import patch_korean_8x16
from pointer_page_loader import (
    LOADER_CAVE_ROM_OFFSET,
    LOADER_CAVE_SIZE,
    LOADER_HOOK_ORIGINAL,
    LOADER_HOOK_ROM_OFFSET,
    PAGE_TABLE_ROM_OFFSET,
    build_generic_mapper_helpers,
    build_loader_helper,
    build_page_scoped_renderer,
    encode_page_table,
    loader_hook,
)
from rom_utils import REPO_ROOT


POINTER_INDEX = 181
DEVELOPMENT_PAGE_INDEX = 3
OUT_STEM = "kunio_period_drama_korean_ptr181_pointer_page_candidate"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "ptr181_pointer_page_candidate"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "ptr181_pointer_page_candidate.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "ptr181_pointer_page_candidate.md"


def apply_pointer_page_candidate(
    base: bytes, font_path: Path
) -> tuple[bytes, list[dict[str, object]]]:
    if (
        base[LOADER_HOOK_ROM_OFFSET:LOADER_HOOK_ROM_OFFSET + len(LOADER_HOOK_ORIGINAL)]
        != LOADER_HOOK_ORIGINAL
    ):
        raise ValueError("dialogue loader hook bytes do not match the base ROM")

    patched = patch_korean_8x16(base, font_path)
    targets: list[dict[str, object]] = [
        {
            "kind": "expanded_chr_base_candidate",
            "rom_offset": len(base),
            "length": len(patched) - len(base),
        }
    ]
    result = bytearray(patched)
    loader = build_loader_helper()
    assignments: list[int | None] = [None] * 248
    assignments[POINTER_INDEX] = DEVELOPMENT_PAGE_INDEX
    page_table = encode_page_table(assignments)
    renderer, marker_cpu = build_page_scoped_renderer(CODE_CAVE_CPU, CODE_CAVE_SIZE)
    wrapper, select, store = build_generic_mapper_helpers(MAPPER_WRAPPER_ORIGINAL)

    writes = (
        ("pointer_page_loader_hook", LOADER_HOOK_ROM_OFFSET, loader_hook()),
        ("pointer_page_loader", LOADER_CAVE_ROM_OFFSET, loader),
        ("pointer_page_table", PAGE_TABLE_ROM_OFFSET, page_table),
        ("page_scoped_renderer", CODE_CAVE_ROM_OFFSET, renderer),
        (
            "page_scoped_renderer_marker_hook",
            RENDER_MARKER_ROM_OFFSET,
            bytes((0x4C, marker_cpu & 0xFF, marker_cpu >> 8)),
        ),
        ("generic_mapper_wrapper", MAPPER_WRAPPER_ROM_OFFSET, wrapper),
        ("generic_mapper_select", MAPPER_SELECT_CAVE_ROM_OFFSET, select),
        ("generic_mapper_store", MAPPER_STORE_CAVE_ROM_OFFSET, store),
    )
    for kind, offset, data in writes:
        result[offset:offset + len(data)] = data
        targets.append(
            {
                "kind": kind,
                "rom_offset": offset,
                "length": len(data),
            }
        )

    if len(loader) != LOADER_CAVE_SIZE:
        raise AssertionError("final loader must exactly fill its reserved layout slot")
    if PAGE_TABLE_ROM_OFFSET != LOADER_CAVE_ROM_OFFSET + len(loader):
        raise AssertionError("page table must immediately follow the loader")
    return bytes(result), targets


def render_report(payload: dict[str, object]) -> str:
    return "\n".join(
        (
            "# PTR-181 Pointer Page Candidate",
            "",
            f"Status: **{payload['status']}**",
            "",
            "- Dialogue loader hook: `$9137`.",
            "- Runtime ID: `$B6`; catalog index: `181`.",
            "- Development page state: `4`; computed MMC3 R1: `$86`.",
            "- Renderer activation and CHR selection now depend on `$07FF`, not a hardcoded record pointer.",
            "- The temporary loader/table region overlaps original Japanese records and is valid only for this bounded development candidate.",
            "- The common loader starts at ROM `0x07000`; the whole-script compiler packs records before it.",
            "",
            f"- Base MD5: `{payload['base_md5']}`.",
            f"- Candidate MD5: `{payload['candidate_md5']}`.",
            f"- Changed spans: `{payload['changed_span_count']}`.",
            "",
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?")
    parser.add_argument("--font")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    from build_ptr181_bank8_page_probe import resolve_base_rom

    base_path = resolve_base_rom(args.rom)
    base = base_path.read_bytes()
    patched, targets = apply_pointer_page_candidate(
        base, default_tall_font(args.font)
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rom_path = args.out_dir / f"{OUT_STEM}.nes"
    ips_path = args.out_dir / f"{OUT_STEM}.ips"
    rom_path.write_bytes(patched)
    write_ips(ips_path, make_records(base, patched))
    payload = {
        "status": "CANDIDATE_BUILT_PENDING_RUNTIME_PROOF",
        "base_md5": hashlib.md5(base).hexdigest(),
        "candidate_md5": hashlib.md5(patched).hexdigest(),
        "rom_path": str(rom_path.relative_to(REPO_ROOT)),
        "ips_path": str(ips_path.relative_to(REPO_ROOT)),
        "changed_span_count": len(changed_spans(base, patched)),
        "targets": targets,
    }
    DEFAULT_REPORT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    DEFAULT_REPORT_MARKDOWN.write_text(render_report(payload), encoding="utf-8")
    print(f"rom={rom_path}")
    print(f"candidate_md5={payload['candidate_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
