#!/usr/bin/env python3
"""Verify the tracked eight-row candidate manifest and IPS are reproducible."""

from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "rom" / "Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes"
MANIFEST = ROOT / "translation" / "script_manifest_p182_p189_candidate.csv"
IPS = ROOT / "patches" / "kunio_period_drama_korean_manifest_p182_p189_candidate.ips"
EXPECTED_CANDIDATE_MD5 = "e0b450a50083dc9dc67aee10af9d130d"
EXPECTED_IPS_SHA256 = "d1ff5e14a1829f06e93eff7c76fbe28dc3de9bd18545830e0d64898aeff03e35"
sys.path.insert(0, str(ROOT / "scripts"))
from apply_ips_standalone import apply_ips  # noqa: E402


def digest(path: Path, algorithm: str) -> str:
    return hashlib.new(algorithm, path.read_bytes()).hexdigest()


def main() -> int:
    for path in (BASE, MANIFEST, IPS):
        if not path.is_file():
            raise SystemExit(f"missing candidate input: {path}")
    if digest(IPS, "sha256") != EXPECTED_IPS_SHA256:
        raise SystemExit("tracked eight-row IPS hash changed")
    with tempfile.TemporaryDirectory(prefix="kunio_manifest_candidate_") as temp:
        root = Path(temp)
        candidate = root / "candidate.nes"
        report = root / "candidate.json"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "build.py"),
                "--input",
                str(BASE),
                "--manifest",
                str(MANIFEST),
                "--output",
                str(candidate),
                "--report",
                str(report),
                "--force",
            ],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        if digest(candidate, "md5") != EXPECTED_CANDIDATE_MD5:
            raise SystemExit("tracked eight-row manifest build hash changed")
        patched = apply_ips(BASE.read_bytes(), IPS)
        if hashlib.md5(patched).hexdigest() != EXPECTED_CANDIDATE_MD5:
            raise SystemExit("tracked eight-row IPS does not reproduce candidate")
    print("OK: tracked eight-row manifest and IPS reproduce the candidate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())