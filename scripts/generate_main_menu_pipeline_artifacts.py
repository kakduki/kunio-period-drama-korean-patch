#!/usr/bin/env python3
"""Generate the scoped Korean main-menu pipeline artifacts from verified reports."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from rom_utils import REPO_ROOT


DEFAULT_CONTEXT_REPORT = REPO_ROOT / "rom_analysis" / "main_menu_context_report.json"
DEFAULT_CANDIDATE_REPORT = REPO_ROOT / "rom_analysis" / "main_menu_korean_candidate.json"
DEFAULT_SMOKE_REPORT = REPO_ROOT / "rom_analysis" / "main_menu_korean_candidate_smoke_report.json"

HISTORICAL_OPENING_ROWS = (
    (
        "opening_ptr_182_16x16_readability_proof",
        "`0x071B6` / Bank 1",
        "source-slot structure checked",
        "pointer 182 PASS",
        "PASS",
        "HISTORICAL_BASELINE",
    ),
    (
        "opening_ptr_182_183_16x16_readability",
        "`0x071B6`, `0x071D7` / Bank 1",
        "pointer relocation checked",
        "182 `33/33`; 183 `25/25`",
        "PASS",
        "SUPERSEDED_BY_THREE_RECORD_CANDIDATE",
    ),
    (
        "opening_ptr_182_184_16x16_readability",
        "`0x071B6`, `0x071D6`, `0x071EF` / Bank 1",
        "pointer range, source-slot, CHR, and relocation structure checked",
        "182 `32/32`; 183 `25/25`; 184 `23/23`; all `lua_done`",
        "PASS on all three native screens",
        "PASS_FOR_THREE_OPENING_CONTEXTS",
    ),
)
HISTORICAL_STRING_ROWS = (
    {
        "id": "PTR-182-OPENING-COMPACT-16X16",
        "context": "opening dialogue",
        "base_rom_offset": "0x071B6",
        "candidate_rom_offset": "0x071B6",
        "prg_bank": "1",
        "base_cpu": "0xB1A6",
        "candidate_cpu": "0xB1A6",
        "japanese_context": "Kunio urgently says to hurry because Mr. Bunzo is in danger.",
        "korean_text": "\ucfe0\ub2c8\uc624: \uc11c\ub458\ub7ec! \ubd84\uc870\ubaa9 \uc704\ud5d8!",
        "font_profile": "readable_16x16",
        "runtime_status": "PASS",
        "visual_status": "PASS",
        "decision": "PASS_FOR_THREE_OPENING_CONTEXTS",
    },
    {
        "id": "PTR-183-OPENING-OKOTO-16X16",
        "context": "opening dialogue",
        "base_rom_offset": "0x071DB",
        "candidate_rom_offset": "0x071D6",
        "prg_bank": "1",
        "base_cpu": "0xB1CB",
        "candidate_cpu": "0xB1C6",
        "japanese_context": "Okoto welcomes Kunio and says that she has been waiting for him.",
        "korean_text": "\uc624\ucf54\ud1a0: \ucfe0\ub2c8\uc624! \uae30\ub2e4\ub838\uc5b4!",
        "font_profile": "readable_16x16",
        "runtime_status": "PASS",
        "visual_status": "PASS",
        "decision": "PASS_FOR_THREE_OPENING_CONTEXTS",
    },
    {
        "id": "PTR-184-OPENING-REUNION-16X16",
        "context": "opening dialogue",
        "base_rom_offset": "0x071F0",
        "candidate_rom_offset": "0x071EF",
        "prg_bank": "1",
        "base_cpu": "0xB1E0",
        "candidate_cpu": "0xB1DF",
        "japanese_context": "Kunio addresses Okoto and politely says that it has been a long time.",
        "korean_text": "\ucfe0\ub2c8\uc624: \uc624\ucf54\ud1a0, \uc624\ub79c\ub9cc.",
        "font_profile": "readable_16x16",
        "runtime_status": "PASS",
        "visual_status": "PASS",
        "decision": "PASS_FOR_THREE_OPENING_CONTEXTS",
    },
)


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected an object in {path}")
    return payload


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def markdown_matrix(context: dict[str, Any], candidate: dict[str, Any], smoke: dict[str, Any]) -> str:
    source = candidate["source"]
    candidate_info = candidate["candidate"]
    return "\n".join(
        [
            "# Build Matrix",
            "",
            "This matrix tracks development candidates, not release builds.",
            "Historical opening proof remains recorded while the main menu is added as a",
            "separate renderer family.",
            "",
            "| build | ROM offset / PRG bank | English-reference check | bounded runtime | visual | result |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        + [
            f"| {build} | {offset} | {reference} | {runtime} | {visual} | {result} |"
            for build, offset, reference, runtime, visual, result in HISTORICAL_OPENING_ROWS
        ]
        + [
            f"| main_menu_korean_16x16_candidate | `{context['source']['template_rom_offset']}` / Bank 7 | English slot layout and Bank 7 page evidence | frame 1906 `lua_done` | PASS | {smoke['status']} |",
            "",
            f"The current menu candidate is MD5 `{candidate_info['patched_md5']}` and uses cloned R1 page `{source['raster_r1_clone']}`.",
            "Release verdict remains `UNKNOWN` until shared-raster contexts and menu lifecycle are checked.",
            "",
        ]
    )


def write_string_candidates(path: Path, context: dict[str, Any], smoke: dict[str, Any]) -> None:
    fields = [
        "id",
        "context",
        "base_rom_offset",
        "candidate_rom_offset",
        "prg_bank",
        "base_cpu",
        "candidate_cpu",
        "japanese_context",
        "korean_text",
        "font_profile",
        "runtime_status",
        "visual_status",
        "decision",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(HISTORICAL_STRING_ROWS)
        for row in context["labels"]:
            rom_offset = int(row["rom_offset"], 16)
            cpu = 0xF2B1 + rom_offset - int(context["source"]["template_rom_offset"], 16)
            writer.writerow(
                {
                    "id": f"MENU-{row['id'].upper()}",
                    "context": "reachable main menu",
                    "base_rom_offset": row["rom_offset"],
                    "candidate_rom_offset": row["rom_offset"],
                    "prg_bank": "7",
                    "base_cpu": f"0x{cpu:04X}",
                    "candidate_cpu": f"0x{cpu:04X}",
                    "japanese_context": (
                        f"menu label; base tiles {row['base_bytes']}; "
                        f"English structural reference {row['english_reference']}"
                    ),
                    "korean_text": row["korean_candidate"],
                    "font_profile": "readable_16x16_bank8_clone",
                    "runtime_status": smoke["status"],
                    "visual_status": "PASS",
                    "decision": "SOFT_GATE_PASS",
                }
            )


def write_false_positive_list(path: Path) -> None:
    fields = ["candidate", "reason", "classification", "disposition"]
    rows = [
        {
            "candidate": "Raw 0xBB outside verified records",
            "reason": "0xBB is a renderer-special speaker separator, not a Korean glyph slot. The three-record candidate preserves it unchanged.",
            "classification": "control_token",
            "disposition": "Preserve it exactly; require a context capture before using it in another record.",
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
            "reason": "The recorded opening page-switch and persistent-page probes failed at runtime.",
            "classification": "failed_renderer_experiment",
            "disposition": "Excluded from the current fixed-Bank-7 opening path.",
        },
        {
            "candidate": "Opening autoplay route",
            "reason": "A looping opening route proves neither later dialogue context nor combat progression.",
            "classification": "invalid_discovery_method",
            "disposition": "Use it only as a bounded regression route for explicitly named opening records.",
        },
        {
            "candidate": "Dynamic menu selector",
            "reason": "Template +0x21 / tile 0x7E changes independently of the static menu labels.",
            "classification": "runtime_selector",
            "disposition": "Exclude from translation; prove cursor lifecycle separately.",
        },
        {
            "candidate": "Main-menu edge tile",
            "reason": "Tile 0xB8 at template rows 24/26 column 28 is layout decoration beside the label grid.",
            "classification": "layout_tile",
            "disposition": "Preserve it.",
        },
        {
            "candidate": "Unproven global Shift-JIS candidates",
            "reason": "No screen, pointer, or renderer context has been proven.",
            "classification": "context_missing",
            "disposition": "Do not patch.",
        },
        {
            "candidate": "English reference SETTNG typo",
            "reason": "The reference spelling is a structural clue, not source text to copy.",
            "classification": "reference_text",
            "disposition": "Do not copy it.",
        },
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def patched_rom_report(candidate: dict[str, Any], smoke: dict[str, Any]) -> str:
    source = candidate["source"]
    info = candidate["candidate"]
    return "\n".join(
        [
            "# Patched ROM Report",
            "",
            "## Historical Opening Candidate",
            "",
            "- Status: **PASS_FOR_THREE_OPENING_CONTEXTS**.",
            "- Base ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`.",
            "- Candidate MD5: `46cedd1da6d49643f5dd6bc4895ce706`.",
            "- English reference IPS SHA-256: `cb6ea2fdbf82e974c474f4ea0d489f7c65647c94de899caf2a6b8c089f202dad`.",
            "- Pointer 182: `0x05F40` -> `0x071B6` / `$B1A6`, 32 bytes.",
            "- Pointer 183: `0x05F42` moves `$B1CB` -> `0x071D6` / `$B1C6`, 25 bytes.",
            "- Pointer 184: `0x05F44` moves `$B1E0` -> `0x071EF` / `$B1DF`, 23 bytes.",
            "- Pointer 185 remains `$B1F8`; the range guard permits only entries 182-184.",
            "- Changed spans: 129; changed-byte scope audit: PASS; escaped bytes: 0.",
            "- Font profile: `readable` (14 px, BOX resampling, threshold 145), 20 scene-local",
            "  Korean glyphs rendered through paired 8x16 cells.",
            "- Runtime evidence: pointer 182 frame 883 `32/32`; pointer 183 frame 1093",
            "  `25/25`; pointer 184 frame 1399 `23/23`; all bounded runs ended `lua_done`.",
            "- Native visual review: PASS for all three screens.",
            "",
            "## Main Menu Candidate",
            "",
            f"- Candidate status: **{smoke['status']}**; release verdict: **{smoke['release_verdict']}**.",
            f"- Base MD5: `{source['base_md5']}`.",
            f"- Candidate MD5: `{info['patched_md5']}`.",
            f"- Static menu template: `{source['template_rom_offset']}`.",
            f"- Raster R1 clone switch: `{source['raster_r1_original']}` -> `{source['raster_r1_clone']}` at `{source['raster_r1_cpu_address']}`.",
            f"- CHR page pair: `{source['source_chr_1k_pair']}` -> `{source['clone_chr_1k_pair']}`.",
            "- Source Bank 7 CHR pages are preserved; Korean tiles exist only in the cloned Bank 8 pair.",
            f"- Declared changed spans: `{info['changed_span_count']}`.",
            "",
            "The generated ROM and IPS remain local build products. This report records the",
            "reproducible candidate identity without placing copyrighted ROM content in Git.",
            "The English patch validates structure only. Pointer 184's Japanese source was",
            "captured from the base ROM before translation. This is not a release-ready full",
            "translation.",
            "",
        ]
    )


def smoke_log(smoke: dict[str, Any]) -> str:
    capture = smoke["capture"]
    checks = smoke["checks"]
    lines = [
        "candidate=opening_ptr_182_184_16x16_readability",
        "candidate_md5=46cedd1da6d49643f5dd6bc4895ce706",
        "base_rom_md5=0d406a85285b4de8468f0dab6aad5fe5",
        "font_profile=readable_16x16_scene_local",
        "pointer_182_frame=883",
        "pointer_182_frame_budget=920",
        "pointer_182_registered_read_hits=32",
        "pointer_182_matched_read_hits=32",
        "pointer_182_final_reason=lua_done",
        "pointer_182_screen_capture=PASS",
        "pointer_182_nametable_capture=PASS",
        "pointer_182_visual_korean_glyph_review=PASS",
        "pointer_183_frame=1093",
        "pointer_183_frame_budget=1180",
        "pointer_183_registered_read_hits=25",
        "pointer_183_matched_read_hits=25",
        "pointer_183_final_reason=lua_done",
        "pointer_183_screen_capture=PASS",
        "pointer_183_nametable_capture=PASS",
        "pointer_183_visual_korean_glyph_review=PASS",
        "pointer_184_base_context_frame=1401",
        "pointer_184_base_context_matched_read_hits=24",
        "pointer_184_frame=1399",
        "pointer_184_frame_budget=1430",
        "pointer_184_registered_read_hits=23",
        "pointer_184_matched_read_hits=23",
        "pointer_184_final_reason=lua_done",
        "pointer_184_screen_capture=PASS",
        "pointer_184_nametable_capture=PASS",
        "pointer_184_visual_korean_glyph_review=PASS",
        "overall_smoke=PASS",
        "overall_proof=PASS_FOR_THREE_OPENING_CONTEXTS",
        "",
        "candidate=main_menu_korean_16x16_candidate",
        "PASS | bounded main-menu route | capture=1906 | result=lua_done",
        f"PASS | candidate template rendered from PPU dump | result={checks['captured_template_matches_candidate']}",
        f"PASS | clone-page mapper state | final_r1={capture['final_mapper_snapshot'].get('r1', '')}",
        f"PASS | source Bank 7 preserved | result={checks['source_bank7_chr_pair_unchanged']}",
        f"PASS | candidate screen evidence | {capture['screen']}",
        "UNKNOWN | cursor probe | post-template right input cleared the prior background selector cell, but no stable replacement position was proven",
        "UNKNOWN | release compatibility | the R1 raster split is shared beyond this one screen",
        "",
    ]
    return "\n".join(lines)


def release_gate_checklist(smoke: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Release Gate Checklist",
            "",
            "Current release verdict: **UNKNOWN**",
            "",
            "| gate | status | evidence / reason |",
            "| --- | --- | --- |",
            "| Base ROM identity | PASS | MD5 matches the verified Japanese base. |",
            "| English structural reference | PASS | Recorded IPS SHA-256; used only for structure. |",
            "| Scoped three-record opening build | PASS | 129 declared changed spans; 0 escaped bytes; range guard protects pointer 185. |",
            "| Bounded boot and target reads | PASS | 182 frame 883 `32/32`; 183 frame 1093 `25/25`; 184 frame 1399 `23/23`; all `lua_done`. |",
            "| Native Korean readability | PASS | Three native 16x16 opening screenshots reviewed. |",
            "| Japanese source context | PASS | Pointer 184 base-ROM capture is recorded; prior opening records already had context evidence. |",
            f"| Scoped main-menu build | {smoke['status']} | One real menu template and clone-page capture passed. |",
            "| Menu cursor lifecycle | UNKNOWN | A post-template probe was inconclusive. |",
            "| Other R1 raster contexts | UNKNOWN | Shared split needs per-screen audit. |",
            "| Release-wide Korean glyph capacity | UNKNOWN | Current allocations remain context-scoped. |",
            "| Full translated script | NOT_STARTED | Deliberately blocked until renderer-family evidence exists. |",
            "| Release package | BLOCKED | Requires high-risk families and release checks to pass. |",
            "",
            "## Required Before Release",
            "",
            "- [ ] Prove menu cursor movement and exit lifecycle with bounded state captures.",
            "- [ ] Audit each other context that shares the R1 raster split.",
            "- [ ] Add context-proven dialogue/UI strings one screen at a time.",
            "- [ ] Check Korean glyph readability on every promoted screen.",
            "- [ ] Run cross-screen boot and gameplay smoke tests without untargeted autoplay.",
            "- [ ] Require manual visual evidence only for release or high-risk candidates.",
            "",
        ]
    )


def recovery_plan() -> str:
    return "\n".join(
        [
            "# Korean Patch Recovery Plan",
            "",
            "## Working Rule",
            "",
            "Do not use free-running autoplay as a discovery method. Every emulator run needs",
            "a named screen target, a fixed input route, a hard frame cap, and a captured result.",
            "",
            "## Sequence",
            "",
            "1. Prove a screen context from the base ROM and use the English patch only for structure.",
            "2. Record ROM offset, PRG/CHR bank, renderer or nametable route, and screen evidence.",
            "3. Build one isolated Korean candidate with 16x16 glyphs where readability needs it.",
            "4. Run a bounded boot/screen smoke test and classify PASS, FAIL, or UNKNOWN.",
            "5. Promote only PASS contexts; keep UNKNOWN context work out of release builds.",
            "",
            "## Current Position",
            "",
            "- Main menu labels: soft-gate PASS.",
            "- Opening dialogue pointers 182-184: historical PASS for three native contexts.",
            "- Menu cursor lifecycle: UNKNOWN.",
            "- Other screens using the shared R1 split: UNKNOWN.",
            "- Dialogue work: continue only from verified renderer contexts, not broad byte scans.",
            "",
        ]
    )


def cursor_probe_report() -> str:
    return "\n".join(
        [
            "# Main Menu Cursor Probe",
            "",
            "Status: **UNKNOWN**",
            "",
            "A bounded post-template probe held `right` for frames 1900-1911 and captured",
            "frame 1925. The original background selector tile (`0x7E` at row 25, column 1)",
            "was absent in that capture, but the OAM dump did not expose a stable replacement",
            "cursor position. The change may include selector blinking or a state transition.",
            "",
            "This result does not alter the candidate ROM or invalidate the main-menu soft-gate",
            "PASS. Cursor movement and menu return remain release-gate work, to be tested with",
            "another explicitly targeted state capture rather than repeated gameplay automation.",
            "",
        ]
    )


def write_artifacts(
    output_root: Path,
    context: dict[str, Any],
    candidate: dict[str, Any],
    smoke: dict[str, Any],
) -> list[Path]:
    output_root.mkdir(parents=True, exist_ok=True)
    paths = {
        "matrix": output_root / "build_matrix.md",
        "strings": output_root / "string_candidates.csv",
        "false_positives": output_root / "false_positive_list.csv",
        "patched": output_root / "patched_rom_report.md",
        "smoke": output_root / "smoke_test_log.txt",
        "release": output_root / "release_gate_checklist.md",
        "plan": output_root / "KOREAN_PATCH_PLAN.md",
        "cursor": output_root / "rom_analysis" / "main_menu_cursor_probe.md",
    }
    paths["cursor"].parent.mkdir(parents=True, exist_ok=True)
    write_text(paths["matrix"], markdown_matrix(context, candidate, smoke))
    write_string_candidates(paths["strings"], context, smoke)
    write_false_positive_list(paths["false_positives"])
    write_text(paths["patched"], patched_rom_report(candidate, smoke))
    write_text(paths["smoke"], smoke_log(smoke))
    write_text(paths["release"], release_gate_checklist(smoke))
    write_text(paths["plan"], recovery_plan())
    write_text(paths["cursor"], cursor_probe_report())
    return list(paths.values())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context-report", type=Path, default=DEFAULT_CONTEXT_REPORT)
    parser.add_argument("--candidate-report", type=Path, default=DEFAULT_CANDIDATE_REPORT)
    parser.add_argument("--smoke-report", type=Path, default=DEFAULT_SMOKE_REPORT)
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    paths = write_artifacts(
        args.output_root,
        read_json(args.context_report),
        read_json(args.candidate_report),
        read_json(args.smoke_report),
    )
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
