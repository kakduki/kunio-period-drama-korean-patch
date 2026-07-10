#!/usr/bin/env python3
"""Derive static leads from English IPS overlap without asserting live NES execution.

A physical PRG bank can appear in several MMC3 CPU windows. Therefore 16-bit
little-endian occurrences are retained only as mapper-unknown search leads.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from analyze_english_reference_runs import EXPECTED_BASE_MD5, EXPECTED_IPS_SHA256, parse_ips

HEADER_BYTES = 16
PRG_BANK_BYTES = 8192
CPU_WINDOWS = (0x8000, 0xA000, 0xC000, 0xE000)
# Official 6502 opcodes whose following two bytes form an absolute address operand.
# This is only local byte-shape filtering: raw PRG can still contain data that mimics code.
ABSOLUTE_OPERAND_OPCODES = {
    0x0D: "ORA abs", 0x19: "ORA abs,Y", 0x1D: "ORA abs,X", 0x20: "JSR abs",
    0x2C: "BIT abs", 0x2D: "AND abs", 0x39: "AND abs,Y", 0x3D: "AND abs,X",
    0x4C: "JMP abs", 0x4D: "EOR abs", 0x59: "EOR abs,Y", 0x5D: "EOR abs,X",
    0x6C: "JMP (abs)", 0x6D: "ADC abs", 0x79: "ADC abs,Y", 0x7D: "ADC abs,X",
    0x8C: "STY abs", 0x8D: "STA abs", 0x8E: "STX abs", 0x99: "STA abs,Y", 0x9D: "STA abs,X",
    0xAC: "LDY abs", 0xAD: "LDA abs", 0xAE: "LDX abs", 0xB9: "LDA abs,Y", 0xBC: "LDY abs,X", 0xBD: "LDA abs,X",
    0xCC: "CPY abs", 0xCD: "CMP abs", 0xCE: "DEC abs", 0xD9: "CMP abs,Y", 0xDD: "CMP abs,X", 0xDE: "DEC abs,X",
    0xEC: "CPX abs", 0xED: "SBC abs", 0xEE: "INC abs", 0xF9: "SBC abs,Y", 0xFD: "SBC abs,X", 0xFE: "INC abs,X",
}


def apply_ips(base: bytes, ips: bytes) -> bytes:
    patched = bytearray(base)
    for start, payload in parse_ips(ips):
        end = start + len(payload)
        if end > len(patched):
            raise ValueError(f"IPS record escapes base ROM at 0x{start:06X}")
        patched[start:end] = payload
    return bytes(patched)


def pointer_candidates(file_offset: int) -> list[int]:
    """Return possible CPU-window addresses for an 8KiB physical PRG location."""
    relative = file_offset - HEADER_BYTES
    if relative < 0:
        raise ValueError("file offset is inside iNES header")
    within_bank = relative % PRG_BANK_BYTES
    return [window + within_bank for window in CPU_WINDOWS]


def little_endian_hits(rom: bytes, address: int, prg_end: int) -> list[dict[str, int]]:
    needle = address.to_bytes(2, "little")
    hits: list[dict[str, int]] = []
    start = HEADER_BYTES
    while True:
        offset = rom.find(needle, start, prg_end)
        if offset < 0:
            return hits
        hits.append({
            "file_offset": offset,
            "physical_prg_bank": (offset - HEADER_BYTES) // PRG_BANK_BYTES,
        })
        start = offset + 1


def opcode_absolute_operand_hits(rom: bytes, address: int, prg_end: int) -> list[dict[str, object]]:
    """Keep raw address matches that are immediately preceded by a 3-byte absolute opcode."""
    hits: list[dict[str, object]] = []
    for raw in little_endian_hits(rom, address, prg_end):
        operand_offset = raw["file_offset"]
        opcode_offset = operand_offset - 1
        opcode = rom[opcode_offset] if opcode_offset >= HEADER_BYTES else None
        if opcode not in ABSOLUTE_OPERAND_OPCODES:
            continue
        hits.append({
            "instruction_file_offset": opcode_offset,
            "operand_file_offset": operand_offset,
            "physical_prg_bank": raw["physical_prg_bank"],
            "opcode": f"0x{opcode:02X}",
            "mnemonic": ABSOLUTE_OPERAND_OPCODES[opcode],
        })
    return hits


def analyze(correlation_path: Path, runs_path: Path, rom_path: Path, ips_path: Path) -> dict[str, object]:
    correlation = json.loads(correlation_path.read_text(encoding="utf-8"))
    runs = json.loads(runs_path.read_text(encoding="utf-8"))
    base = rom_path.read_bytes()
    ips = ips_path.read_bytes()
    base_md5 = hashlib.md5(base).hexdigest()
    ips_sha256 = hashlib.sha256(ips).hexdigest()
    if base_md5 != EXPECTED_BASE_MD5:
        raise ValueError(f"base ROM MD5 {base_md5} != verified {EXPECTED_BASE_MD5}")
    if ips_sha256 != EXPECTED_IPS_SHA256:
        raise ValueError(f"English IPS SHA-256 {ips_sha256} != verified {EXPECTED_IPS_SHA256}")
    if correlation["base"]["md5"] != base_md5 or runs["base"]["md5"] != base_md5:
        raise ValueError("input artifact base digest mismatch")
    if correlation["reference"]["ips_sha256"] != ips_sha256 or runs["ips"]["sha256"] != ips_sha256:
        raise ValueError("input artifact English IPS digest mismatch")

    patched = apply_ips(base, ips)
    prg_end = int(runs["layout"]["prg"][1])
    leads: list[dict[str, object]] = []
    for row in correlation["rows"]:
        if row["classification"] != "structurally_supported":
            continue
        start = int(row["file_offset"])
        expected = bytes.fromhex(row["base_bytes_expected"])
        end = start + len(expected)
        if base[start:end] != expected:
            raise ValueError(f"task {row['task']} base bytes changed after correlation")
        cpu_addresses = pointer_candidates(start)
        candidate_rows = []
        for address in cpu_addresses:
            candidate_rows.append({
                "cpu_address": f"0x{address:04X}",
                "base_little_endian_hits": little_endian_hits(base, address, prg_end),
                "english_little_endian_hits": little_endian_hits(patched, address, prg_end),
            })
        english_bytes = patched[start:end]
        leads.append({
            "task": row["task"],
            "file_offset": start,
            "file_offset_hex": f"0x{start:05X}",
            "byte_length": len(expected),
            "source_display": row["source_display"],
            "korean_display": row["korean_display"],
            "classification": "static_only",
            "base_bytes": expected.hex(" ").upper(),
            "english_bytes": english_bytes.hex(" ").upper(),
            "english_target_bytes_differ": english_bytes != expected,
            "overlap_ranges": row["overlap_ranges"],
            "run_context": [
                {
                    "run_id": run["id"],
                    "file_start": run["start"],
                    "file_end_exclusive": run["end_exclusive"],
                    "base_hex": run["base_hex"],
                    "english_hex": run["english_hex"],
                }
                for run in runs["runs"]
                if run["id"] in row["overlap_run_ids"]
            ],
            "pointer_scan": {
                "status": "mapper_unknown_static_candidates",
                "method": "scan PRG for little-endian occurrences of all four possible 8KiB MMC3 CPU-window addresses, then retain the subset immediately preceded by an official 6502 absolute-operand opcode; no mapper state or instruction-boundary proof asserted",
                "cpu_address_candidates": len(cpu_addresses),
                "candidate_windows": candidate_rows,
                "opcode_absolute_operand_hits": [
                    {
                        "cpu_address": f"0x{address:04X}",
                        "base_hits": opcode_absolute_operand_hits(base, address, prg_end),
                        "english_hits": opcode_absolute_operand_hits(patched, address, prg_end),
                    }
                    for address in cpu_addresses
                ],
            },
            "runtime_proof_required": True,
            "release_ready": False,
            "limitations": "Byte replacement and 16-bit occurrences are static leads only; they do not prove a text pointer, CPU read, renderer path, or matching scene.",
        })
    return {
        "schema_version": 1,
        "purpose": "static English-reference byte and candidate-pointer leads only; no emulator/runtime claim",
        "offset_convention": {
            "coordinate_space": "iNES file offset including 16-byte header",
            "header_bytes": HEADER_BYTES,
            "intervals": "start inclusive, end_exclusive",
        },
        "base": {"path": str(rom_path), "md5": base_md5},
        "english_reference": {"ips_path": str(ips_path), "ips_sha256": ips_sha256},
        "input_artifacts": {"correlation": str(correlation_path), "runs": str(runs_path)},
        "lead_count": len(leads),
        "leads": leads,
    }


def markdown(result: dict[str, object]) -> str:
    lines = [
        "# English-reference static leads for Korean targets",
        "",
        "> These are physical byte-diff and mapper-unknown pointer-search leads. They are not CPU-read, renderer, visual, or release evidence.",
        "",
        f"- Verified base MD5: `{result['base']['md5']}`",
        f"- Verified English IPS SHA-256: `{result['english_reference']['ips_sha256']}`",
        f"- Static leads: **{result['lead_count']}**",
        "",
        "| task | offset | source → Korean | base bytes | English bytes | overlap | pointer candidates |",
        "|---:|---|---|---|---|---:|---:|",
    ]
    for lead in result["leads"]:
        overlap_bytes = sum(entry["overlap_bytes"] for entry in lead["overlap_ranges"])
        lines.append(
            f"| {lead['task']} | `{lead['file_offset_hex']}` | {lead['source_display']} → {lead['korean_display']} | "
            f"`{lead['base_bytes']}` | `{lead['english_bytes']}` | {overlap_bytes}B | {lead['pointer_scan']['cpu_address_candidates']} |"
        )
    lines += [
        "",
        "## Hard limits",
        "",
        "- A changed English byte at the same file offset establishes only physical-diff overlap.",
        "- Each 8KiB PRG location has four possible CPU-window representations. The scan records raw little-endian occurrences; it does not establish mapper state, opcode semantics, or a live pointer table.",
        "- No Korean IPS/ROM is generated or modified by this artifact.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--correlation", type=Path, default=Path("analysis/korean_target_english_reference_correlation.json"))
    parser.add_argument("--runs", type=Path, default=Path("analysis/english_reference_runs.json"))
    parser.add_argument("--rom", type=Path, default=Path("rom/kunio.nes"))
    parser.add_argument("--ips", type=Path, default=Path("reference/technos-samurai-v1/TSe-v10.ips"))
    parser.add_argument("--json-output", type=Path, default=Path("analysis/english_target_static_leads.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("analysis/english_target_static_leads.md"))
    args = parser.parse_args()
    result = analyze(args.correlation, args.runs, args.rom, args.ips)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(markdown(result), encoding="utf-8")
    print(json.dumps({"lead_count": result["lead_count"], "tasks": [lead["task"] for lead in result["leads"]]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
