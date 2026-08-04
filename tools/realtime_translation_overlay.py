"""Display bounded FCEUX text events as a Korean translation overlay.

The receiver is deliberately independent of an AI provider. It resolves a
translation from a CSV cache first, then optionally invokes a user-supplied
translator command for an uncached event. The command receives one JSON object
on stdin and must print the translated line to stdout.
"""

from __future__ import annotations

import argparse
import csv
import json
import shlex
import subprocess
import time
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TextEvent:
    frame: int
    event_id: str
    category: str
    context: str
    expected_bytes: str
    record_snapshot: str


def load_translation_cache(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = csv.DictReader(handle)
        result: dict[str, str] = {}
        for row in rows:
            event_id = (row.get("id") or "").strip()
            translated = (row.get("translated_text") or "").strip()
            if event_id and translated and translated.upper() != "UNKNOWN":
                result[event_id] = translated
        return result


def parse_event(line: str) -> TextEvent | None:
    parts = line.rstrip("\r\n").split("\t")
    if len(parts) < 7 or parts[0] != "text":
        return None
    try:
        frame = int(parts[1])
    except ValueError:
        return None
    return TextEvent(frame, parts[2], parts[3], parts[4], parts[5], parts[6])


def translate_with_command(event: TextEvent, command: str | None, timeout: float) -> str | None:
    if not command:
        return None
    payload = json.dumps({
        "id": event.event_id,
        "category": event.category,
        "context": event.context,
        "expected_bytes": event.expected_bytes,
        "record_snapshot": event.record_snapshot,
    }, ensure_ascii=False)
    completed = subprocess.run(
        shlex.split(command, posix=False),
        input=payload,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    if completed.returncode != 0:
        return None
    translated = completed.stdout.strip()
    return translated or None


def resolve_text(event: TextEvent, cache: dict[str, str], command: str | None, timeout: float) -> tuple[str, str]:
    cached = cache.get(event.event_id)
    if cached:
        return cached, "CACHED"
    translated = translate_with_command(event, command, timeout)
    if translated:
        return translated, "AI_UNCHECKED"
    return f"[{event.event_id}] 번역 대기", "UNCHECKED"


def format_event(event: TextEvent, cache: dict[str, str], command: str | None = None, timeout: float = 20.0) -> str:
    translated, status = resolve_text(event, cache, command, timeout)
    return f"{translated}\n[{status} | frame {event.frame} | {event.context}]"


def latest_event(path: Path) -> TextEvent | None:
    if not path.exists():
        return None
    last: TextEvent | None = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        event = parse_event(line)
        if event is not None:
            last = event
    return last


def run_window(events: Path, cache: dict[str, str], command: str | None, timeout: float, poll_ms: int) -> None:
    root = tk.Tk()
    root.title("Kunio Korean Overlay")
    root.configure(bg="#111111")
    root.attributes("-topmost", True)
    root.geometry("640x100+40+420")
    label = tk.Label(
        root,
        text="FCEUX 이벤트 대기 중",
        bg="#111111",
        fg="#FFFFFF",
        font=("Malgun Gothic", 18, "bold"),
        justify="left",
        anchor="w",
        padx=12,
        pady=8,
    )
    label.pack(fill="both", expand=True)
    seen_frame = -1

    def poll() -> None:
        nonlocal seen_frame
        event = latest_event(events)
        if event is not None and event.frame != seen_frame:
            label.configure(text=format_event(event, cache, command, timeout))
            seen_frame = event.frame
        root.after(poll_ms, poll)

    poll()
    root.mainloop()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, default=Path("rom_analysis/realtime_overlay/events.tsv"))
    parser.add_argument("--cache", type=Path, default=Path("translation/script.csv"))
    parser.add_argument("--translator-command", help="Optional command receiving one JSON event on stdin.")
    parser.add_argument("--translator-timeout", type=float, default=20.0)
    parser.add_argument("--poll-ms", type=int, default=250)
    parser.add_argument("--once", action="store_true", help="Print the latest resolved event and exit.")
    args = parser.parse_args()
    cache = load_translation_cache(args.cache)
    if args.once:
        event = latest_event(args.events)
        if event is None:
            print("NO_EVENT")
            return 2
        print(format_event(event, cache, args.translator_command, args.translator_timeout))
        return 0
    run_window(args.events, cache, args.translator_command, args.translator_timeout, args.poll_ms)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
