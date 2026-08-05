from pathlib import Path


SOURCE = Path(__file__).parents[1] / "lua" / "kunio_name_entry_probe.lua"


def test_name_probe_is_bounded_and_does_not_write_memory() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    assert "MAX_FRAMES" in text
    assert "KUNIO_NAME_SELECT_FRAME" in text
    assert "_nametable_2000_23ff.bin" in text
    assert "memory.writebyte" not in text
    assert "memory.writedword" not in text
    assert "memory.registerwrite" in text
    assert "cursor_write_trace.tsv" in text
    assert "KOGANEMUSHI_ROUTE and frame >= CHEAT_START_FRAME" in text
    assert "KUNIO_NAME_CALIBRATION" in text
    assert "CHEAT_DIRECTION_PULSE" in text
    assert "CHEAT_CONFIRM_PULSE" in text
    assert 'add_cheat_button("down", 4)' in text
    assert 'add_cheat_button("right", 9)' in text
    assert "POST_CHEAT_ROUTE" in text
    assert '"lua_done"' in text


if __name__ == "__main__":
    test_name_probe_is_bounded_and_does_not_write_memory()
    print("kunio_name_entry_probe checks passed")
