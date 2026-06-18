#!/usr/bin/env python3
"""Audit soft-gate candidate ROM patch scope against the font-expanded ROM."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


PIPELINE_DIR = REPO_ROOT / "rom_analysis" / "candidate_pipeline"
OUT_JSON = PIPELINE_DIR / "patch_scope_audit.json"
OUT_MD = PIPELINE_DIR / "patch_scope_audit.md"
REPORTS = sorted((REPO_ROOT / "output").glob("kunio_period_drama_softgate_*_report.json"))


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def parse_hex(text: str) -> bytes:
    return bytes(int(part, 16) for part in text.split() if part)


def diff_offsets(before: bytes, after: bytes) -> list[int]:
    if len(before) != len(after):
        raise ValueError(f"ROM size differs: {len(before)} != {len(after)}")
    return [index for index, (left, right) in enumerate(zip(before, after)) if left != right]


def contiguous_spans(offsets: list[int]) -> list[dict[str, object]]:
    if not offsets:
        return []
    spans = []
    start = previous = offsets[0]
    for offset in offsets[1:]:
        if offset == previous + 1:
            previous = offset
            continue
        spans.append({"start": f"0x{start:05X}", "end": f"0x{previous + 1:05X}", "length": previous + 1 - start})
        start = previous = offset
    spans.append({"start": f"0x{start:05X}", "end": f"0x{previous + 1:05X}", "length": previous + 1 - start})
    return spans


def expected_spans(report: dict[str, object]) -> list[dict[str, object]]:
    if "applied" in report:
        rows = report.get("applied", [])
    else:
        rows = [report]
    spans = []
    for row in rows:
        rom_offset = int(str(row["rom_offset"]), 16)
        old_bytes = parse_hex(str(row["old_bytes"]))
        new_bytes = parse_hex(str(row["new_bytes"]))
        spans.append(
            {
                "rom_offset": f"0x{rom_offset:05X}",
                "start": rom_offset,
                "end": rom_offset + len(new_bytes),
                "old_bytes": old_bytes,
                "new_bytes": new_bytes,
                "label": str(row.get("build_id", report.get("build_id", ""))),
            }
        )
    return spans


def audit_report(report_path: Path) -> dict[str, object]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    build_id = str(report.get("build_id", report_path.stem))
    if report.get("build_status") != "PASS":
        return {
            "build_id": build_id,
            "report": rel(report_path),
            "status": "SKIP",
            "reason": f"build_status={report.get('build_status')}",
        }

    font_rom = REPO_ROOT / str(report["font_rom"])
    candidate_rom = REPO_ROOT / str(report["candidate_rom"])
    before = font_rom.read_bytes()
    after = candidate_rom.read_bytes()
    offsets = diff_offsets(before, after)
    spans = expected_spans(report)
    expected_offsets = sorted(
        {
            int(span["start"]) + index
            for span in spans
            for index, (old, new) in enumerate(zip(span["old_bytes"], span["new_bytes"]))
            if old != new
        }
    )
    errors: list[str] = []

    if offsets != expected_offsets:
        extra = sorted(set(offsets) - set(expected_offsets))
        missing = sorted(set(expected_offsets) - set(offsets))
        if extra:
            errors.append("unexpected changed offsets: " + ", ".join(f"0x{offset:05X}" for offset in extra[:16]))
        if missing:
            errors.append("expected offsets unchanged: " + ", ".join(f"0x{offset:05X}" for offset in missing[:16]))

    seen: list[tuple[int, int, str]] = []
    for span in spans:
        start = int(span["start"])
        end = int(span["end"])
        for previous_start, previous_end, label in seen:
            if start < previous_end and previous_start < end:
                errors.append(f"expected span {span['rom_offset']} overlaps {label}")
        seen.append((start, end, str(span["label"])))
        if before[start:end] != span["old_bytes"]:
            errors.append(
                f"{span['rom_offset']} font bytes {before[start:end].hex(' ').upper()} != old {span['old_bytes'].hex(' ').upper()}"
            )
        if after[start:end] != span["new_bytes"]:
            errors.append(
                f"{span['rom_offset']} candidate bytes {after[start:end].hex(' ').upper()} != new {span['new_bytes'].hex(' ').upper()}"
            )

    return {
        "build_id": build_id,
        "report": rel(report_path),
        "candidate_rom": rel(candidate_rom),
        "font_rom": rel(font_rom),
        "status": "FAIL" if errors else "PASS",
        "failure_class": "PATCH_SCOPE_MISMATCH" if errors else "none",
        "changed_offset_count": len(offsets),
        "expected_offset_count": len(expected_offsets),
        "expected_spans": [
            {
                "rom_offset": span["rom_offset"],
                "length": int(span["end"]) - int(span["start"]),
                "old_bytes": span["old_bytes"].hex(" ").upper(),
                "new_bytes": span["new_bytes"].hex(" ").upper(),
            }
            for span in spans
        ],
        "actual_changed_spans": contiguous_spans(offsets),
        "errors": errors,
    }


def make_payload() -> dict[str, object]:
    rows = [audit_report(path) for path in REPORTS]
    status_counts = {
        status: sum(1 for row in rows if row.get("status") == status)
        for status in ["PASS", "FAIL", "SKIP"]
    }
    return {
        "source": {
            "reports_glob": "output/kunio_period_drama_softgate_*_report.json",
            "comparison_base": "font_rom in each report",
        },
        "summary": {
            "row_count": len(rows),
            "status_counts": status_counts,
            "all_pass": status_counts.get("FAIL", 0) == 0 and status_counts.get("PASS", 0) > 0,
        "rule": "Each candidate ROM may differ from its font-expanded base only where planned PRG replacement bytes actually change.",
        },
        "rows": rows,
    }


def write_markdown(payload: dict[str, object]) -> None:
    lines = [
        "# Patch Scope Audit",
        "",
        "This audit compares each soft-gate candidate ROM against its font-expanded base ROM.",
        "It catches accidental edits outside the planned PRG replacement spans.",
        "",
        f"- Rows: **{payload['summary']['row_count']}**",
        f"- Status counts: `{payload['summary']['status_counts']}`",
        f"- All pass: `{payload['summary']['all_pass']}`",
        "",
        "| build id | status | changed offsets | expected offsets | spans | failure class |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for row in payload["rows"]:
        span_text = "<br>".join(
            f"`{span['rom_offset']}` {span['old_bytes']} -> {span['new_bytes']}"
            for span in row.get("expected_spans", [])
        )
        lines.append(
            f"| `{row['build_id']}` | {row['status']} | {row.get('changed_offset_count', 0)} | "
            f"{row.get('expected_offset_count', 0)} | {span_text or '-'} | {row.get('failure_class', 'none')} |"
        )
    failures = [row for row in payload["rows"] if row.get("errors")]
    if failures:
        lines += ["", "## Failures", ""]
        for row in failures:
            lines.append(f"### `{row['build_id']}`")
            lines.extend(f"- {error}" for error in row["errors"])
            lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    PIPELINE_DIR.mkdir(parents=True, exist_ok=True)
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"status_counts={payload['summary']['status_counts']}")
    return 0 if payload["summary"]["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
