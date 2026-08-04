#!/usr/bin/env python3
"""Build a development candidate from a verified base and an independent source."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
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


def changed_records(original: bytes, patched: bytes) -> list[tuple[int, bytes]]:
    records: list[tuple[int, bytes]] = []
    index = 0
    while index < len(patched):
        if index < len(original) and original[index] == patched[index]:
            index += 1
            continue
        start = index
        payload = bytearray()
        while index < len(patched) and (index >= len(original) or original[index] != patched[index]):
            payload.append(patched[index])
            index += 1
        records.append((start, bytes(payload)))
    return records


def write_ips(path: Path, records: list[tuple[int, bytes]]) -> None:
    with path.open("wb") as handle:
        handle.write(b"PATCH")
        for offset, data in records:
            for chunk_start in range(0, len(data), 0xFFFF):
                chunk = data[chunk_start : chunk_start + 0xFFFF]
                handle.write(struct.pack(">I", offset + chunk_start)[1:])
                handle.write(struct.pack(">H", len(chunk)))
                handle.write(chunk)
        handle.write(b"EOF")


def resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def manifest_candidate(base_path: Path, manifest_path: Path) -> tuple[bytes, dict[str, object]]:
    build_root = ROOT / "build"
    build_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="manifest_build_", dir=build_root) as temp:
        output_dir = Path(temp)
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "insert_text.py"),
                "--rom",
                str(base_path),
                "--manifest",
                str(manifest_path),
                "--output-dir",
                str(output_dir),
            ],
            cwd=ROOT,
            check=True,
        )
        candidates = sorted(output_dir.glob("*.nes"))
        if len(candidates) != 1:
            raise RuntimeError(f"manifest build expected one candidate, found {len(candidates)}")
        return candidates[0].read_bytes(), {
            "mode": "translation_manifest",
            "manifest": str(manifest_path),
            "candidate_source": str(candidates[0]),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="verified Japanese base ROM")
    parser.add_argument("--output", type=Path, required=True, help="new candidate ROM path")
    parser.add_argument("--ips", type=Path, default=DEFAULT_IPS)
    parser.add_argument("--manifest", type=Path, help="optional translation/script.csv build source")
    parser.add_argument("--patch-output", type=Path, help="optional IPS generated from input to output")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    base_path = resolve_path(args.input).resolve()
    output_path = resolve_path(args.output).resolve()
    ips_path = resolve_path(args.ips).resolve()
    manifest_path = resolve_path(args.manifest).resolve() if args.manifest else None
    patch_output = resolve_path(args.patch_output).resolve() if args.patch_output else None
    if not base_path.is_file():
        raise SystemExit(f"base ROM not found: {base_path}")
    if manifest_path is None and not ips_path.is_file():
        raise SystemExit(f"IPS patch not found: {ips_path}")
    if manifest_path is not None and not manifest_path.is_file():
        raise SystemExit(f"translation manifest not found: {manifest_path}")
    if base_path == output_path or (patch_output is not None and patch_output == base_path):
        raise SystemExit("refusing to write over the input ROM")
    if output_path.exists() and not args.force:
        raise SystemExit(f"output exists; use --force: {output_path}")
    if patch_output is not None and patch_output.exists() and not args.force:
        raise SystemExit(f"patch output exists; use --force: {patch_output}")

    base = base_path.read_bytes()
    if len(base) != EXPECTED_SIZE or base[:16] != EXPECTED_HEADER:
        raise SystemExit("base ROM size or iNES header does not match the recorded base")
    base_hashes = hashes(base)
    if base_hashes["md5"] != EXPECTED_MD5:
        raise SystemExit(f"base ROM MD5 mismatch: {base_hashes['md5']}")

    if manifest_path is not None:
        candidate, source_report = manifest_candidate(base_path, manifest_path)
        input_ips_report = None
    else:
        input_patch = ips_path.read_bytes()
        candidate = apply_ips(base, input_patch)
        source_report = {"mode": "ips", "candidate_source": str(ips_path)}
        input_ips_report = {"path": str(ips_path), **hashes(input_patch)}

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(candidate)
    candidate_hashes = hashes(candidate)

    patch_report: dict[str, object] | None = None
    if patch_output is not None:
        records = changed_records(base, candidate)
        patch_output.parent.mkdir(parents=True, exist_ok=True)
        write_ips(patch_output, records)
        patch_bytes = patch_output.read_bytes()
        patch_report = {
            "path": str(patch_output),
            **hashes(patch_bytes),
            "records": len(records),
            "source": "generated from the verified Japanese base and candidate bytes",
        }

    report_path = resolve_path(args.report) if args.report else output_path.with_suffix(".build.json")
    report_path = report_path.resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "base": {"path": str(base_path), **base_hashes},
        "source": source_report,
        "input_ips": input_ips_report,
        "candidate": {"path": str(output_path), **candidate_hashes},
        "generated_patch": patch_report,
        "default_candidate_hash_match": candidate_hashes["md5"] == DEFAULT_CANDIDATE_MD5,
        "development_status": "NOT_READY",
        "distribution": "IPS patch only; original and candidate ROMs are local artifacts",
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())