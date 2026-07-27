# Korean Patch Recovery Plan

## Reset Rule

Do not use free-running autoplay as a discovery method. Every emulator run needs
a named screen target, a fixed input route, a hard frame cap, a capture frame, and an explicit stop reason.

## Reference Model

The English patch is structural evidence only: screen labels, code ranges, active CHR pages, and pointer or queue layout.
It is never a source for Korean text or artwork. The Japanese base ROM remains the source of every candidate's runtime path.

## Per-Screen Pipeline

1. Capture the base and English reference at the same bounded screen route.
2. Record ROM offset, PRG bank, CPU address, mapper page, work buffer, PPU destination, and screenshot.
3. Classify the string as runtime-proven, structural-only, or screen-only before translating it.
4. Allocate a screen-owned 16x16 Korean glyph page that passes the Malgun Gothic Bold quality gate.
5. Patch exactly one screen context and smoke it with the same bounded route plus all known sharing contexts.
6. Mark PASS, FAIL, or UNKNOWN. Only PASS contexts can enter a development build; a shared-page FAIL quarantines the ROM.

## Renderer Families

- Opening dialogue: three native pointer contexts are historical PASS and remain regression-only evidence.
- Main menu labels: the isolated screenshot and bounded Items page-isolation smoke pass the development soft gate.
- Items actions: ROM 0x13727 -> CPU B717 -> SRAM 6360 -> PPU 2363 is runtime-proven. Korean Items text still needs its own source owner and second queue row.
- Combined development candidate: three opening records plus main-menu labels; runtime report `rom_analysis/korean_development_candidate_runtime.md` is SOFT_GATE_PASS.
- Dynamic titles, combat dialogue, and later menus: do not patch until they each have an equivalent bounded source-chain record.

## Controlled Game Progress

Do not try to discover late dialogue by looping the opening or clearing combat automatically. When a later screen matters, first identify a save state, a verified RAM state, or a documented cheat that enters that named screen. The resulting probe still needs a fixed input route and hard cap.

## Promotion Rules

- Development soft gate: runtime source chain and bounded boot/screen smoke are required.
- High-risk candidate: require a native screenshot and every known shared-context smoke.
- Release gate: require full screen-family coverage, Korean readability review, cross-screen regression, and a clean IPS scope audit.
