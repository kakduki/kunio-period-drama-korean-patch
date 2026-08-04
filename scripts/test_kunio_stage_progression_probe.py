from pathlib import Path


SOURCE = Path(__file__).parents[1] / "lua" / "kunio_stage_progression_probe.lua"


def test_counter_read_trace_is_bounded_and_read_only() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    required = [
        "KUNIO_COUNTER_READ_TRACE",
        "KUNIO_COUNTER_READ_TRACE_LIMIT",
        "counter_reads.tsv",
        "register_exec(0xA661",
        "register_exec(0xAD76",
        "register_exec(0xAD86",
        "register_exec(0xAD89",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert not missing, f"stage probe missing: {', '.join(missing)}"
    assert "memory.writebyte(0x7A" not in text


if __name__ == "__main__":
    test_counter_read_trace_is_bounded_and_read_only()
    print("kunio_stage_progression_probe checks passed")