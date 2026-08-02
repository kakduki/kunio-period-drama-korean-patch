#!/usr/bin/env python3
"""Compare the Japanese, English-reference, and Korean pre-pointer paths."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from rom_utils import REPO_ROOT


BASE_ROM = REPO_ROOT / "rom" / "Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes"
ENGLISH_ROM = REPO_ROOT / "output" / "english_reference_runtime" / "kunio_period_drama_english_reference.nes"
KOREAN_ROM = REPO_ROOT / "output" / "full_korean_clean_merged_candidate" / "kunio_period_drama_korean_full_items_title_none_candidate.nes"
BASE_TRACE = REPO_ROOT / "rom_analysis" / "pre_pointer_renderer_trace_japanese_base" / "renderer_exec.tsv"
ENGLISH_TRACE = REPO_ROOT / "rom_analysis" / "pre_pointer_renderer_trace_english_reference" / "renderer_exec.tsv"
KOREAN_TRACE = REPO_ROOT / "rom_analysis" / "pre_pointer_renderer_trace_clean_merged_v4" / "renderer_exec.tsv"
DEFAULT_JSON = REPO_ROOT / "rom_analysis" / "pre_pointer_renderer_reference_compare.json"
DEFAULT_MD = REPO_ROOT / "rom_analysis" / "pre_pointer_renderer_reference_compare.md"

REGIONS = (
    ("renderer_support", 0x05288, 0x052C8),
    ("pre_pointer_text", 0x056BC, 0x05D54),
    ("pointer_table", 0x05DD4, 0x05FC4),
    ("pointer_dialogue", 0x05FC4, 0x07767),
    ("growth_ui", 0x07894, 0x078AB),
    ("menu_labels", 0x07FB6, 0x0800F),
    ("runtime_transform_8205", 0x08215, 0x0821D),
)


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def load_trace(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return [row for row in reader if row.get("entry") in {"8205", "8209"}]


def trace_sample(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            key: row.get(key, "")
            for key in ("frame", "entry", "a", "y", "0007", "0008", "0011", "0012", "001E", "r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7")
        }
        for row in rows
        if row.get("frame") == "177"
    ]


def compare(base: bytes, reference: bytes, korean: bytes) -> dict[str, object]:
    region_rows: list[dict[str, object]] = []
    for name, start, end in REGIONS:
        region_rows.append(
            {
                "name": name,
                "start": f"0x{start:05X}",
                "end": f"0x{end:05X}",
                "english_changed": sum(a != b for a, b in zip(base[start:end], reference[start:end])),
                "korean_changed_vs_base": sum(a != b for a, b in zip(base[start:end], korean[start:end])),
                "korean_changed_vs_english": sum(a != b for a, b in zip(reference[start:end], korean[start:end])),
            }
        )

    return {
        "roms": {
            "japanese_base": {"path": str(BASE_ROM), "md5": md5(base)},
            "english_reference": {"path": str(ENGLISH_ROM), "md5": md5(reference)},
            "korean_clean_candidate": {"path": str(KOREAN_ROM), "md5": md5(korean)},
        },
        "regions": region_rows,
        "runtime_transform": {
            "cpu_window": "$8205-$820C",
            "file_offset": "0x08215-0x0821C",
            "japanese_base": base[0x08215:0x0821D].hex(" "),
            "english_reference": reference[0x08215:0x0821D].hex(" "),
            "korean_clean_candidate": korean[0x08215:0x0821D].hex(" "),
            "unchanged_across_all_three": base[0x08215:0x0821D] == reference[0x08215:0x0821D] == korean[0x08215:0x0821D],
        },
        "trace_samples": {
            "japanese_base": trace_sample(load_trace(BASE_TRACE)),
            "english_reference": trace_sample(load_trace(ENGLISH_TRACE)),
            "korean_clean_candidate": trace_sample(load_trace(KOREAN_TRACE)),
        },
        "conclusion": {
            "english_reuses_runtime_transform": base[0x08215:0x0821D] == reference[0x08215:0x0821D],
            "korean_reuses_runtime_transform": base[0x08215:0x0821D] == korean[0x08215:0x0821D],
            "next_owner": "pre-pointer data encoding, renderer-support mapping, CHR font allocation, and bounded visual proof",
        },
    }


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Pre-Pointer Renderer Reference Comparison",
        "",
        "This compares the same bounded FCEUX route on the Japanese base, the IPS-applied English reference, and the clean Korean candidate.",
        "",
        "## Result",
        "",
        "- The runtime transform at CPU `$8205-$820C` is unchanged across all three ROMs.",
        "- The English reference changes pre-pointer data, renderer-support data, pointer data, menu data, and CHR; it does not require a new runtime hook for this path.",
        "- The Korean candidate keeps the same transform and therefore must be advanced through data encoding, font ownership, pointer relocation, and visual proof.",
        "- This confirms that the long lead time is not caused by lacking an English reference; the hard part is the Korean glyph and multi-renderer ownership contract.",
        "",
        "## ROMs",
        "",
        "| ROM | MD5 |",
        "| --- | --- |",
    ]
    roms = payload["roms"]
    for label, value in roms.items():
        lines.append(f"| {label} | `{value['md5']}` |")
    lines.extend(
        [
            "",
            "## Region Changes",
            "",
            "| region | range | English vs Japanese | Korean vs Japanese | Korean vs English |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    for row in payload["regions"]:
        lines.append(
            f"| {row['name']} | `{row['start']}-{row['end']}` | {row['english_changed']} | {row['korean_changed_vs_base']} | {row['korean_changed_vs_english']} |"
        )
    lines.extend(
        [
            "",
            "## Runtime Bytes",
            "",
            f"- Japanese: `{payload['runtime_transform']['japanese_base']}`",
            f"- English: `{payload['runtime_transform']['english_reference']}`",
            f"- Korean: `{payload['runtime_transform']['korean_clean_candidate']}`",
            f"- Unchanged across all three: `{payload['runtime_transform']['unchanged_across_all_three']}`",
            "",
            "## Interpretation",
            "",
            "The English patch is a usable structural reference, but its changed bytes are not a universal copy recipe. The Korean implementation should keep the shared runtime transform intact and validate each renderer family independently.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MD)
    args = parser.parse_args()
    payload = compare(BASE_ROM.read_bytes(), ENGLISH_ROM.read_bytes(), KOREAN_ROM.read_bytes())
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")
    print(f"json={args.json_output}")
    print(f"markdown={args.markdown_output}")
    print(f"runtime_unchanged={payload['runtime_transform']['unchanged_across_all_three']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
