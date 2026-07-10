#!/usr/bin/env python3
"""Classify Korean v0.4.3 targets by static overlap with verified English IPS runs.

This intentionally answers only whether the English patch also touched the physical
PRG bytes. It never asserts that either patch's bytes are executed or displayed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


EXPECTED_BASE_MD5 = "0d406a85285b4de8468f0dab6aad5fe5"
OFFSET_CONVENTION = "iNES file offset including 16-byte header"


def overlap(start_a: int, end_a: int, start_b: int, end_b: int) -> bool:
    return start_a < end_b and start_b < end_a


def correlate(status_path: Path, runs_path: Path, base_path: Path) -> dict[str, object]:
    status = json.loads(status_path.read_text(encoding="utf-8"))
    run_map = json.loads(runs_path.read_text(encoding="utf-8"))
    base = base_path.read_bytes()
    base_md5 = hashlib.md5(base).hexdigest()
    if base_md5 != EXPECTED_BASE_MD5:
        raise ValueError(f"base ROM MD5 {base_md5} != verified {EXPECTED_BASE_MD5}")
    if run_map["base"]["md5"] != base_md5:
        raise ValueError("run map base digest does not match correlation base ROM")

    output_rows: list[dict[str, object]] = []
    for source in status["rows"]:
        start = int(source["rom_offset"], 16)
        expected = bytes.fromhex(source["original_bytes"])
        end = start + len(expected)
        actual = base[start:end]
        if actual != expected:
            raise ValueError(
                f"task {source['task']} original bytes mismatch at 0x{start:05X}: "
                f"status={expected.hex(' ').upper()} base={actual.hex(' ').upper()}"
            )
        hits = [run for run in run_map["runs"] if overlap(start, end, int(run["start"]), int(run["end_exclusive"]))]
        supported = bool(hits) and all(run["region"] == "prg" for run in hits)
        classification = "structurally_supported" if supported else "unrelated_to_english_reference"
        hit_ranges = [
            {
                "run_id": run["id"],
                "file_start": run["start"],
                "file_end_exclusive": run["end_exclusive"],
                "physical_bank": run["physical_bank"],
                "overlap_start": max(start, int(run["start"])),
                "overlap_end_exclusive": min(end, int(run["end_exclusive"])),
                "overlap_bytes": min(end, int(run["end_exclusive"])) - max(start, int(run["start"])),
            }
            for run in hits
        ]
        if supported:
            reason = (
                "The verified English patch changes this exact PRG byte span; this is reusable "
                "structural prioritization only, not proof of the Japanese renderer/pointer path."
            )
        else:
            reason = (
                "No verified English changed run overlaps this exact span. This does not disprove "
                "the Japanese target, but the English reference supplies no physical support here."
            )
        output_rows.append({
            "task": source["task"],
            "file_offset": start,
            "rom_offset": source["rom_offset"],
            "byte_length": len(expected),
            "offset_convention": OFFSET_CONVENTION,
            "base_bytes_expected": source["original_bytes"],
            "base_bytes_actual": actual.hex(" ").upper(),
            "base_bytes_verified": True,
            "planned_korean_prg_bytes": source["planned_prg_bytes"],
            "source_display": source["source_display"],
            "korean_display": source["korean_display"],
            "classification": classification,
            "overlap_run_ids": [entry["run_id"] for entry in hit_ranges],
            "overlap_ranges": hit_ranges,
            "runtime_proof_required": True,
            "release_ready": False,
            "reason": reason,
        })
    counts: dict[str, int] = {}
    for row in output_rows:
        counts[row["classification"]] = counts.get(row["classification"], 0) + 1
    return {
        "schema_version": 1,
        "purpose": "static physical-offset correlation only; no emulator or runtime claim",
        "offset_convention": {
            "coordinate_space": OFFSET_CONVENTION,
            "header_bytes": 16,
            "intervals": "start inclusive, end_exclusive",
            "target_span_rule": "file_offset + len(original_bytes)",
            "physical_prg_bank_rule": "(file_offset - 0x10) // 0x2000; not a CPU mapper bank",
        },
        "method": "exact physical byte-span overlap against digest-verified English IPS runs; no emulator evidence used",
        "base": {"path": str(base_path), "md5": base_md5},
        "reference": {"runs_path": str(runs_path), "ips_sha256": run_map["ips"]["sha256"], "record_count": run_map["ips"]["records"]},
        "source_status": str(status_path),
        "classification_counts": counts,
        "rows": output_rows,
    }


def markdown(result: dict[str, object]) -> str:
    rows = list(result["rows"])
    lines = [
        "# Korean targets × English-reference structural correlation",
        "",
        "> Decision rule: this report replaces menu-loop observation with a reproducible physical-diff check. “Structurally supported” means only that the verified English patch also changes the exact Japanese PRG span. It is **not** a pointer, CPU-read, visual, or release proof.",
        "",
        f"- Base MD5: `{result['base']['md5']}`",
        f"- English IPS SHA-256: `{result['reference']['ips_sha256']}`",
        f"- English IPS records: **{result['reference']['record_count']}**",
        f"- Classifications: `{result['classification_counts']}`",
        "",
        "| task | target file offset | source → Korean | static result | English run IDs | runtime/release |",
        "|---:|---|---|---|---|---|",
    ]
    for row in rows:
        source = f"{row['source_display']} → {row['korean_display']}"
        ids = ", ".join(str(value) for value in row["overlap_run_ids"]) or "—"
        lines.append(f"| {row['task']} | `0x{row['file_offset']:05X}` | {source} | `{row['classification']}` | {ids} | required / no |")
    lines += [
        "",
        "## Interpretation",
        "",
        "- **Supported rows are prioritization candidates, not patch-ready rows.** They show that the historical English patch altered the same PRG span, so these offsets deserve code/pointer analysis before unrelated targets.",
        "- **Unrelated rows are not rejected.** They simply cannot borrow structural confidence from the English IPS and must wait for another static route or a debugger-capable runtime trace.",
        "- No Korean IPS/ROM was generated or modified by this analysis.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", type=Path, default=Path("rom_analysis/v043_proof_status.json"))
    parser.add_argument("--runs", type=Path, default=Path("analysis/english_reference_runs.json"))
    parser.add_argument("--rom", type=Path, default=Path("rom/kunio.nes"))
    parser.add_argument("--json-output", type=Path, default=Path("analysis/korean_target_english_reference_correlation.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("analysis/korean_target_english_reference_correlation.md"))
    args = parser.parse_args()
    result = correlate(args.status, args.runs, args.rom)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(markdown(result), encoding="utf-8")
    print(json.dumps({"classification_counts": result["classification_counts"], "targets": len(result["rows"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
