#!/usr/bin/env python3
"""Build a v0.4.3 candidate only from manually verified broad-scan proof.

This builder is deliberately evidence-gated. A CPU read hit alone is not enough:
the matching ROM offset must also be marked `visual_context_confirmed=true` in
the visual review JSON before any byte is promoted into a ROM/IPS candidate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_patch import make_records, write_ips
from readable_labels import readable_for_romaji
from rom_utils import REPO_ROOT, find_rom_path


DEFAULT_V042_ROM = REPO_ROOT / "output" / "kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes"
DEFAULT_PROOF_PACKET = REPO_ROOT / "rom_analysis" / "v042_manual_proof_packet.json"
DEFAULT_SUMMARY = REPO_ROOT / "rom_analysis" / "manual_screen_dump_broad_scan" / "summary.json"
DEFAULT_REVIEW = REPO_ROOT / "rom_analysis" / "manual_screen_dump_broad_scan" / "visual_review.json"
DEFAULT_OUT_DIR = REPO_ROOT / "output"
OUT_STEM = "kunio_period_drama_korean_prg_plan_v0.4.3_broad_verified"


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def parse_hex_bytes(raw: str) -> bytes:
    return bytes(int(part.replace("0x", ""), 16) for part in str(raw).split() if part)


def normalize_rom(raw: object) -> str:
    text = str(raw).replace("ROM+", "").strip()
    return f"0x{int(text, 16):05X}"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def write_review_template(path: Path, proof_packet: dict[str, object]) -> bool:
    rows_by_rom: dict[str, dict[str, object]] = {}
    if path.exists():
        current = load_json(path)
        for row in current.get("rows", []):
            if isinstance(row, dict) and row.get("rom_offset"):
                rows_by_rom[normalize_rom(row.get("rom_offset"))] = dict(row)

    rows = []
    for task in proof_packet.get("tasks", []):
        rom = normalize_rom(task.get("rom_offset"))
        row = rows_by_rom.get(rom, {})
        row.update({
            "task": task.get("task"),
            "rom_offset": task.get("rom_offset"),
            "label": task.get("label", ""),
            "romaji": task.get("romaji", ""),
            "source_display": readable_for_romaji(task.get("romaji", "")).get("source_display", ""),
            "korean_display": readable_for_romaji(task.get("romaji", "")).get("korean_display", ""),
            "meaning": readable_for_romaji(task.get("romaji", "")).get("meaning", ""),
            "screen_hint": readable_for_romaji(task.get("romaji", "")).get("screen_hint", ""),
            "category": task.get("category", ""),
            "source": task.get("source", ""),
            "korean": task.get("korean", ""),
        })
        row.setdefault("visual_context_confirmed", False)
        row.setdefault("screen_context", "")
        row.setdefault("reviewer_note", "")
        rows.append(row)

    payload = {
        "purpose": "Set visual_context_confirmed=true only after the FCEUX screenshot/visible screen matches this row.",
        "source_proof_packet": str(DEFAULT_PROOF_PACKET.relative_to(REPO_ROOT)),
        "rows": rows,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return not bool(rows_by_rom)


def approved_reviews(review: dict[str, object]) -> dict[str, dict[str, object]]:
    out = {}
    for row in review.get("rows", []):
        if not isinstance(row, dict):
            continue
        if row.get("visual_context_confirmed") is True:
            out[normalize_rom(row.get("rom_offset"))] = row
    return out


def summary_matches(summary: dict[str, object]) -> dict[str, dict[str, object]]:
    out = {}
    for row in summary.get("promotable_after_visual_review", []):
        if not isinstance(row, dict):
            continue
        out[normalize_rom(row.get("rom_offset"))] = row
    return out


def proof_tasks(proof_packet: dict[str, object]) -> dict[str, dict[str, object]]:
    out = {}
    for row in proof_packet.get("tasks", []):
        if not isinstance(row, dict):
            continue
        out[normalize_rom(row.get("rom_offset"))] = row
    return out


def build_candidate(
    *,
    base_rom: Path,
    v042_rom: Path,
    proof_packet_path: Path,
    summary_path: Path,
    review_path: Path,
    out_dir: Path,
    out_stem: str,
) -> dict[str, object]:
    proof_packet = load_json(proof_packet_path)
    review_created = write_review_template(review_path, proof_packet)
    summary = load_json(summary_path)
    review = load_json(review_path)

    approved = approved_reviews(review)
    matches = summary_matches(summary)
    tasks = proof_tasks(proof_packet)
    base = base_rom.read_bytes()
    patched = bytearray(v042_rom.read_bytes())

    applied = []
    skipped = []
    for rom_offset, task in sorted(tasks.items()):
        review_row = approved.get(rom_offset)
        match_row = matches.get(rom_offset)
        if review_row is None:
            skipped.append({
                "rom_offset": rom_offset,
                "romaji": task.get("romaji", ""),
                "category": task.get("category", ""),
                "source": task.get("source", ""),
                "korean": task.get("korean", ""),
                "reason": "visual_context_confirmed is not true",
            })
            continue
        if match_row is None:
            skipped.append({
                "rom_offset": rom_offset,
                "romaji": task.get("romaji", ""),
                "category": task.get("category", ""),
                "source": task.get("source", ""),
                "korean": task.get("korean", ""),
                "reason": "no active CPU read match in broad-scan summary",
            })
            continue

        offset = int(rom_offset, 16)
        original = parse_hex_bytes(str(task.get("original_bytes", "")))
        planned = parse_hex_bytes(str(task.get("planned_prg_bytes", "")))
        base_current = base[offset:offset + len(original)]
        v042_current = bytes(patched[offset:offset + len(original)])
        if not original or not planned:
            skipped.append({"rom_offset": rom_offset, "reason": "missing original or planned bytes"})
            continue
        if len(original) != len(planned):
            skipped.append({"rom_offset": rom_offset, "reason": "planned bytes are not equal length"})
            continue
        if base_current != original:
            skipped.append({
                "rom_offset": rom_offset,
                "reason": f"base bytes {base_current.hex(' ').upper()} do not match expected {original.hex(' ').upper()}",
            })
            continue
        if v042_current != original:
            skipped.append({
                "rom_offset": rom_offset,
                "reason": f"v0.4.2 bytes {v042_current.hex(' ').upper()} are not still original {original.hex(' ').upper()}",
            })
            continue

        patched[offset:offset + len(planned)] = planned
        applied.append({
            "rom_offset": rom_offset,
            "task": task.get("task"),
            "kind": task.get("kind", ""),
            "confidence": task.get("confidence", ""),
            "romaji": task.get("romaji", ""),
            "category": task.get("category", ""),
            "source": task.get("source", ""),
            "korean": task.get("korean", ""),
            "old_bytes": original.hex(" ").upper(),
            "new_bytes": planned.hex(" ").upper(),
            "screen_context": review_row.get("screen_context", ""),
            "reviewer_note": review_row.get("reviewer_note", ""),
        })

    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"{out_stem}_build_report.json"
    report: dict[str, object] = {
        "verdict": "no candidate built; manual CPU-read and visual-context evidence is incomplete",
        "base_rom": rel(base_rom),
        "v042_rom": rel(v042_rom),
        "proof_packet": rel(proof_packet_path),
        "summary": rel(summary_path),
        "visual_review": rel(review_path),
        "visual_review_template_created": review_created,
        "base_md5": md5(base),
        "v042_md5": md5(v042_rom.read_bytes()),
        "summary_status": summary.get("status", "missing"),
        "approved_visual_reviews": len(approved),
        "active_summary_matches": len(matches),
        "applied_count": len(applied),
        "skipped_count": len(skipped),
        "applied": applied,
        "skipped": skipped,
    }

    if applied:
        records = make_records(base, bytes(patched))
        ips_path = out_dir / f"{out_stem}.ips"
        patched_path = out_dir / f"{out_stem}.nes"
        write_ips(ips_path, records)
        patched_path.write_bytes(patched)
        report.update(
            {
                "verdict": "manual-test candidate built from v0.4.2 plus visually confirmed broad-scan proof",
                "patched_rom_path": rel(patched_path),
                "ips_path": rel(ips_path),
                "patched_md5": md5(bytes(patched)),
                "ips_records": len(records),
            }
        )

    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?", help="Base .nes ROM path; defaults to rom/*.nes")
    parser.add_argument("--rom", dest="rom_option", help="Base .nes ROM path; overrides positional rom.")
    parser.add_argument("--v042-rom", default=str(DEFAULT_V042_ROM))
    parser.add_argument("--proof-packet", default=str(DEFAULT_PROOF_PACKET))
    parser.add_argument("--summary", default=str(DEFAULT_SUMMARY))
    parser.add_argument("--visual-review", default=str(DEFAULT_REVIEW))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--out-stem", default=OUT_STEM)
    args = parser.parse_args()

    report = build_candidate(
        base_rom=find_rom_path(args.rom_option or args.rom).resolve(),
        v042_rom=Path(args.v042_rom).expanduser().resolve(),
        proof_packet_path=Path(args.proof_packet).expanduser().resolve(),
        summary_path=Path(args.summary).expanduser().resolve(),
        review_path=Path(args.visual_review).expanduser().resolve(),
        out_dir=Path(args.out_dir).expanduser().resolve(),
        out_stem=args.out_stem,
    )
    print(f"verdict={report['verdict']}")
    print(f"applied={report['applied_count']} skipped={report['skipped_count']}")
    if "ips_path" in report:
        print(f"IPS: {report['ips_path']}")
        print(f"patched MD5: {report['patched_md5']}")
    else:
        print(f"report only: output/{args.out_stem}_build_report.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
