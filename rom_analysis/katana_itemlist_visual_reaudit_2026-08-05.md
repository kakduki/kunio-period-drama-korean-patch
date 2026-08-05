# Katana item-list runtime re-audit (2026-08-05)

## Scope

This is a development probe only. It is not release approval and does not promote the target into the release manifest.

## Candidate and target

- Candidate: `output/full_nonpointer_korean_candidate/kunio_period_drama_korean_full_nonpointer_candidate.nes`
- Candidate MD5: `18284402f073b91c09d05f52a16b9b9d`
- Base ROM offset: `0x07227`
- Base bytes: `8A 94 99`
- Candidate bytes: `88 89 8A`
- Expected text: `カタナ` -> `카타나`
- Runtime snapshot: `85 88 89 8A 00`
- Explorer: `lua/kunio_katana_visual_explorer_v042.lua`
- Bounded run: 3000 frames; output directory `C:/tmp/kunio_katana_visual_explorer_current`

## Runtime result

The candidate bytes were read at the expected target during the bounded route:

- frame 302: target match true
- frame 392: target match true
- frame 2025: target match true
- frame 2115: target match true

The explorer produced screen dumps at these frames, including:

- `manual_frame_002025_screen.gd`
- `manual_frame_002115_screen.gd`

The route reached the scripted menu-pattern phase after frame 1020. This is stronger than the earlier opening-only runs, but it is still not proof that the target was rendered in the intended item-list context.

## Gate

| Check | Result | Reason |
|---|---|---|
| Static target bytes | PASS | Base and candidate bytes match the quarantined target definition. |
| Runtime target read | PASS | The expected bytes were observed at four bounded frames. |
| Menu phase reached | PASS | The explorer entered its post-opening menu-pattern phase. |
| Native visual item-list proof | UNKNOWN | The generated PNG capture could not be opened by the current local image inspection helper. |
| Release promotion | NOT READY | Visual context, source ownership, and font dependency are not all proven for this isolated target. |

## Interpretation

This probe does not justify adding `0x07227` to `translation/script.csv` or shipping a standalone patch. The next useful verification is to open `manual_frame_002025_screen.gd` or `manual_frame_002115_screen.gd` in FCEUX/another image viewer and confirm both the item-list context and the visible Korean glyphs. The English IPS remains a structural reference only; it does not remove this runtime-context gate.

