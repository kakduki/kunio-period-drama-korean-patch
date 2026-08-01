#!/usr/bin/env python3
"""Generate a Lua owner probe from a bounded candidate report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rom_utils import REPO_ROOT


DEFAULT_REPORT = REPO_ROOT / "rom_analysis" / "full_korean_expanded_candidate.json"
DEFAULT_TEMPLATE = REPO_ROOT / "lua" / "kunio_pre_pointer_korean_probe.lua"
DEFAULT_OUTPUT = REPO_ROOT / "lua" / "kunio_pre_pointer_expanded_korean_probe.lua"


def format_bytes(value: str) -> str:
    return "{" + ",".join(f"0x{int(part, 16):02X}" for part in value.split()) + "}"


def generate(report_path: Path, template_path: Path, output_path: Path) -> int:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    template = template_path.read_text(encoding="utf-8")
    start = template.index("local TARGETS = {")
    end = template.index("\n}\n\nlocal function mkdir", start) + 2
    rows = [
        f'    {{ id = "{row["record_id"]}", offset = "{row["rom_offset"][2:]}", english = {format_bytes(row["old_bytes"])}, korean = {format_bytes(row["new_bytes"])} }},'
        for row in report["targets"]
    ]
    block = "local TARGETS = {\n" + "\n".join(rows) + "\n}"
    output = template[:start] + block + template[end:]
    output = output.replace("local MAX_CAPTURES = 10", f"local MAX_CAPTURES = {len(rows)}")
    output_path.write_text(output, encoding="utf-8")
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    count = generate(args.report, args.template, args.output)
    print(f"generated_targets={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
