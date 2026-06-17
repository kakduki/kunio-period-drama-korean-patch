#!/usr/bin/env python3
"""Build an experimental ROM with planned CHR glyphs plus safe PRG text edits.

Only equal-length runtime-confirmed text targets are patched by default. Targets
that need shortening or padding are reported but left untouched until the table
control/padding rules are confirmed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_patch import make_records, write_ips
from rom_utils import REPO_ROOT, find_rom_path


DEFAULT_PLAN = REPO_ROOT / "rom_analysis" / "korean_slot_allocation_plan.json"
DEFAULT_PADDING = REPO_ROOT / "rom_analysis" / "prg_padding_options.json"
DEFAULT_FONT_ROM = REPO_ROOT / "output" / "kunio_period_drama_korean_plan_v0.2.nes"
DEFAULT_OUT_DIR = REPO_ROOT / "output"
OUT_STEM = "kunio_period_drama_korean_prg_plan_v0.3"


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def parse_byte_list(values: list[str]) -> bytes:
    return bytes(int(value, 16) for value in values)


def parse_hex_bytes(text: str) -> bytes:
    return bytes(int(part, 16) for part in text.split() if part)


def load_padding_risks(path: Path) -> dict[str, dict[str, object]]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        str(target.get("label")): target
        for target in data.get("targets", [])
    }


def build_prg_patch(
    original_rom_path: Path,
    font_rom_path: Path,
    plan_path: Path,
    padding_path: Path,
    out_dir: Path,
    *,
    include_evidence: set[str],
    include_risks: set[str],
    exclude_labels: set[str],
    out_stem: str,
) -> dict[str, object]:
    original = original_rom_path.read_bytes()
    patched = bytearray(font_rom_path.read_bytes())
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    padding_risks = load_padding_risks(padding_path)

    applied: list[dict[str, object]] = []
    skipped: list[dict[str, object]] = []
    applied_spans: list[tuple[int, int, dict[str, object]]] = []
    for target in plan["targets"]:
        label = str(target.get("label"))
        evidence = str(target.get("evidence_level", ""))
        risk = str(padding_risks.get(label, {}).get("risk", "unknown"))
        if label in exclude_labels:
            skipped.append({
                "label": label,
                "rom_hit": target.get("rom_hit"),
                "source": target.get("source"),
                "korean": target.get("korean"),
                "risk": risk,
                "reason": "excluded by label",
            })
            continue
        if evidence not in include_evidence:
            skipped.append({
                "label": label,
                "rom_hit": target.get("rom_hit"),
                "source": target.get("source"),
                "korean": target.get("korean"),
                "risk": risk,
                "reason": f"evidence level {evidence!r} not selected",
            })
            continue
        if risk not in include_risks:
            skipped.append({
                "label": label,
                "rom_hit": target.get("rom_hit"),
                "source": target.get("source"),
                "korean": target.get("korean"),
                "risk": risk,
                "reason": f"patch risk {risk!r} not selected",
            })
            continue

        planned = parse_byte_list(list(target.get("planned_prg_bytes", [])))
        original_expected = parse_hex_bytes(str(target.get("original_expected_bytes", "")))
        rom_hit = int(str(target["rom_hit"]), 16)
        current = bytes(original[rom_hit:rom_hit + len(original_expected)])

        if not planned:
            skipped.append({
                "label": label,
                "rom_hit": target.get("rom_hit"),
                "source": target.get("source"),
                "korean": target.get("korean"),
                "risk": risk,
                "reason": "no planned PRG bytes",
            })
            continue
        if current != original_expected:
            skipped.append({
                "label": label,
                "rom_hit": target.get("rom_hit"),
                "source": target.get("source"),
                "korean": target.get("korean"),
                "risk": risk,
                "reason": f"ROM bytes {current.hex(' ').upper()} do not match expected {original_expected.hex(' ').upper()}",
            })
            continue
        if len(planned) != len(original_expected):
            skipped.append({
                "label": label,
                "rom_hit": target.get("rom_hit"),
                "source": target.get("source"),
                "korean": target.get("korean"),
                "risk": risk,
                "reason": f"length mismatch planned={len(planned)} original={len(original_expected)}",
            })
            continue
        overlap = next(
            (
                row
                for start, end, row in applied_spans
                if rom_hit < end and start < rom_hit + len(planned)
            ),
            None,
        )
        if overlap:
            skipped.append({
                "label": label,
                "rom_hit": target.get("rom_hit"),
                "source": target.get("source"),
                "korean": target.get("korean"),
                "risk": risk,
                "reason": (
                    "overlaps already-applied target "
                    f"{overlap.get('label')} at {overlap.get('rom_hit')}"
                ),
            })
            continue

        patched[rom_hit:rom_hit + len(planned)] = planned
        applied_row = {
            "label": label,
            "rom_hit": target.get("rom_hit"),
            "source": target.get("source"),
            "korean": target.get("korean"),
            "old_bytes": original_expected.hex(" ").upper(),
            "new_bytes": planned.hex(" ").upper(),
            "evidence_level": evidence,
            "risk": risk,
        }
        applied.append(applied_row)
        applied_spans.append((rom_hit, rom_hit + len(planned), applied_row))

    records = make_records(original, bytes(patched))
    out_dir.mkdir(parents=True, exist_ok=True)
    ips_path = out_dir / f"{out_stem}.ips"
    patched_path = out_dir / f"{out_stem}.nes"
    report_path = out_dir / f"{out_stem}_build_report.json"

    write_ips(ips_path, records)
    patched_path.write_bytes(patched)

    changed_offsets = [
        offset for offset, (a, b) in enumerate(zip(original, patched)) if a != b
    ]
    report = {
        "plan": str(plan_path),
        "padding_options": str(padding_path),
        "font_rom": str(font_rom_path),
        "original_rom": str(original_rom_path),
        "original_md5": md5(original),
        "patched_md5": md5(bytes(patched)),
        "patched_rom_path": str(patched_path),
        "ips_path": str(ips_path),
        "include_evidence": sorted(include_evidence),
        "include_risks": sorted(include_risks),
        "exclude_labels": sorted(exclude_labels),
        "applied_count": len(applied),
        "skipped_count": len(skipped),
        "changed_bytes_total": len(changed_offsets),
        "changed_rom_range": [
            f"0x{min(changed_offsets):05X}",
            f"0x{max(changed_offsets):05X}",
        ] if changed_offsets else [],
        "ips_records": len(records),
        "applied": applied,
        "skipped": skipped,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?", help="Optional original .nes path; defaults to rom/*.nes")
    parser.add_argument("--rom", dest="rom_option", help="Optional original .nes path; overrides the positional rom argument.")
    parser.add_argument("--font-rom", default=str(DEFAULT_FONT_ROM))
    parser.add_argument("--plan", default=str(DEFAULT_PLAN))
    parser.add_argument("--padding-options", default=str(DEFAULT_PADDING))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--out-stem", default=OUT_STEM)
    parser.add_argument(
        "--include-evidence",
        default="runtime-confirmed",
        help="Comma-separated evidence levels to patch.",
    )
    parser.add_argument(
        "--include-risks",
        default="safe-equal-length",
        help="Comma-separated patch-risk labels to patch.",
    )
    parser.add_argument(
        "--exclude-labels",
        default="",
        help="Comma-separated target labels to leave unpatched even if otherwise selected.",
    )
    args = parser.parse_args()

    rom_arg = args.rom_option or args.rom
    original_rom = find_rom_path(rom_arg).resolve()
    font_rom = Path(args.font_rom).expanduser().resolve()
    plan = Path(args.plan).expanduser().resolve()
    padding = Path(args.padding_options).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    include_evidence = {part.strip() for part in args.include_evidence.split(",") if part.strip()}
    include_risks = {part.strip() for part in args.include_risks.split(",") if part.strip()}
    exclude_labels = {part.strip() for part in args.exclude_labels.split(",") if part.strip()}

    report = build_prg_patch(
        original_rom,
        font_rom,
        plan,
        padding,
        out_dir,
        include_evidence=include_evidence,
        include_risks=include_risks,
        exclude_labels=exclude_labels,
        out_stem=args.out_stem,
    )
    print(f"patched ROM: {report['patched_rom_path']}")
    print(f"IPS: {report['ips_path']}")
    print(f"applied={report['applied_count']} skipped={report['skipped_count']} changed_bytes={report['changed_bytes_total']}")
    print(f"patched MD5: {report['patched_md5']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
