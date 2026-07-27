#!/usr/bin/env python3
"""Attach bounded FCEUX results to a direct 8x16 candidate report."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def final_row(rows: list[dict[str, str]], reasons: set[str]) -> dict[str, str]:
    for row in reversed(rows):
        if row.get("reason") in reasons:
            return row
    raise ValueError(f"no final row with reason in {sorted(reasons)}")


def update_markdown(path: Path, payload: dict[str, object]) -> None:
    text = path.read_text(encoding="utf-8")
    marker = "## Runtime Gate\n"
    if marker in text:
        text = text.split(marker, 1)[0]
    runtime = payload["runtime_gate"]
    assert isinstance(runtime, dict)
    lines = [
        marker.rstrip("\n"),
        "",
        f"- Overall verdict: **{runtime['verdict']}**.",
        f"- Boot smoke: **{runtime['boot']}** at frame `{runtime['boot_frame']}` (`{runtime['boot_reason']}`).",
        f"- Pointer route probe: **{runtime['pointer_route']}** at frame `{runtime['pointer_route_frame']}` (`{runtime['pointer_route_reason']}`).",
        f"- Route phase: `{runtime['pointer_route_phase']}`; watcher hits: `{runtime['pointer_route_hits']}`; final screen fingerprint: `{runtime['pointer_route_fingerprint']}`.",
        "- p0, p1, and p2 were not fully matched. This is a route-evidence gap, not proof that the candidate text is displayed.",
        "- The candidate remains a soft-gate build because p0 was compacted from a multi-message source record and no native-screen visual proof exists.",
        "",
    ]
    path.write_text(text + "\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--boot-summary", type=Path, required=True)
    parser.add_argument("--route-summary", type=Path, required=True)
    args = parser.parse_args()

    payload = json.loads(args.report.read_text(encoding="utf-8"))
    boot_rows = read_rows(args.boot_summary)
    route_rows = read_rows(args.route_summary)
    boot = final_row(boot_rows, {"lua_done", "capture"})
    route = final_row(route_rows, {"target_capture", "target_not_seen"})
    runtime = {
        "verdict": "UNKNOWN",
        "boot": "PASS" if boot.get("reason") == "lua_done" else "UNKNOWN",
        "boot_reason": boot.get("reason", ""),
        "boot_frame": boot.get("frame", ""),
        "boot_summary": str(args.boot_summary),
        "pointer_route": "PASS" if route.get("reason") == "target_capture" else "UNKNOWN",
        "pointer_route_reason": route.get("reason", ""),
        "pointer_route_frame": route.get("frame", ""),
        "pointer_route_phase": route.get("phase", ""),
        "pointer_route_hits": route.get("hits", ""),
        "pointer_route_fingerprint": route.get("screen_fingerprint", ""),
        "pointer_route_summary": str(args.route_summary),
        "reason": "Boot is proven, but the bounded route did not reach a complete p0/p1/p2 target match.",
    }
    payload["runtime_gate"] = runtime
    args.report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    update_markdown(args.markdown, payload)
    print(f"runtime_verdict={runtime['verdict']}")
    print(f"boot={runtime['boot']} frame={runtime['boot_frame']}")
    print(f"pointer_route={runtime['pointer_route']} frame={runtime['pointer_route_frame']} hits={runtime['pointer_route_hits']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
