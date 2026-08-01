-- All possible CPU windows for PRG 8 KiB bank 2, which contains ROM+0x05BDF.
return {
  { label = "english_thick_cpu_8000", category = "prepointer_item_label", rom = 0x05BDF, start = 0x9BCF, stop = 0x9BE5, bytes = "88 89 94 85 FF" },
  { label = "english_thick_cpu_A000", category = "prepointer_item_label", rom = 0x05BDF, start = 0xBBCF, stop = 0xBBE5, bytes = "88 89 94 85 FF" },
  { label = "english_thick_cpu_C000", category = "prepointer_item_label", rom = 0x05BDF, start = 0xDBCF, stop = 0xDBE5, bytes = "88 89 94 85 FF" },
  { label = "english_thick_cpu_E000", category = "prepointer_item_label", rom = 0x05BDF, start = 0xFBCF, stop = 0xFBE5, bytes = "88 89 94 85 FF" },
}
