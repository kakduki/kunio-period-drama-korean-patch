#!/usr/bin/env python3
"""Generate a short manual proof packet for v0.4.2 promotion candidates."""

from __future__ import annotations

import json
from pathlib import Path

from readable_labels import readable_for_romaji


ROOT = Path(__file__).resolve().parents[1]
READINESS = ROOT / "rom_analysis" / "v042_text_promotion_readiness.json"
BROAD_TARGETS = ROOT / "rom_analysis" / "broad_scan_fceux_targets.json"
OUT_JSON = ROOT / "rom_analysis" / "v042_manual_proof_packet.json"
OUT_MD = ROOT / "rom_analysis" / "v042_manual_proof_packet.md"

BASE_ROM = "rom/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes"
CAPTURE_LUA = "lua/kunio_manual_broad_scan_dump.lua"
SUMMARY_COMMAND = "python scripts/analyze_broad_scan_manual_dump.py"
SUMMARY_JSON = "rom_analysis/manual_screen_dump_broad_scan/summary.json"


KIND_RANK = {
    "non_overlapping_needs_manual_screen": 0,
    "conflict_alternative_needs_manual_screen": 1,
}
CONFIDENCE_RANK = {
    "high": 0,
    "medium": 1,
    "low": 2,
}


def as_hex_bytes(values: object) -> str:
    if isinstance(values, list):
        return " ".join(str(value).replace("0x", "").upper().zfill(2) for value in values)
    return str(values)


def sort_key(row: dict[str, object]) -> tuple[int, int, int]:
    return (
        KIND_RANK.get(str(row.get("kind", "")), 99),
        CONFIDENCE_RANK.get(str(row.get("confidence", "")), 99),
        int(str(row["rom_offset"]), 16),
    )


def load_target_hints() -> dict[str, dict[str, object]]:
    payload = json.loads(BROAD_TARGETS.read_text(encoding="utf-8"))
    return {str(row["rom_offset"]).upper(): row for row in payload.get("targets", [])}


def build_packet() -> dict[str, object]:
    readiness = json.loads(READINESS.read_text(encoding="utf-8"))
    target_hints = load_target_hints()
    candidates = sorted(readiness.get("candidates", []), key=sort_key)
    tasks = []
    for number, row in enumerate(candidates, start=1):
        hints = target_hints.get(str(row.get("rom_offset", "")).upper(), {})
        task = {
            "task": number,
            "kind": row.get("kind", ""),
            "confidence": row.get("confidence", ""),
            "label": hints.get("label", ""),
            "romaji": hints.get("romaji", ""),
            "source_display": readable_for_romaji(hints.get("romaji", "")).get("source_display", ""),
            "korean_display": readable_for_romaji(hints.get("romaji", "")).get("korean_display", ""),
            "meaning": readable_for_romaji(hints.get("romaji", "")).get("meaning", ""),
            "screen_hint": readable_for_romaji(hints.get("romaji", "")).get("screen_hint", ""),
            "category": hints.get("category", ""),
            "source": row.get("source", ""),
            "korean": row.get("korean", ""),
            "rom_offset": row.get("rom_offset", ""),
            "bank16": row.get("bank16", ""),
            "original_bytes": row.get("original_bytes", ""),
            "planned_prg_bytes": as_hex_bytes(row.get("planned_prg_bytes", [])),
            "rom_to_open": BASE_ROM,
            "capture_lua": CAPTURE_LUA,
            "summary_command": SUMMARY_COMMAND,
            "summary_json": SUMMARY_JSON,
            "decision_rule": "A read hit plus matching screen context is required before this offset can be promoted.",
        }
        tasks.append(task)

    return {
        "source": str(READINESS.relative_to(ROOT)),
        "summary": {
            "task_count": len(tasks),
            "non_overlapping_first": sum(
                1 for task in tasks if task["kind"] == "non_overlapping_needs_manual_screen"
            ),
            "conflict_alternatives": sum(
                1 for task in tasks if task["kind"] == "conflict_alternative_needs_manual_screen"
            ),
            "rom_to_open": BASE_ROM,
            "capture_lua": CAPTURE_LUA,
            "summary_command": SUMMARY_COMMAND,
            "summary_json": SUMMARY_JSON,
            "rule": "Stop blind autoplay when the screen is stagnant; manually reach the target screen and run one dump.",
        },
        "tasks": tasks,
    }


def write_markdown(packet: dict[str, object]) -> None:
    summary = packet["summary"]
    lines = [
        "# v0.4.2 Manual Proof Packet",
        "",
        "Use this instead of extending blind FCEUX autoplay when the emulator keeps repeating the first screen.",
        "",
        f"- Source: `{packet['source']}`",
        f"- Tasks: **{summary['task_count']}**",
        f"- Non-overlapping candidates: **{summary['non_overlapping_first']}**",
        f"- Conflict alternatives: **{summary['conflict_alternatives']}**",
        f"- Open ROM: `{summary['rom_to_open']}`",
        f"- Run Lua at the target screen: `{summary['capture_lua']}`",
        f"- Summarize: `{summary['summary_command']}`",
        f"- Machine-readable result: `{summary['summary_json']}`",
        "- Human hints: use `romaji` first when Japanese/Korean text appears garbled in the console.",
        "",
        "## Workflow",
        "",
        "1. Open the base ROM in FCEUX.",
        "2. Manually reach the related item/status/dialogue screen; do not keep extending autoplay on a stagnant title/start screen.",
        "3. Pause on the screen with text visible.",
        f"4. Run `{summary['capture_lua']}` from the FCEUX Lua menu.",
        f"5. Run `{summary['summary_command']}` from the repository root.",
        f"6. Review `{summary['summary_json']}` and the screenshot/visible screen together.",
        "7. Promote only rows with both a CPU read hit and matching visible screen context.",
        "",
        "## Tasks",
        "",
        "| # | kind | confidence | ROM | romaji | human hint | expected visible text | Korean | screen hint | original | planned v0.4.2 bytes | decision |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for task in packet["tasks"]:
        lines.append(
            f"| {task['task']} | {task['kind']} | {task['confidence']} | `{task['rom_offset']}` | "
            f"{task['romaji'] or '-'} | {task['meaning'] or '-'} | {task['source_display'] or task['source']} | "
            f"{task['korean_display'] or task['korean']} | {task['screen_hint'] or '-'} | `{task['original_bytes']}` | "
            f"`{task['planned_prg_bytes']}` | read hit + screen context |"
        )
    lines += [
        "",
        "## Notes",
        "",
        "- The four non-overlapping rows are the safest first proof targets.",
        "- The three conflict alternatives overlap earlier v0.4 interpretations and must decide between competing meanings.",
        "- YouTube footage can help identify scene order and wording, but it cannot replace byte/read evidence for patch promotion.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(packet)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"tasks={packet['summary']['task_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
