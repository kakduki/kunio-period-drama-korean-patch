#!/usr/bin/env python3
"""Test bounded pointer-dialogue runtime classification."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from analyze_pointer_dialogue_batch_probe import classify, render_markdown


def main() -> int:
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        probe = root / "probe.tsv"
        boot = root / "boot.tsv"
        candidate = root / "candidate.json"
        probe.write_text(
            "frame\treason\ttarget\tscreenshot\ttarget_match\n"
            "0\twatchers_registered\t63\tfalse\tfalse\n"
            "1200\ttarget_not_seen\tpointer_002_003\tfalse\tfalse\n",
            encoding="utf-8",
        )
        boot.write_text(
            "frame\treason\tregistered\thits\tdetail\n"
            "1095\tcapture\t21\t21\tscreenshot=true;target_match=true\n",
            encoding="utf-8",
        )
        candidate.write_text(json.dumps({"candidate": {"patched_md5": "test-md5"}}), encoding="utf-8")
        payload = classify(probe, boot, candidate)
        assert payload["status"] == "SOFT_GATE_BOOT_PASS_BOSS_TARGET_UNKNOWN"
        assert payload["probe"]["registered_watchers"] == 63
        assert payload["boot_regression"]["verdict"] == "PASS"
        assert "bounded" in render_markdown(payload)
    print("Pointer dialogue runtime analyzer tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
