#!/usr/bin/env python3
"""Verify that the broad preview IPS applies to the expected base ROM."""

from __future__ import annotations

import hashlib
from pathlib import Path

from rom_utils import REPO_ROOT, find_rom_path
from verify_primary_patch import apply_ips


BASE_MD5 = "0d406a85285b4de8468f0dab6aad5fe5"
PREVIEW_MD5 = "f9a990581775963bc9d4875cada8ae10"
PREVIEW_IPS = REPO_ROOT / "output" / "kunio_period_drama_korean_prg_plan_v0.4.3_broad_preview_unverified.ips"


def md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def main() -> int:
    rom_path = find_rom_path(None).resolve()
    base = rom_path.read_bytes()
    base_md5 = md5_bytes(base)
    preview_md5 = md5_bytes(apply_ips(base, PREVIEW_IPS))

    print(f"base_rom={rom_path}")
    print(f"preview_ips={PREVIEW_IPS}")
    print(f"expected_base_md5={BASE_MD5}")
    print(f"actual_base_md5={base_md5}")
    print(f"expected_preview_md5={PREVIEW_MD5}")
    print(f"actual_preview_md5={preview_md5}")

    if base_md5 != BASE_MD5:
        print("ERROR: base ROM MD5 does not match the expected Japanese ROM.")
        return 1
    if preview_md5 != PREVIEW_MD5:
        print("ERROR: preview IPS output MD5 does not match the expected unverified preview.")
        return 1

    print("OK: broad preview IPS applies cleanly and matches the expected preview MD5.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
