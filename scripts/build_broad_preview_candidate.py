#!/usr/bin/env python3
"""Build an unverified broad-scan preview IPS for manual screen testing.

This is intentionally not a primary candidate. It applies only non-overlapping
font-ready broad-scan rows to v0.4.2 so a tester can reach the related screen
and see whether the expected text changes in the right context.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_patch import make_records, write_ips
from readable_labels import readable_for_romaji
from rom_utils import REPO_ROOT, find_rom_path


READINESS_JSON = REPO_ROOT / "rom_analysis" / "v042_text_promotion_readiness.json"
BASE_V042_ROM = REPO_ROOT / "output" / "kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes"
OUT_DIR = REPO_ROOT / "output"
REPORT_DIR = REPO_ROOT / "rom_analysis"
OUT_STEM = "kunio_period_drama_korean_prg_plan_v0.4.3_broad_preview_unverified"


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def parse_hex_bytes(raw: object) -> bytes:
    return bytes(int(part.replace("0x", ""), 16) for part in str(raw).split() if part)


def planned_bytes(row: dict[str, object]) -> bytes:
    values = row.get("planned_prg_bytes", [])
    if isinstance(values, list):
        return bytes(int(str(value).replace("0x", ""), 16) for value in values)
    return parse_hex_bytes(values)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def candidate_rows(include_conflicts: bool) -> list[dict[str, object]]:
    readiness = json.loads(READINESS_JSON.read_text(encoding="utf-8"))
    rows = []
    for row in readiness.get("candidates", []):
        kind = str(row.get("kind", ""))
        if kind == "non_overlapping_needs_manual_screen" or (
            include_conflicts and kind == "conflict_alternative_needs_manual_screen"
        ):
            rows.append(row)
    return sorted(rows, key=lambda row: int(str(row["rom_offset"]), 16))


def write_markdown(path: Path, report: dict[str, object]) -> None:
    lines = [
        "# Broad Preview Candidate",
        "",
        "This is an unverified manual-screen-test IPS. It is not the primary patch.",
        "",
        f"- Candidate: **{report['candidate']}**",
        f"- Base v0.4.2 MD5: `{report['base_v042_md5']}`",
        f"- Preview MD5: `{report['patched_md5']}`",
        f"- Applied rows: **{report['applied_count']}**",
        f"- Skipped rows: **{report['skipped_count']}**",
        f"- IPS records: **{report.get('ips_records', 0)}**",
        f"- Local IPS: `{report.get('ips_path', '')}`",
        f"- Local ROM: `{report.get('patched_rom_path', '')}`",
        "",
        "## Applied Rows",
        "",
        "| ROM | expected text | Korean | original bytes | preview bytes | reason |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in report["applied"]:
        lines.append(
            f"| `{row['rom_offset']}` | {row['source_display']} | {row['korean_display']} | "
            f"`{row['old_bytes']}` | `{row['new_bytes']}` | {row['reason']} |"
        )

    if report["skipped"]:
        lines += [
            "",
            "## Skipped Rows",
            "",
            "| ROM | expected text | reason |",
            "| --- | --- | --- |",
        ]
        for row in report["skipped"]:
            lines.append(f"| `{row['rom_offset']}` | {row['source_display']} | {row['reason']} |")

    lines += [
        "",
        "## Rules",
        "",
        "- Use this only for manual FCEUX screen comparison.",
        "- Do not mark these rows as verified until the base-ROM CPU read and visible screen context gates pass.",
        "- The tracked release remains v0.4.2 font-expanded unless the strict v0.4.3 proof builder approves rows.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build(include_conflicts: bool = False) -> dict[str, object]:
    base_rom = find_rom_path(None).resolve()
    base = base_rom.read_bytes()
    if not BASE_V042_ROM.exists():
        raise FileNotFoundError(f"Missing v0.4.2 ROM: {BASE_V042_ROM}")
    patched = bytearray(BASE_V042_ROM.read_bytes())
    base_v042 = bytes(patched)

    applied = []
    skipped = []
    for row in candidate_rows(include_conflicts):
        rom_offset = str(row["rom_offset"])
        offset = int(rom_offset, 16)
        original = parse_hex_bytes(row.get("original_bytes", ""))
        planned = planned_bytes(row)
        readable = readable_for_romaji(row.get("romaji", ""))
        source_display = readable.get("source_display") or str(row.get("source", ""))
        korean_display = readable.get("korean_display") or str(row.get("korean", ""))

        if not original or not planned:
            skipped.append(
                {
                    "rom_offset": rom_offset,
                    "source_display": source_display,
                    "korean_display": korean_display,
                    "reason": "missing original or planned bytes",
                }
            )
            continue
        if len(original) != len(planned):
            skipped.append(
                {
                    "rom_offset": rom_offset,
                    "source_display": source_display,
                    "korean_display": korean_display,
                    "reason": "planned bytes are not equal length",
                }
            )
            continue
        current = bytes(patched[offset:offset + len(original)])
        if current != original:
            skipped.append(
                {
                    "rom_offset": rom_offset,
                    "source_display": source_display,
                    "korean_display": korean_display,
                    "reason": f"v0.4.2 bytes {current.hex(' ').upper()} do not match expected {original.hex(' ').upper()}",
                }
            )
            continue

        patched[offset:offset + len(planned)] = planned
        applied.append(
            {
                "rom_offset": rom_offset,
                "kind": row.get("kind", ""),
                "confidence": row.get("confidence", ""),
                "romaji": row.get("romaji", ""),
                "source_display": source_display,
                "korean_display": korean_display,
                "old_bytes": original.hex(" ").upper(),
                "new_bytes": planned.hex(" ").upper(),
                "reason": "non-overlapping broad-scan preview row",
            }
        )

    records = make_records(base, bytes(patched))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ips_path = OUT_DIR / f"{OUT_STEM}.ips"
    patched_path = OUT_DIR / f"{OUT_STEM}.nes"
    report_json = REPORT_DIR / f"{OUT_STEM}_report.json"
    report_md = REPORT_DIR / f"{OUT_STEM}_report.md"
    write_ips(ips_path, records)
    patched_path.write_bytes(patched)

    report = {
        "candidate": "v0.4.3 broad preview unverified",
        "verdict": "manual-screen-test preview only; not primary and not proof-approved",
        "base_rom": rel(base_rom),
        "base_md5": md5(base),
        "base_v042_rom": rel(BASE_V042_ROM),
        "base_v042_md5": md5(base_v042),
        "patched_rom_path": rel(patched_path),
        "ips_path": rel(ips_path),
        "patched_md5": md5(bytes(patched)),
        "include_conflicts": include_conflicts,
        "applied_count": len(applied),
        "skipped_count": len(skipped),
        "ips_records": len(records),
        "applied": applied,
        "skipped": skipped,
    }
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(report_md, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--include-conflicts",
        action="store_true",
        help="Also include conflict alternatives. Off by default to keep preview low-risk.",
    )
    args = parser.parse_args()
    report = build(include_conflicts=args.include_conflicts)
    print(f"verdict={report['verdict']}")
    print(f"applied={report['applied_count']} skipped={report['skipped_count']}")
    print(f"IPS: {report['ips_path']}")
    print(f"patched MD5: {report['patched_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
