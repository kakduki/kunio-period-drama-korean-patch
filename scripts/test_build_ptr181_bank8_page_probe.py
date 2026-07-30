from build_ptr181_bank8_page_probe import (
    POINTER_INDEX,
    RECORD_LENGTH,
    TARGET_CPU,
    TEST_RECORD,
    retarget_helper,
)


assert POINTER_INDEX == 181
assert TARGET_CPU == 0xB188
assert len(TEST_RECORD) == RECORD_LENGTH == 30
assert TEST_RECORD[-1] == 0
assert retarget_helper()[3:6] == bytes.fromhex("C9 88 D0")

print("PTR-181 Bank 8 page probe builder tests passed.")
