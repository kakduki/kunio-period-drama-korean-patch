#!/usr/bin/env python3
"""Summarize Bank 1 offset coverage by patch-readiness status."""

from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION_DATA = ROOT / "text_data" / "translation_data.txt"
INVENTORY_JSON = ROOT / "rom_analysis" / "bank1_offset_inventory.json"
BLOCK_MAP_JSON = ROOT / "rom_analysis" / "bank1_text_block_map.json"
PADDING_JSON = ROOT / "rom_analysis" / "prg_padding_options.json"
OUT_MD = ROOT / "rom_analysis" / "bank1_offset_status.md"
OUT_JSON = ROOT / "rom_analysis" / "bank1_offset_status.json"


GROUPS = {
    "items/equipment": {"무기", "회복", "방어구", "특수"},
    "menu": {"타이틀", "메뉴", "모드"},
    "UI/status": {"UI", "능력치", "캐릭터명"},
    "event/dialogue-related": {"대사", "이벤트", "보스", "스테이지", "엔딩", "기술"},
}


def group_for_category(category: str) -> str:
    for group, categories in GROUPS.items():
        if category in categories:
            return group
    return "other"


def read_translation_categories() -> dict[str, Counter[str]]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for raw in TRANSLATION_DATA.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "|" not in line:
            continue
        parts = [part.strip() for part in line.split("|")]
        while len(parts) < 3:
            parts.append("")
        category = parts[2]
        counts[group_for_category(category)][category] += 1
    return counts


def load_padding_by_offset() -> dict[str, dict[str, object]]:
    if not PADDING_JSON.exists():
        return {}
    data = json.loads(PADDING_JSON.read_text(encoding="utf-8"))
    return {str(row["rom_hit"]).upper(): row for row in data.get("targets", [])}


def patch_risk_for(row: dict[str, object], padding: dict[str, dict[str, object]]) -> str:
    risk = padding.get(str(row.get("rom_hit", "")).upper(), {}).get("risk")
    return str(risk or "not-in-current-allocation-plan")


def summarize() -> dict[str, object]:
    inventory = json.loads(INVENTORY_JSON.read_text(encoding="utf-8"))
    block_map = json.loads(BLOCK_MAP_JSON.read_text(encoding="utf-8"))
    padding = load_padding_by_offset()
    translation_categories = read_translation_categories()

    targets = list(inventory.get("targets", []))
    for target in targets:
        target["patch_risk"] = patch_risk_for(target, padding)

    by_group: dict[str, list[dict[str, object]]] = defaultdict(list)
    for target in targets:
        by_group[str(target.get("category_group", "other"))].append(target)

    groups: dict[str, dict[str, object]] = {}
    for group in ("items/equipment", "menu", "UI/status", "event/dialogue-related", "other"):
        rows = by_group.get(group, [])
        evidence_counts = Counter(str(row.get("evidence_level", "")) for row in rows)
        risk_counts = Counter(str(row.get("patch_risk", "")) for row in rows)
        categories_found = Counter(str(row.get("category", "")) for row in rows)
        groups[group] = {
            "translation_data_categories": dict(sorted(translation_categories.get(group, {}).items())),
            "target_count": len(rows),
            "runtime_confirmed_count": evidence_counts.get("runtime-confirmed", 0),
            "watch_range_count": sum(1 for row in rows if row.get("in_watch_range")),
            "evidence_counts": dict(sorted(evidence_counts.items())),
            "patch_risk_counts": dict(sorted(risk_counts.items())),
            "categories_found": dict(sorted(categories_found.items())),
            "missing_translation_categories": [
                category
                for category in sorted(translation_categories.get(group, {}))
                if category not in categories_found
            ],
            "targets": sorted(
                rows,
                key=lambda row: (
                    str(row.get("evidence_level")) != "runtime-confirmed",
                    str(row.get("patch_risk")) != "safe-equal-length",
                    str(row.get("rom_hit")),
                    str(row.get("source")),
                ),
            ),
        }

    return {
        "source": {
            "inventory": str(INVENTORY_JSON.relative_to(ROOT)),
            "block_map": str(BLOCK_MAP_JSON.relative_to(ROOT)),
            "padding_options": str(PADDING_JSON.relative_to(ROOT)),
            "translation_data": str(TRANSLATION_DATA.relative_to(ROOT)),
        },
        "summary": {
            "target_count": len(targets),
            "runtime_confirmed_count": sum(1 for row in targets if row.get("evidence_level") == "runtime-confirmed"),
            "watch_range_target_count": sum(1 for row in targets if row.get("in_watch_range")),
            "watch_range_block_count": block_map.get("summary", {}).get("block_count"),
            "watch_range_translation_hit_count": block_map.get("summary", {}).get("translation_hit_count"),
            "watch_range_safe_equal_length_distinct_targets": block_map.get("summary", {}).get("safe_equal_length_distinct_targets"),
        },
        "groups": groups,
    }


