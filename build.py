#!/usr/bin/env python3
"""Apply a development IPS candidate to a verified Japanese base ROM."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_IPS = ROOT / "output" / "full_pointer_korean_candidate" / "kunio_period_drama_korean_full_pointer_candidate.ips"
EXPECTED_SIZE = 262_160
EXPECTED_HEADER = bytes.fromhex("4E 45 53 1A 08 10 41 00 00 00 00 00 00 00 00 00")
EXPECTED_MD5 = "0d406a85285b4de8468f0dab6aad5fe5"
DEFAULT_CANDIDATE_MD5 = "0a983c3d8494444935f000963f415253"


def hashes(data: bytes) -> dict[str, str | int]:
    return {
        "size": len(data),
        "crc32": f"{zlib.crc32(data) & 0xFFFFFFFF:08X}",
        "md5": hashlib.md5(data).hexdigest(),
        "sha1": hashlib.sha1(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def apply_ips(base: bytes, patch: bytes) -> bytes:
    if patch[:5] != b"PATCH":
        raise ValueError("IPS header is missing")
    result = bytearray(base)
    pos = 5
    while pos < len(patch):
        if patch[pos : pos + 3] == b"EOF":
            return bytes(result)
        if pos + 5 > len(patch):
            raise ValueError("truncated IPS record")
        offset = int.from_bytes(patch[pos : pos + 3], "big")
        size = int.from_bytes(patch[pos + 3 : pos + 5], "big")
        pos += 5
        if size:
            end = pos + size
            if end > len(patch):
                raise ValueError("truncated IPS payload")
            payload = patch[pos:end]
            pos = end
        else:
            if pos + 3 > len(patch):
                raise ValueError("truncated IPS RLE record")
            rle_size = int.from_bytes(patch[pos : pos + 2], "big")
            value = patch[pos + 2]
            pos += 3
            payload = bytes([value]) * rle_size
        end = offset + len(payload)
        if end > len(result):
            result.extend(b"\x00" * (end - len(result)))
        result[offset:end] = payload
    raise ValueError("IPS EOF marker is missing")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="verified Japanese base ROM")
    parser.add_argument("--output", type=Path, required=True, help="new candidate ROM path")
    parser.add_argument("--ips", type=Path, default=DEFAULT_IPS)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    base_path = args.input if args.input.is_absolute() else ROOT / args.input
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    ips_path = args.ips if args.ips.is_absolute() else ROOT / args.ips
    if not base_path.is_file():
        raise SystemExit(f"base ROM not found: {base_path}")
    if not ips_path.is_file():
        raise SystemExit(f"IPS patch not found: {ips_path}")
    if base_path.resolve() == output_path.resolve():
        raise SystemExit("refusing to overwrite the input ROM")
    if output_path.exists() and not args.force:
        raise SystemExit(f"output exists; use --force to replace: {output_path}")

    base = base_path.read_bytes()
    if len(base) != EXPECTED_SIZE or base[:16] != EXPECTED_HEADER:
        raise SystemExit("base ROM size or iNES header does not match the recorded base")
    base_hashes = hashes(base)
    if base_hashes["md5"] != EXPECTED_MD5:
        raise SystemExit(f"base ROM MD5 mismatch: {base_hashes['md5']}")
    candidate = apply_ips(base, ips_path.read_bytes())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(candidate)
    candidate_hashes = hashes(candidate)
    report_path = args.report or output_path.with_suffix(".build.json")
    report_path = report_path if report_path.is_absolute() else ROOT / report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "base": {"path": str(base_path), **base_hashes},
        "ips": {"path": str(ips_path), **hashes(ips_path.read_bytes())},
        "candidate": {"path": str(output_path), **candidate_hashes},
        "default_candidate_hash_match": candidate_hashes["md5"] == DEFAULT_CANDIDATE_MD5,
        "development_status": "NOT_READY",
        "distribution": "IPS patch only; original and candidate ROMs are local artifacts",
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
