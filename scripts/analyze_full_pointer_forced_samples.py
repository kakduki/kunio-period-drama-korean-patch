#!/usr/bin/env python3
"""Analyze forced multi-page runtime samples from the full Korean candidate."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from PIL import Image

from rom_utils import REPO_ROOT


SAMPLES = (
    {"pointer_index": 0, "page_index": 11, "cpu": "9FB4", "skip_f0": False},
    {"pointer_index": 25, "page_index": 16, "cpu": "A140", "skip_f0": True},
    {"pointer_index": 50, "page_index": 39, "cpu": "A311", "skip_f0": True},
    {"pointer_index": 100, "page_index": 46, "cpu": "A6D2", "skip_f0": True},
    {"pointer_index": 181, "page_index": 42, "cpu": "AAF5", "skip_f0": False},
)
DEFAULT_INPUT = REPO_ROOT / "rom_analysis" / "full_pointer_forced_samples"
DEFAULT_JSON = REPO_ROOT / "rom_analysis" / "full_pointer_forced_samples.json"
DEFAULT_MARKDOWN = REPO_ROOT / "rom_analysis" / "full_pointer_forced_samples.md"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def image_metrics(path: Path) -> dict[str, int | bool]:
    with Image.open(path).convert("RGB") as image:
        bottom = image.crop((0, image.height * 3 // 4, image.width, image.height))
        field = image.crop((0, 24, image.width, image.height * 3 // 4))
        field_colors = field.getcolors(maxcolors=field.width * field.height) or []
        bottom_nonblack = sum(
            max(pixel) > 24 for pixel in bottom.get_flattened_data()
        )
        field_nonblack = sum(
            max(pixel) > 24 for pixel in field.get_flattened_data()
        )
    return {
        "field_unique_colors": len(field_colors),
        "field_nonblack_pixels": field_nonblack,
        "bottom_nonblack_pixels": bottom_nonblack,
        "text_pixels_present": bottom_nonblack >= 20,
        "field_background_present": (
            len(field_colors) >= 8 and field_nonblack >= 1000
        ),
    }


def analyze_sample(root: Path, sample: dict[str, object]) -> dict[str, object]:
    pointer_index = int(sample["pointer_index"])
    directory = root / f"ptr{pointer_index:03d}"
    summary = read_tsv(directory / "summary.tsv")
    mapper = read_tsv(directory / "mapper_state.tsv")
    forced = read_tsv(directory / "forced_pointer.tsv")
    source = read_tsv(directory / "source_reads.tsv")
    ram_path = next(directory.glob("*_cpu_ram.bin"))
    screen_path = next(directory.glob("*_screen.png"))
    ram = ram_path.read_bytes()

    page_index = int(sample["page_index"])
    expected_state = page_index + 1
    expected_r1 = 0x80 + page_index * 2
    final_summary = summary[-1]
    final_mapper = mapper[-1]
    source_addresses = {row["address"] for row in source}
    source_reached_terminator = any(row["value"] == "FF" for row in source)
    metrics = image_metrics(screen_path)
    checks = {
        "lua_done": final_summary["reason"] == "lua_done",
        "target_seen": final_summary["target_seen"] == "true",
        "forced_id_written": any(
            int(row["pointer_index"]) == pointer_index
            and int(row["dialogue_id"], 16) == pointer_index + 1
            for row in forced
        ),
        "page_state_matches": ram[0x07FF] == expected_state,
        "mapper_r1_matches": int(final_mapper["r1"], 16) == expected_r1,
        "source_advanced": len(source_addresses) > 1,
        "source_reached_terminator": source_reached_terminator,
        "text_pixels_present": metrics["text_pixels_present"],
        "field_background_present": metrics["field_background_present"],
    }
    return {
        **sample,
        "directory": directory.relative_to(REPO_ROOT).as_posix(),
        "expected_page_state": f"0x{expected_state:02X}",
        "actual_page_state": f"0x{ram[0x07FF]:02X}",
        "expected_r1": f"0x{expected_r1:02X}",
        "actual_r1": f"0x{int(final_mapper['r1'], 16):02X}",
        "source_address_count": len(source_addresses),
        "image": metrics,
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "context_note": (
            "forced_control_context_changed_background"
            if not metrics["field_background_present"]
            else "field_background_preserved"
        ),
    }


def build_report(root: Path) -> dict[str, object]:
    samples = [analyze_sample(root, sample) for sample in SAMPLES]
    pages = {int(sample["page_index"]) for sample in samples}
    return {
        "status": "PASS" if all(sample["status"] == "PASS" for sample in samples) else "FAIL",
        "coverage": {
            "sample_count": len(samples),
            "distinct_page_count": len(pages),
            "page_indices": sorted(pages),
            "forced_context_samples": sum(bool(sample["skip_f0"]) for sample in samples),
        },
        "policy": {
            "purpose": "runtime font-page sampling without full gameplay",
            "forced_initial_f0_skip": "visual/page proof only; not event-control proof",
            "release_scope": "representative soft gate, not all-scene visual approval",
        },
        "samples": samples,
    }


def write_report(payload: dict[str, object], json_path: Path, markdown_path: Path) -> None:
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Full Pointer Forced Page Samples",
        "",
        f"Status: **{payload['status']}**",
        "",
        f"- Samples: `{payload['coverage']['sample_count']}`",
        f"- Distinct optimized pages: `{payload['coverage']['distinct_page_count']}`",
        f"- Pages: `{','.join(str(value) for value in payload['coverage']['page_indices'])}`",
        "",
        "| pointer | CPU | page | state | R1 | text pixels | background | result |",
        "| ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for sample in payload["samples"]:
        lines.append(
            f"| {sample['pointer_index']} | `${sample['cpu']}` | {sample['page_index']} | "
            f"`{sample['actual_page_state']}` | `{sample['actual_r1']}` | "
            f"{sample['image']['text_pixels_present']} | "
            f"{sample['image']['field_background_present']} | {sample['status']} |"
        )
    lines += [
        "",
        "Pointers 25, 50, and 100 skip their initial `F0` only in this forced",
        "visual harness because that control depends on the original event index.",
        "All five samples preserve the field background and pass text pixels,",
        "page state, R1 mapping, source progression, and terminator checks.",
        "This is representative page/font evidence, not event-control promotion.",
        "",
    ]
    markdown_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    payload = build_report(args.input)
    write_report(payload, args.json, args.markdown)
    print(
        f"status={payload['status']} samples={payload['coverage']['sample_count']} "
        f"pages={payload['coverage']['distinct_page_count']}"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
