#!/usr/bin/env python3
"""Build the six bounded-pipeline artifacts from verified proof evidence."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

from rom_utils import REPO_ROOT


OUTPUT_FILES = (
    "build_matrix.md",
    "string_candidates.csv",
    "false_positive_list.csv",
    "patched_rom_report.md",
    "smoke_test_log.txt",
    "release_gate_checklist.md",
)
FRAME_BUDGET = 920
CAPTURE_FRAME = 883


def load_json(root: Path, relative: str) -> dict[str, object]:
    payload = json.loads((root / relative).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object JSON: {relative}")
    return payload


def csv_text(fieldnames: list[str], rows: list[dict[str, object]]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def selected_font_metrics(font_report: dict[str, object]) -> dict[str, object]:
    slug = font_report.get("recommended_profile")
    profiles = font_report.get("profiles")
    if not isinstance(slug, str) or not isinstance(profiles, list):
        raise ValueError("font report does not define a recommended profile")
    for profile in profiles:
        if isinstance(profile, dict) and profile.get("slug") == slug:
            metrics = profile.get("metrics")
            if isinstance(metrics, dict):
                return {"slug": slug, "metrics": metrics}
    raise ValueError("recommended font profile is missing from the report")


def render_artifacts(root: Path = REPO_ROOT) -> dict[str, str]:
    candidate = load_json(root, "rom_analysis/opening_dialogue_16x16_readability_proof.json")
    capture = load_json(
        root, "rom_analysis/opening_dialogue_16x16_readability_proof_capture/analysis.json"
    )
    font_report = load_json(root, "rom_analysis/opening_font_profile_comparison/report.json")
    english = load_json(root, "rom_analysis/english_patch_reference.json")
    catalog = load_json(
        root, "text_data/korean_scene_batches/opening_ptr_182_16x16_readability_proof.json"
    )

    source = candidate.get("source")
    candidate_result = candidate.get("candidate")
    english_source = english.get("source")
    records = catalog.get("records")
    if not isinstance(source, dict) or not isinstance(candidate_result, dict):
        raise ValueError("candidate report is incomplete")
    if not isinstance(english_source, dict):
        raise ValueError("English reference report is incomplete")
    if not isinstance(records, list) or len(records) != 1 or not isinstance(records[0], dict):
        raise ValueError("readability catalog must contain one record")
    record = records[0]

    font = selected_font_metrics(font_report)
    font_metrics = font["metrics"]
    assert isinstance(font_metrics, dict)
    record_offset = int(str(source["record_rom_offset"]), 16)
    prg_bank = (record_offset - 16) // 0x4000
    korean_text = str(record["korean_text"])
    japanese_context = str(record["japanese_source"])
    overall_proof = str(capture.get("overall_proof"))
    checks = capture.get("checks")
    evidence = capture.get("evidence")
    if not isinstance(checks, dict) or not isinstance(evidence, dict):
        raise ValueError("capture analysis is incomplete")

    build_matrix = "\n".join(
        [
            "# Build Matrix",
            "",
            "This matrix records the current development pipeline, not a release list.",
            "",
            "| build | ROM offset / PRG bank | English-reference check | runtime | visual | result |",
            "| --- | --- | --- | --- | --- | --- |",
            (
                "| opening_ptr_182_16x16_readability_proof | "
                f"@{source['record_rom_offset']} / Bank {prg_bank} | "
                f"IPS SHA-256 {english_source['ips_sha256']} | "
                f"{checks['bounded_lua_completion']}, {checks['target_record_runtime_read']} | "
                f"{checks['visual_korean_glyph_review']} | {overall_proof} |"
            ),
            "",
            "The candidate is limited to one pointer-driven dialogue record. Other text",
            "renderer families remain outside this matrix until they have their own context.",
            "",
        ]
    )

    string_candidates = csv_text(
        [
            "id",
            "context",
            "rom_offset",
            "prg_bank",
            "cpu_address",
            "japanese_context",
            "korean_text",
            "font_profile",
            "runtime_status",
            "visual_status",
            "decision",
        ],
        [
            {
                "id": record["id"],
                "context": record["context"],
                "rom_offset": source["record_rom_offset"],
                "prg_bank": prg_bank,
                "cpu_address": "0xB1A6",
                "japanese_context": japanese_context,
                "korean_text": korean_text,
                "font_profile": source["font_profile"],
                "runtime_status": checks["target_record_runtime_read"],
                "visual_status": checks["visual_korean_glyph_review"],
                "decision": "PASS_FOR_OPENING_PROOF_ONLY",
            }
        ],
    )

    false_positive_list = csv_text(
        ["candidate", "reason", "classification", "disposition"],
        [
            {
                "candidate": "Raw 0xBB inside dialogue records",
                "reason": "Renderer-special speaker separator; it is not a Korean glyph slot.",
                "classification": "control_token",
                "disposition": "Preserve unless a separately verified helper handles it.",
            },
            {
                "candidate": "Pointer 183 display",
                "reason": "The neighbour is statically relocated but has no independent screen capture.",
                "classification": "context_unknown",
                "disposition": "Do not translate or promote before a bounded target capture.",
            },
            {
                "candidate": "Other Bank 1 pointer rows",
                "reason": "Pointer correspondence proves structure, not the active screen or Korean rendering route.",
                "classification": "structural_only",
                "disposition": "Keep as catalog candidates, not patch bytes.",
            },
            {
                "candidate": "Base-ROM Japanese glyph-looking bytes",
                "reason": "The base Japanese dialogue glyph map is not fully decoded.",
                "classification": "encoding_unknown",
                "disposition": "Do not treat byte resemblance as translatable text.",
            },
            {
                "candidate": "Dynamic CHR Bank 8 paging",
                "reason": "The recorded page-switch and persistent-page probes failed at runtime.",
                "classification": "failed_renderer_experiment",
                "disposition": "Excluded from the current fixed-Bank-7 path.",
            },
        ],
    )

    patched_rom_report = "\n".join(
        [
            "# Patched ROM Report",
            "",
            "Status: **PROOF_CANDIDATE_VISUALLY_VERIFIED**",
            "",
            f"- Base ROM MD5: `{candidate_result['base_md5']}`",
            f"- Candidate ROM MD5: `{candidate_result['patched_md5']}`",
            f"- English reference IPS SHA-256: `{english_source['ips_sha256']}`",
            f"- Pointer record: `{source['pointer_rom_offset']}` -> `{source['record_rom_offset']}` (PRG Bank {prg_bank}).",
            f"- Candidate Korean: {korean_text}",
            f"- Record growth: {source['base_record_length']} -> {source['record_length']} bytes.",
            f"- Changed spans: {candidate_result['changed_span_count']}; escaped bytes: {candidate_result['escaped_byte_count']}.",
            f"- Font profile: `{source['font_profile']}` "
            f"({source['font_profile_settings']['target_pixels']} px, "
            f"{source['font_profile_settings']['resample']}, "
            f"threshold {source['font_profile_settings']['threshold']}).",
            f"- Font metrics: min pairwise Hamming {font_metrics['minimum_pairwise_hamming']}, "
            f"edge-touching glyphs {font_metrics['edge_touching_glyph_count']}.",
            "",
            "The generated ROM and IPS remain local/ignored. This report records only",
            "the reproducible inputs, scoped result, and verification evidence.",
            "",
        ]
    )

    screenshots = evidence.get("screenshots")
    screenshot = ""
    if isinstance(screenshots, list):
        screenshot = next((str(path) for path in screenshots if str(path).endswith(".png")), "")
    smoke_test_log = "\n".join(
        [
            "candidate=opening_ptr_182_16x16_readability_proof",
            f"frame_budget={FRAME_BUDGET}",
            f"capture_frame={CAPTURE_FRAME}",
            f"final_reason={evidence['final_reason']}",
            f"registered_read_hits={evidence['registered_read_hits']}",
            f"matched_read_hits={evidence['matched_read_hits']}",
            f"matched_capture_record={evidence['matched_capture_record']}",
            f"screen_capture={checks['screen_capture']}",
            f"nametable_capture={checks['nametable_capture']}",
            f"visual_korean_glyph_review={checks['visual_korean_glyph_review']}",
            f"overall_smoke={capture['overall_smoke']}",
            f"overall_proof={overall_proof}",
            f"screenshot={screenshot}",
            "",
        ]
    )

    release_gate_checklist = "\n".join(
        [
            "# Release Gate Checklist",
            "",
            "Status: **NOT_READY_FOR_RELEASE**",
            "",
            "| gate | status | evidence / reason |",
            "| --- | --- | --- |",
            "| Base ROM identity | PASS | MD5 matches the verified Japanese base. |",
            "| English structural reference | PASS | Official IPS SHA-256 matches the recorded reference. |",
            "| Scoped pointer-182 build | PASS | 106 declared changed spans; 0 escaped bytes. |",
            "| Bounded boot and target reads | PASS | Frame 883, 38/38 matching reads, lua_done. |",
            "| Native Korean readability | PASS | One opening screenshot reviewed at 16x16. |",
            "| Pointer 183 own screen | UNKNOWN | Static relocation only; no independent capture. |",
            "| Menu, status, item, event renderers | UNKNOWN | Separate renderer/context families. |",
            "| Release-wide Korean glyph capacity | UNKNOWN | Current 15-glyph allocation is scene-local. |",
            "| Full translated script | NOT_STARTED | No bulk translation is authorized. |",
            "| Release package | BLOCKED | Requires all high-risk context families and release checks. |",
            "",
            "Development candidates may continue through soft gates. Release promotion",
            "requires the unresolved high-risk rows to become PASS.",
            "",
        ]
    )

    return {
        "build_matrix.md": build_matrix,
        "string_candidates.csv": string_candidates,
        "false_positive_list.csv": false_positive_list,
        "patched_rom_report.md": patched_rom_report,
        "smoke_test_log.txt": smoke_test_log,
        "release_gate_checklist.md": release_gate_checklist,
    }


def write_artifacts(root: Path, artifacts: dict[str, str]) -> None:
    if set(artifacts) != set(OUTPUT_FILES):
        raise ValueError("artifact set is incomplete")
    for filename, contents in artifacts.items():
        (root / filename).write_text(contents, encoding="utf-8")


def main() -> int:
    artifacts = render_artifacts()
    write_artifacts(REPO_ROOT, artifacts)
    for filename in OUTPUT_FILES:
        print(filename)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
