#!/usr/bin/env python3
"""Fetch the archived Technos Samurai v1.0 nested ZIP by HTTP ranges.

Avoids downloading the multi-gigabyte archive and verifies required members.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import re
import struct
import urllib.parse
import urllib.request
import zipfile
import zlib
from pathlib import Path

ARCHIVE_ID = "translation-patches-ug"
ARCHIVE_FILE = "TranslationPatchesUg.zip"
NESTED_MEMBER = "Nes/Downtown Special Kunio-kun no Jidaigeki Dayo Zenin Shuugou!.zip"
EXPECTED = {
    "TSe-v10.ips": (15054, "cb6ea2fdbf82e974c474f4ea0d489f7c65647c94de899caf2a6b8c089f202dad"),
    "Tsamurai.nfo": (6511, None),
}


def range_get(url: str, value: str) -> tuple[bytes, str]:
    request = urllib.request.Request(url, headers={"Range": value, "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read(), response.headers["Content-Range"]


def nested_zip_bytes() -> bytes:
    url = f"https://archive.org/download/{ARCHIVE_ID}/{urllib.parse.quote(ARCHIVE_FILE)}"
    tail, content_range = range_get(url, "bytes=-2097152")
    content_range_match = re.search(r"bytes (\d+)-", content_range)
    if not content_range_match:
        raise ValueError(f"unexpected Content-Range: {content_range}")
    start = int(content_range_match.group(1))
    eocd = tail.rfind(b"PK\x05\x06")
    if eocd < 0:
        raise ValueError("outer ZIP EOCD not found in tail range")
    _, _, _, entries, _, cd_size, cd_offset, _ = struct.unpack_from("<4s4H2LH", tail, eocd)
    position = cd_offset - start
    for _ in range(entries):
        values = struct.unpack_from("<4s6H3L5H2L", tail, position)
        name_len, extra_len, comment_len = values[10:13]
        name = tail[position + 46 : position + 46 + name_len].decode("cp437")
        if name == NESTED_MEMBER:
            method, compressed_size, local_offset = values[4], values[8], values[16]
            local, _ = range_get(url, f"bytes={local_offset}-{local_offset + 30 + name_len + 2048 + compressed_size}")
            _, _, _, _, _, _, _, _, _, local_name_len, local_extra_len = struct.unpack_from("<4s5H3L2H", local, 0)
            payload_start = 30 + local_name_len + local_extra_len
            payload = local[payload_start : payload_start + compressed_size]
            return payload if method == 0 else zlib.decompress(payload, -15)
        position += 46 + name_len + extra_len + comment_len
    raise ValueError(f"nested member not found: {NESTED_MEMBER}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("reference/technos-samurai-v1"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    nested = zipfile.ZipFile(io.BytesIO(nested_zip_bytes()))
    for name, (expected_size, expected_sha256) in EXPECTED.items():
        content = nested.read(name)
        if len(content) != expected_size:
            raise ValueError(f"{name}: expected {expected_size} bytes, got {len(content)}")
        digest = hashlib.sha256(content).hexdigest()
        if expected_sha256 and digest != expected_sha256:
            raise ValueError(f"{name}: expected sha256 {expected_sha256}, got {digest}")
        (args.output / name).write_bytes(content)
        print(f"{name}\t{len(content)}\t{digest}")


if __name__ == "__main__":
    main()
