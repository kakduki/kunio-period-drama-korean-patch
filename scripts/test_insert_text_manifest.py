"""Test the selected-only translation manifest plan."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.insert_text import make_manifest_plan  # noqa: E402


def main() -> int:
    pages = [{"page_index": index, "syllables": []} for index in range(48)]
    payload = {
        "optimized_pages": pages,
        "pointer_page_assignments": [0] * 248,
    }
    with tempfile.TemporaryDirectory(prefix="manifest_plan_test_") as temp:
        root = Path(temp)
        source = root / "plan.json"
        source.write_text(json.dumps(payload) + "\n", encoding="utf-8")
        output = make_manifest_plan(source, {182: "\ucfe0\ub2c8\ub9c8\uc0ac \uc5b4\uc11c", 183: "\uc624\ucf54\ud1a0 \ucfe0b2c\uc624"}, root)
        result = json.loads(output.read_text(encoding="utf-8"))
    assignments = result["pointer_page_assignments"]
    assert assignments[182] == 48
    assert assignments[183] == 48
    assert all(value is None for index, value in enumerate(assignments) if index not in {182, 183})
    assert set(result["optimized_pages"][48]["syllables"]) == {character for character in "\ucfe0\ub2c8\ub9c8\uc0ac \uc5b4\uc11c \uc624\ucf54\ud1a0 \ucfe0\ub2c8\uc624" if "\uac00" <= character <= "\ud7a3"}
    print("OK: selected-only manifest font page plan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())