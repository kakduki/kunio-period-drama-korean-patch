# Real-Time AI Overlay Strategy

Date: 2026-08-05

## Decision

Keep the real-time translation overlay as a usable fallback and continue the
native Korean ROM patch as the primary preservation target. The overlay does
not replace ROM patching because it depends on emulator integration, can show
uncorrected AI output, and does not change menus, graphics, save data, or
offline ROM behavior.

## Why the English reference does not make this instant

The English IPS is valuable technical evidence, but it is not a Korean script
or a drop-in translation layer. It confirms several reusable mechanisms:

- relocated variable-length dialogue records and updated pointers;
- separate pre-pointer, menu, and pointer renderers;
- control-code preservation;
- paired dialogue character tiles and an expanded text area.

Korean still requires an independently verified text catalog, Korean glyph
tiles, width and line-break decisions, pointer allocation, and runtime checks.
The English patch also does not contain a stage warp or a boss-clear cheat, so
it cannot remove the need to reach and identify later scenes.

## Current overlay proof

The existing bounded MVP has already demonstrated the following path:

```text
FCEUX source-read event -> events.tsv -> Korean cache lookup -> overlay text
```

The 1,900-frame recheck reached four opening targets and resolved the known
records from `translation/realtime_overlay.csv`. Unknown records are marked
`AI_UNCHECKED`; they are not written into the ROM or promoted automatically.

## Recommended operating modes

1. Use the overlay for immediate play and for collecting scene evidence.
2. Save every source event with frame, screen fingerprint, source bytes, and
   context before asking an AI translator to produce Korean.
3. Review the Korean result and add it to the catalog only after the source
   window and control skeleton are verified.
4. Promote reviewed catalog rows into the native patch pipeline.
5. Keep native release approval separate from overlay success.

## Current gate

The unified native candidate passes bounded boot and combat entry, but natural
enemy-clear, boss spawn, and boss dialogue coverage remain `UNKNOWN`. This is
not a release-ready patch. The overlay MVP is a development aid and fallback,
not evidence of full-game translation coverage.
