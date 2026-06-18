#!/usr/bin/env python3
"""Generate a compact report for the v0.4.2 auto-input capture evidence."""

from __future__ import annotations

import json
from pathlib import Path

from rom_utils import REPO_ROOT


SUMMARY_JSON = REPO_ROOT / "rom_analysis" / "fceux_input_explorer_v042" / "summary.json"
REVIEW_CROPS_JSON = REPO_ROOT / "rom_analysis" / "fceux_input_explorer_v042" / "review_crops.json"
PRIMARY_VISUAL_JSON = REPO_ROOT / "rom_analysis" / "primary_visual_checklist.json"
OUT_JSON = REPO_ROOT / "rom_analysis" / "auto_input_evidence_report.json"
OUT_MD = REPO_ROOT / "rom_analysis" / "auto_input_evidence_report.md"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path_text: str) -> str:
    return path_text.replace("\\", "/")


def visual_rows_by_rom() -> dict[str, dict[str, object]]:
    data = load_json(PRIMARY_VISUAL_JSON)
    result = {}
    for row in data.get("rows", []):
        if isinstance(row, dict):
            result[str(row.get("rom_hit", ""))] = row
    return result


def normalize_rom(value: object) -> str:
    text = str(value or "").replace("ROM+", "").strip()
    if text.lower().startswith("0x"):
        return f"0x{int(text, 16):05X}"
    return text


def make_payload() -> dict[str, object]:
    summary = load_json(SUMMARY_JSON)
    review_crops = load_json(REVIEW_CROPS_JSON) if REVIEW_CROPS_JSON.exists() else {"crops": []}
    visual_rows = visual_rows_by_rom()
    latest_png = rel(str(summary.get("latest_png_review_image", "")))
    latest_stem = Path(latest_png).stem
    latest_crops = [
        crop for crop in review_crops.get("crops", [])
        if isinstance(crop, dict) and Path(str(crop.get("path", ""))).stem.startswith(latest_stem)
    ]
    matched_rows = []
    for match in summary.get("active_matches", []):
        if not isinstance(match, dict):
            continue
        rom_hit = normalize_rom(match.get("rom_hit"))
        visual = visual_rows.get(rom_hit, {})
        matched_rows.append(
            {
                "rom_hit": rom_hit,
                "romaji": visual.get("romaji", ""),
                "meaning": visual.get("meaning", ""),
                "evidence_level": visual.get("evidence_level", ""),
                "screen_hint": visual.get("screen_hint", ""),
                "cpu_range": match.get("cpu_range", ""),
                "expected_bytes": match.get("expected_bytes", ""),
                "record_snapshot": match.get("record_snapshot", ""),
                "review_status": visual.get("review_status", ""),
            }
        )
    matched_rows.sort(key=lambda row: str(row["rom_hit"]))

    return {
        "source": rel(str(SUMMARY_JSON.relative_to(REPO_ROOT))),
        "summary": {
            "frame": summary.get("frame"),
            "targets_checked": summary.get("targets_checked"),
            "active_expected_matches": summary.get("active_expected_matches"),
            "matched_primary_rows": len(matched_rows),
            "latest_screenshot": rel(str(summary.get("latest_screenshot", ""))),
            "latest_png_review_image": latest_png,
            "review_crops": rel(str(REVIEW_CROPS_JSON.relative_to(REPO_ROOT))) if REVIEW_CROPS_JSON.exists() else "",
            "latest_crop_count": len(latest_crops),
            "latest_meta": rel(str(summary.get("latest_meta", ""))),
            "route_note": summary.get("visual_route_note", ""),
            "current_limit": (
                "This proves the scripted route reached an in-game dialogue screen and loaded the expected "
                "patched byte sequences into CPU memory. It does not by itself prove the final Korean glyphs "
                "are visually correct."
            ),
        },
        "latest_crops": latest_crops,
        "matched_rows": matched_rows,
    }


def write_markdown(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    lines = [
        "# Auto-Input Evidence Report",
        "",
        "This report ties the v0.4.2 scripted FCEUX route to its review image and active byte matches.",
        "",
        "## Summary",
        "",
        f"- Frame: **{summary['frame']}**",
        f"- Targets checked: **{summary['targets_checked']}**",
        f"- Active expected matches: **{summary['active_expected_matches']}**",
        f"- Matched primary rows: **{summary['matched_primary_rows']}**",
        f"- Latest screenshot: `{summary['latest_screenshot']}`",
        f"- PNG review image: `{summary['latest_png_review_image']}`",
        f"- Review crops: `{summary['review_crops']}`",
        f"- Latest-frame crops: **{summary['latest_crop_count']}**",
        f"- Metadata: `{summary['latest_meta']}`",
        f"- Route note: {summary['route_note']}",
        f"- Current limit: {summary['current_limit']}",
        "",
        "## Matched Rows",
        "",
        "| ROM | romaji | hint | CPU range | expected bytes | review status |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["matched_rows"]:
        lines.append(
            f"| `{row['rom_hit']}` | {row['romaji'] or '-'} | {row['screen_hint'] or '-'} | "
            f"`{row['cpu_range']}` | `{row['expected_bytes']}` | `{row['review_status']}` |"
        )
    lines += [
        "",
        "## Latest-Frame Crops",
        "",
        "| crop | image | region |",
        "| --- | --- | --- |",
    ]
    for row in payload["latest_crops"]:
        lines.append(
            f"| `{row['crop']}` | `{row['path']}` | {row['x']},{row['y']} {row['width']}x{row['height']} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- Use this as route and byte-load evidence for the current automated path.",
        "- Keep final visual approval separate until a patched-ROM screen visibly shows the intended Korean text in context.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = make_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON.relative_to(REPO_ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(REPO_ROOT)}")
    print(f"matched_primary_rows={payload['summary']['matched_primary_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
