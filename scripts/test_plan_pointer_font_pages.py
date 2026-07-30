#!/usr/bin/env python3

from plan_pointer_font_pages import PAGE_SYLLABLE_CAPACITY, build_plan


def row(index: int, text: str, status: str = "english_semantic_draft") -> dict[str, str]:
    return {
        "pointer_index": str(index),
        "translation_status": status,
        "korean_text": text,
    }


def main() -> int:
    rows = [row(index, "") for index in range(248)]
    rows[0] = row(0, "가나다")
    rows[1] = row(1, "다라마")
    rows[2] = row(
        2, "".join(chr(0xAC00 + index) for index in range(PAGE_SYLLABLE_CAPACITY + 1))
    )
    rows[3] = row(3, "가", "excluded_non_dialogue")
    payload = build_plan(rows)
    assert payload["status"] == "READY_WITH_TEXT_REVISIONS"
    assert payload["coverage"]["assigned_rows"] == 246
    assert payload["coverage"]["oversize_rows"] == 1
    assert payload["oversize_records"][0]["pointer_index"] == 2
    assert all(
        page["syllable_count"] <= PAGE_SYLLABLE_CAPACITY
        for page in payload["optimized_pages"]
    )
    assert payload["pointer_page_assignments"][0] is not None
    assert payload["pointer_page_assignments"][2] is None
    assert payload["pointer_page_assignments"][3] is None
    print("plan_pointer_font_pages tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
