#!/usr/bin/env python3
"""Merge Bank 1 block, offset, patch, and PPU evidence into one report."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLOCK_MAP = ROOT / "rom_analysis" / "bank1_text_block_map.json"
INVENTORY = ROOT / "rom_analysis" / "bank1_offset_inventory.json"
V04_TARGETS = ROOT / "rom_analysis" / "v04_equal_length_fceux_targets.json"
V04_BUILD_REPORT = ROOT / "output" / "kunio_period_drama_korean_prg_plan_v0.4_equal_length_static_build_report.json"
V04_PPU_ANALYSIS = ROOT / "rom_analysis" / "fceux_v04_ppu_watch" / "analysis_v2_v04_targets.md"
OUT_MD = ROOT / "rom_analysis" / "bank1_block_identification.md"
OUT_JSON = ROOT / "rom_analysis" / "bank1_block_identification.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_hex(value: str) -> int:
    value = value.strip()
    if value.startswith("ROM+"):
        value = value[4:]
    return int(value, 16)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_ppu_matched_labels(path: Path) -> set[str]:
    if not path.exists():
        return set()
    labels: set[str] = set()
    pattern = re.compile(r"\|\s*\d+\s*\|\s*`([^`]+)`\s*\|")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            labels.add(match.group(1))
    return labels


def block_range(block: dict) -> tuple[int, int]:
    start, end = block["rom_range"]
    return parse_hex(start), parse_hex(end)


def block_for_offset(blocks: list[dict], rom_offset: int) -> dict | None:
    for block in blocks:
        start, end = block_range(block)
        if start <= rom_offset < end:
            return block
    return None


def build_inventory_by_offset(inventory: dict) -> dict[int, list[dict]]:
    by_offset: dict[int, list[dict]] = defaultdict(list)
    for target in inventory.get("targets", []):
        by_offset[parse_hex(target["rom_hit"])].append(target)
    return by_offset


def build_v04_maps() -> tuple[dict[str, dict], dict[str, dict], set[str]]:
    targets = load_json(V04_TARGETS)
    target_by_source = {
        str(target.get("source_label", "")): target
        for target in targets.get("targets", [])
    }
    target_by_label = {
        str(target.get("label", "")): target
        for target in targets.get("targets", [])
    }

    report = load_json(V04_BUILD_REPORT)
    patch_by_source: dict[str, dict] = {}
    for row in report.get("applied", []):
        patch_by_source[str(row.get("label", ""))] = {"status": "applied", **row}
    for row in report.get("skipped", []):
        patch_by_source[str(row.get("label", ""))] = {"status": "skipped", **row}

    ppu_matches = parse_ppu_matched_labels(V04_PPU_ANALYSIS)
    ppu_source_labels = {
        target["source_label"]
        for label, target in target_by_label.items()
        if label in ppu_matches and target.get("source_label")
    }
    return target_by_source, patch_by_source, ppu_source_labels


def evidence_rank(text: str) -> int:
    order = {
        "runtime-confirmed": 4,
        "encoding-exact": 3,
        "static-candidate+pointer": 2,
        "static-candidate": 1,
    }
    return order.get(text, 0)


def summarize_identification(rows: list[dict]) -> tuple[str, str]:
    if not rows:
        return "unidentified", "no translation-data target in this block yet"

    groups = Counter(row["category_group"] for row in rows)
    best_count = max(groups.values())
    best_groups = sorted(group for group, count in groups.items() if count == best_count)
    if len(groups) > 1:
        best_group = "mixed: " + " + ".join(sorted(groups))
    else:
        best_group = best_groups[0]
    best_evidence = max(rows, key=lambda row: evidence_rank(row["evidence_level"]))["evidence_level"]
    if any(row["ppu_patched_sequence_seen"] for row in rows):
        best_evidence += "+ppu-sequence"
    return best_group, best_evidence


def row_from_target(
    target: dict,
    source_label: str,
    v04_target: dict | None,
    patch: dict | None,
    ppu_source_labels: set[str],
) -> dict:
    runtime_hits = int(target.get("runtime_hits", 0) or 0)
    runtime_matches = int(target.get("runtime_active_expected_matches", 0) or 0)
    return {
        "label": source_label,
        "rom_hit": target["rom_hit"],
        "category_group": target.get("category_group", "other"),
        "category": target.get("category", ""),
        "source": target.get("source", ""),
        "korean": target.get("korean", ""),
        "expected_bytes": target.get("expected_bytes", ""),
        "evidence_level": target.get("evidence_level", ""),
        "runtime_hits": runtime_hits,
        "runtime_active_expected_matches": runtime_matches,
        "v04_target": bool(v04_target),
        "v04_patched_bytes": (v04_target or {}).get("expected_patched_bytes", ""),
        "v04_patch_status": (patch or {}).get("status", "not-in-v04"),
        "v04_skip_reason": (patch or {}).get("reason", ""),
        "ppu_patched_sequence_seen": source_label in ppu_source_labels,
        "ppu_note": "ambiguous shared sequence" if source_label in ppu_source_labels else "",
    }


def make_payload() -> dict:
    block_map = load_json(BLOCK_MAP)
    inventory = load_json(INVENTORY)
    blocks = block_map.get("blocks", [])
    inventory_by_offset = build_inventory_by_offset(inventory)
    v04_by_source, patch_by_source, ppu_source_labels = build_v04_maps()

    identified_blocks = []
    for block in blocks:
        start, end = block_range(block)
        rows = []
        for rom_offset, targets in inventory_by_offset.items():
            if not start <= rom_offset < end:
                continue
            for target in targets:
                label = target.get("label", "")
                rows.append(
                    row_from_target(
                        target,
                        label,
                        v04_by_source.get(label),
                        patch_by_source.get(label),
                        ppu_source_labels,
                    )
                )

        role, evidence = summarize_identification(rows)
        identified_blocks.append(
            {
                "index": block["index"],
                "rom_range": block["rom_range"],
                "prg_start": block["prg_start"],
                "length": block["length"],
                "bytes": block["bytes"],
                "identification": role,
                "identification_evidence": evidence,
                "target_count": len(rows),
                "targets": sorted(rows, key=lambda row: (parse_hex(row["rom_hit"]), row["label"])),
            }
        )

    with_targets = [block for block in identified_blocks if block["target_count"]]
    ppu_blocks = [
        block
        for block in identified_blocks
        if any(row["ppu_patched_sequence_seen"] for row in block["targets"])
    ]
    runtime_blocks = [
        block
        for block in identified_blocks
        if any(row["runtime_active_expected_matches"] for row in block["targets"])
    ]
    role_counts = Counter(block["identification"] for block in identified_blocks)

    return {
        "source": {
            "block_map": rel(BLOCK_MAP),
            "inventory": rel(INVENTORY),
            "v04_targets": rel(V04_TARGETS),
            "v04_build_report": rel(V04_BUILD_REPORT),
            "v04_ppu_analysis": rel(V04_PPU_ANALYSIS),
        },
        "summary": {
            "block_count": len(identified_blocks),
            "blocks_with_targets": len(with_targets),
            "blocks_without_targets": len(identified_blocks) - len(with_targets),
            "blocks_with_runtime_active_match": len(runtime_blocks),
            "blocks_with_v04_ppu_patched_sequence": len(ppu_blocks),
            "role_counts": dict(sorted(role_counts.items())),
        },
        "blocks": identified_blocks,
    }


def write_markdown(payload: dict) -> None:
    summary = payload["summary"]
    blocks = payload["blocks"]
    lines = [
        "# Bank 1 Block Identification",
        "",
        "This report merges the tentative `0xFF` block map for `ROM+0x05610-0x05810` with Bank 1 offset inventory, v0.4 patch status, and v0.4 PPU write-watch evidence.",
        "",
        "## Summary",
        "",
        f"- Blocks analyzed: **{summary['block_count']}**",
        f"- Blocks with translation/inventory targets: **{summary['blocks_with_targets']}**",
        f"- Blocks without targets: **{summary['blocks_without_targets']}**",
        f"- Blocks with runtime active-byte evidence inside this range: **{summary['blocks_with_runtime_active_match']}**",
        f"- Blocks with v0.4 patched-byte PPU sequence evidence: **{summary['blocks_with_v04_ppu_patched_sequence']}**",
        "",
        "Role counts:",
        "",
    ]
    for role, count in summary["role_counts"].items():
        lines.append(f"- `{role}`: {count}")

    lines += [
        "",
        "## Identified Blocks",
        "",
        "| block | ROM range | bytes | identification | evidence | targets | v0.4/PPU status |",
        "| ---: | --- | ---: | --- | --- | --- | --- |",
    ]
    for block in blocks:
        targets = block["targets"]
        target_text = "-"
        status_text = "-"
        if targets:
            target_text = "<br>".join(
                f"`{row['rom_hit']}` {row['category_group']} `{row['expected_bytes']}`"
                for row in targets
            )
            status_text = "<br>".join(
                f"{row['v04_patch_status']}"
                + (", PPU ambiguous" if row["ppu_patched_sequence_seen"] else "")
                + (f", skip: {row['v04_skip_reason']}" if row["v04_skip_reason"] else "")
                for row in targets
            )
        lines.append(
            f"| {block['index']} | `{block['rom_range'][0]}-{block['rom_range'][1]}` | "
            f"{block['length']} | {block['identification']} | {block['identification_evidence']} | "
            f"{target_text} | {status_text} |"
        )

    lines += [
        "",
        "## PPU-Ambiguous v0.4 Matches",
        "",
        "The following blocks contain targets whose patched byte sequence appeared in the v0.4 PPU stream. All current matches share the same `8B 8C` byte sequence, so this confirms screen/PPU visibility of that sequence but not the exact source ROM offset.",
        "",
        "| block | ROM hit | ROM range | expected patched bytes | status |",
        "| ---: | --- | --- | --- | --- |",
    ]
    ppu_rows = [
        (block, row)
        for block in blocks
        for row in block["targets"]
        if row["ppu_patched_sequence_seen"]
    ]
    if ppu_rows:
        for block, row in ppu_rows:
            lines.append(
                f"| {block['index']} | `{row['rom_hit']}` | `{block['rom_range'][0]}-{block['rom_range'][1]}` | "
                f"`{row['v04_patched_bytes']}` | {row['v04_patch_status']} / {row['ppu_note']} |"
            )
    else:
        lines.append("| - | - | - | - | - |")

    lines += [
        "",
        "## Remaining Gaps",
        "",
        "- Menu/title/mode strings are still not identified inside this `ROM+0x05610-0x05810` block map.",
        "- No block in this watch range has runtime active-byte read evidence yet; the runtime-confirmed Bank 1 targets remain outside this narrow range.",
        "- The v0.4 PPU matches prove patched bytes reached the PPU stream, but shared two-byte sequences prevent offset-level proof for the five matched blocks.",
        "- Blocks marked `unidentified` need broader runtime capture, better scene routing, or additional translation-data matching before they can be treated as real user-visible text.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(
        "blocks={block_count} with_targets={blocks_with_targets} ppu_blocks={blocks_with_v04_ppu_patched_sequence}".format(
            **payload["summary"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
