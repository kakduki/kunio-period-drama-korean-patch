#!/usr/bin/env python3
"""Package the current primary IPS as a ROM-free test release bundle."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

from rom_utils import REPO_ROOT


MANIFEST_JSON = REPO_ROOT / "rom_analysis" / "patch_candidate_manifest.json"
MANIFEST_MD = REPO_ROOT / "rom_analysis" / "patch_candidate_manifest.md"
DECISION_MATRIX_JSON = REPO_ROOT / "rom_analysis" / "patch_decision_matrix.json"
DECISION_MATRIX_MD = REPO_ROOT / "rom_analysis" / "patch_decision_matrix.md"
MANUAL_CAPTURE_CARDS_JSON = REPO_ROOT / "rom_analysis" / "manual_capture_cards.json"
MANUAL_CAPTURE_CARDS_MD = REPO_ROOT / "rom_analysis" / "manual_capture_cards.md"
MANUAL_CAPTURE_STATUS_JSON = REPO_ROOT / "rom_analysis" / "manual_capture_status.json"
MANUAL_CAPTURE_STATUS_MD = REPO_ROOT / "rom_analysis" / "manual_capture_status.md"
STANDALONE_APPLIER = REPO_ROOT / "scripts" / "apply_ips_standalone.py"
RELEASE_ROOT = REPO_ROOT / "release"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def safe_copy(src: Path, dst: Path) -> None:
    if src.suffix.lower() in {".nes", ".zip"}:
        raise ValueError(f"Release bundle must not include ROM/ZIP input artifact: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def write_release_readme(path: Path, summary: dict[str, object], ips_name: str) -> None:
    lines = [
        "# Kunio Period Drama Korean Patch v0.4.1 Test",
        "",
        "This is an incomplete manual-test IPS bundle, not a final release.",
        "",
        "## Files",
        "",
        f"- `{ips_name}`: primary IPS patch",
        "- `patch_candidate_manifest.md`: candidate status and verification notes",
        "- `patch_decision_matrix.md`: next manual verification priorities",
        "- `manual_capture_cards.md`: short FCEUX tasks to avoid blind autoplay loops",
        "- `manual_capture_status.md`: generated status of manual dump evidence",
        "- `apply_ips_standalone.py`: standalone IPS applier for this bundle",
        "- `SHA256SUMS.txt`: checksums for bundle files",
        "",
        "## Required Base ROM",
        "",
        f"- Expected base MD5: `{summary['base_md5']}`",
        "- Use your own legally obtained Japanese ROM.",
        "- Do not distribute ROM files.",
        "",
        "## Expected Result",
        "",
        f"- Primary candidate: **{summary['primary_candidate']}**",
        f"- Expected patched MD5: `{summary['primary_candidate_md5']}`",
        "",
        "## Apply In Repository",
        "",
        "From the repository root, after putting your base ROM in `rom/`:",
        "",
        "```powershell",
        "python scripts/apply_primary_patch.py --output output/kunio_period_drama_korean_v0.4.1_test_applied.nes",
        "```",
        "",
        "## Apply From This Bundle Only",
        "",
        "From inside this extracted bundle folder:",
        "",
        "```powershell",
        "python apply_ips_standalone.py C:\\path\\to\\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes",
        "```",
        "",
        "## Verify In Repository",
        "",
        "From the repository root:",
        "",
        "```powershell",
        "python scripts/verify_primary_patch.py",
        "python scripts/run_project_checks.py",
        "```",
        "",
        "## Current Limitations",
        "",
        "- Still needs manual FCEUX screen verification.",
        "- v0.4 broad-scan conflicts are intentionally excluded from this v0.4.1 candidate.",
        "- Padding/shortened replacements are not included.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def package() -> dict[str, object]:
    manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    summary = manifest["summary"]
    primary_name = str(summary["primary_candidate"]).replace(" ", "_").replace(".", "_")
    bundle_dir = RELEASE_ROOT / f"kunio_period_drama_korean_{primary_name}_test"
    zip_path = RELEASE_ROOT / f"{bundle_dir.name}.zip"

    if bundle_dir.parent != RELEASE_ROOT:
        raise ValueError(f"Unexpected release bundle path: {bundle_dir}")
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir(parents=True, exist_ok=True)

    ips_path = REPO_ROOT / str(summary["primary_ips"])
    if ips_path.suffix.lower() != ".ips":
        raise ValueError(f"Primary patch is not an IPS file: {ips_path}")

    copied_files = []
    for src, name in [
        (ips_path, ips_path.name),
        (MANIFEST_MD, "patch_candidate_manifest.md"),
        (MANIFEST_JSON, "patch_candidate_manifest.json"),
        (DECISION_MATRIX_MD, "patch_decision_matrix.md"),
        (DECISION_MATRIX_JSON, "patch_decision_matrix.json"),
        (MANUAL_CAPTURE_CARDS_MD, "manual_capture_cards.md"),
        (MANUAL_CAPTURE_CARDS_JSON, "manual_capture_cards.json"),
        (MANUAL_CAPTURE_STATUS_MD, "manual_capture_status.md"),
        (MANUAL_CAPTURE_STATUS_JSON, "manual_capture_status.json"),
        (STANDALONE_APPLIER, "apply_ips_standalone.py"),
    ]:
        dst = bundle_dir / name
        safe_copy(src, dst)
        copied_files.append(dst)

    readme_path = bundle_dir / "README.md"
    write_release_readme(readme_path, summary, ips_path.name)
    copied_files.append(readme_path)

    checksums_path = bundle_dir / "SHA256SUMS.txt"
    checksum_lines = [f"{sha256(path)}  {path.name}" for path in sorted(copied_files, key=lambda p: p.name)]
    checksums_path.write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    copied_files.append(checksums_path)

    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(bundle_dir.iterdir(), key=lambda p: p.name):
            if path.suffix.lower() in {".nes"}:
                raise ValueError(f"Refusing to zip ROM file: {path}")
            archive.write(path, arcname=f"{bundle_dir.name}/{path.name}")

    report = {
        "bundle_dir": str(bundle_dir.relative_to(REPO_ROOT)),
        "zip_path": str(zip_path.relative_to(REPO_ROOT)),
        "zip_size": zip_path.stat().st_size,
        "zip_md5": md5(zip_path),
        "primary_ips": str(ips_path.relative_to(REPO_ROOT)),
        "primary_candidate": summary["primary_candidate"],
        "primary_candidate_md5": summary["primary_candidate_md5"],
        "base_md5": summary["base_md5"],
        "files": [str(path.relative_to(REPO_ROOT)) for path in sorted(copied_files, key=lambda p: p.name)],
    }
    report_path = bundle_dir / "release_manifest.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return report


def main() -> int:
    report = package()
    print(f"bundle_dir={report['bundle_dir']}")
    print(f"zip_path={report['zip_path']}")
    print(f"zip_md5={report['zip_md5']}")
    print(f"zip_size={report['zip_size']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
