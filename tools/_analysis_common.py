"""Small dependency-free helpers shared by repository analysis tools."""

from __future__ import annotations

import hashlib
import zlib
from pathlib import Path


def hashes(data: bytes) -> dict[str, str | int]:
    return {
        "size": len(data),
        "crc32": f"{zlib.crc32(data) & 0xFFFFFFFF:08X}",
        "md5": hashlib.md5(data).hexdigest(),
        "sha1": hashlib.sha1(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def load(path: Path) -> bytes:
    if not path.is_file():
        raise SystemExit(f"file not found: {path}")
    return path.read_bytes()


def parse_ines(data: bytes) -> dict[str, int | bool | str]:
    if data[:4] != b"NES\x1a" or len(data) < 16:
        raise ValueError("not an iNES ROM")
    trainer = bool(data[6] & 0x04)
    prg_size = data[4] * 0x4000
    chr_size = data[5] * 0x2000
    payload_start = 16 + (512 if trainer else 0)
    return {
        "header_size": 16,
        "trainer": trainer,
        "prg_size": prg_size,
        "chr_size": chr_size,
        "payload_start": payload_start,
        "prg_start": payload_start,
        "prg_end": payload_start + prg_size,
        "chr_start": payload_start + prg_size,
        "chr_end": payload_start + prg_size + chr_size,
        "mapper": (data[6] >> 4) | (data[7] & 0xF0),
    }


def apply_ips(base: bytes, patch: bytes) -> bytes:
    if patch[:5] != b"PATCH":
        raise ValueError("IPS header is missing")
    result = bytearray(base)
    pos = 5
    while pos < len(patch):
        if patch[pos : pos + 3] == b"EOF":
            return bytes(result)
        if pos + 5 > len(patch):
            raise ValueError("truncated IPS record")
        offset = int.from_bytes(patch[pos : pos + 3], "big")
        size = int.from_bytes(patch[pos + 3 : pos + 5], "big")
        pos += 5
        if size:
            end = pos + size
            if end > len(patch):
                raise ValueError("truncated IPS payload")
            payload = patch[pos:end]
            pos = end
        else:
            if pos + 3 > len(patch):
                raise ValueError("truncated IPS RLE record")
            run_length = int.from_bytes(patch[pos : pos + 2], "big")
            value = patch[pos + 2]
            pos += 3
            payload = bytes([value]) * run_length
        end = offset + len(payload)
        if end > len(result):
            result.extend(b"\x00" * (end - len(result)))
        result[offset:end] = payload
    raise ValueError("IPS EOF marker is missing")


def changed_spans(before: bytes, after: bytes) -> list[tuple[int, int]]:
    limit = max(len(before), len(after))
    spans: list[tuple[int, int]] = []
    start: int | None = None
    for offset in range(limit):
        old = before[offset] if offset < len(before) else None
        new = after[offset] if offset < len(after) else None
        changed = old != new
        if changed and start is None:
            start = offset
        elif not changed and start is not None:
            spans.append((start, offset))
            start = None
    if start is not None:
        spans.append((start, limit))
    return spans


def region_for(offset: int, layout: dict[str, int | bool | str]) -> str:
    if offset < int(layout["payload_start"]):
        return "header_or_trainer"
    if offset < int(layout["prg_end"]):
        return "prg"
    if offset < int(layout["chr_end"]):
        return "chr"
    return "expanded_or_trailing"


def hex_preview(data: bytes, limit: int = 64) -> str:
    value = data[:limit].hex(" ")
    return value + (" ..." if len(data) > limit else "")


def pointer_candidates(data: bytes, start: int, end: int) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    begin = max(0, start - 1)
    stop = min(len(data) - 1, end + 1)
    for offset in range(begin, stop):
        value = data[offset] | (data[offset + 1] << 8)
        if 0x8000 <= value <= 0xFFFF:
            rows.append({"file_offset": offset, "cpu_address": value})
    return rows[:32]


def likelihoods(original: bytes, changed: bytes, region: str) -> dict[str, float]:
    if not changed:
        return {"string": 0.0, "graphics": 0.0, "code": 0.0}
    printable = sum(32 <= value < 127 for value in changed) / len(changed)
    controls = sum(value in (0x00, 0xBB, 0xCA, 0xF8, 0xFF) for value in changed) / len(changed)
    opcode_hits = sum(value in (0x20, 0x4C, 0x60, 0xA9, 0x85, 0x8D, 0xBD, 0xB1, 0xC9) for value in changed) / len(changed)
    graphics = 1.0 if region == "chr" else 0.0
    return {
        "string": round(min(1.0, printable * 0.7 + controls * 0.3), 3),
        "graphics": round(graphics, 3),
        "code": round(opcode_hits if region == "prg" else 0.0, 3),
    }
