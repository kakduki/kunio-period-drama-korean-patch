#!/usr/bin/env python3
"""Standalone IPS applier for the ROM-free test release bundle."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


EXPECTED_BASE_MD5 = "0d406a85285b4de8468f0dab6aad5fe5"
DEFAULT_IPS = "kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.ips"
KNOWN_PATCHES = {
    "kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.ips": {
        "label": "v0.4.2 font-expanded primary manual-test patch",
        "expected_md5": "ea11dc002a1a7b07682ce00a754b1a61",
        "default_output": "kunio_period_drama_korean_v0.4.2_test_applied.nes",
    },
    "kunio_period_drama_korean_prg_plan_v0.4.3_broad_preview_unverified.ips": {
        "label": "v0.4.3 broad preview, unverified manual-screen-test patch",
        "expected_md5": "f9a990581775963bc9d4875cada8ae10",
        "default_output": "kunio_period_drama_korean_v0.4.3_broad_preview_unverified.nes",
    },
}


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_rom", help="Path to your legally obtained Japanese base .nes ROM.")
    parser.add_argument("--ips", default=DEFAULT_IPS, help="IPS patch path. Defaults to the bundled v0.4.2 IPS.")
    parser.add_argument("--output", help="Patched ROM output path. Defaults depend on the selected IPS.")
    parser.add_argument("--force", action="store_true", help="Overwrite output file if it already exists.")
    args = parser.parse_args()

    base_path = Path(args.base_rom).expanduser().resolve()
    ips_path = Path(args.ips).expanduser()
    if not ips_path.is_absolute():
        ips_path = Path.cwd() / ips_path
    ips_path = ips_path.resolve()
    patch_info = KNOWN_PATCHES.get(ips_path.name)
    if patch_info is None:
        known = ", ".join(sorted(KNOWN_PATCHES))
        print(f"ERROR: unknown bundled IPS {ips_path.name!r}. Known IPS files: {known}")
        return 1

    output_default = str(patch_info["default_output"])
    output_path = Path(args.output or output_default).expanduser()
    if not output_path.is_absolute():
        output_path = Path.cwd() / output_path
    output_path = output_path.resolve()

    base = base_path.read_bytes()
    base_md5 = md5_bytes(base)
    patched = apply_ips(base, ips_path)
    patched_md5 = md5_bytes(patched)

    print(f"base_rom={base_path}")
    print(f"ips={ips_path}")
    print(f"patch_label={patch_info['label']}")
    print(f"output={output_path}")
    print(f"expected_base_md5={EXPECTED_BASE_MD5}")
    print(f"actual_base_md5={base_md5}")
    print(f"expected_patched_md5={patch_info['expected_md5']}")
    print(f"actual_patched_md5={patched_md5}")

    if base_md5 != EXPECTED_BASE_MD5:
        print("ERROR: base ROM MD5 does not match the expected Japanese ROM.")
        return 1
    if patched_md5 != patch_info["expected_md5"]:
        print("ERROR: applied IPS MD5 does not match the expected test patch.")
        return 1
    if output_path.exists() and not args.force:
        print("ERROR: output already exists. Pass --force to overwrite it.")
        return 1

    output_path.write_bytes(patched)
    print("OK: patched ROM written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
