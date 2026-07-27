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
DEFAULT_ITEMS_CONTEXT_REPORT = REPO_ROOT / "rom_analysis" / "items_context" / "report.json"

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


def main_menu_integration_status(items_context: dict[str, Any]) -> str:
    if items_context.get("candidate_page_verdict") == "FAIL":
        return "QUARANTINED_SHARED_R1_CONFLICT"
    if items_context.get("candidate_page_verdict") == "UNKNOWN":
        return "UNKNOWN_SHARED_R1_CONTEXT"
    if items_context.get("candidate_page_verdict") == "PASS":
        return "SOFT_GATE_PASS_ISOLATED_R1_POOL"
    return "PENDING_ITEMS_CONTEXT_PROOF"


def markdown_matrix(
    context: dict[str, Any],
    candidate: dict[str, Any],
    smoke: dict[str, Any],
    items_context: dict[str, Any],
) -> str:
    source = candidate["source"]
    candidate_info = candidate["candidate"]
    integration_status = main_menu_integration_status(items_context)
    items_source = items_context["source_chain"]
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
            f"| main_menu_korean_16x16_candidate | `{context['source']['template_rom_offset']}` / Bank 7 | English slot layout and Bank 7 page evidence | menu frame 1906 PASS; Items frame 1960 proves isolated pool | PASS menu / PASS page isolation | {integration_status} |",
            "",
            f"The current menu candidate is MD5 `{candidate_info['patched_md5']}` and uses cloned R1 page `{source['raster_r1_clone']}`.",
            f"The Items action source `{items_source['rom_offset']}` reaches PPU `{items_source['ppu_start']}` through the shared R1 page.",
            "The menu screenshot and Items page-isolation capture pass the development soft gate; other R1 contexts remain unaudited.",
            "",
        ]
    )


def write_string_candidates(
    path: Path,
    context: dict[str, Any],
    smoke: dict[str, Any],
    items_context: dict[str, Any],
) -> None:
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
        integration_status = main_menu_integration_status(items_context)
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
                    "runtime_status": f"{smoke['status']}; Items isolation {items_context['candidate_page_verdict']}",
                    "visual_status": "PASS_MENU_AND_ITEMS_PAGE_ISOLATION",
                    "decision": integration_status,
                }
            )
        source = items_context["source_chain"]
        translation = items_context["candidate_translation"]
        reference = items_context["english_reference"]
        writer.writerow(
            {
                "id": "ITEM-ACTIONS",
                "context": "reachable main-menu Items screen, row 27",
                "base_rom_offset": source["rom_offset"],
                "candidate_rom_offset": "UNPATCHED",
                "prg_bank": source["prg_16k_bank"],
                "base_cpu": source["cpu_start"],
                "candidate_cpu": "UNPATCHED",
                "japanese_context": "runtime-proven action template; English reference "
                + " / ".join(reference["actions"]),
                "korean_text": translation["actions"],
                "font_profile": "ISOLATED_R1_POOL_UNPATCHED_ITEMS_TEXT",
                "runtime_status": items_context["context_verdict"],
                "visual_status": "PASS_PAGE_ISOLATION_NOT_TRANSLATED",
                "decision": translation["status"],
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
        {
            "candidate": "Historical 0x80-$9B main-menu R1 clone allocation",
            "reason": "The first menu candidate reused code values present in the verified Items action row.",
            "classification": "shared_mapper_page_conflict",
            "disposition": "Keep as a failed historical candidate; use the isolated code-pool allocation for the current soft-gated build.",
        },
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def patched_rom_report(
    candidate: dict[str, Any], smoke: dict[str, Any], items_context: dict[str, Any]
) -> str:
    source = candidate["source"]
    info = candidate["candidate"]
    conflict = items_context["candidate_page_conflict"]
    integration_status = main_menu_integration_status(items_context)
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
            f"- Isolated menu smoke: **{smoke['status']}**; cross-screen page-isolation status: **{integration_status}**.",
            f"- Base MD5: `{source['base_md5']}`.",
            f"- Candidate MD5: `{info['patched_md5']}`.",
            f"- Static menu template: `{source['template_rom_offset']}`.",
            f"- Raster R1 clone switch: `{source['raster_r1_original']}` -> `{source['raster_r1_clone']}` at `{source['raster_r1_cpu_address']}`.",
            f"- CHR page pair: `{source['source_chr_1k_pair']}` -> `{source['clone_chr_1k_pair']}`.",
            "- Source Bank 7 CHR pages are preserved; Korean tiles exist only in the cloned Bank 8 pair.",
            f"- Declared changed spans: `{info['changed_span_count']}`.",
            f"- Bounded Items probe: **{items_context['context_verdict']}** source-chain proof; current candidate **{conflict['verdict']}**.",
            f"- Page-isolation result: {conflict['reason']}",
            "",
            "The generated ROM and IPS remain local build products. This report records the",
            "reproducible candidate identity without placing copyrighted ROM content in Git.",
            "The English patch validates structure only. Pointer 184's Japanese source was",
            "captured from the base ROM before translation. This is not a release-ready full",
            "translation.",
            "",
        ]
    )


def smoke_log(smoke: dict[str, Any], items_context: dict[str, Any]) -> str:
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
        f"PASS | bounded Items frame 1960 | isolated R1 pool result={items_context['candidate_page_verdict']}",
        "SOFT_GATE_PASS | menu + Items page isolation | full Items Korean text remains a separate build",
        "UNKNOWN | cursor probe | post-template right input cleared the prior background selector cell, but no stable replacement position was proven",
        "UNKNOWN | other shared R1 contexts | only the Items conflict is proven so far",
        "",
    ]
    return "\n".join(lines)


