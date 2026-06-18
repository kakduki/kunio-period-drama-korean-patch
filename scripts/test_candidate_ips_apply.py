#!/usr/bin/env python3
"""Verify soft-gate IPS files apply cleanly to the clean base ROM."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from apply_ips_standalone import apply_ips
from rom_utils import REPO_ROOT


CANDIDATE_REPORTS = sorted((REPO_ROOT / "output").glob("kunio_period_drama_softgate_*_report.json"))


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def main() -> int:
    errors: list[str] = []
    if not CANDIDATE_REPORTS:
        errors.append("no softgate candidate reports found; run scripts/build_candidate_pipeline.py first")

    for report_path in CANDIDATE_REPORTS:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        build_id = str(report.get("build_id", report_path.stem))
        if report.get("build_status") != "PASS":
            continue

        base_path = REPO_ROOT / str(report["base_rom"])
        candidate_rom = REPO_ROOT / str(report["candidate_rom"])
        candidate_ips = REPO_ROOT / str(report["candidate_ips"])
        expected_md5 = str(report["candidate_md5"])

        missing = False
        for path, label in [(base_path, "base ROM"), (candidate_rom, "candidate ROM"), (candidate_ips, "candidate IPS")]:
            if not path.is_file():
                errors.append(f"{build_id}: missing {label}: {path.relative_to(REPO_ROOT).as_posix()}")
                missing = True
        if missing:
            continue

        applied = apply_ips(base_path.read_bytes(), candidate_ips)
        applied_md5 = md5(applied)
        actual_candidate_md5 = md5(candidate_rom.read_bytes())

        if applied_md5 != expected_md5:
            errors.append(f"{build_id}: applied IPS MD5 {applied_md5} != report candidate MD5 {expected_md5}")
        if actual_candidate_md5 != expected_md5:
            errors.append(f"{build_id}: candidate ROM MD5 {actual_candidate_md5} != report candidate MD5 {expected_md5}")
        if applied != candidate_rom.read_bytes():
            errors.append(f"{build_id}: applied IPS bytes differ from candidate ROM bytes")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {len(CANDIDATE_REPORTS)} softgate IPS files apply cleanly from the base ROM")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
