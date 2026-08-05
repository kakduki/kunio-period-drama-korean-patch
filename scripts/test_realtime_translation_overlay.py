"""Pure-function checks for the real-time overlay receiver."""

from __future__ import annotations

import csv
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.realtime_translation_overlay import format_event, load_translation_cache, parse_event, render_event



def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        cache_path = Path(directory) / "cache.csv"
        with cache_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["id", "translated_text"])
            writer.writeheader()
            writer.writerow({"id": "OPENING-182", "translated_text": "\uad6c\ub2c8\ub9c8\uc0ac: \uc5b4\uc11c \uc6c0\uc9c1\uc5ec! \ubd84\uc870 \ub450\ubaa9\uc774 \ud070\uc77c\uc774\uc57c!"})

        cache = load_translation_cache(cache_path)
        event = parse_event("text" + chr(9) + "883" + chr(9) + "OPENING-182" + chr(9) + "dialogue" + chr(9) + "pointer_182" + chr(9) + "88 96" + chr(9) + "88 96")
        assert event is not None
        rendered = format_event(event, cache)
        assert "\uad6c\ub2c8\ub9c8\uc0ac" in rendered
        assert "CACHED" in rendered

        unknown = parse_event("text" + chr(9) + "900" + chr(9) + "UNKNOWN-1" + chr(9) + "dialogue" + chr(9) + "ctx" + chr(9) + "AA" + chr(9) + "AA")
        assert unknown is not None
        unknown_rendered = format_event(unknown, cache)
        assert "\ubc88\uc5ed \ub300\uae30" in unknown_rendered
        assert "UNCHECKED" in unknown_rendered

        translator = Path(directory) / "translator.py"
        translator.write_text('print("AI translated")\n', encoding="utf-8")
        command = f"{sys.executable} {translator}"
        ai_rendered = format_event(unknown, cache, command=command)
        assert "AI translated" in ai_rendered
        assert "AI_UNCHECKED" in ai_rendered

        draft_path = Path(directory) / "drafts.tsv"
        render_event(unknown, cache, command=command, draft_log=draft_path)
        draft = draft_path.read_text(encoding="utf-8")
        assert "pending_review" in draft
        assert "UNKNOWN-1" in draft


    test_overlay_targets_cover_verified_records()
    print("OK: realtime translation overlay receiver")
    return 0



def test_overlay_targets_cover_verified_records() -> None:
    target_text = (Path(__file__).parents[1] / "lua" / "kunio_translation_overlay_targets.lua").read_text(encoding="utf-8")
    cache_text = (Path(__file__).parents[1] / "translation" / "realtime_overlay.csv").read_text(encoding="utf-8-sig")
    for event_id in ("OPENING-182", "OPENING-183", "OPENING-184", "OPENING-185", "OPENING-194", "OPENING-195"):
        assert event_id in target_text
        assert event_id in cache_text
    assert "OPENING-196" not in target_text
    assert "OPENING-197" not in target_text

def test_manual_launcher_contract() -> None:
    launcher = (Path(__file__).parents[1] / "scripts" / "run_realtime_overlay.py").read_text(encoding="utf-8")
    assert '"KUNIO_OVERLAY_DRIVE": "0"' in launcher
    assert '"KUNIO_OVERLAY_INTERACTIVE": "1"' in launcher
    assert "Close FCEUX" in launcher

if __name__ == "__main__":
    raise SystemExit(main())
