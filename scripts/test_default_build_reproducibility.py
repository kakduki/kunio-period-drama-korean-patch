#!/usr/bin/env python3
"""Verify the default build uses a tracked patch and is reproducible."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "rom" / "Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes"
TRACKED_IPS = ROOT / "patches" / "kunio_period_drama_korean_development.ips"
EXPECTED_CANDIDATE_MD5 = "0a983c3d8494444935f000963f415253"
MANIFEST = ROOT / "translation" / "script.csv"


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def main() -> int:
    if not BASE.is_file():
        print(f"SKIP: base ROM not available: {BASE}")
        return 0
    if not TRACKED_IPS.is_file():
        print(f"ERROR: tracked default IPS is missing: {TRACKED_IPS}")
        return 1

    with tempfile.TemporaryDirectory(prefix="kunio_default_build_") as temp:
        temp_dir = Path(temp)
        output = temp_dir / "candidate.nes"
        patch = temp_dir / "candidate.ips"
        report = temp_dir / "candidate.json"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "build.py"),
                "--input",
                str(BASE),
                "--output",
                str(output),
                "--patch-output",
                str(patch),
                "--report",
                str(report),
                "--force",
            ],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        payload = json.loads(report.read_text(encoding="utf-8"))
        assert payload["input_ips"]["path"].replace("\\", "/").endswith(
            "patches/kunio_period_drama_korean_development.ips"
        )
        assert md5(output) == EXPECTED_CANDIDATE_MD5
        assert payload["candidate"]["md5"] == EXPECTED_CANDIDATE_MD5

        manifest_output = temp_dir / "manifest.nes"
        manifest_report = temp_dir / "manifest.json"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "build.py"),
                "--input",
                str(BASE),
                "--manifest",
                str(MANIFEST),
                "--output",
                str(manifest_output),
                "--report",
                str(manifest_report),
                "--force",
            ],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        manifest_payload = json.loads(manifest_report.read_text(encoding="utf-8"))
        assert manifest_payload["source"]["candidate_source"] == (
            "tools/insert_text.py --manifest translation/script.csv"
        )
        assert "manifest_build_" not in json.dumps(manifest_payload)
        assert manifest_output.is_file()

    print("OK: default build uses the tracked IPS and reproduces the candidate hash")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
