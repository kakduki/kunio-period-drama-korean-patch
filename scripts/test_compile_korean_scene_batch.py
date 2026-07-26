#!/usr/bin/env python3
"""Focused tests for explicit Korean scene-batch compilation."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from build_opening_dialogue_proof import PROOF_RECORD
from compile_korean_scene_batch import AVAILABLE_GLYPH_CODES, CatalogError, compile_catalog


def write_catalog(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text(
        json.dumps({"schema_version": 1, "batch_id": "test", "records": records}, ensure_ascii=False),
        encoding="utf-8",
    )


def base_record(tokens: list[dict[str, str]]) -> dict[str, object]:
    return {
        "id": "PTR-TEST",
        "context": "test",
        "pointer_index": 1,
        "pointer_rom_offset": "0x00010",
        "record_rom_offset": "0x00020",
        "expected_original_bytes": "00 FF",
        "expected_length": 2,
        "korean_text": "가",
        "tokens": tokens,
    }


def test_default_catalog() -> None:
    root = Path(__file__).resolve().parents[1]
    compiled = compile_catalog(root / "text_data" / "korean_scene_batches" / "opening_ptr_182.json")
    assert compiled["batch_id"] == "opening_ptr_182_proof"
    assert list(compiled["glyph_codes"].values()) == [
        0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89,
        0x8C, 0x8D, 0x8E, 0x8F, 0x90, 0x91, 0x92, 0x93,
    ]
    record = compiled["records"][0]
    assert record["encoded"] == PROOF_RECORD


def test_bad_control_and_capacity_rejected() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        bad_control = root / "bad_control.json"
        write_catalog(bad_control, [base_record([{"byte": "NO"}, {"byte": "FF"}])])
        try:
            compile_catalog(bad_control)
        except CatalogError:
            pass
        else:
            raise AssertionError("invalid control byte was accepted")

        too_many = root / "too_many.json"
        glyphs = [{"glyph": chr(ord("A") + index)} for index in range(len(AVAILABLE_GLYPH_CODES) + 1)]
        record = base_record([*glyphs, {"byte": "FF"}])
        record["expected_length"] = len(glyphs) + 1
        record["expected_original_bytes"] = " ".join(["00"] * len(glyphs) + ["FF"])
        write_catalog(too_many, [record])
        try:
            compile_catalog(too_many)
        except CatalogError as exc:
            assert "verified pool" in str(exc)
        else:
            raise AssertionError("oversized glyph batch was accepted")


def main() -> int:
    test_default_catalog()
    test_bad_control_and_capacity_rejected()
    print("Korean scene-batch compiler tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
