from analyze_full_script_font_capacity import pack_rows


rows = [
    {"section": "A", "category": "", "source": "a", "korean": "가나다"},
    {"section": "A", "category": "", "source": "b", "korean": "나다라"},
    {"section": "B", "category": "", "source": "c", "korean": "마바사아"},
]

packed = pack_rows(rows, 4)
assert packed["page_count"] == 2
assert len(packed["oversize_rows"]) == 0

oversize = pack_rows(rows, 3)
assert len(oversize["oversize_rows"]) == 1

print("Full-script font capacity analyzer tests passed.")
