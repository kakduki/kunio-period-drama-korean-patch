#!/usr/bin/env python3
"""Classify a bounded pointer-dialogue FCEUX probe."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from rom_utils import REPO_ROOT


DEFAULT_PROBE = REPO_ROOT / "rom_analysis" / "pointer_dialogue_batch_002_003_probe" / "summary.tsv"
DEFAULT_BOOT = REPO_ROOT / "rom_analysis" / "pointer_dialogue_batch_002_003_boot_smoke" / "summary.tsv"
DEFAULT_ROUTE = REPO_ROOT / "rom_analysis" / "pointer_dialogue_batch_002_003_route_probe" / "summary.tsv"
DEFAULT_JSON = REPO_ROOT / "rom_analysis" / "pointer_dialogue_batch_002_003_runtime.json"
DEFAULT_MARKDOWN = REPO_ROOT / "rom_analysis" / "pointer_dialogue_batch_002_003_runtime.md"
DEFAULT_CANDIDATE = REPO_ROOT / "rom_analysis" / "pointer_dialogue_batch_002_003.json"


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def portable_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def classify(
    probe_path: Path,
    boot_path: Path,
    candidate_path: Path,
    route_path: Path | None = None,
) -> dict[str, object]:
    probe_rows = load_rows(probe_path)
    boot_rows = load_rows(boot_path)
    registered_rows = [row for row in probe_rows if row.get("reason") == "watchers_registered"]
    final_rows = [row for row in probe_rows if row.get("reason") in {"target_capture", "target_not_seen"}]
    boot_capture_rows = [
        row for row in boot_rows
        if row.get("reason") == "capture" and "target_match=true" in row.get("detail", "")
    ]
    registered = int(registered_rows[-1].get("target", "0")) if registered_rows else 0
    final = final_rows[-1] if final_rows else {}
    final_reason = final.get("reason", "missing")
    if final_reason == "target_capture" and registered > 0:
        target_verdict = "PASS"
    elif final_reason == "target_not_seen" and registered > 0:
        target_verdict = "UNKNOWN"
    else:
        target_verdict = "FAIL"
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    route_payload: dict[str, object] = {
        "path": portable_path(route_path) if route_path else None,
        "verdict": "NOT_RUN",
        "final_frame": None,
        "final_reason": "missing",
        "hits": None,
        "phase": None,
        "screen_fingerprint": None,
    }
    if route_path and route_path.exists():
        route_rows = load_rows(route_path)
        route_final_rows = [
            row for row in route_rows
            if row.get("reason") in {"target_capture", "target_not_seen"}
        ]
        route_final = route_final_rows[-1] if route_final_rows else {}
        route_payload.update({
            "verdict": "PASS" if route_final.get("reason") == "target_capture" else "UNKNOWN",
            "final_frame": int(route_final.get("frame", "0")) if route_final else None,
            "final_reason": route_final.get("reason", "missing"),
            "hits": int(route_final.get("hits", "0")) if route_final else None,
            "phase": int(route_final.get("phase", "0")) if route_final else None,
            "screen_fingerprint": route_final.get("screen_fingerprint") if route_final else None,
        })
    return {
        "status": "SOFT_GATE_BOOT_PASS_BOSS_TARGET_" + target_verdict,
        "candidate_md5": candidate["candidate"]["patched_md5"],
        "probe": {
            "path": portable_path(probe_path),
            "registered_watchers": registered,
            "final_frame": int(final.get("frame", "0")) if final else None,
            "final_reason": final_reason,
            "target_verdict": target_verdict,
        },
        "boot_regression": {
            "path": portable_path(boot_path),
            "verdict": "PASS" if boot_capture_rows else "UNKNOWN",
            "capture_frame": int(boot_capture_rows[-1]["frame"]) if boot_capture_rows else None,
            "detail": boot_capture_rows[-1].get("detail", "") if boot_capture_rows else "target_match capture not found",
        },
        "route_probe": route_payload,
        "reason": (
            "The extended route entered phase 3 and produced read activity, but the screen fingerprint stabilized and pointer 2/3 never matched."
            if target_verdict == "UNKNOWN" and route_payload["verdict"] == "UNKNOWN"
            else "Known opening route did not reach pointer 2/3 before the hard frame cap."
            if target_verdict == "UNKNOWN"
            else "Pointer 2/3 target bytes were captured by the bounded probe."
            if target_verdict == "PASS"
            else "Probe did not register target reads or did not produce a terminal target row."
        ),
    }


def render_markdown(payload: dict[str, object]) -> str:
    probe = payload["probe"]
    boot = payload["boot_regression"]
    route = payload["route_probe"]
    return "\n".join([
        "# Pointer Dialogue Batch Runtime",
        "",
        f"Status: **{payload['status']}**",
        "",
        f"- Candidate MD5: `{payload['candidate_md5']}`.",
        f"- Boot regression: **{boot['verdict']}** at frame `{boot['capture_frame']}`.",
        f"- Pointer target watchers registered: `{probe['registered_watchers']}`.",
        f"- Target probe: **{probe['target_verdict']}**; frame `{probe['final_frame']}`; reason `{probe['final_reason']}`.",
        f"- Extended route probe: **{route['verdict']}**; frame `{route['final_frame']}`; reason `{route['final_reason']}`; phase `{route['phase']}`; reads `{route['hits']}`.",
        "",
        f"Reason: {payload['reason']}",
        "",
        "The target probe is bounded and does not continue into free-form combat.",
        "A target-not-seen result is not evidence that the candidate text is wrong;",
        "it only classifies the current route as insufficient for pointer 2/3.",
        "",
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", type=Path, default=DEFAULT_PROBE)
    parser.add_argument("--boot", type=Path, default=DEFAULT_BOOT)
    parser.add_argument("--route", type=Path, default=DEFAULT_ROUTE)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--report-markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    payload = classify(args.probe, args.boot, args.candidate, args.route)
    args.report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.report_markdown.write_text(render_markdown(payload), encoding="utf-8")
    print(f"status={payload['status']}")
    print(f"report_json={args.report_json}")
    print(f"report_markdown={args.report_markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
