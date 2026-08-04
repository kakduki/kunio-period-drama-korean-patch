# Pointer Format

## Known pointer area

The English reference analysis identifies a 248-entry pointer table at file offsets `0x05DD4-0x05FC3`, with related pre-pointer data at `0x056BC-0x05D54` and pointer data at `0x05FC4-0x07767`.

The table is interpreted in the active PRG-bank context. Any future pointer edit must record:

1. pointer-table file offset;
2. raw pointer bytes;
3. decoded target CPU address or bank-relative address;
4. active PRG bank;
5. target file offset;
6. stream length and terminator/control bytes.

## Safety rules

- Do not patch an address from a disassembly without its bank context.
- Preserve pointer-table ownership unless the replacement stream has a measured, proven destination.
- Prefer a new stream in an unused or explicitly appended region, followed by a pointer update, over overwriting an unrelated stream.
- A candidate with unresolved pointer ownership is `UNKNOWN`, even when its bytes look like text.
