#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_translation_coverage_bridge.py"


def main() -> int:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    data = json.loads((ROOT / "rom_analysis" / "translation_coverage_bridge.json").read_text(encoding="utf-8"))
    assert data["summary"]["translation_entries"] == 144
    assert sum(data["summary"]["status_counts"].values()) == 144
    with (ROOT / "rom_analysis" / "translation_coverage_bridge.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 144
    assert all(row["runtime_status"] == "not_runtime_proven" for row in rows)
    assert any(row["status"] == "static_candidate_known_bank1" for row in rows)
    assert any(row["status"] == "no_static_candidate" for row in rows)
    print("OK: translation coverage bridge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())