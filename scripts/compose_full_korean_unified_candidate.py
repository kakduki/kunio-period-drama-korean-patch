#!/usr/bin/env python3
"""Compose pointer and non-pointer Korean changes without losing structure.

The pointer candidate is the executable/text-structure owner.  The secondary
candidate contributes only bytes that differ from the Japanese base, with
conflicting offsets retained from the pointer owner and reported for review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_patch import make_records, write_ips
from rom_utils import REPO_ROOT


DEFAULT_BASE = REPO_ROOT / "rom" / "Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes"
DEFAULT_POINTER = REPO_ROOT / "output" / "full_korean_expanded_candidate" / "kunio_period_drama_korean_expanded_candidate.nes"
DEFAULT_OVERLAY = REPO_ROOT / "output" / "full_korean_items_title_none_nonpointer_candidate" / "kunio_period_drama_korean_expanded_nonpointer_candidate.nes"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "full_korean_unified_candidate"
DEFAULT_REPORT_JSON = REPO_ROOT / "rom_analysis" / "full_korean_unified_candidate.json"
DEFAULT_REPORT_MARKDOWN = REPO_ROOT / "rom_analysis" / "full_korean_unified_candidate.md"
OUT_STEM = "kunio_period_drama_korean_unified_candidate"


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def compose(base: bytes, pointer: bytes, overlay: bytes) -> tuple[bytes, list[dict[str, object]], list[dict[str, object]]]:
    if len(pointer) < len(base) or len(overlay) < len(base):
        raise ValueError("candidate is shorter than the base ROM")
    result = bytearray(pointer)
    overlay_changes: list[dict[str, object]] = []
    conflicts: list[dict[str, object]] = []
    for offset in range(len(base)):
        base_byte, pointer_byte, overlay_byte = base[offset], pointer[offset], overlay[offset]
        if overlay_byte == base_byte:
            continue
        row = {
            "rom_offset": f"0x{offset:05X}",
            "base": f"0x{base_byte:02X}",
            "pointer": f"0x{pointer_byte:02X}",
            "overlay": f"0x{overlay_byte:02X}",
        }
        if pointer_byte != base_byte and pointer_byte != overlay_byte:
            conflicts.append(row)
            continue
        result[offset] = overlay_byte
        overlay_changes.append(row)
    if len(overlay) > len(base):
        result.extend(overlay[len(base) :])
    return bytes(result), overlay_changes, conflicts


def build(base_path: Path, pointer_path: Path, overlay_path: Path, output_dir: Path, report_json: Path, report_markdown: Path, out_stem: str = OUT_STEM) -> dict[str, object]:
    base = base_path.read_bytes()
    pointer = pointer_path.read_bytes()
    overlay = overlay_path.read_bytes()
    candidate, overlay_changes, conflicts = compose(base, pointer, overlay)
    output_dir.mkdir(parents=True, exist_ok=True)
    rom_path = output_dir / f"{out_stem}.nes"
    ips_path = output_dir / f"{out_stem}.ips"
    rom_path.write_bytes(candidate)
    records = make_records(base, candidate)
    write_ips(ips_path, records)
    payload: dict[str, object] = {
        "status": "COMPOSED_POINTER_OWNER_WITH_NONPOINTER_OVERLAY",
        "release_status": "NOT_READY",
        "base_rom": str(base_path),
        "pointer_owner_rom": str(pointer_path),
        "overlay_rom": str(overlay_path),
        "base_md5": md5(base),
        "pointer_owner_md5": md5(pointer),
        "overlay_md5": md5(overlay),
        "candidate_rom": str(rom_path),
        "candidate_ips": str(ips_path),
        "candidate_md5": md5(candidate),
        "overlay_change_count": len(overlay_changes),
        "conflict_count": len(conflicts),
        "ips_record_count": len(records),
        "conflicts": conflicts,
        "known_limits": [
            "Pointer candidate remains the executable and pointer-table owner.",
            "Non-pointer overlay contributes only base-relative changes with no conflicting byte.",
            "Runtime route and native pixel proof remain pending for the new composition.",
        ],
    }
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Full Korean Unified Candidate",
        "",
        f"- Candidate MD5: `{payload['candidate_md5']}`.",
        f"- Pointer owner MD5: `{payload['pointer_owner_md5']}`.",
        f"- Non-pointer overlay changes applied: `{payload['overlay_change_count']}` bytes.",
        f"- Conflicting bytes retained from pointer owner: `{payload['conflict_count']}`.",
        f"- IPS records: `{payload['ips_record_count']}`.",
        "- Composition rule: pointer candidate owns structure; non-pointer candidate contributes only non-conflicting base-relative changes.",
        "- Release status: `NOT_READY`.",
        "",
        "| offset | base | pointer owner | overlay | result |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in conflicts[:200]:
        lines.append(f"| `{row['rom_offset']}` | {row['base']} | {row['pointer']} | {row['overlay']} | pointer-owner |")
    if not conflicts:
        lines.append("| none | - | - | - | no conflicts |")
    report_markdown.parent.mkdir(parents=True, exist_ok=True)
    report_markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--pointer-owner", type=Path, default=DEFAULT_POINTER)
    parser.add_argument("--overlay", type=Path, default=DEFAULT_OVERLAY)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_REPORT_MARKDOWN)
    parser.add_argument("--out-stem", default=OUT_STEM)
    args = parser.parse_args()
    payload = build(args.base.resolve(), args.pointer_owner.resolve(), args.overlay.resolve(), args.out_dir.resolve(), args.report_json.resolve(), args.report_markdown.resolve(), args.out_stem)
    print(json.dumps({
        "status": payload["status"], "candidate_md5": payload["candidate_md5"],
        "overlay_change_count": payload["overlay_change_count"], "conflict_count": payload["conflict_count"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
