-- Exact CPU-window target for pointer-table entry 182.
-- The candidate keeps this record at the original CPU range $B1A6-$B1CA.
return {
    { label = "opening_ptr_182_korean_slot_expansion", category = "opening_dialogue", rom = 0x071B6, start = 0xB1A6, stop = 0xB1CA, bytes = "81 82 83 84 85 86 87 88 C8 C9 00 89 8A 8B 8C 00 8D 8E 8F 90 91 92 CA F8 93 94 95 96 00 97 98 99 9A C4 C5 00 C0", old_bytes = "88 96 9F 8B BB 9A A4 88 8C 98 B2 86 82 CA F8 F9 00 1C AE 0F 83 85 A4 1C AE 06 00 93 B2 9D AE 95 AE 13 84 CA FF", source = "Japanese opening pointer 182", korean = "Korean 8x16 slot-expansion proof" },
}
