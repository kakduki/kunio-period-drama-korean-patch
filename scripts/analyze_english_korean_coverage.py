#!/usr/bin/env python3
"""Compare English IPS change ownership with a Korean candidate ROM."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from analyze_reference_ips import apply_records, parse_ines_layout, parse_ips, region_for_offset


def changed_offsets(before: bytes, after: bytes) -> set[int]:
    common = min(len(before), len(after))
    changed = {index for index in range(common) if before[index] != after[index]}
    changed.update(range(common, max(len(before), len(after))))
    return changed


def parse_offset(value: str) -> int:
    return int(value, 0)


def load_classifications(path: Path) -> dict[int, str]:
    if not path.exists():
        return {}
    result: dict[int, str] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            result[int(row["record_index"])] = row.get("classification", "")
    return result


def record_report(
    base: bytes,
    reference: bytes,
    korean: bytes,
    records,
    classifications: dict[int, str],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index, record in enumerate(records):
        start = record.offset
        end = min(len(reference), start + len(record.data))
        english_changed = {
            offset for offset in range(start, end) if base[offset] != reference[offset]
        }
        korean_changed = {
            offset for offset in range(start, min(len(korean), end)) if base[offset] != korean[offset]
        }
        overlap = english_changed & korean_changed
        ratio = len(overlap) / len(english_changed) if english_changed else 1.0
        if not english_changed:
            status = "REFERENCE_NOOP"
        elif ratio == 1.0:
            status = "COVERED_SAME_OFFSETS"
        elif ratio > 0:
            status = "PARTIAL_SAME_OFFSETS"
        else:
            status = "MISSING_SAME_OFFSETS"
        region, bank = region_for_offset(start, parse_ines_layout(base))
        rows.append(
            {
                "record_index": index,
                "start": f"0x{start:05X}",
                "end_exclusive": f"0x{end:05X}",
                "length": end - start,
                "region": region,
                "bank": bank,
                "classification": classifications.get(index, ""),
                "english_changed_bytes": len(english_changed),
                "korean_changed_bytes": len(korean_changed),
                "same_offset_bytes": len(overlap),
                "same_offset_ratio": round(ratio, 4),
                "status": status,
            }
        )
    return rows


def render_markdown(payload: dict[str, object]) -> str:
    summary = payload["summary"]
    rows = payload["records"]
    assert isinstance(summary, dict)
    assert isinstance(rows, list)
    lines = [
        "# English-to-Korean Change Coverage",
        "",
        "This is an offset-ownership audit. Same-offset coverage is not semantic or visual proof; relocated Korean records may legitimately have lower overlap.",
        "",
        f"- Base MD5: `{payload['base_md5']}`.",
        f"- English reference IPS: `{payload['english_ips']}`.",
        f"- Korean candidate: `{payload['korean_rom']}`.",
        f"- English changed bytes: `{summary['english_changed_bytes']}`.",
        f"- Korean changed bytes inside English record spans: `{summary['korean_changed_bytes_in_reference_spans']}`.",
        f"- Same-offset covered bytes: `{summary['same_offset_bytes']}`.",
        f"- Records: `{summary['record_count']}`; covered `{summary['covered_records']}`; partial `{summary['partial_records']}`; missing `{summary['missing_records']}`.",
        "",
        "## Records",
        "",
        "| record | region | bank | classification | English bytes | Korean bytes | same offset | ratio | status |",
        "| ---: | --- | ---: | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['record_index']} | {row['region']} | {row['bank'] if row['bank'] is not None else '-'} | "
            f"{row['classification']} | {row['english_changed_bytes']} | {row['korean_changed_bytes']} | "
            f"{row['same_offset_bytes']} | {row['same_offset_ratio']:.2f} | {row['status']} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- `COVERED_SAME_OFFSETS` means the candidate changes every English-changed offset in that IPS record; it does not prove that the Korean bytes are correct.",
        "- `PARTIAL_SAME_OFFSETS` is expected for a candidate that implements only one renderer family or relocates records.",
        "- `MISSING_SAME_OFFSETS` identifies English-patch regions with no Korean byte change and therefore a concrete implementation gap.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_rom", type=Path)
    parser.add_argument("english_ips", type=Path)
    parser.add_argument("korean_rom", type=Path)
    parser.add_argument("--record-map", type=Path, default=Path("rom_analysis/english_patch_record_map.csv"))
    parser.add_argument("--output-json", type=Path, default=Path("rom_analysis/english_korean_coverage.json"))
    parser.add_argument("--output-markdown", type=Path, default=Path("rom_analysis/english_korean_coverage.md"))
    args = parser.parse_args()

    base = args.base_rom.read_bytes()
    korean = args.korean_rom.read_bytes()
    records, truncate_size = parse_ips(args.english_ips.read_bytes())
    reference = apply_records(base, records, truncate_size)
    if hashlib.md5(base).hexdigest() != "0d406a85285b4de8468f0dab6aad5fe5":
        raise SystemExit("unsupported base ROM")
    classifications = load_classifications(args.record_map)
    rows = record_report(base, reference, korean, records, classifications)
    english_changed = changed_offsets(base, reference)
    korean_changed = changed_offsets(base, korean)
    reference_spans = {
        offset
        for row in rows
        for offset in range(int(row["start"], 16), int(row["end_exclusive"], 16))
    }
    covered = sum(row["status"] == "COVERED_SAME_OFFSETS" for row in rows)
    partial = sum(row["status"] == "PARTIAL_SAME_OFFSETS" for row in rows)
    missing = sum(row["status"] == "MISSING_SAME_OFFSETS" for row in rows)
    payload = {
        "base_md5": hashlib.md5(base).hexdigest(),
        "english_ips": str(args.english_ips),
        "korean_rom": str(args.korean_rom),
        "summary": {
            "english_changed_bytes": len(english_changed),
            "korean_changed_bytes_in_reference_spans": len(korean_changed & reference_spans),
            "same_offset_bytes": sum(
                int(row["same_offset_bytes"]) for row in rows
            ),
            "record_count": len(rows),
            "covered_records": covered,
            "partial_records": partial,
            "missing_records": missing,
        },
        "records": rows,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.output_markdown.write_text(render_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
