#!/usr/bin/env python3
"""Compare v0.4 applied PRG edits with broad-scan promotion candidates.

The broad scan found likely additional labels in the same Bank 1 area. This
report highlights overlaps so a future v0.5 does not blindly stack conflicting
edits on top of v0.4.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V04_REPORT = ROOT / "output" / "kunio_period_drama_korean_prg_plan_v0.4_equal_length_static_build_report.json"
BROAD_PATCHABILITY = ROOT / "rom_analysis" / "broad_scan_patchability.json"
OUT_JSON = ROOT / "rom_analysis" / "v04_broad_candidate_conflicts.json"
OUT_MD = ROOT / "rom_analysis" / "v04_broad_candidate_conflicts.md"


def parse_hex_bytes(raw: str) -> bytes:
    return bytes(int(part, 16) for part in raw.split() if part)


def span(start: int, raw_bytes: str) -> tuple[int, int]:
    return start, start + len(parse_hex_bytes(raw_bytes))


def overlap(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a[0] < b[1] and b[0] < a[1]


def build_report() -> dict[str, object]:
    v04 = json.loads(V04_REPORT.read_text(encoding="utf-8"))
    broad = json.loads(BROAD_PATCHABILITY.read_text(encoding="utf-8"))

    v04_rows = []
    for row in v04.get("applied", []):
        start = int(str(row["rom_hit"]), 16)
        current_span = span(start, str(row["old_bytes"]))
        v04_rows.append(
            {
                "label": row.get("label", ""),
                "source": row.get("source", ""),
                "korean": row.get("korean", ""),
                "rom_hit": f"0x{start:05X}",
                "span": [f"0x{current_span[0]:05X}", f"0x{current_span[1] - 1:05X}"],
                "old_bytes": row.get("old_bytes", ""),
                "new_bytes": row.get("new_bytes", ""),
                "evidence_level": row.get("evidence_level", ""),
                "risk": row.get("risk", ""),
                "_span_int": current_span,
            }
        )

    broad_rows = []
    for row in broad.get("promotion_candidates", []):
        start = int(str(row["rom_offset"]), 16)
        current_span = span(start, str(row["bytes"]))
        broad_rows.append(
            {
                "source": row.get("source", ""),
                "romaji": row.get("romaji", ""),
                "korean": row.get("korean", ""),
                "confidence": row.get("confidence", ""),
                "rom_hit": f"0x{start:05X}",
                "span": [f"0x{current_span[0]:05X}", f"0x{current_span[1] - 1:05X}"],
                "original_bytes": row.get("bytes", ""),
                "new_glyphs": row.get("new_glyphs", []),
                "_span_int": current_span,
            }
        )

    conflicts = []
    clean_broad = []
    for broad_row in broad_rows:
        hits = [v04_row for v04_row in v04_rows if overlap(broad_row["_span_int"], v04_row["_span_int"])]
        if not hits:
            clean_broad.append(broad_row)
            continue
        for v04_row in hits:
            conflicts.append(
                {
                    "broad_rom_hit": broad_row["rom_hit"],
                    "broad_span": broad_row["span"],
                    "broad_source": broad_row["source"],
                    "broad_romaji": broad_row["romaji"],
                    "broad_korean": broad_row["korean"],
                    "broad_confidence": broad_row["confidence"],
                    "broad_original_bytes": broad_row["original_bytes"],
                    "v04_rom_hit": v04_row["rom_hit"],
                    "v04_span": v04_row["span"],
                    "v04_label": v04_row["label"],
                    "v04_source": v04_row["source"],
                    "v04_korean": v04_row["korean"],
                    "v04_old_bytes": v04_row["old_bytes"],
                    "v04_new_bytes": v04_row["new_bytes"],
                    "decision": "manual screen proof required before keeping either interpretation",
                }
            )

    for row in v04_rows:
        row.pop("_span_int", None)
    for row in broad_rows:
        row.pop("_span_int", None)
    for row in clean_broad:
        row.pop("_span_int", None)

    high_conflict_count = sum(1 for row in conflicts if row["broad_confidence"] == "high")
    return {
        "source": {
            "v04_report": str(V04_REPORT.relative_to(ROOT)),
            "broad_patchability": str(BROAD_PATCHABILITY.relative_to(ROOT)),
        },
        "summary": {
            "v04_applied_edits": len(v04_rows),
            "broad_promotion_candidates": len(broad_rows),
            "overlapping_conflicts": len(conflicts),
            "high_confidence_conflicts": high_conflict_count,
            "non_overlapping_broad_candidates": len(clean_broad),
        },
        "conflicts": conflicts,
        "non_overlapping_broad_candidates": clean_broad,
        "rule": [
            "Do not build v0.5 by simply adding broad candidates on top of v0.4.",
            "Overlapping records indicate ambiguous static interpretation; manual screen evidence decides.",
            "If a broad candidate is confirmed, the conflicting v0.4 edit may need to be replaced or removed.",
        ],
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# v0.4 / Broad Candidate Conflicts",
        "",
        "This report compares v0.4 applied PRG edits with broad-scan promotion candidates.",
        "",
        "## Summary",
        "",
        f"- v0.4 applied edits: **{summary['v04_applied_edits']}**",
        f"- Broad promotion candidates: **{summary['broad_promotion_candidates']}**",
        f"- Overlapping conflicts: **{summary['overlapping_conflicts']}**",
        f"- High-confidence conflicts: **{summary['high_confidence_conflicts']}**",
        f"- Non-overlapping broad candidates: **{summary['non_overlapping_broad_candidates']}**",
        "",
        "## Conflicts",
        "",
        "| broad ROM/span | broad meaning | confidence | v0.4 ROM/span | v0.4 meaning | decision |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["conflicts"]:
        lines.append(
            f"| `{row['broad_rom_hit']}` `{row['broad_span'][0]}-{row['broad_span'][1]}` | "
            f"{row['broad_source']} -> {row['broad_korean']} | {row['broad_confidence']} | "
            f"`{row['v04_rom_hit']}` `{row['v04_span'][0]}-{row['v04_span'][1]}` | "
            f"{row['v04_source']} -> {row['v04_korean']} | {row['decision']} |"
        )

    lines += [
        "",
        "## Non-Overlapping Broad Candidates",
        "",
        "| ROM/span | source | korean | confidence | original bytes | new glyphs |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["non_overlapping_broad_candidates"]:
        new_glyphs = "".join(row.get("new_glyphs", [])) or "-"
        lines.append(
            f"| `{row['rom_hit']}` `{row['span'][0]}-{row['span'][1]}` | "
            f"{row['source']} | {row['korean']} | {row['confidence']} | "
            f"`{row['original_bytes']}` | {new_glyphs} |"
        )

    lines += [
        "",
        "## Rule",
        "",
        "- Do not build v0.5 by simply adding broad candidates on top of v0.4.",
        "- Overlapping records indicate ambiguous static interpretation; manual screen evidence decides.",
        "- If a broad candidate is confirmed, the conflicting v0.4 edit may need to be replaced or removed.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = build_report()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(
        "v04={v04_applied_edits} broad={broad_promotion_candidates} conflicts={overlapping_conflicts} high_conflicts={high_confidence_conflicts}".format(
            **payload["summary"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
