# Koganemushi Post-Route Navigation

## Scope

This is a bounded follow-up after the verified Koganemushi name-entry route. It checks whether the resulting setup state can be advanced into the field or Map Cursor without blind long-running autoplay.

## Evidence

- Correct route run: `C:\tmp\english_koganemushi_end_row7`
- Post-navigation run: `C:\tmp\english_koganemushi_post_nav`
- Extended setup attempt: `C:\tmp\english_koganemushi_post_setup`
- The correct name route leaves the name-entry screen at frame 3605 and renders the post-name setup state by frame 3665.
- The bounded post-navigation attempts changed setup/menu RAM and screen contents, but did not produce a distinct Map Cursor screen, a confirmed field entry, or a source-text read.
- `$04F1` remained `01` in the observed post-route captures; this is not sufficient to identify a field or event state.

## Result

| Check | Result | Note |
|---|---|---|
| Koganemushi name-entry exit | PASS | Differentially reproduced on the English reference. |
| Post-name setup transition | PASS | A distinct post-name setup screen was rendered. |
| Map Cursor ownership/state | UNKNOWN | No distinct Map Cursor screen or source read was proven. |
| Natural field entry | UNKNOWN | The tested menu inputs did not establish the field state. |
| Boss/event trigger | UNKNOWN | No boss dialogue or event transition was observed. |

The post-route result is intentionally not promoted to a cheat or release prerequisite. The next probe should identify the exact setup-menu state transition from a captured screen and compare it with the already verified normal combat route before testing Map Cursor or boss events.

## Field-state follow-up source watch

- Run: `C:\tmp\koganemushi_map_source_probe`
- The corrected Koganemushi route reached a distinct green field/map-like screen at frames `3845-3925` with `$04F1=08`.
- A read watch on the Map CRSR candidate window `$9C59-$9C61` recorded `0` reads through frame `4200`.
- Result: `PASS_FIELD_STATE_TRANSITION`; `UNKNOWN_MAP_CRSR_SOURCE`.

The state transition is useful route evidence, but the zero source-read count prevents promoting the Map CRSR label or any related RAM address. Boss dialogue and natural event progression remain unproven.
