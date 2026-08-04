#!/usr/bin/env python3
"""Compare CHR tile regions without assuming a particular font encoding."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _analysis_common import hashes, load, parse_ines  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--tile-size", type=int, default=16)
    parser.add_argument("--include-expanded", action="store_true", help="include a bounded sample of trailing candidate tiles")
    parser.add_argument("--output", type=Path, default=Path("rom_analysis/font_region_analysis.json"))
    args = parser.parse_args()
    before = load(args.base.resolve())
    after = load(args.candidate.resolve())
    layout = parse_ines(before)
    start = int(layout["chr_start"])
    declared_end = int(layout["chr_end"])
    compare_end = min(declared_end, len(before), len(after))
    rows: list[dict[str, object]] = []
    for offset in range(start, compare_end, args.tile_size):
        old = before[offset : offset + args.tile_size]
        new = after[offset : offset + args.tile_size]
        if old == new:
            continue
        tile_index = (offset - start) // args.tile_size
        rows.append(
            {
                "file_offset": f"0x{offset:06X}",
                "chr_tile_index": tile_index,
                "chr_bank_8k": tile_index // 512,
                "changed_bytes": sum(left != right for left, right in zip(old, new)),
                "base_tile_sha1": hashlib.sha1(old).hexdigest(),
                "candidate_tile_sha1": hashlib.sha1(new).hexdigest(),
                "base_tile_hex": old.hex(" "),
                "candidate_tile_hex": new.hex(" "),
            }
        )
    trailing_start = len(before)
    trailing = after[trailing_start:]
    expanded_sample: list[dict[str, object]] = []
    if args.include_expanded:
        for offset in range(trailing_start, len(after) - (len(after) - trailing_start) % args.tile_size, args.tile_size):
            tile = after[offset : offset + args.tile_size]
            if tile != bytes(args.tile_size):
                expanded_sample.append(
                    {
                        "file_offset": f"0x{offset:06X}",
                        "changed_bytes": sum(value != 0 for value in tile),
                        "tile_sha1": hashlib.sha1(tile).hexdigest(),
                    }
                )
                if len(expanded_sample) >= 128:
                    break
    payload = {
        "base": hashes(before),
        "candidate": hashes(after),
        "tile_size": args.tile_size,
        "declared_chr_file_range": [start, declared_end],
        "changed_declared_chr_tiles": len(rows),
        "candidate_trailing_range": [trailing_start, len(after)],
        "candidate_trailing_bytes": len(trailing),
        "candidate_trailing_sha256": hashlib.sha256(trailing).hexdigest() if trailing else None,
        "expanded_nonzero_tile_sample": expanded_sample,
        "rows": rows,
        "interpretation": "tile changes are graphics evidence only; code-to-glyph mapping remains separate",
    }
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"changed_declared_chr_tiles={len(rows)}")
    print(f"candidate_trailing_bytes={len(trailing)}")
    print(f"output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())