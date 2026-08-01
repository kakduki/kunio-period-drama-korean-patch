-- Narrow runtime target for an English pre-pointer label.
-- ROM+0x05BDF maps to CPU $9BCD while Bank 1 is visible.
return {
  {
    label = "english_pre_pointer_thick",
    category = "prepointer_item_label",
    rom = 0x05BDF,
    start = 0x9BCD,
    stop = 0x9BE3,
    bytes = "88 89 94 85 FF",
  },
}
