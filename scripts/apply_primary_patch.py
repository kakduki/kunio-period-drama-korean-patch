#!/usr/bin/env python3
"""Apply the current primary IPS to a user-provided base ROM."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rom_utils import REPO_ROOT, find_rom_path
from verify_primary_patch import apply_ips


MANIFEST = REPO_ROOT / "rom_analysis" / "patch_candidate_manifest.json"
DEFAULT_OUTPUT = REPO_ROOT / "output" / "kunio_period_drama_korean_v0.4.1_test_applied.nes"


def md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def resolve_repo_path(raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", nargs="?", help="Base .nes ROM path; defaults to first rom/*.nes.")
    parser.add_argument("--manifest", default=str(MANIFEST), help="Patch candidate manifest to read.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Patched ROM output path.")
    parser.add_argument("--dry-run", action="store_true", help="Verify hashes without writing the patched ROM.")
    parser.add_argument("--force", action="store_true", help="Overwrite output file if it already exists.")
    args = parser.parse_args()

    manifest_path = Path(args.manifest).expanduser().resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    summary = manifest["summary"]

    base_path = find_rom_path(args.rom).resolve()
    output_path = Path(args.output).expanduser()
    if not output_path.is_absolute():
        output_path = REPO_ROOT / output_path
    output_path = output_path.resolve()
    ips_path = resolve_repo_path(str(summary["primary_ips"])).resolve()

    base = base_path.read_bytes()
    base_md5 = md5_bytes(base)
    expected_base = str(summary["base_md5"])
    expected_patched = str(summary["primary_candidate_md5"])
    patched = apply_ips(base, ips_path)
    patched_md5 = md5_bytes(patched)

    print(f"base_rom={base_path}")
    print(f"primary_ips={ips_path}")
    print(f"output={output_path}")
    print(f"expected_base_md5={expected_base}")
    print(f"actual_base_md5={base_md5}")
    print(f"expected_patched_md5={expected_patched}")
    print(f"actual_patched_md5={patched_md5}")

    if base_md5 != expected_base:
        print("ERROR: base ROM MD5 does not match the expected Japanese ROM.")
        return 1
    if patched_md5 != expected_patched:
        print("ERROR: applied IPS MD5 does not match the manifest.")
        return 1

    if args.dry_run:
        print("OK: dry run passed; patched ROM was not written.")
        return 0

    if output_path.exists() and not args.force:
        print("ERROR: output already exists. Pass --force to overwrite it.")
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(patched)
    print("OK: patched ROM written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
