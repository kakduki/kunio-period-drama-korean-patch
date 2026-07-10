#!/usr/bin/env python3
"""Map the verified Technos Samurai English IPS without inferring a live renderer path."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


HEADER_SIZE = 16
EXPECTED_BASE_MD5 = "0d406a85285b4de8468f0dab6aad5fe5"
EXPECTED_IPS_SHA256 = "cb6ea2fdbf82e974c474f4ea0d489f7c65647c94de899caf2a6b8c089f202dad"


def parse_ips(data: bytes) -> list[tuple[int, bytes]]:
    if not data.startswith(b"PATCH") or not data.endswith(b"EOF"):
        raise ValueError("not a complete IPS file")
    index = 5
    records: list[tuple[int, bytes]] = []
    while data[index : index + 3] != b"EOF":
        if index + 5 > len(data):
            raise ValueError("truncated IPS record header")
        offset = int.from_bytes(data[index : index + 3], "big")
        size = int.from_bytes(data[index + 3 : index + 5], "big")
        index += 5
        if size == 0:
            if index + 3 > len(data):
                raise ValueError("truncated IPS RLE record")
            repeat = int.from_bytes(data[index : index + 2], "big")
            payload = data[index + 2 : index + 3] * repeat
            index += 3
        else:
            if index + size > len(data):
                raise ValueError("truncated IPS payload")
            payload = data[index : index + size]
            index += size
        records.append((offset, payload))
    return records


def classify_region(offset: int, prg_end: int, rom_size: int) -> str:
    if offset < HEADER_SIZE:
        return "header"
    if offset < prg_end:
        return "prg"
    if offset < rom_size:
        return "chr"
    return "out_of_rom"


def physical_bank(offset: int, region: str, prg_end: int) -> int | None:
    if region == "prg":
        return (offset - HEADER_SIZE) // 8192
    if region == "chr":
        return (offset - prg_end) // 1024
    return None


def changed_runs(changed_offsets: list[int]) -> list[tuple[int, int]]:
    if not changed_offsets:
        return []
    result: list[tuple[int, int]] = []
    start = previous = changed_offsets[0]
    for offset in changed_offsets[1:]:
        if offset != previous + 1:
            result.append((start, previous + 1))
            start = offset
        previous = offset
    result.append((start, previous + 1))
    return result


def analyze(base_path: Path, ips_path: Path) -> dict[str, object]:
    base = base_path.read_bytes()
    ips = ips_path.read_bytes()
    if len(base) < HEADER_SIZE or base[:4] != b"NES\x1a":
        raise ValueError("base ROM has no iNES header")
    base_md5 = hashlib.md5(base).hexdigest()
    if base_md5 != EXPECTED_BASE_MD5:
        raise ValueError(f"base ROM MD5 {base_md5} != verified {EXPECTED_BASE_MD5}")
    ips_sha256 = hashlib.sha256(ips).hexdigest()
    if ips_sha256 != EXPECTED_IPS_SHA256:
        raise ValueError(f"English IPS SHA-256 {ips_sha256} != verified {EXPECTED_IPS_SHA256}")

    prg_end = HEADER_SIZE + base[4] * 16_384
    records = parse_ips(ips)
    patched = bytearray(base)
    changed: list[int] = []
    record_rows: list[dict[str, object]] = []
    record_region_counts: Counter[str] = Counter()
    for record_id, (start, payload) in enumerate(records, start=1):
        end = start + len(payload)
        if end > len(base):
            raise ValueError(f"record {record_id} escapes ROM at 0x{start:06X}")
        record_region = classify_region(start, prg_end, len(base))
        record_region_counts[record_region] += 1
        before = bytes(patched[start:end])
        for local, value in enumerate(payload):
            absolute = start + local
            if patched[absolute] != value:
                changed.append(absolute)
            patched[absolute] = value
        record_rows.append({
            "id": record_id,
            "start": start,
            "end_exclusive": end,
            "bytes": len(payload),
            "region": record_region,
            "physical_bank": physical_bank(start, record_region, prg_end),
            "base_hex": before.hex(" ").upper(),
            "english_hex": payload.hex(" ").upper(),
        })

    changed = sorted(set(changed))
    region_counts = Counter(classify_region(offset, prg_end, len(base)) for offset in changed)
    run_rows = []
    for run_id, (start, end) in enumerate(changed_runs(changed), start=1):
        run_region = classify_region(start, prg_end, len(base))
        run_rows.append({
            "id": run_id,
            "start": start,
            "end_exclusive": end,
            "bytes": end - start,
            "region": run_region,
            "physical_bank": physical_bank(start, run_region, prg_end),
            "base_hex": base[start:end].hex(" ").upper(),
            "english_hex": bytes(patched[start:end]).hex(" ").upper(),
        })

    prg_banks = Counter((offset - HEADER_SIZE) // 8192 for offset in changed if HEADER_SIZE <= offset < prg_end)
    chr_banks = Counter((offset - prg_end) // 1024 for offset in changed if prg_end <= offset < len(base))
    return {
        "method": "static physical IPS diff only; PRG runs are structural candidates, never live pointer/render proof",
        "base": {"path": str(base_path), "bytes": len(base), "md5": base_md5},
        "ips": {"path": str(ips_path), "sha256": ips_sha256, "records": len(records)},
        "layout": {"header": [0, HEADER_SIZE], "prg": [HEADER_SIZE, prg_end], "chr": [prg_end, len(base)]},
        "records_by_start_region": dict(sorted(record_region_counts.items())),
        "changed_bytes_by_region": dict(sorted(region_counts.items())),
        "prg_8k_bank_changed_bytes": dict(sorted(prg_banks.items())),
        "chr_1k_bank_changed_bytes": dict(sorted(chr_banks.items())),
        "records": record_rows,
        "runs": run_rows,
    }


def markdown(result: dict[str, object]) -> str:
    runs = list(result["runs"])
    largest = sorted(runs, key=lambda run: int(run["bytes"]), reverse=True)[:12]
    lines = [
        "# English IPS record/run map",
        "",
        "> This is static structural evidence only. It does not prove a live text pointer or renderer route.",
        "",
        f"- Verified base MD5: `{result['base']['md5']}`",
        f"- Verified IPS SHA-256: `{result['ips']['sha256']}`",
        f"- IPS records: **{result['ips']['records']}**",
        f"- Changed bytes by region: `{result['changed_bytes_by_region']}`",
        f"- Contiguous changed runs: **{len(runs)}**",
        "",
        "## Largest changed runs",
        "",
        "| run | file range | region | physical bank | bytes |",
        "|---:|---|---|---:|---:|",
    ]
    for run in largest:
        bank = "—" if run["physical_bank"] is None else str(run["physical_bank"])
        lines.append(f"| {run['id']} | `0x{run['start']:05X}–0x{run['end_exclusive'] - 1:05X}` | {run['region']} | {bank} | {run['bytes']} |")
    lines += ["", "## Constraint", "", "A Korean target may cite a run ID as structural support. It remains `requires_runtime_proof` until an independent debugger-capable trace demonstrates the actual load/display path.", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path, default=Path("rom/kunio.nes"))
    parser.add_argument("--ips", type=Path, default=Path("reference/technos-samurai-v1/TSe-v10.ips"))
    parser.add_argument("--json-output", type=Path, default=Path("analysis/english_reference_runs.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("analysis/english_reference_runs.md"))
    args = parser.parse_args()
    result = analyze(args.rom, args.ips)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(markdown(result), encoding="utf-8")
    print(json.dumps({"records": result["ips"]["records"], "runs": len(result["runs"]), "changed": result["changed_bytes_by_region"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
