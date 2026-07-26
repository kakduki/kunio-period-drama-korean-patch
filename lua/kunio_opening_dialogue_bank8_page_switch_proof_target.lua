-- Exact CPU-window target for the bounded Bank 8 clone-page proof.
return {
  { label = "opening_ptr_182_korean_bank8_page_switch_proof", category = "opening_dialogue", rom = 0x071B6, start = 0xB1A6, stop = 0xB1CA, bytes = "81 82 83 84 85 86 87 88 C8 C9 00 89 8A 8B 8C CA 00 FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00", old_bytes = "88 96 9F 8B BB 9A A4 88 8C 98 B2 86 82 CA F8 F9 00 1C AE 0F 83 85 A4 1C AE 06 00 93 B2 9D AE 95 AE 13 84 CA FF", source = "Bank 7 clone page is mapped through R0/R1 while pointer 182 renders", korean = "Korean Bank 8 page-switch proof" },
}
