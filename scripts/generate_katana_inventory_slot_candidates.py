#!/usr/bin/env python3
"""Rank Katana inventory slot candidates from checked-in menu/item-list dumps."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


RUN_DIR = REPO_ROOT / "rom_analysis" / "katana_visual_explorer_v042"
MENU_CPU = RUN_DIR / "manual_frame_001906_cpu_ram.bin"
ITEM_CPU = RUN_DIR / "manual_frame_002385_cpu_ram.bin"
MENU_SRAM = RUN_DIR / "manual_frame_001906_sram_6000_7fff.bin"
ITEM_SRAM = RUN_DIR / "manual_frame_002385_sram_6000_7fff.bin"
OUT_JSON = REPO_ROOT / "rom_analysis" / "katana_inventory_slot_candidates.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "katana_inventory_slot_candidates.md"
SINGLE_SLOT_0502_NOTES = REPO_ROOT / "rom_analysis" / "katana_single_slot_probe_0502_notes.md"


PROBED_ADDRESSES = [
    0x0502,
    0x0503,
    0x0506,
    0x0508,
    0x0509,
    0x0700,
    0x0701,
    0x0702,
    0x0706,
    0x0707,
    0x071D,
    0x071E,
    0x071F,
    0x7700,
    0x7701,
    0x7705,
    0x7720,
    0x7721,
    0x7722,
]


def read(path: Path) -> bytes:
    return path.read_bytes()


def byte_at(data: bytes, addr: int, base: int = 0) -> int:
    offset = addr - base
    if offset < 0 or offset >= len(data):
        raise ValueError(f"address out of range: 0x{addr:04X}")
    return data[offset]


def classify(addr: int, menu_value: int, item_value: int) -> tuple[str, str]:
    if 0x6000 <= addr <= 0x6BFF:
        return "exclude_ppu_shadow", "This range mirrors visible nametable/menu tiles; writing here can corrupt rendering."
    if addr in {0x7700, 0x7701, 0x7705}:
        return "exclude_menu_state", "Observed route/menu-control bytes, not stable item-slot storage."
    if 0x7720 <= addr <= 0x7722:
        return "defer_unknown_state", "Nearby state changed during menu transitions; test only after narrower evidence."
    if 0x0700 <= addr <= 0x071F:
        return "defer_runtime_state", "CPU runtime state differs by menu screen; may affect control flow."
    if 0x0500 <= addr <= 0x050F:
        return "candidate_small_probe", "Small CPU state area that changed without being direct nametable data."
    if menu_value != item_value:
        return "defer_changed_state", "Value changes between menu and item-list frames."
    return "low_priority", "No strong signal from current dumps."


def row_for(addr: int, menu_cpu: bytes, item_cpu: bytes, menu_sram: bytes, item_sram: bytes) -> dict[str, object]:
    if addr < 0x6000:
        menu_value = byte_at(menu_cpu, addr)
        item_value = byte_at(item_cpu, addr)
        domain = "cpu"
    else:
        menu_value = byte_at(menu_sram, addr, 0x6000)
        item_value = byte_at(item_sram, addr, 0x6000)
        domain = "sram"
    classification, reason = classify(addr, menu_value, item_value)
    return {
        "address": f"0x{addr:04X}",
        "domain": domain,
        "menu_value": f"0x{menu_value:02X}",
        "item_list_value": f"0x{item_value:02X}",
        "changed": menu_value != item_value,
        "classification": classification,
        "reason": reason,
    }


def make_payload() -> dict[str, object]:
    menu_cpu = read(MENU_CPU)
    item_cpu = read(ITEM_CPU)
    menu_sram = read(MENU_SRAM)
    item_sram = read(ITEM_SRAM)
    rows = [row_for(addr, menu_cpu, item_cpu, menu_sram, item_sram) for addr in PROBED_ADDRESSES]
    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row["classification"])] = counts.get(str(row["classification"]), 0) + 1
    return {
        "source": {
            "menu_cpu": str(MENU_CPU.relative_to(REPO_ROOT)).replace("\\", "/"),
            "item_cpu": str(ITEM_CPU.relative_to(REPO_ROOT)).replace("\\", "/"),
            "menu_sram": str(MENU_SRAM.relative_to(REPO_ROOT)).replace("\\", "/"),
            "item_sram": str(ITEM_SRAM.relative_to(REPO_ROOT)).replace("\\", "/"),
            "failed_probe": "lua/kunio_katana_inventory_probe_v042.lua",
        },
        "summary": {
            "probed_addresses": len(rows),
            "classification_counts": counts,
            "completed_single_slot_probes": ["0x0502"] if SINGLE_SLOT_0502_NOTES.exists() else [],
            "recommended_next_probe": "Try one candidate_small_probe address at a time. 0x0502 was tested alone and did not show the Katana label; continue with 0x0503.",
        },
        "rows": rows,
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# Katana Inventory Slot Candidates",
        "",
        "This ranks the addresses from the failed temporary-state probe so the next run can be narrower.",
        "",
        "## Summary",
        "",
        f"- Probed addresses: **{summary['probed_addresses']}**",
        f"- Completed single-slot probes: {', '.join(summary['completed_single_slot_probes']) or '-'}",
        f"- Recommended next probe: {summary['recommended_next_probe']}",
        "",
        "| classification | count |",
        "| --- | ---: |",
    ]
    for name, count in sorted(summary["classification_counts"].items()):
        lines.append(f"| `{name}` | {count} |")
    lines += [
        "",
        "## Address Rows",
        "",
        "| address | domain | menu | item list | changed | classification | reason |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['address']}` | {row['domain']} | `{row['menu_value']}` | `{row['item_list_value']}` | "
            f"{str(row['changed']).lower()} | `{row['classification']}` | {row['reason']} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON.relative_to(REPO_ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(REPO_ROOT)}")
    print(f"recommended={payload['summary']['recommended_next_probe']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
