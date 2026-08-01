from __future__ import annotations

from pathlib import Path

from scripts.inventory_pre_pointer_korean_candidates import inventory


ROOT = Path(__file__).resolve().parents[1]


def test_inventory_keeps_pre_pointer_records_separate() -> None:
    rows = inventory(
        ROOT / "rom_analysis" / "english_script_dump.tsv",
        ROOT / "text_data" / "translation_readable_reference.json",
        ROOT / "text_data" / "direct_low_korean_labels.json",
        ROOT / "rom_analysis" / "korean_slot_allocation_plan.json",
        ROOT / "rom_analysis" / "next_glyph_expansion_plan.json",
    )
    assert len(rows) == 250
    assert all(row["context"] in {
        "Bank 1 name-table area",
        "Bank 1 pre-pointer text area",
    } for row in rows)
    assert sum(row["readiness"] == "BLOCKED_CONTROL_SKELETON" for row in rows) == 17
    thick = next(row for row in rows if "THICK" in str(row["english_text"]))
    assert thick["patch_authorized"] is False