def target_line(row: dict[str, object]) -> str:
    runtime = ""
    if row.get("runtime_hits"):
        runtime = f"; runtime hits {row.get('runtime_hits')}, active {row.get('runtime_active_expected_matches')}"
    return (
        f"`{row.get('rom_hit')}` {row.get('source')}->{row.get('korean')} "
        f"({row.get('category')}, {row.get('evidence_level')}, {row.get('patch_risk')}{runtime})"
    )


def write_markdown(report: dict[str, object]) -> None:
    summary = report["summary"]
    groups = report["groups"]
    lines = [
        "# Bank 1 Offset Status",
        "",
        "This report summarizes current offset coverage by category and patch-readiness.",
        "",
        "## Summary",
        "",
        f"- Total Bank 1 targets: `{summary['target_count']}`",
        f"- Runtime-confirmed targets: `{summary['runtime_confirmed_count']}`",
        f"- Watch-range targets: `{summary['watch_range_target_count']}`",
        f"- Watch-range blocks: `{summary['watch_range_block_count']}`",
        f"- Watch-range translation hits: `{summary['watch_range_translation_hit_count']}`",
        f"- Watch-range distinct equal-length candidates: `{summary['watch_range_safe_equal_length_distinct_targets']}`",
        "",
        "## Category Status",
        "",
        "| group | translation categories | targets | runtime-confirmed | watch-range | safe equal-length | needs padding | missing translation categories |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for group, info in groups.items():
        risk_counts = info["patch_risk_counts"]
        translation_categories = ", ".join(info["translation_data_categories"].keys()) or "-"
        missing = ", ".join(info["missing_translation_categories"]) or "-"
        lines.append(
            f"| {group} | {translation_categories} | {info['target_count']} | "
            f"{info['runtime_confirmed_count']} | {info['watch_range_count']} | "
            f"{risk_counts.get('safe-equal-length', 0)} | {risk_counts.get('needs-padding-rule', 0)} | {missing} |"
        )

    lines.extend(["", "## Priority Offsets", ""])
    for group, info in groups.items():
        lines.extend([f"### {group}", ""])
        targets = info["targets"]
        if not targets:
            lines.append("_No current targets._")
            lines.append("")
            continue
        confirmed = [row for row in targets if row.get("evidence_level") == "runtime-confirmed"]
        safe_static = [
            row for row in targets
            if row.get("evidence_level") != "runtime-confirmed" and row.get("patch_risk") == "safe-equal-length"
        ][:8]
        padding_risk = [row for row in targets if row.get("patch_risk") == "needs-padding-rule"][:8]
        padding_risk = [
            row for row in padding_risk
            if row.get("evidence_level") != "runtime-confirmed"
        ]

        if confirmed:
            lines.append("Runtime-confirmed:")
            for row in confirmed:
                lines.append(f"- {target_line(row)}")
        if safe_static:
            lines.append("Equal-length candidates needing runtime screen confirmation:")
            for row in safe_static:
                lines.append(f"- {target_line(row)}")
        if padding_risk:
            lines.append("Padding-rule blockers:")
            for row in padding_risk:
                lines.append(f"- {target_line(row)}")
        lines.append("")

    lines.extend(
        [
            "## Current Gaps",
            "",
            "- Menu/title/mode strings are present in `translation_data.txt`, but no Bank 1 menu-category target is currently identified.",
            "- Event/dialogue work is still mostly static candidate evidence; no full dialogue block is runtime-confirmed yet.",
            "- Shortened Korean replacements such as `ちから` -> `힘`, `やり` -> `창`, `そうび` -> `장비`, and `おかね` -> `돈` remain blocked on padding/terminator behavior.",
            "- Equal-length static candidates can be used as FCEUX breakpoint/watch priorities, but should not be promoted to final patch offsets until the corresponding screen is observed.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = summarize()
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(report)
    summary = report["summary"]
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(
        " ".join(
            [
                f"targets={summary['target_count']}",
                f"runtime_confirmed={summary['runtime_confirmed_count']}",
                f"watch={summary['watch_range_target_count']}",
            ]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
