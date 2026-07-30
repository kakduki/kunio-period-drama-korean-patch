from build_ptr181_dynamic_page_probe import retarget_helper


helper, marker_cpu = retarget_helper()
assert helper[3:6] == bytes.fromhex("C9 88 D0")
assert marker_cpu > 0xBFA5

print("PTR-181 dynamic page probe builder tests passed.")
