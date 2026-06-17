#!/usr/bin/env python3
"""Generate a compact decision matrix for the next Korean patch work."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


PRIMARY_REPORT = REPO_ROOT / "output" / "kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded_build_report.json"
MANUAL_QUEUE = REPO_ROOT / "rom_analysis" / "manual_capture_queue.json"
CONFLICTS = REPO_ROOT / "rom_analysis" / "v04_broad_candidate_conflicts.json"
BROAD_PATCHABILITY = REPO_ROOT / "rom_analysis" / "broad_scan_patchability.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "patch_decision_matrix.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "patch_decision_matrix.md"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def span_key(start: str, end: str) -> tuple[int, int]:
    return int(start, 16), int(end, 16)


def classify_skip(row: dict[str, object], queue_by_label: dict[str, dict[str, object]], conflict_labels: set[str]) -> str:
    label = str(row.get("label", ""))
    reason = str(row.get("reason", ""))
    risk = str(row.get("risk", ""))
    queued = queue_by_label.get(label)
    if label in conflict_labels or "excluded by label" in reason:
        return "conflict_needs_manual_screen"
    if "overlaps already-applied" in reason:
        return "local_overlap_needs_manual_screen"
    if risk == "needs-padding-rule":
        if queued and "runtime-confirmed shortened" in str(queued.get("capture_reason", "")):
            return "runtime_padding_rule_blocker"
        if queued and int(queued.get("runtime_hits", 0) or 0) > 0:
            return "wrong_context_or_padding_candidate"
        return "padding_rule_blocker"
    if queued:
        return "screen_proof_needed"
    return "deferred_low_evidence"


def next_action(kind: str) -> str:
    actions = {
        "applied": "Use v0.4.2 ROM and manually verify the visible text on its target screen.",
        "conflict_needs_manual_screen": "Use base ROM broad-scan dump first, then decide whether to keep v0.4.1 exclusion or replace with broad interpretation.",
        "local_overlap_needs_manual_screen": "Manually capture this exact screen; the nearby applied row may represent a different overlapping interpretation.",
        "runtime_padding_rule_blocker": "Test padding experiment ROMs visually on the same status screen before promoting a shortened replacement.",
        "wrong_context_or_padding_candidate": "Capture the exact screen manually; previous autoplay read hits used the wrong active bank/context.",
        "padding_rule_blocker": "Do not patch until a padding/terminator rule is proven visually.",
        "screen_proof_needed": "Manually reach the target screen and run the one-shot screen dump.",
        "deferred_low_evidence": "Leave unpatched until stronger static or runtime evidence appears.",
        "broad_non_overlapping": "Capture on base ROM; if confirmed, extend glyph plan and build a separate v0.5 experiment.",
    }
    return actions.get(kind, "Review manually before patching.")


def make_matrix() -> dict[str, object]:
    primary = load_json(PRIMARY_REPORT)
    manual = load_json(MANUAL_QUEUE)
    conflicts = load_json(CONFLICTS)
    broad = load_json(BROAD_PATCHABILITY)

    queue_by_label = {str(row.get("label")): row for row in manual.get("queue", [])}
    conflict_labels = {str(row.get("v04_label")) for row in conflicts.get("conflicts", []) if row.get("v04_label")}

    rows: list[dict[str, object]] = []
    for row in primary.get("applied", []):
        label = str(row.get("label", ""))
        queued = queue_by_label.get(label, {})
        rows.append(
            {
                "label": label,
                "status": "applied",
                "priority": int(queued.get("capture_priority", 25) or 25),
                "kind": "applied",
                "rom_hit": row.get("rom_hit", ""),
                "source": row.get("source", ""),
                "korean": row.get("korean", ""),
                "evidence_level": row.get("evidence_level", ""),
                "risk": row.get("risk", ""),
                "old_bytes": row.get("old_bytes", ""),
                "new_bytes": row.get("new_bytes", ""),
                "capture_reason": queued.get("capture_reason", "applied candidate still needs visual proof"),
                "next_action": next_action("applied"),
            }
        )

    for row in primary.get("skipped", []):
        label = str(row.get("label", ""))
        queued = queue_by_label.get(label, {})
        kind = classify_skip(row, queue_by_label, conflict_labels)
        rows.append(
            {
                "label": label,
                "status": "skipped",
                "priority": int(queued.get("capture_priority", 80) or 80),
                "kind": kind,
                "rom_hit": row.get("rom_hit", ""),
                "source": row.get("source", ""),
                "korean": row.get("korean", ""),
                "evidence_level": queued.get("evidence_level", ""),
                "risk": row.get("risk", ""),
                "old_bytes": queued.get("expected_bytes", ""),
                "new_bytes": "",
                "capture_reason": queued.get("capture_reason", row.get("reason", "")),
                "skip_reason": row.get("reason", ""),
                "runtime_hits": queued.get("runtime_hits", 0),
                "runtime_active_expected_matches": queued.get("runtime_active_expected_matches", 0),
                "next_action": next_action(kind),
            }
        )

    for row in conflicts.get("non_overlapping_broad_candidates", []):
        rows.append(
            {
                "label": f"broad_{row.get('rom_hit', '')}",
                "status": "broad_candidate",
                "priority": 35 if row.get("confidence") == "medium" else 25,
                "kind": "broad_non_overlapping",
                "rom_hit": row.get("rom_hit", ""),
                "source": row.get("source", ""),
                "romaji": row.get("romaji", ""),
                "korean": row.get("korean", ""),
                "evidence_level": row.get("confidence", ""),
                "risk": "safe-equal-length after screen proof",
                "old_bytes": row.get("original_bytes", ""),
                "new_glyphs": row.get("new_glyphs", []),
                "capture_reason": "non-overlapping broad-scan candidate; not in v0.4.1 yet",
                "next_action": next_action("broad_non_overlapping"),
            }
        )

    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row["kind"])] = counts.get(str(row["kind"]), 0) + 1

    high_value = sorted(
        [row for row in rows if row["status"] != "applied" and int(row["priority"]) <= 45],
        key=lambda row: (int(row["priority"]), str(row["kind"]), str(row["rom_hit"])),
    )

    return {
        "source": {
            "primary_report": rel(PRIMARY_REPORT),
            "manual_queue": rel(MANUAL_QUEUE),
            "conflicts": rel(CONFLICTS),
            "broad_patchability": rel(BROAD_PATCHABILITY),
        },
        "summary": {
            "current_primary": "v0.4.2 font-expanded",
            "applied_rows": len(primary.get("applied", [])),
            "skipped_rows": len(primary.get("skipped", [])),
            "broad_non_overlapping_rows": len(conflicts.get("non_overlapping_broad_candidates", [])),
            "high_value_next_checks": len(high_value),
            "kind_counts": counts,
        },
        "rows": sorted(rows, key=lambda row: (int(row["priority"]), str(row["status"]), str(row["kind"]), str(row["rom_hit"]))),
        "high_value_next_checks": high_value[:20],
        "rule": [
            "Do not extend blind autoplay after stagnant_screen; switch to manual capture.",
            "Do not promote needs-padding-rule rows until a visual padding strategy is proven.",
            "Do not patch v0.4/broad overlaps until a manually reached screen identifies the correct interpretation.",
            "A YouTube transcript can identify expected text, but ROM offset promotion still requires byte/runtime/screen evidence.",
        ],
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    rows = payload["rows"]
    high_value = payload["high_value_next_checks"]

    lines = [
        "# Patch Decision Matrix",
        "",
        "This file ranks the remaining Korean patch decisions after the current primary candidate.",
        "",
        "## Summary",
        "",
        f"- Current primary: **{summary['current_primary']}**",
        f"- Applied in primary: **{summary['applied_rows']}**",
        f"- Skipped from primary: **{summary['skipped_rows']}**",
        f"- Non-overlapping broad candidates: **{summary['broad_non_overlapping_rows']}**",
        f"- High-value next checks: **{summary['high_value_next_checks']}**",
        "",
        "## Rules",
        "",
    ]
    for rule in payload["rule"]:
        lines.append(f"- {rule}")

    lines += [
        "",
        "## Highest-Value Next Checks",
        "",
        "| priority | kind | ROM hit | source | Korean | evidence/risk | next action |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for row in high_value:
        lines.append(
            f"| {row.get('priority', '')} | `{row.get('kind', '')}` | `{row.get('rom_hit', '')}` | "
            f"{row.get('source', '')} | {row.get('korean', '')} | "
            f"{row.get('evidence_level', '')} / {row.get('risk', '')} | {row.get('next_action', '')} |"
        )

    lines += [
        "",
        "## Full Matrix",
        "",
        "| priority | status | kind | ROM hit | label | bytes | reason |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        bytes_desc = row.get("old_bytes", "")
        if row.get("new_bytes"):
            bytes_desc = f"{bytes_desc} -> {row.get('new_bytes')}"
        lines.append(
            f"| {row.get('priority', '')} | {row.get('status', '')} | `{row.get('kind', '')}` | "
            f"`{row.get('rom_hit', '')}` | `{row.get('label', '')}` | `{bytes_desc}` | "
            f"{row.get('capture_reason') or row.get('skip_reason', '')} |"
        )

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_matrix()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"high_value_next_checks={payload['summary']['high_value_next_checks']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
