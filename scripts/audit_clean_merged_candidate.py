#!/usr/bin/env python3
"""Summarize the clean full-pointer/non-pointer Korean candidate gates."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from rom_utils import REPO_ROOT


BASE = REPO_ROOT / "rom" / "Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes"
POINTER = REPO_ROOT / "output" / "full_pointer_korean_candidate" / "kunio_period_drama_korean_full_pointer_candidate.nes"
CANDIDATE = REPO_ROOT / "output" / "full_korean_clean_merged_candidate" / "kunio_period_drama_korean_full_items_title_none_candidate.nes"
BUILD_REPORT = REPO_ROOT / "rom_analysis" / "full_korean_clean_merged_candidate.json"
PRE_BUILD_REPORT = REPO_ROOT / "rom_analysis" / "pre_pointer_clean_expanded_full_pointer_candidate_v2.json"
PRE_RUNTIME = REPO_ROOT / "rom_analysis" / "pre_pointer_clean_merged_runtime"
ITEMS_ACTION = REPO_ROOT / "rom_analysis" / "full_korean_clean_merged_items_action_runtime.json"
ITEMS_TITLE_NONE = REPO_ROOT / "rom_analysis" / "full_korean_clean_merged_items_runtime.json"
STAGE_RUNTIME = REPO_ROOT / "rom_analysis" / "stage_progression_clean_merged"
POINTER_INPUT = REPO_ROOT / "rom_analysis" / "full_pointer_clean_merged_input_runtime"
OUTPUT_JSON = REPO_ROOT / "rom_analysis" / "full_korean_clean_merged_runtime.json"
OUTPUT_MARKDOWN = REPO_ROOT / "rom_analysis" / "full_korean_clean_merged_runtime.md"


ALLOWED_OVERLAY_RANGES = {
    "pre_pointer": (0x056BC, 0x05D53),
    "items_name_prg": (0x0561B, 0x05620),
    "items_name_chr": (0x3FB32, 0x3FB37),
    "items_none": (0x0FC31, 0x0FC36),
    "items_title": (0x136F4, 0x13700),
    "items_action": (0x13727, 0x13748),
    "bank7_font_pool": (0x2F000, 0x30000),
}


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def changed_offsets(left: bytes, right: bytes) -> list[int]:
    return [index for index, (a, b) in enumerate(zip(left, right)) if a != b]


def in_allowed(offset: int) -> bool:
    return any(start <= offset < end for start, end in ALLOWED_OVERLAY_RANGES.values())


def summarize_pre_pointer() -> dict[str, object]:
    summary = load_tsv(PRE_RUNTIME / "summary.tsv")
    matches = load_tsv(PRE_RUNTIME / "matches.tsv")
    done = next((row for row in reversed(summary) if row.get("reason") == "lua_done"), {})
    match_rows = [row for row in matches if row.get("representation") == "korean"]
    target_ids = sorted({row.get("target") for row in match_rows if row.get("target")})
    return {
        "target_count": 22,
        "korean_target_count": len(target_ids),
        "target_ids": target_ids,
        "capture_frame": int(match_rows[0]["frame"]) if match_rows else None,
        "lua_done": bool(done),
        "terminal_frame": int(done["frame"]) if done else None,
        "final_matched_targets": int(done.get("matched_targets", 0)) if done else None,
    }


def summarize_stage() -> dict[str, object]:
    summary = load_tsv(STAGE_RUNTIME / "summary.tsv")
    captures = load_tsv(STAGE_RUNTIME / "captures.tsv")
    done = next((row for row in reversed(summary) if row.get("reason") == "lua_done"), {})
    combat = [int(row["frame"]) for row in captures if row.get("reason") == "combat_screen_change"]
    events = [int(row["frame"]) for row in captures if row.get("reason") == "combat_screen_change" and int(row["frame"]) >= 1900]
    return {
        "lua_done": bool(done),
        "terminal_frame": int(done["frame"]) if done else None,
        "unique_screens": int(done.get("unique", 0)) if done else None,
        "combat_frames": combat,
        "late_event_like_frames": events,
        "boss_proof": False,
    }


def summarize_pointer_input() -> dict[str, object]:
    rows = load_tsv(POINTER_INPUT / "summary.tsv")
    done = next((row for row in reversed(rows) if row.get("label") == "lua_done"), {})
    changes = [int(row["frame"]) for row in rows if row.get("label") == "screen_change"]
    return {
        "lua_done": bool(done),
        "terminal_frame": int(done["frame"]) if done else None,
        "screen_change_frames": changes,
        "first_dialogue_route_reached": any(frame >= 300 for frame in changes),
    }


def audit() -> dict[str, object]:
    base = BASE.read_bytes()
    pointer = POINTER.read_bytes()
    candidate = CANDIDATE.read_bytes()
    pointer_diff = changed_offsets(pointer, candidate)
    bad_pointer_diff = [offset for offset in pointer_diff if not in_allowed(offset)]
    pre_build = load_json(PRE_BUILD_REPORT)
    action = load_json(ITEMS_ACTION)
    title_none = load_json(ITEMS_TITLE_NONE)
    build = load_json(BUILD_REPORT)
    pointer_tail_same = candidate[len(base) :] == pointer[len(base) :]
    pointer_core_ranges = {
        "renderer_hooks": (0x05288, 0x052C7),
        "pointer_table": (0x05DD4, 0x05FC4),
        "pointer_records_and_loader": (0x05FC4, 0x0800F),
    }
    pointer_core_same = {
        name: candidate[start:end] == pointer[start:end]
        for name, (start, end) in pointer_core_ranges.items()
    }
    pre_runtime = summarize_pre_pointer()
    stage = summarize_stage()
    pointer_input = summarize_pointer_input()
    soft_gate = all(pointer_core_same.values()) and pointer_tail_same and not bad_pointer_diff
    soft_gate = soft_gate and pre_runtime["korean_target_count"] == 22
    soft_gate = soft_gate and bool(action.get("verdict") == "PASS")
    soft_gate = soft_gate and bool(title_none.get("runtime_byte_gate"))
    soft_gate = soft_gate and bool(stage["lua_done"] and stage["combat_frames"])
    soft_gate = soft_gate and bool(pointer_input["lua_done"] and pointer_input["first_dialogue_route_reached"])
    return {
        "status": "SOFT_GATE_PASS_CLEAN_MERGED_CANDIDATE" if soft_gate else "FAIL_CLEAN_MERGED_CANDIDATE",
        "release_status": "NOT_READY",
        "base_md5": md5(base),
        "pointer_owner_md5": md5(pointer),
        "candidate_md5": md5(candidate),
        "candidate_rom": str(CANDIDATE),
        "candidate_size": len(candidate),
        "pointer_core_same": pointer_core_same,
        "pointer_tail_same": pointer_tail_same,
        "changed_vs_pointer_count": len(pointer_diff),
        "unexpected_changed_vs_pointer": [f"0x{offset:05X}" for offset in bad_pointer_diff],
        "pre_pointer_build": {
            "candidate_md5": pre_build.get("candidate_md5"),
            "patched_count": pre_build.get("patched_count"),
            "preserved_existing": pre_build.get("status_counts", {}).get("PRESERVED_EXISTING", 0),
            "overflow_quarantined": pre_build.get("status_counts", {}).get("SKIPPED_GLYPH_OVERFLOW", 0),
            "missing_glyph_quarantined": pre_build.get("status_counts", {}).get("SKIPPED_MISSING_GLYPH", 0),
        },
        "pre_pointer_runtime": pre_runtime,
        "items_action_runtime": action,
        "items_title_none_runtime": title_none,
        "pointer_input_runtime": pointer_input,
        "stage_progression": stage,
        "visual_gate": "UNKNOWN_NATIVE_GDSCREENSHOT_TRANSPARENT",
        "natural_boss_route": "UNKNOWN",
        "known_limits": [
            "This is a development candidate, not a final release ROM.",
            "57 pre-pointer rows were quarantined by the safe glyph pool and one by a missing font glyph.",
            "Pointer forced page samples remain representative predecessor evidence because the pointer core and appended CHR tail are byte-identical.",
            "Native screenshot pixels and an enemy-clear/boss-spawn route remain unproven.",
        ],
    }


def render_markdown(payload: dict[str, object]) -> str:
    pre = payload["pre_pointer_runtime"]
    stage = payload["stage_progression"]
    pointer_input = payload["pointer_input_runtime"]
    return "\n".join(
        [
            "# Clean Merged Candidate Runtime Audit",
            "",
            f"- Status: **{payload['status']}**.",
            f"- Release status: **{payload['release_status']}**.",
            f"- Candidate MD5: `{payload['candidate_md5']}`.",
            f"- Candidate size: `{payload['candidate_size']}` bytes; appended CHR tail preserved: `{payload['pointer_tail_same']}`.",
            "",
            "## Ownership Safety",
            "",
            f"- Pointer core spans preserved: `{payload['pointer_core_same']}`.",
            f"- Candidate-vs-pointer changed bytes: `{payload['changed_vs_pointer_count']}`; unexpected outside declared overlay ranges: `{len(payload['unexpected_changed_vs_pointer'])}`.",
            f"- Safe pre-pointer additions: `{payload['pre_pointer_build']['patched_count']}`; existing 22-row high-code rows preserved: `{payload['pre_pointer_build']['preserved_existing']}`.",
            f"- Quarantined by glyph-pool overflow: `{payload['pre_pointer_build']['overflow_quarantined']}`; missing glyph: `{payload['pre_pointer_build']['missing_glyph_quarantined']}`.",
            "",
            "## Runtime Gates",
            "",
            f"- Fixed-label runtime: `{pre['korean_target_count']}/{pre['target_count']}` exact Korean owners; `lua_done`={pre['lua_done']} at frame `{pre['terminal_frame']}`.",
            f"- Items action verifier: `{payload['items_action_runtime']['verdict']}`.",
            f"- Items name/title/NONE byte gate: `{payload['items_title_none_runtime']['status']}`; queue frames `{payload['items_title_none_runtime']['queue_frames']}`.",
            f"- Full-pointer input route: `lua_done`={pointer_input['lua_done']}; screen changes `{pointer_input['screen_change_frames'][:6]}`; first dialogue route reached={pointer_input['first_dialogue_route_reached']}.",
            f"- Stage progression: `lua_done`={stage['lua_done']} at frame `{stage['terminal_frame']}`; unique screens `{stage['unique_screens']}`; combat frames `{stage['combat_frames']}`.",
            "",
            "## Remaining Gates",
            "",
            f"- Native visual gate: **{payload['visual_gate']}**.",
            f"- Natural boss route: **{payload['natural_boss_route']}**.",
            "- Release promotion: **NOT_READY**.",
            "",
            "This candidate is the clean integration base for continued work. It keeps the English patch's full-pointer renderer and appended font pages, then applies only bounded non-pointer owner chains. It does not claim that every Korean wording has been Japanese-context reviewed or visually approved.",
            "",
        ]
    )


def main() -> int:
    payload = audit()
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MARKDOWN.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("status", "candidate_md5", "pre_pointer_runtime", "stage_progression", "visual_gate", "natural_boss_route")}, ensure_ascii=False))
    return 0 if payload["status"] == "SOFT_GATE_PASS_CLEAN_MERGED_CANDIDATE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
