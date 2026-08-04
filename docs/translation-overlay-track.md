# Optional Translation Overlay Track

The project now has two deliberately separate tracks:

1. The ROM patch remains the primary deliverable. It preserves the original game flow, replaces verified text/font/pointer ownership, and requires runtime evidence before release approval.
2. A screen-translation overlay is an optional interim play aid. It can make the Japanese ROM usable while dialogue/event routing is still being verified.

## Why an overlay helps

- It does not require changing the ROM or reverse-engineering every event branch first.
- It can be used with FCEUX immediately, including screens that are not yet reachable by the bounded route.
- Current Windows tools already offer OCR overlays, including local/offline options and optional cloud translation backends.

## Why it cannot replace the patch

NES dialogue is low-resolution tile graphics, not ordinary Japanese text. Generic OCR can merge separate lines, misread custom glyphs, and lose control-code context. An overlay also does not translate menus stored outside the OCR crop, preserve text timing, or prove that the Korean ROM follows the correct boss/event route.

## Project-specific overlay design

The useful version for this ROM should be a companion validation tool, not a second patching system:

- capture only the dialogue/menu regions from the FCEUX window;
- prefer nametable/tile decoding when the emulator is available, with OCR as fallback;
- normalize recognized strings against the English reference label/script inventory;
- use the reviewed Korean glossary first, then an AI translator only for unresolved text;
- display the result in a separate overlay and save the source image, recognized text, translation, frame, and confidence;
- never write to the ROM, SRAM, or emulator memory.

The overlay should be used for playability and route discovery. Any text promoted into the Korean ROM still goes through the normal offset, pointer, font, runtime, and visual gates.

