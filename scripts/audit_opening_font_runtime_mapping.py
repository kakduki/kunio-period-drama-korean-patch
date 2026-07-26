#!/usr/bin/env python3
"""Audit emitted opening-dialogue tile codes against runtime MMC3 state."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from analyze_reference_ips import InesLayout, parse_ines_layout
from rom_utils import REPO_ROOT, find_rom_path


DEFAULT_PROBE_DIR = (
    REPO_ROOT / "rom_analysis" / "opening_dialogue_renderer_probe_speaker_separator_candidate"
)
DEFAULT_CANDIDATE_REPORT = (
    REPO_ROOT / "rom_analysis" / "opening_dialogue_16x16_speaker_separator_proof.json"
)
DEFAULT_CANDIDATE_ROM = (
    REPO_ROOT
    / "output"
    / "opening_dialogue_16x16_speaker_separator_proof"
    / "kunio_period_drama_korean_opening_dialogue_16x16_speaker_separator_proof.nes"
)
DEFAULT_JSON_OUTPUT = REPO_ROOT / "rom_analysis" / "opening_font_runtime_mapping_audit.json"
DEFAULT_MARKDOWN_OUTPUT = REPO_ROOT / "rom_analysis" / "opening_font_runtime_mapping_audit.md"
CHR_TILE_SIZE = 16
CHR_8K_SIZE = 0x2000
MAPPER_CHR_REGISTER_COUNT = 6


def parse_hex(value: object) -> int:
    if isinstance(value, int):
        return value
    token = str(value).strip()
    if not token:
        raise ValueError("missing hexadecimal value")
    return int(token, 16)


def hex_offset(value: int) -> str:
    return f"0x{value:05X}"


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"required runtime trace is missing: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def resolve_chr_windows(control: int, registers: list[int]) -> list[int]:
    if len(registers) != MAPPER_CHR_REGISTER_COUNT:
        raise ValueError("MMC3 background mapping needs r0 through r5")
    r0, r1, r2, r3, r4, r5 = registers
    pair0 = (r0 & 0xFE, r0 | 0x01)
    pair1 = (r1 & 0xFE, r1 | 0x01)
    if control & 0x80:
        return [r2, r3, r4, r5, *pair0, *pair1]
    return [*pair0, *pair1, r2, r3, r4, r5]


def map_background_tile(
    tile_code: int,
    *,
    mapper_control: int,
    ppu_control: int,
    registers: list[int],
    layout: InesLayout,
) -> dict[str, object]:
    chr_windows = resolve_chr_windows(mapper_control, registers)
    background_pattern_base = 0x1000 if ppu_control & 0x10 else 0x0000
    ppu_address = background_pattern_base + tile_code * CHR_TILE_SIZE
    window_index = ppu_address // 0x400
    if not 0 <= window_index < len(chr_windows):
        raise ValueError(f"tile code 0x{tile_code:02X} maps outside PPU pattern memory")
    chr_1k_bank = chr_windows[window_index]
    physical_chr_bank = chr_1k_bank // 8
    local_tile = (chr_1k_bank % 8) * 0x40 + (ppu_address % 0x400) // CHR_TILE_SIZE
    rom_offset = (
        layout.chr_start
        + physical_chr_bank * CHR_8K_SIZE
        + local_tile * CHR_TILE_SIZE
    )
    if rom_offset + CHR_TILE_SIZE > layout.chr_end:
        raise ValueError("runtime tile maps outside CHR ROM")
    return {
        "tile_code": f"0x{tile_code:02X}",
        "ppu_pattern_address": f"0x{ppu_address:04X}",
        "background_pattern_base": f"0x{background_pattern_base:04X}",
        "chr_1k_bank": chr_1k_bank,
        "physical_chr_8k_bank": physical_chr_bank,
        "physical_tile_in_bank": f"0x{local_tile:03X}",
        "rom_offset": rom_offset,
    }


def candidate_font_targets(report: dict[str, object]) -> tuple[set[int], dict[int, int]]:
    source = report.get("source")
    candidate = report.get("candidate")
    if not isinstance(source, dict) or not isinstance(candidate, dict):
        raise ValueError("candidate report has no source/candidate sections")
    pairs = source.get("glyph_code_pairs")
    targets = candidate.get("targets")
    if not isinstance(pairs, dict) or not isinstance(targets, list):
        raise ValueError("candidate report has no glyph-code or target list")

    source_codes: set[int] = set()
    for pair in pairs.values():
        if not isinstance(pair, list):
            raise ValueError("candidate glyph-code pair is not a list")
        source_codes.update(parse_hex(code) for code in pair)

    font_targets: dict[int, int] = {}
    for target in targets:
        if not isinstance(target, dict):
            continue
        kind = str(target.get("kind", ""))
        if not kind.startswith("font_tile_"):
            continue
        code = parse_hex(target.get("code"))
        offset = target.get("rom_offset")
        if not isinstance(offset, int):
            raise ValueError(f"font target 0x{code:02X} has no integer ROM offset")
        if code in font_targets and font_targets[code] != offset:
            raise ValueError(f"font target code 0x{code:02X} has conflicting offsets")
        font_targets[code] = offset
    if not source_codes or not font_targets:
        raise ValueError("candidate report does not declare font targets")
    return source_codes, font_targets


def emitted_rows_for_candidate(
    rows: list[dict[str, str]], source_codes: set[int]
) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    for row in rows:
        try:
            source = parse_hex(row.get("source_byte", ""))
            emitted = parse_hex(row.get("value", ""))
        except ValueError:
            continue
        if source not in source_codes:
            continue
        role = row.get("role", "")
        if role not in {"top", "bottom"}:
            continue
        if emitted == 0xB1:
            continue
        selected.append(row)
    return selected


def audit_emitted_tiles(
    rows: list[dict[str, str]],
    *,
    source_codes: set[int],
    font_targets: dict[int, int],
    layout: InesLayout,
    base: bytes,
    candidate: bytes,
) -> dict[str, object]:
    selected = emitted_rows_for_candidate(rows, source_codes)
    audits: list[dict[str, object]] = []
    missing_state = 0
    for row in selected:
        try:
            mapper_control = parse_hex(row.get("mapper_control", ""))
            ppu_control = parse_hex(row.get("ppu_control", ""))
            registers = [parse_hex(row.get(f"r{index}", "")) for index in range(6)]
            emitted = parse_hex(row["value"])
            source = parse_hex(row["source_byte"])
        except ValueError:
            missing_state += 1
            continue

        runtime = map_background_tile(
            emitted,
            mapper_control=mapper_control,
            ppu_control=ppu_control,
            registers=registers,
            layout=layout,
        )
        actual_offset = int(runtime["rom_offset"])
        declared_offset = font_targets.get(emitted)
        runtime_slot_changed = (
            base[actual_offset : actual_offset + CHR_TILE_SIZE]
            != candidate[actual_offset : actual_offset + CHR_TILE_SIZE]
        )
        target_matches_runtime_slot = declared_offset == actual_offset
        if declared_offset is None:
            reason = "no declared candidate target for emitted tile"
        elif not target_matches_runtime_slot:
            reason = "declared candidate target differs from runtime physical tile"
        elif not runtime_slot_changed:
            reason = "runtime physical tile was not changed in candidate ROM"
        else:
            reason = "runtime physical tile matches the declared changed target"
        audits.append(
            {
                "frame": int(row.get("frame") or 0),
                "role": row.get("role"),
                "source_code": f"0x{source:02X}",
                "emitted_tile_code": f"0x{emitted:02X}",
                "mapper_control": f"0x{mapper_control:02X}",
                "ppu_control": f"0x{ppu_control:02X}",
                "runtime_physical_chr_bank": runtime["physical_chr_8k_bank"],
                "runtime_physical_tile": runtime["physical_tile_in_bank"],
                "runtime_rom_offset": hex_offset(actual_offset),
                "declared_candidate_rom_offset": (
                    hex_offset(declared_offset) if declared_offset is not None else None
                ),
                "target_matches_runtime_slot": target_matches_runtime_slot,
                "runtime_slot_changed": runtime_slot_changed,
                "result": (
                    "PASS"
                    if target_matches_runtime_slot and runtime_slot_changed
                    else "FAIL"
                ),
                "reason": reason,
            }
        )

    if not audits or missing_state:
        verdict = "UNKNOWN"
    elif any(row["result"] == "FAIL" for row in audits):
        verdict = "FAIL"
    else:
        verdict = "PASS"
    return {
        "overall_verdict": verdict,
        "selected_emitted_tile_rows": len(selected),
        "missing_mapper_state_rows": missing_state,
        "pass_count": sum(row["result"] == "PASS" for row in audits),
        "fail_count": sum(row["result"] == "FAIL" for row in audits),
        "audits": audits,
    }


def analyze(
    *,
    probe_dir: Path,
    candidate_report_path: Path,
    base_rom_path: Path,
    candidate_rom_path: Path,
) -> dict[str, object]:
    rows = read_tsv(probe_dir / "emitted_tiles.tsv")
    report = json.loads(candidate_report_path.read_text(encoding="utf-8"))
    source_codes, font_targets = candidate_font_targets(report)
    base = base_rom_path.read_bytes()
    candidate = candidate_rom_path.read_bytes()
    layout = parse_ines_layout(base)
    if len(base) != len(candidate):
        raise ValueError("candidate ROM length differs from base ROM")
    payload = audit_emitted_tiles(
        rows,
        source_codes=source_codes,
        font_targets=font_targets,
        layout=layout,
        base=base,
        candidate=candidate,
    )
    payload["inputs"] = {
        "renderer_probe_dir": str(probe_dir),
        "candidate_report": str(candidate_report_path),
        "base_rom": str(base_rom_path),
        "candidate_rom": str(candidate_rom_path),
        "candidate_source_code_count": len(source_codes),
        "declared_font_target_count": len(font_targets),
    }
    return payload


def render_markdown(payload: dict[str, object]) -> str:
    inputs = payload["inputs"]
    audits = payload["audits"]
    failures = [row for row in audits if row["result"] == "FAIL"]
    lines = [
        "# Opening Font Runtime Mapping Audit",
        "",
        f"Status: {payload['overall_verdict']}",
        "",
        f"- Candidate source codes: {inputs['candidate_source_code_count']}",
        f"- Candidate declared font targets: {inputs['declared_font_target_count']}",
        f"- Runtime emitted tile rows audited: {payload['selected_emitted_tile_rows']}",
        f"- Rows with incomplete mapper state: {payload['missing_mapper_state_rows']}",
        f"- Runtime mappings passing: {payload['pass_count']}",
        f"- Runtime mappings failing: {payload['fail_count']}",
        "",
    ]
    if payload["overall_verdict"] == "PASS":
        lines.extend(
            [
                "Every audited emitted tile maps to the physical CHR tile changed by the",
                "candidate. This is still one opening-scene result, not release approval.",
                "",
            ]
        )
        return "\n".join(lines)
    if payload["overall_verdict"] == "UNKNOWN":
        lines.extend(
            [
                "The renderer probe did not provide complete tile-plus-mapper evidence.",
                "Do not promote the candidate or infer a general font allocation.",
                "",
            ]
        )
        return "\n".join(lines)

    lines.extend(
        [
            "The candidate changes a different physical CHR tile for at least one tile",
            "that the runtime actually emits. The affected source range must not be",
            "used as a release-capable Korean font allocation.",
            "",
            "| source | emitted | runtime bank/tile | runtime ROM | candidate ROM | reason |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in failures:
        lines.append(
            f"| {row['source_code']} | {row['emitted_tile_code']} | "
            f"Bank {row['runtime_physical_chr_bank']} / {row['runtime_physical_tile']} | "
            f"{row['runtime_rom_offset']} | {row['declared_candidate_rom_offset'] or 'none'} | "
            f"{row['reason']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe-dir", type=Path, default=DEFAULT_PROBE_DIR)
    parser.add_argument("--candidate-report", type=Path, default=DEFAULT_CANDIDATE_REPORT)
    parser.add_argument("--base-rom", type=Path, default=None)
    parser.add_argument("--candidate-rom", type=Path, default=DEFAULT_CANDIDATE_ROM)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    args = parser.parse_args()

    base_rom = args.base_rom or find_rom_path()
    payload = analyze(
        probe_dir=args.probe_dir,
        candidate_report_path=args.candidate_report,
        base_rom_path=base_rom,
        candidate_rom_path=args.candidate_rom,
    )
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")
    print(f"overall_verdict={payload['overall_verdict']}")
    print(f"json={args.json_output}")
    print(f"markdown={args.markdown_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
