#!/usr/bin/env python3
"""Verify that the primary IPS applies cleanly to the expected base ROM."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rom_utils import REPO_ROOT, find_rom_path


MANIFEST = REPO_ROOT / "rom_analysis" / "patch_candidate_manifest.json"


def md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def apply_ips(base: bytes, ips_path: Path) -> bytes:
    patch = ips_path.read_bytes()
    if not patch.startswith(b"PATCH"):
        raise ValueError(f"Not an IPS patch: {ips_path}")

    result = bytearray(base)
    pos = 5
    while pos < len(patch):
        if patch[pos : pos + 3] == b"EOF":
            pos += 3
            if pos != len(patch):
                raise ValueError(f"Trailing bytes after IPS EOF: {ips_path}")
            return bytes(result)

        if pos + 5 > len(patch):
            raise ValueError(f"Truncated IPS record header: {ips_path}")
        offset = int.from_bytes(patch[pos : pos + 3], "big")
        pos += 3
        size = int.from_bytes(patch[pos : pos + 2], "big")
        pos += 2

        if size == 0:
            if pos + 3 > len(patch):
                raise ValueError(f"Truncated IPS RLE record: {ips_path}")
            rle_size = int.from_bytes(patch[pos : pos + 2], "big")
            pos += 2
            value = patch[pos]
            pos += 1
            end = offset + rle_size
            if end > len(result):
                raise ValueError(f"IPS RLE record exceeds ROM size: {ips_path}")
            result[offset:end] = bytes([value]) * rle_size
            continue

        end_pos = pos + size
        end = offset + size
        if end_pos > len(patch):
            raise ValueError(f"Truncated IPS data record: {ips_path}")
        if end > len(result):
            raise ValueError(f"IPS data record exceeds ROM size: {ips_path}")
        result[offset:end] = patch[pos:end_pos]
        pos = end_pos

    raise ValueError(f"IPS patch missing EOF marker: {ips_path}")


def resolve_repo_path(raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?", help="Base .nes ROM path; defaults to rom/*.nes")
    parser.add_argument("--manifest", default=str(MANIFEST))
    args = parser.parse_args()

    manifest_path = Path(args.manifest).expanduser().resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    summary = manifest["summary"]

    rom_path = find_rom_path(args.rom).resolve()
    ips_path = resolve_repo_path(str(summary["primary_ips"])).resolve()
    expected_base = str(summary["base_md5"])
    expected_patched = str(summary["primary_candidate_md5"])

    base = rom_path.read_bytes()
    base_md5 = md5_bytes(base)
    patched_md5 = md5_bytes(apply_ips(base, ips_path))

    print(f"base_rom={rom_path}")
    print(f"primary_ips={ips_path}")
    print(f"expected_base_md5={expected_base}")
    print(f"actual_base_md5={base_md5}")
    print(f"expected_patched_md5={expected_patched}")
    print(f"actual_patched_md5={patched_md5}")

    ok = True
    if base_md5 != expected_base:
        print("ERROR: base ROM MD5 does not match the expected Japanese ROM.")
        ok = False
    if patched_md5 != expected_patched:
        print("ERROR: applied IPS MD5 does not match the primary candidate.")
        ok = False

    if ok:
        print("OK: primary IPS applies cleanly and matches the manifest.")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
