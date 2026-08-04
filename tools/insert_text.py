#!/usr/bin/env python3
"""Compile the reviewed pointer candidate from the Japanese base ROM."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DRAFT = ROOT / "text_data" / "pointer_dialogue_korean_draft.tsv"
POINTER_TABLE_OFFSET = 0x05DD4


def inside_root(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except ValueError:
        return False


def parse_manifest(path: Path) -> tuple[dict[int, str], list[dict[str, str]]]:
    updates: dict[int, str] = {}
    skipped: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            translated = (row.get("translated_text") or "").strip()
            pointer = (row.get("pointer_address") or "").strip()
            row_id = (row.get("id") or "UNKNOWN").strip()
            if not translated or translated.upper() == "UNKNOWN":
                skipped.append({"id": row_id, "reason": "empty_or_unknown_translation"})
                continue
            try:
                pointer_offset = int(pointer, 0)
            except ValueError:
                skipped.append({"id": row_id, "reason": "pointer_address_unknown"})
                continue
            delta = pointer_offset - POINTER_TABLE_OFFSET
            if delta < 0 or delta % 2:
                skipped.append({"id": row_id, "reason": "pointer_address_not_in_declared_table"})
                continue
            index = delta // 2
            if index >= 248:
                skipped.append({"id": row_id, "reason": "pointer_index_out_of_range"})
                continue
            updates[index] = translated
    return updates, skipped


def make_manifest_draft(manifest: Path, draft: Path, directory: Path) -> tuple[Path, int, int]:
    updates, skipped = parse_manifest(manifest)
    with draft.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    applied = 0
    for row in rows:
        try:
            index = int(row["pointer_index"])
        except (KeyError, ValueError):
            continue
        if index not in updates:
            # A manifest build is an explicit allow-list. Do not compile the
            # draft's unverified Korean rows just because they exist in the
            # full-pointer source catalog; preserve their Japanese bytes.
            row["translation_status"] = "excluded_manifest_unselected"
            row["basis"] = "manifest allow-list; runtime and visual gates remain separate"
            continue
        row["korean_text"] = updates[index]
        row["translation_status"] = "manifest_test"
        row["basis"] = "translation/script.csv"
        row["notes"] = "Manifest override; source context and visual gate remain separate."
        applied += 1
    output = directory / "pointer_dialogue_korean_manifest_overlay.tsv"
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return output, applied, len(skipped)


def make_manifest_plan(plan: Path, updates: dict[int, str], directory: Path) -> Path:
    """Give each explicitly selected manifest row a private compact font page."""
    payload = json.loads(plan.read_text(encoding="utf-8"))
    pages = list(payload["optimized_pages"])
    assignments = [None] * len(payload["pointer_page_assignments"])
    max_pages = 52
    max_glyphs = 34
    for index, translated in sorted(updates.items()):
        glyphs = sorted({
            character
            for character in translated
            if "\uac00" <= character <= "\ud7a3"
        })
        if len(glyphs) > max_glyphs:
            raise ValueError(
                f"manifest pointer {index} needs {len(glyphs)} glyphs; "
                f"one page supports {max_glyphs}"
            )
        if len(pages) >= max_pages:
            raise ValueError("manifest font pages exceed the MMC3 expansion budget")
        page_index = len(pages)
        pages.append({"page_index": page_index, "syllables": glyphs})
        assignments[index] = page_index
    payload["optimized_pages"] = pages
    payload["pointer_page_assignments"] = assignments
    output = directory / "pointer_font_manifest_plan.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("build/pointer_candidate"))
    parser.add_argument("--font", type=Path)
    parser.add_argument("--draft", type=Path)
    parser.add_argument("--english", type=Path)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--segments", type=Path)
    parser.add_argument("--manifest", type=Path, help="optional translation/script.csv overlay")
    args = parser.parse_args()
    rom = args.rom if args.rom.is_absolute() else ROOT / args.rom
    if not rom.is_file():
        raise SystemExit(f"base ROM not found: {rom}")
    out = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    out = out.resolve()
    command_base = [
        sys.executable,
        str(ROOT / "scripts" / "build_full_pointer_korean_candidate.py"),
        str(rom.resolve()),
    ]
    values = {
        "--font": args.font,
        "--draft": args.draft,
        "--english": args.english,
        "--plan": args.plan,
        "--segments": args.segments,
    }

    build_root = ROOT / "build"
    build_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pointer_candidate_", dir=build_root) as temp:
        temp_path = Path(temp)
        manifest_updates = 0
        manifest_skipped = 0
        draft_path = values["--draft"]
        if args.manifest:
            manifest = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
            source_draft = (draft_path if draft_path and draft_path.is_absolute() else ROOT / draft_path) if draft_path else DEFAULT_DRAFT
            overlay, manifest_updates, manifest_skipped = make_manifest_draft(manifest, source_draft, temp_path)
            draft_path = overlay
            selected, _ = parse_manifest(manifest)
            base_plan = values["--plan"]
            base_plan = (base_plan if base_plan and base_plan.is_absolute() else ROOT / base_plan) if base_plan else ROOT / "rom_analysis" / "pointer_font_page_plan.json"
            values["--plan"] = make_manifest_plan(base_plan, selected, temp_path)
            if values["--segments"] is None:
                empty_segments = temp_path / "manifest_segments.json"
                empty_segments.write_text("{}\n", encoding="utf-8")
                values["--segments"] = empty_segments
        compiler_out = out if inside_root(out) else temp_path / "candidate"
        command = command_base + ["--out-dir", str(compiler_out)]
        if draft_path:
            command.extend(["--draft", str(draft_path if draft_path.is_absolute() else ROOT / draft_path)])
        for flag in ("--font", "--english", "--plan", "--segments"):
            value = values[flag]
            if value:
                command.extend([flag, str(value if value.is_absolute() else ROOT / value)])
        subprocess.run(command, cwd=ROOT, check=True)
        if compiler_out != out:
            out.mkdir(parents=True, exist_ok=True)
            for source in compiler_out.iterdir():
                destination = out / source.name
                if source.is_file():
                    shutil.copy2(source, destination)
    if args.manifest:
        print(f"manifest_updates={manifest_updates}")
        print(f"manifest_skipped={manifest_skipped}")
    print(f"pointer candidate: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())