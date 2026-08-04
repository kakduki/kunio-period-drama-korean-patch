#!/usr/bin/env python3
"""List contiguous changed regions without interpreting them as text."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _analysis_common import changed_spans, hashes, load, parse_ines, region_for  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--output", type=Path, default=Path("rom_analysis/changed_regions.json"))
    args = parser.parse_args()
    before = load(args.base.resolve())
    after = load(args.candidate.resolve())
    layout = parse_ines(before)
    rows = [
        {
            "start": start,
            "end_exclusive": end,
            "length": end - start,
            "region": region_for(start, layout),
        }
        for start, end in changed_spans(before, after)
    ]
    payload = {
        "base": hashes(before),
        "candidate": hashes(after),
        "rom_expanded": len(before) != len(after),
        "size_delta": len(after) - len(before),
        "regions": rows,
    }
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"regions={len(rows)}")
    print(f"output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
