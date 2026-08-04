# Text Format

## Confirmed facts

- The base is an iNES NES/Famicom image with a 16-byte header, 128 KiB PRG, and 128 KiB CHR.
- The game uses mapper 4 (MMC3), so a CPU address alone is not a stable ROM location. A record must include the active PRG bank and the file offset.
- The known dialogue renderer reads a byte stream through a runtime pointer. The stream can contain control bytes, terminators, line/page controls, and tile codes.
- The English reference changes both PRG and CHR and includes renderer/menu support. It is a structural reference, not a Korean text source.

## Working representation

Each candidate string is recorded in `translation/script.csv` with:

- original and translated byte sequences;
- CPU address, file offset, and active bank when known;
- control-code bytes and maximum display width;
- scene, speaker, and evidence status.

Unknown decoding is kept as `UNKNOWN`; it is never silently treated as text. A string becomes patchable only after a runtime or screen-context proof.

## Encoding policy

The project does not assume Shift-JIS. The original game uses a game-specific tile/code table. ASCII or Japanese Unicode is used only in analysis files; ROM insertion uses the project character map and control-code map.
