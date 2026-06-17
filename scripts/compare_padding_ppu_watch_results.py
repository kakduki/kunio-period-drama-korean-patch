#!/usr/bin/env python3
"""Compare PPU write-watch results for PRG padding experiment strategies."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "rom_analysis" / "prg_padding_fceux_targets.json"
OUT_MD = ROOT / "rom_analysis" / "fceux_padding_exp_ppu_watch_comparison.md"
OUT_JSON = ROOT / "rom_analysis" / "fceux_padding_exp_ppu_watch_comparison.json"


def parse_bytes(text: str) -> list[int]:
    return [int(byte, 16) for byte in text.split() if byte]


def watch_dir_for(strategy: str) -> Path:
    return ROOT / "rom_analysis" / f"fceux_padding_exp_{strategy}_ppu_watch"


def read_summary(input_dir: Path) -> dict[str, str]:
    path = input_dir / "summary.tsv"
    if not path.exists():
        return {}
    rows = list(csv.DictReader(path.open(encoding="utf-8"), delimiter="\t"))
    return rows[-1] if rows else {}


def read_writes(input_dir: Path) -> list[dict[str, str]]:
    path = input_dir / "ppu_writes.tsv"
    if not path.exists():
        return []
    return list(csv.DictReader(path.open(encoding="utf-8"), delimiter="\t"))


def exact_matches(rows: list[dict[str, str]], expected: list[int]) -> list[dict[str, object]]:
    """Find same-frame, consecutive-VRAM matches only.

    The looser phase-stream analyzer is useful for fill-stripped text, but it
    can false-positive when padding bytes are intentionally part of the target.
    """

    by_frame: dict[int, dict[int, int]] = defaultdict(dict)
    meta: dict[tuple[int, int], dict[str, str]] = {}
    for row in rows:
        try:
            frame = int(row["frame"])
            addr = int(row["vram_addr"].lstrip("$"), 16)
            byte = int(row["byte"], 16)
        except (KeyError, ValueError):
            continue
        if 0x2000 <= addr < 0x3000 and (addr & 0x3FF) < 0x3C0:
            by_frame[frame][addr] = byte
            meta[(frame, addr)] = row

    matches: list[dict[str, object]] = []
    seq_len = len(expected)
    for frame, cells in sorted(by_frame.items()):
        for addr in sorted(cells):
            actual = [cells.get(addr + offset) for offset in range(seq_len)]
            if actual == expected:
                row = meta.get((frame, addr), {})
                matches.append(
                    {
                        "frame": frame,
                        "vram_addr": f"${addr:04X}",
                        "nt": row.get("nt", ""),
                        "tile_row": row.get("tile_row", ""),
                        "tile_col": row.get("tile_col", ""),
                    }
                )
    return matches


def main() -> int:
    targets = json.loads(TARGETS.read_text(encoding="utf-8"))
    results = []
    for strategy, target_rows in targets["targets_by_strategy"].items():
        target = target_rows[0]
        input_dir = watch_dir_for(strategy)
        expected = parse_bytes(target["expected_patched_bytes"])
        writes = read_writes(input_dir)
        summary = read_summary(input_dir)
        matches = exact_matches(writes, expected)
        results.append(
            {
                "strategy": strategy,
                "input_dir": str(input_dir.relative_to(ROOT)),
                "expected_bytes": target["expected_patched_bytes"],
                "ppu_writes": len(writes),
                "frames_captured": len({row.get("frame") for row in writes}),
                "final_frame": summary.get("frame", ""),
                "final_reason": summary.get("reason", ""),
                "exact_vram_matches": len(matches),
                "match_locations": matches[:12],
                "screen_verdict": "not-visual-confirmed",
            }
        )

    payload = {
        "source": str(TARGETS.relative_to(ROOT)),
        "summary": {
            "strategy_count": len(results),
            "all_have_exact_vram_match": all(row["exact_vram_matches"] > 0 for row in results),
            "screen_verdict": "not-visual-confirmed",
        },
        "results": results,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# FCEUX Padding Experiment PPU Watch Comparison",
        "",
        "This compares same-frame, consecutive-VRAM PPU writes for the five `ROM+0x071A4` padding experiment ROMs.",
        "",
        "Important: this is stricter than the phase-stream analyzer and avoids false positives caused by padding bytes such as `00` and `7A`.",
        "",
        "| strategy | expected bytes | PPU writes | frames | final frame | exact VRAM matches | first locations | screen verdict |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in results:
        locations = "<br>".join(
            f"`frame {match['frame']} {match['vram_addr']} r{match['tile_row']}c{match['tile_col']}`"
            for match in row["match_locations"][:4]
        ) or "-"
        lines.append(
            f"| {row['strategy']} | `{row['expected_bytes']}` | {row['ppu_writes']} | "
            f"{row['frames_captured']} | {row['final_frame']} | {row['exact_vram_matches']} | "
            f"{locations} | {row['screen_verdict']} |"
        )
    lines += [
        "",
        "## Notes",
        "",
        "- `not-visual-confirmed` means the bytes were checked in PPU writes, but no screenshot/PPU Viewer visual verdict has been made.",
        "- The current autoplay Lua reaches the menu/status transfer window, but it is not yet a reliable full gameplay bot.",
        "- Prefer strategies with exact VRAM matches for follow-up visual inspection.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(f"strategies={len(results)} all_exact={payload['summary']['all_have_exact_vram_match']}")
    for row in results:
        print(f"{row['strategy']}: exact={row['exact_vram_matches']} writes={row['ppu_writes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