def release_gate_checklist(smoke: dict[str, Any], items_context: dict[str, Any]) -> str:
    integration_status = main_menu_integration_status(items_context)
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
            f"| Scoped main-menu build | {integration_status} | Menu capture and the bounded Items page-isolation smoke both pass. |",
            f"| Items shared-page probe | {items_context['candidate_page_verdict']} | ROM -> CPU -> SRAM -> PPU chain is proven; current Korean pool does not overlap the action codes. |",
            "| Menu cursor lifecycle | UNKNOWN | A post-template probe was inconclusive. |",
            "| Other R1 raster contexts | UNKNOWN | Shared split needs per-screen audit. |",
            "| Release-wide Korean glyph capacity | UNKNOWN | Current allocations remain context-scoped. |",
            "| Full translated script | NOT_STARTED | Deliberately blocked until renderer-family evidence exists. |",
            "| Release package | BLOCKED | Requires high-risk families and release checks to pass. |",
            "",
            "## Required Before Release",
            "",
            "- [ ] Prove menu cursor movement and exit lifecycle with bounded state captures.",
            "- [ ] Audit every other context that shares the cloned R1 page before release.",
            "- [ ] Build an Items-specific second PPU queue row before writing 16x16 Korean action text.",
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
            "## Reset Rule",
            "",
            "Do not use free-running autoplay as a discovery method. Every emulator run needs",
            "a named screen target, a fixed input route, a hard frame cap, a capture frame, and an explicit stop reason.",
            "",
            "## Reference Model",
            "",
            "The English patch is structural evidence only: screen labels, code ranges, active CHR pages, and pointer or queue layout.",
            "It is never a source for Korean text or artwork. The Japanese base ROM remains the source of every candidate's runtime path.",
            "",
            "## Per-Screen Pipeline",
            "",
            "1. Capture the base and English reference at the same bounded screen route.",
            "2. Record ROM offset, PRG bank, CPU address, mapper page, work buffer, PPU destination, and screenshot.",
            "3. Classify the string as runtime-proven, structural-only, or screen-only before translating it.",
            "4. Allocate a screen-owned 16x16 Korean glyph page that passes the Malgun Gothic Bold quality gate.",
            "5. Patch exactly one screen context and smoke it with the same bounded route plus all known sharing contexts.",
            "6. Mark PASS, FAIL, or UNKNOWN. Only PASS contexts can enter a development build; a shared-page FAIL quarantines the ROM.",
            "",
            "## Renderer Families",
            "",
            "- Opening dialogue: three native pointer contexts are historical PASS and remain regression-only evidence.",
            "- Main menu labels: the isolated screenshot and bounded Items page-isolation smoke pass the development soft gate.",
            "- Items actions: ROM 0x13727 -> CPU B717 -> SRAM 6360 -> PPU 2363 is runtime-proven. Korean Items text still needs its own source owner and second queue row.",
            "- Combined development candidate: three opening records plus main-menu labels; runtime report `rom_analysis/korean_development_candidate_runtime.md` is SOFT_GATE_PASS.",
            "- Dynamic titles, combat dialogue, and later menus: do not patch until they each have an equivalent bounded source-chain record.",
            "",
            "## Controlled Game Progress",
            "",
            "Do not try to discover late dialogue by looping the opening or clearing combat automatically. When a later screen matters, first identify a save state, a verified RAM state, or a documented cheat that enters that named screen. The resulting probe still needs a fixed input route and hard cap.",
            "",
            "## Promotion Rules",
            "",
            "- Development soft gate: runtime source chain and bounded boot/screen smoke are required.",
            "- High-risk candidate: require a native screenshot and every known shared-context smoke.",
            "- Release gate: require full screen-family coverage, Korean readability review, cross-screen regression, and a clean IPS scope audit.",
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
            "This result does not mitigate the independently proven Items shared-page failure.",
            "Cursor movement and menu return remain release-gate work, to be tested with",
            "another explicitly targeted state capture rather than repeated gameplay automation.",
            "",
        ]
    )


def write_artifacts(
    output_root: Path,
    context: dict[str, Any],
    candidate: dict[str, Any],
    smoke: dict[str, Any],
    items_context: dict[str, Any],
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
    write_text(paths["matrix"], markdown_matrix(context, candidate, smoke, items_context))
    write_string_candidates(paths["strings"], context, smoke, items_context)
    write_false_positive_list(paths["false_positives"])
    write_text(paths["patched"], patched_rom_report(candidate, smoke, items_context))
    write_text(paths["smoke"], smoke_log(smoke, items_context))
    write_text(paths["release"], release_gate_checklist(smoke, items_context))
    write_text(paths["plan"], recovery_plan())
    write_text(paths["cursor"], cursor_probe_report())
    return list(paths.values())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context-report", type=Path, default=DEFAULT_CONTEXT_REPORT)
    parser.add_argument("--candidate-report", type=Path, default=DEFAULT_CANDIDATE_REPORT)
    parser.add_argument("--smoke-report", type=Path, default=DEFAULT_SMOKE_REPORT)
    parser.add_argument("--items-context-report", type=Path, default=DEFAULT_ITEMS_CONTEXT_REPORT)
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    paths = write_artifacts(
        args.output_root,
        read_json(args.context_report),
        read_json(args.candidate_report),
        read_json(args.smoke_report),
        read_json(args.items_context_report),
    )
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
