-- Target definitions for the first non-opening Korean pointer-dialogue batch.
-- PTR-003 is relocated from $A012 to $A011 by the candidate.
return {
  { label = "pointer_002_korean_early_boss", category = "pointer_dialogue", rom = 0x06014, start = 0xA004, stop = 0xA010, bytes = "F0 BB 00 81 82 83 84 85 86 87 88 CA FF", old_bytes = "F0 BB 9F 90 00 81 82 8C A4 8C 90 98 CD FF", source = "English pointer 002 semantic reference; Korean candidate", korean = "Ah, we meet again." },
  { label = "pointer_003_korean_early_boss", category = "pointer_dialogue", rom = 0x06021, start = 0xA011, stop = 0xA042, bytes = "F0 BB 00 89 8A 8B 8C 8D 8E 8F 90 00 91 92 93 94 95 96 CA F8 97 98 99 9A 8F 90 C0 C1 C2 C3 CA 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FF", old_bytes = "F0 BB 8F 85 82 A4 AF 00 A0 B7 83 95 9C 90 A8 08 A0 06 82 A4 8C 90 98 F8 F9 00 85 A2 B2 8B AE 06 00 8B 06 8C 93 A9 A4 92 A7 96 00 91 09 B2 98 B2 A6 FF", source = "English pointer 003 semantic reference; Korean candidate", korean = "Those guys... remember? It is them." },
}
