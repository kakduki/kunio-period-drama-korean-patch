#!/usr/bin/env python3
"""Generate a readable contents report for the current primary patch."""

from __future__ import annotations

import json
from pathlib import Path

from readable_labels import readable_for_romaji
from rom_utils import REPO_ROOT


BUILD_REPORT = REPO_ROOT / "output" / "kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded_build_report.json"
MANIFEST = REPO_ROOT / "rom_analysis" / "patch_candidate_manifest.json"
INVENTORY = REPO_ROOT / "rom_analysis" / "bank1_offset_inventory.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "primary_patch_contents.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "primary_patch_contents.md"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path | str) -> str:
    path = Path(path)
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return path.name


def inventory_by_rom_hit() -> dict[str, dict[str, object]]:
    data = load_json(INVENTORY)
    return {str(row["rom_hit"]).upper(): row for row in data.get("targets", [])}


def classify_manual_status(evidence_level: str) -> str:
    if evidence_level == "runtime-confirmed":
        return "runtime read confirmed; still needs visual screen review"
    if evidence_level == "encoding-exact":
        return "PPU/text-sequence evidence; needs visual screen review"
    return "static candidate; needs manual screen proof"


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    report = load_json(BUILD_REPORT)
    manifest = load_json(MANIFEST)
    inventory = inventory_by_rom_hit()

    rows: list[dict[str, object]] = []
    for index, row in enumerate(report.get("applied", []), start=1):
        rom_hit = str(row["rom_hit"]).upper()
        inv = inventory.get(rom_hit, {})
        romaji = str(inv.get("source_romaji") or "")
        if not romaji:
            # The v0.4.2 build applies one row at 0x07227 outside the narrow
            # supplemental inventory table; the label identifies it as Katana.
            if rom_hit == "0X07227":
                romaji = "Katana"
            elif "0736" in rom_hit or "0739" in rom_hit:
                romaji = "Raifu"
        display = readable_for_romaji(romaji)
        evidence = str(row.get("evidence_level", ""))
        rows.append(
            {
                "index": index,
                "rom_hit": rom_hit.replace("0X", "0x"),
                "label": row.get("label", ""),
                "romaji": romaji or "unknown",
                "source_display": display.get("source_display", ""),
                "korean_display": display.get("korean_display", ""),
                "meaning": display.get("meaning", ""),
                "old_bytes": row.get("old_bytes", ""),
                "new_bytes": row.get("new_bytes", ""),
                "evidence_level": evidence,
                "risk": row.get("risk", ""),
                "manual_status": classify_manual_status(evidence),
                "category_group": inv.get("category_group", ""),
                "record_rom_range": inv.get("record_rom_range", []),
                "record_cpu_range": inv.get("record_cpu_range", []),
            }
        )

    summary = {
        "primary_candidate": manifest["summary"]["primary_candidate"],
        "primary_ips": manifest["summary"]["primary_ips"],
        "base_md5": manifest["summary"]["base_md5"],
        "primary_candidate_md5": manifest["summary"]["primary_candidate_md5"],
        "build_report": rel(BUILD_REPORT),
        "applied_count": len(rows),
        "runtime_confirmed_count": sum(1 for row in rows if row["evidence_level"] == "runtime-confirmed"),
        "ppu_or_encoding_evidence_count": sum(1 for row in rows if row["evidence_level"] == "encoding-exact"),
        "static_candidate_count": sum(1 for row in rows if str(row["evidence_level"]).startswith("static-candidate")),
        "changed_bytes_total": report.get("changed_bytes_total"),
        "ips_records": report.get("ips_records"),
        "manual_verification_required": True,
    }
    return rows, summary


def write_outputs(rows: list[dict[str, object]], summary: dict[str, object]) -> None:
    payload = {
        "summary": summary,
        "applied_rows": rows,
        "warnings": [
            "This is a manual-test patch report, not final release approval.",
            "Rows marked static candidate still need direct FCEUX screen proof.",
            "v0.4 broad-scan conflicts and shortened padding-risk rows are intentionally excluded.",
            "YouTube footage can help scene order/transcription, but exact ROM offsets still require ROM/runtime evidence.",
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Primary Patch Contents",
        "",
        "This report explains what the current primary IPS changes, without bundling any ROM data.",
        "",
        "## Summary",
        "",
        f"- Primary candidate: **{summary['primary_candidate']}**",
        f"- Primary IPS: `{summary['primary_ips']}`",
        f"- Base ROM MD5: `{summary['base_md5']}`",
        f"- Expected patched MD5: `{summary['primary_candidate_md5']}`",
        f"- Applied text rows: **{summary['applied_count']}**",
        f"- Runtime-confirmed rows: **{summary['runtime_confirmed_count']}**",
        f"- PPU/encoding-evidence rows: **{summary['ppu_or_encoding_evidence_count']}**",
        f"- Static candidate rows: **{summary['static_candidate_count']}**",
        f"- Total changed bytes versus base ROM: **{summary['changed_bytes_total']}**",
        f"- IPS records: **{summary['ips_records']}**",
        "",
        "## Applied Text Rows",
        "",
        "| # | ROM offset | romaji | human hint | source | Korean | old bytes | new bytes | evidence | manual status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        source = row["source_display"] or "-"
        korean = row["korean_display"] or "-"
        display_row = dict(row)
        display_row["meaning"] = row["meaning"] or "-"
        display_row["source"] = source
        display_row["korean"] = korean
        lines.append(
            "| {index} | `{rom_hit}` | {romaji} | {meaning} | {source} | {korean} | `{old_bytes}` | `{new_bytes}` | {evidence_level} | {manual_status} |".format(
                **display_row,
            )
        )

    lines += [
        "",
        "## Notes",
        "",
        "- The primary candidate is still for manual testing, not a final release.",
        "- Rows with runtime or PPU evidence still need visible-screen confirmation in FCEUX.",
        "- Static rows should be treated as hypotheses until their exact screen is reached and dumped.",
        "- Shortened replacements and broad-scan conflicts are excluded from v0.4.2 on purpose.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows, summary = build_rows()
    write_outputs(rows, summary)
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(
        "applied={applied_count} runtime={runtime_confirmed_count} encoding={ppu_or_encoding_evidence_count} static={static_candidate_count}".format(
            **summary
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
