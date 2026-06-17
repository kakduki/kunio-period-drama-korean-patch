#!/usr/bin/env python3
"""Check manual screen dump summaries include machine-readable JSON."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from rom_utils import REPO_ROOT


def main() -> int:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        records = tmp / "manual_frame_000123_target_records.tsv"
        records.write_text(
            "\n".join(
                [
                    "frame\tlabel\tcategory\trom_hit\tcpu_range\texpected_bytes\tactive_expected_match\trecord_snapshot",
                    "123\ttest_match\tui\tROM+0x01234\t$8123-$8125\tAA BB\ttrue\t00 AA BB 00",
                    "123\ttest_miss\tui\tROM+0x05678\t$8567-$8569\tCC DD\tfalse\t00 11 22 00",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (tmp / "manual_frame_000123_meta.txt").write_text("frame=123\n", encoding="utf-8")
        (tmp / "manual_frame_000123_screen.gd").write_bytes(b"fake-gd")
        output = tmp / "summary.md"
        json_output = tmp / "summary.json"
        result = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "analyze_manual_screen_dump.py"),
                "--input-dir",
                str(tmp),
                "--output",
                str(output),
                "--json-output",
                str(json_output),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            return result.returncode

        payload = json.loads(json_output.read_text(encoding="utf-8"))
        errors = []
        if payload["frame"] != "123":
            errors.append(f"unexpected frame {payload['frame']!r}")
        if payload["targets_checked"] != 2:
            errors.append(f"unexpected target count {payload['targets_checked']!r}")
        if payload["active_expected_matches"] != 1:
            errors.append(f"unexpected match count {payload['active_expected_matches']!r}")
        if not payload["latest_screenshot"].endswith("manual_frame_000123_screen.gd"):
            errors.append("latest screenshot was not recorded")
        markdown = output.read_text(encoding="utf-8")
        for expected in ["Screenshot:", "test_match", "Captured Files"]:
            if expected not in markdown:
                errors.append(f"{expected!r} missing from markdown")

        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 1

    print("OK: manual screen dump analyzer writes markdown and JSON")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
