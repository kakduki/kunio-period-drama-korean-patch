from pathlib import Path


SOURCE = Path(__file__).parents[1] / "lua" / "kunio_sram_route_probe.lua"


def test_probe_is_bounded_and_read_only() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    assert "MAX_FRAMES" in text
    assert "CAPTURE_GAP" in text
    assert "sram_diff.tsv" in text
    assert "SRAM_START" in text
    assert "SRAM_LENGTH" in text
    assert "read_blob(SRAM_START, SRAM_LENGTH)" in text
    assert "memory.writebyte" not in text
    assert "KUNIO_MAP_SOURCE_ROUTE" in text


if __name__ == "__main__":
    test_probe_is_bounded_and_read_only()
    print("kunio_sram_route_probe checks passed")
