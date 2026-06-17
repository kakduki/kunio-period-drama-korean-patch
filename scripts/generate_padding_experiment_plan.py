#!/usr/bin/env python3
"""Generate an experiment plan for shortened PRG text replacements."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PADDING_OPTIONS = ROOT / "rom_analysis" / "prg_padding_options.json"
INVENTORY = ROOT / "rom_analysis" / "bank1_offset_inventory.json"
OUT_MD = ROOT / "rom_analysis" / "prg_padding_experiment_plan.md"
OUT_JSON = ROOT / "rom_analysis" / "prg_padding_experiment_plan.json"


PADDING_STRATEGIES = {
    "pad_00": "00",
    "pad_7a": "7A",
    "pad_ff": "FF",
    "pad_f8f9": "F8 F9",
    "preserve_tail": "original-tail",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_bytes(text: str) -> list[int]:
    return [int(part, 16) for part in str(text).split() if part]


def fmt_bytes(values: list[int]) -> str:
    return " ".join(f"{value:02X}" for value in values)


def strategy_bytes(name: str, tail_len: int, original_tail: list[int]) -> list[int] | None:
    if name == "preserve_tail":
        return list(original_tail)
    seed = parse_bytes(PADDING_STRATEGIES[name])
    if not seed:
        return None
    out = []
    while len(out) < tail_len:
        out.extend(seed)
    return out[:tail_len]


def inventory_by_label() -> dict[str, dict]:
    data = load_json(INVENTORY)
    return {str(row["label"]): row for row in data.get("targets", [])}


def main() -> int:
    padding = load_json(PADDING_OPTIONS)
    inventory = inventory_by_label()

    experiments = []
    blockers = [
        row
        for row in padding.get("targets", [])
        if row.get("risk") == "needs-padding-rule"
    ]
    for row in blockers:
        label = str(row["label"])
        original = parse_bytes(row["original_bytes"])
        planned = parse_bytes(row["planned_bytes"])
        tail = original[len(planned):]
        inv = inventory.get(label, {})
        strategy_rows = []
        for strategy in PADDING_STRATEGIES:
            pad = strategy_bytes(strategy, len(tail), tail)
            if pad is None:
                continue
            patched = planned + pad
            strategy_rows.append(
                {
                    "strategy": strategy,
                    "patched_bytes": fmt_bytes(patched),
                    "pad_bytes": fmt_bytes(pad),
                    "changes_original_tail": pad != tail,
                    "note": "control/fill hypothesis" if strategy != "preserve_tail" else "baseline: only first glyph byte changes",
                }
            )
        experiments.append(
            {
                "label": label,
                "rom_hit": row["rom_hit"],
                "category_group": inv.get("category_group"),
                "category": row.get("category"),
                "source": row.get("source"),
                "source_romaji": inv.get("source_romaji", ""),
                "source_context": inv.get("source_context", ""),
                "korean": row.get("korean"),
                "evidence_level": row.get("evidence_level"),
                "runtime_hits": inv.get("runtime_hits", 0),
                "runtime_active_expected_matches": inv.get("runtime_active_expected_matches", 0),
                "original_bytes": row["original_bytes"],
                "planned_bytes": row["planned_bytes"],
                "tail_bytes": row["tail_bytes_if_shorter"],
                "tail_len": len(tail),
                "reason": row["reason"],
                "strategies": strategy_rows,
            }
        )

    runtime_ready = [
        row
        for row in experiments
        if row["evidence_level"] == "runtime-confirmed"
        and int(row["runtime_active_expected_matches"] or 0) > 0
    ]

    payload = {
        "source": {
            "padding_options": str(PADDING_OPTIONS.relative_to(ROOT)),
            "inventory": str(INVENTORY.relative_to(ROOT)),
        },
        "summary": {
            "needs_padding_rule_count": len(experiments),
            "runtime_confirmed_padding_blockers": len(runtime_ready),
            "strategy_count": len(PADDING_STRATEGIES),
        },
        "strategies": PADDING_STRATEGIES,
        "experiments": experiments,
        "runtime_confirmed_first_targets": runtime_ready,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# PRG Padding Experiment Plan",
        "",
        "This report turns `needs-padding-rule` replacements into explicit experimental byte strategies. It does not claim any strategy is safe; it defines reproducible FCEUX checks.",
        "",
        "## Summary",
        "",
        f"- Needs-padding-rule targets: **{len(experiments)}**",
        f"- Runtime-confirmed padding blockers: **{len(runtime_ready)}**",
        f"- Padding strategies: **{len(PADDING_STRATEGIES)}**",
        "",
        "## Runtime-Confirmed First Targets",
        "",
    ]
    if runtime_ready:
        lines.append("| ROM hit | Japanese | Korean | original | planned | tail | runtime evidence |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        for row in runtime_ready:
            source = row["source"]
            if row.get("source_romaji"):
                source = f"{source} ({row['source_romaji']})"
            lines.append(
                f"| `{row['rom_hit']}` | {source} | {row['korean']} | `{row['original_bytes']}` | "
                f"`{row['planned_bytes']}` | `{row['tail_bytes']}` | "
                f"{row['runtime_hits']} hits, active {row['runtime_active_expected_matches']} |"
            )
    else:
        lines.append("_No runtime-confirmed shortened targets yet._")

    lines += [
        "",
        "## Strategy Matrix",
        "",
        "| ROM hit | Japanese | category | evidence | strategy | patched bytes | pad bytes | note |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in experiments:
        source = row["source"]
        if row.get("source_romaji"):
            source = f"{source} ({row['source_romaji']})"
        for strategy in row["strategies"]:
            lines.append(
                f"| `{row['rom_hit']}` | {source} | {row['category']} | {row['evidence_level']} | "
                f"{strategy['strategy']} | `{strategy['patched_bytes']}` | `{strategy['pad_bytes']}` | {strategy['note']} |"
            )

    lines += [
        "",
        "## Recommended FCEUX Check",
        "",
        "1. Start with the runtime-confirmed target `ROM+0x071A4` (`ちから`/Chikara -> `힘`).",
        "2. Build one experimental ROM per padding strategy from this plan.",
        "3. In FCEUX, reach the same status screen/read-watch route that confirmed `$B192-$B19C`.",
        "4. Accept a strategy only if the visible label renders cleanly and neighboring status fields remain intact.",
        "5. If more than one strategy works visually, prefer the one that matches observed control/fill behavior elsewhere in the same record family.",
        "",
        "## Notes",
        "",
        "- `preserve_tail` is a baseline, not a final translation: it changes only the first planned glyph byte and leaves the old tail bytes.",
        "- `pad_00`, `pad_7a`, `pad_ff`, and `pad_f8f9` are hypotheses that need screen verification before any final patch.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(
        f"needs_padding={len(experiments)} runtime_confirmed={len(runtime_ready)} strategies={len(PADDING_STRATEGIES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
