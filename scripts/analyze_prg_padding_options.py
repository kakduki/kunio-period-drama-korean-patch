#!/usr/bin/env python3
"""Analyze padding risks for planned PRG text replacements."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "rom_analysis" / "korean_slot_allocation_plan.json"
OUT_MD = ROOT / "rom_analysis" / "prg_padding_options.md"
OUT_JSON = ROOT / "rom_analysis" / "prg_padding_options.json"


KNOWN_FILL_BYTES = {0x00, 0x7A, 0xFF, 0xF8, 0xF9, 0xCA, 0xCB}


def parse_hex_bytes(text: str) -> list[int]:
    return [int(part, 16) for part in str(text).split() if part]


def parse_planned(values: list[str]) -> list[int]:
    return [int(value, 16) for value in values]


def risk_for(original: list[int], planned: list[int]) -> tuple[str, str]:
    if len(planned) == len(original):
        return "safe-equal-length", "planned bytes exactly fill candidate span"
    if len(planned) > len(original):
        return "unsafe-overflow", f"planned length {len(planned)} exceeds original span {len(original)}"
    tail = original[len(planned):]
    if all(byte in KNOWN_FILL_BYTES for byte in tail):
        return "maybe-pad-over-fill", "remaining original bytes are known fill/control candidates"
    return "needs-padding-rule", "remaining original bytes decode as non-fill candidate text/control bytes"


def build_rows() -> list[dict[str, object]]:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []
    for target in plan["targets"]:
        original = parse_hex_bytes(str(target["original_expected_bytes"]))
        planned = parse_planned(list(target["planned_prg_bytes"]))
        risk, reason = risk_for(original, planned)
        rows.append(
            {
                "label": target["label"],
                "evidence_level": target["evidence_level"],
                "rom_hit": target["rom_hit"],
                "category": target["category"],
                "source": target["source"],
                "korean": target["korean"],
                "original_len": len(original),
                "planned_len": len(planned),
                "original_bytes": " ".join(f"{byte:02X}" for byte in original),
                "planned_bytes": " ".join(f"{byte:02X}" for byte in planned),
                "tail_bytes_if_shorter": " ".join(f"{byte:02X}" for byte in original[len(planned):]),
                "risk": risk,
                "reason": reason,
            }
        )
    return rows


def write_markdown(rows: list[dict[str, object]]) -> None:
    by_risk: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        by_risk.setdefault(str(row["risk"]), []).append(row)

    lines = [
        "# PRG Padding Options",
        "",
        "This report compares original candidate byte spans with planned Korean PRG bytes.",
        "",
        "Risk labels:",
        "",
        "- `safe-equal-length`: direct byte replacement can preserve record length.",
        "- `maybe-pad-over-fill`: planned bytes are shorter, but the remaining bytes are known fill/control candidates.",
        "- `needs-padding-rule`: planned bytes are shorter and the remaining original bytes are not known safe fill bytes.",
        "- `unsafe-overflow`: planned bytes are longer than the candidate span.",
        "",
        "## Summary",
        "",
        "| risk | count |",
        "| --- | ---: |",
    ]
    for risk in sorted(by_risk):
        lines.append(f"| {risk} | {len(by_risk[risk])} |")

    for risk in sorted(by_risk):
        lines.extend(["", f"## {risk}", ""])
        lines.append("| evidence | ROM hit | category | Japanese | Korean | len old/new | old bytes | planned bytes | tail | reason |")
        lines.append("| --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- |")
        for row in sorted(by_risk[risk], key=lambda r: (str(r["evidence_level"]), str(r["rom_hit"]))):
            lines.append(
                f"| {row['evidence_level']} | `{row['rom_hit']}` | {row['category']} | "
                f"{row['source']} | {row['korean']} | {row['original_len']}/{row['planned_len']} | "
                f"`{row['original_bytes']}` | `{row['planned_bytes']}` | "
                f"`{row['tail_bytes_if_shorter'] or '-'}` | {row['reason']} |"
            )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `ちから` -> `힘` is deliberately left in `needs-padding-rule`: its remaining bytes are `88 AA`, not known fill/control bytes.",
            "- Do not apply shorter replacements until the renderer's pad/terminator behavior is observed in FCEUX for the specific record.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = build_rows()
    OUT_JSON.write_text(json.dumps({"source": str(PLAN.relative_to(ROOT)), "targets": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(rows)
    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row["risk"])] = counts.get(str(row["risk"]), 0) + 1
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(" ".join(f"{risk}={count}" for risk, count in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
