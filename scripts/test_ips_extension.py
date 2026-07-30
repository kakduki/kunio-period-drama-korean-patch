#!/usr/bin/env python3

import tempfile
from pathlib import Path

from apply_ips_standalone import apply_ips
from build_patch import make_records, write_ips


def main() -> int:
    base = bytes.fromhex("00 01 02 03")
    patched = bytes.fromhex("00 FF 02 03 AA BB CC DD")
    records = make_records(base, patched)
    assert records == [(1, b"\xFF"), (4, b"\xAA\xBB\xCC\xDD")]
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "extended.ips"
        write_ips(path, records)
        assert apply_ips(base, path) == patched
    print("IPS extension tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
