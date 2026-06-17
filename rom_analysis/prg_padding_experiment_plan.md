# PRG Padding Experiment Plan

This report turns `needs-padding-rule` replacements into explicit experimental byte strategies. It does not claim any strategy is safe; it defines reproducible FCEUX checks.

## Summary

- Needs-padding-rule targets: **29**
- Runtime-confirmed padding blockers: **1**
- Padding strategies: **5**

## Runtime-Confirmed First Targets

| ROM hit | Japanese | Korean | original | planned | tail | runtime evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `0x071A4` | ちから (Chikara) | 힘 | `93 88 AA` | `87` | `88 AA` | 1797 hits, active 11 |

## Strategy Matrix

| ROM hit | Japanese | category | evidence | strategy | patched bytes | pad bytes | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `0x071A4` | ちから (Chikara) | 능력치 | runtime-confirmed | pad_00 | `87 00 00` | `00 00` | control/fill hypothesis |
| `0x071A4` | ちから (Chikara) | 능력치 | runtime-confirmed | pad_7a | `87 7A 7A` | `7A 7A` | control/fill hypothesis |
| `0x071A4` | ちから (Chikara) | 능력치 | runtime-confirmed | pad_ff | `87 FF FF` | `FF FF` | control/fill hypothesis |
| `0x071A4` | ちから (Chikara) | 능력치 | runtime-confirmed | pad_f8f9 | `87 F8 F9` | `F8 F9` | control/fill hypothesis |
| `0x071A4` | ちから (Chikara) | 능력치 | runtime-confirmed | preserve_tail | `87 88 AA` | `88 AA` | baseline: only first glyph byte changes |
| `0x05AA3` | やり (Yari) | 무기 | static-candidate+pointer | pad_00 | `91 00` | `00` | control/fill hypothesis |
| `0x05AA3` | やり (Yari) | 무기 | static-candidate+pointer | pad_7a | `91 7A` | `7A` | control/fill hypothesis |
| `0x05AA3` | やり (Yari) | 무기 | static-candidate+pointer | pad_ff | `91 FF` | `FF` | control/fill hypothesis |
| `0x05AA3` | やり (Yari) | 무기 | static-candidate+pointer | pad_f8f9 | `91 F8` | `F8` | control/fill hypothesis |
| `0x05AA3` | やり (Yari) | 무기 | static-candidate+pointer | preserve_tail | `91 A0` | `A0` | baseline: only first glyph byte changes |
| `0x05AA5` | やり (Yari) | 무기 | static-candidate+pointer | pad_00 | `91 00` | `00` | control/fill hypothesis |
| `0x05AA5` | やり (Yari) | 무기 | static-candidate+pointer | pad_7a | `91 7A` | `7A` | control/fill hypothesis |
| `0x05AA5` | やり (Yari) | 무기 | static-candidate+pointer | pad_ff | `91 FF` | `FF` | control/fill hypothesis |
| `0x05AA5` | やり (Yari) | 무기 | static-candidate+pointer | pad_f8f9 | `91 F8` | `F8` | control/fill hypothesis |
| `0x05AA5` | やり (Yari) | 무기 | static-candidate+pointer | preserve_tail | `91 A0` | `A0` | baseline: only first glyph byte changes |
| `0x05BBA` | やり (Yari) | 무기 | static-candidate+pointer | pad_00 | `91 00` | `00` | control/fill hypothesis |
| `0x05BBA` | やり (Yari) | 무기 | static-candidate+pointer | pad_7a | `91 7A` | `7A` | control/fill hypothesis |
| `0x05BBA` | やり (Yari) | 무기 | static-candidate+pointer | pad_ff | `91 FF` | `FF` | control/fill hypothesis |
| `0x05BBA` | やり (Yari) | 무기 | static-candidate+pointer | pad_f8f9 | `91 F8` | `F8` | control/fill hypothesis |
| `0x05BBA` | やり (Yari) | 무기 | static-candidate+pointer | preserve_tail | `91 A3` | `A3` | baseline: only first glyph byte changes |
| `0x05BDF` | くすり (Kusuri) | 회복 | static-candidate+pointer | pad_00 | `92 00 00` | `00 00` | control/fill hypothesis |
| `0x05BDF` | くすり (Kusuri) | 회복 | static-candidate+pointer | pad_7a | `92 7A 7A` | `7A 7A` | control/fill hypothesis |
| `0x05BDF` | くすり (Kusuri) | 회복 | static-candidate+pointer | pad_ff | `92 FF FF` | `FF FF` | control/fill hypothesis |
| `0x05BDF` | くすり (Kusuri) | 회복 | static-candidate+pointer | pad_f8f9 | `92 F8 F9` | `F8 F9` | control/fill hypothesis |
| `0x05BDF` | くすり (Kusuri) | 회복 | static-candidate+pointer | preserve_tail | `92 87 A3` | `87 A3` | baseline: only first glyph byte changes |
| `0x05C09` | やり (Yari) | 무기 | static-candidate+pointer | pad_00 | `91 00` | `00` | control/fill hypothesis |
| `0x05C09` | やり (Yari) | 무기 | static-candidate+pointer | pad_7a | `91 7A` | `7A` | control/fill hypothesis |
| `0x05C09` | やり (Yari) | 무기 | static-candidate+pointer | pad_ff | `91 FF` | `FF` | control/fill hypothesis |
| `0x05C09` | やり (Yari) | 무기 | static-candidate+pointer | pad_f8f9 | `91 F8` | `F8` | control/fill hypothesis |
| `0x05C09` | やり (Yari) | 무기 | static-candidate+pointer | preserve_tail | `91 A3` | `A3` | baseline: only first glyph byte changes |
| `0x05C69` | やり (Yari) | 무기 | static-candidate+pointer | pad_00 | `91 00` | `00` | control/fill hypothesis |
| `0x05C69` | やり (Yari) | 무기 | static-candidate+pointer | pad_7a | `91 7A` | `7A` | control/fill hypothesis |
| `0x05C69` | やり (Yari) | 무기 | static-candidate+pointer | pad_ff | `91 FF` | `FF` | control/fill hypothesis |
| `0x05C69` | やり (Yari) | 무기 | static-candidate+pointer | pad_f8f9 | `91 F8` | `F8` | control/fill hypothesis |
| `0x05C69` | やり (Yari) | 무기 | static-candidate+pointer | preserve_tail | `91 A3` | `A3` | baseline: only first glyph byte changes |
| `0x0602E` | そうび (Soubi) | UI | static-candidate+pointer | pad_00 | `93 94 00` | `00` | control/fill hypothesis |
| `0x0602E` | そうび (Soubi) | UI | static-candidate+pointer | pad_7a | `93 94 7A` | `7A` | control/fill hypothesis |
| `0x0602E` | そうび (Soubi) | UI | static-candidate+pointer | pad_ff | `93 94 FF` | `FF` | control/fill hypothesis |
| `0x0602E` | そうび (Soubi) | UI | static-candidate+pointer | pad_f8f9 | `93 94 F8` | `F8` | control/fill hypothesis |
| `0x0602E` | そうび (Soubi) | UI | static-candidate+pointer | preserve_tail | `93 94 A8` | `A8` | baseline: only first glyph byte changes |
| `0x066FB` | ちから (Chikara) | 능력치 | static-candidate+pointer | pad_00 | `87 00 00` | `00 00` | control/fill hypothesis |
| `0x066FB` | ちから (Chikara) | 능력치 | static-candidate+pointer | pad_7a | `87 7A 7A` | `7A 7A` | control/fill hypothesis |
| `0x066FB` | ちから (Chikara) | 능력치 | static-candidate+pointer | pad_ff | `87 FF FF` | `FF FF` | control/fill hypothesis |
| `0x066FB` | ちから (Chikara) | 능력치 | static-candidate+pointer | pad_f8f9 | `87 F8 F9` | `F8 F9` | control/fill hypothesis |
| `0x066FB` | ちから (Chikara) | 능력치 | static-candidate+pointer | preserve_tail | `87 88 AA` | `88 AA` | baseline: only first glyph byte changes |
| `0x06839` | やり (Yari) | 무기 | static-candidate+pointer | pad_00 | `91 00` | `00` | control/fill hypothesis |
| `0x06839` | やり (Yari) | 무기 | static-candidate+pointer | pad_7a | `91 7A` | `7A` | control/fill hypothesis |
| `0x06839` | やり (Yari) | 무기 | static-candidate+pointer | pad_ff | `91 FF` | `FF` | control/fill hypothesis |
| `0x06839` | やり (Yari) | 무기 | static-candidate+pointer | pad_f8f9 | `91 F8` | `F8` | control/fill hypothesis |
| `0x06839` | やり (Yari) | 무기 | static-candidate+pointer | preserve_tail | `91 A7` | `A7` | baseline: only first glyph byte changes |
| `0x06845` | ちから (Chikara) | 능력치 | static-candidate+pointer | pad_00 | `87 00 00` | `00 00` | control/fill hypothesis |
| `0x06845` | ちから (Chikara) | 능력치 | static-candidate+pointer | pad_7a | `87 7A 7A` | `7A 7A` | control/fill hypothesis |
| `0x06845` | ちから (Chikara) | 능력치 | static-candidate+pointer | pad_ff | `87 FF FF` | `FF FF` | control/fill hypothesis |
| `0x06845` | ちから (Chikara) | 능력치 | static-candidate+pointer | pad_f8f9 | `87 F8 F9` | `F8 F9` | control/fill hypothesis |
| `0x06845` | ちから (Chikara) | 능력치 | static-candidate+pointer | preserve_tail | `87 88 AA` | `88 AA` | baseline: only first glyph byte changes |
| `0x068C3` | やり (Yari) | 무기 | static-candidate+pointer | pad_00 | `91 00` | `00` | control/fill hypothesis |
| `0x068C3` | やり (Yari) | 무기 | static-candidate+pointer | pad_7a | `91 7A` | `7A` | control/fill hypothesis |
| `0x068C3` | やり (Yari) | 무기 | static-candidate+pointer | pad_ff | `91 FF` | `FF` | control/fill hypothesis |
| `0x068C3` | やり (Yari) | 무기 | static-candidate+pointer | pad_f8f9 | `91 F8` | `F8` | control/fill hypothesis |
| `0x068C3` | やり (Yari) | 무기 | static-candidate+pointer | preserve_tail | `91 9A` | `9A` | baseline: only first glyph byte changes |
| `0x0691E` | やり (Yari) | 무기 | static-candidate+pointer | pad_00 | `91 00` | `00` | control/fill hypothesis |
| `0x0691E` | やり (Yari) | 무기 | static-candidate+pointer | pad_7a | `91 7A` | `7A` | control/fill hypothesis |
| `0x0691E` | やり (Yari) | 무기 | static-candidate+pointer | pad_ff | `91 FF` | `FF` | control/fill hypothesis |
| `0x0691E` | やり (Yari) | 무기 | static-candidate+pointer | pad_f8f9 | `91 F8` | `F8` | control/fill hypothesis |
| `0x0691E` | やり (Yari) | 무기 | static-candidate+pointer | preserve_tail | `91 A9` | `A9` | baseline: only first glyph byte changes |
| `0x069C5` | やり (Yari) | 무기 | static-candidate+pointer | pad_00 | `91 00` | `00` | control/fill hypothesis |
| `0x069C5` | やり (Yari) | 무기 | static-candidate+pointer | pad_7a | `91 7A` | `7A` | control/fill hypothesis |
| `0x069C5` | やり (Yari) | 무기 | static-candidate+pointer | pad_ff | `91 FF` | `FF` | control/fill hypothesis |
| `0x069C5` | やり (Yari) | 무기 | static-candidate+pointer | pad_f8f9 | `91 F8` | `F8` | control/fill hypothesis |
| `0x069C5` | やり (Yari) | 무기 | static-candidate+pointer | preserve_tail | `91 A2` | `A2` | baseline: only first glyph byte changes |
| `0x06BC6` | やり (Yari) | 무기 | static-candidate+pointer | pad_00 | `91 00` | `00` | control/fill hypothesis |
| `0x06BC6` | やり (Yari) | 무기 | static-candidate+pointer | pad_7a | `91 7A` | `7A` | control/fill hypothesis |
| `0x06BC6` | やり (Yari) | 무기 | static-candidate+pointer | pad_ff | `91 FF` | `FF` | control/fill hypothesis |
| `0x06BC6` | やり (Yari) | 무기 | static-candidate+pointer | pad_f8f9 | `91 F8` | `F8` | control/fill hypothesis |
| `0x06BC6` | やり (Yari) | 무기 | static-candidate+pointer | preserve_tail | `91 A4` | `A4` | baseline: only first glyph byte changes |
| `0x06BDF` | そうび (Soubi) | UI | static-candidate+pointer | pad_00 | `93 94 00` | `00` | control/fill hypothesis |
| `0x06BDF` | そうび (Soubi) | UI | static-candidate+pointer | pad_7a | `93 94 7A` | `7A` | control/fill hypothesis |
| `0x06BDF` | そうび (Soubi) | UI | static-candidate+pointer | pad_ff | `93 94 FF` | `FF` | control/fill hypothesis |
| `0x06BDF` | そうび (Soubi) | UI | static-candidate+pointer | pad_f8f9 | `93 94 F8` | `F8` | control/fill hypothesis |
| `0x06BDF` | そうび (Soubi) | UI | static-candidate+pointer | preserve_tail | `93 94 A8` | `A8` | baseline: only first glyph byte changes |
| `0x06D1B` | やり (Yari) | 무기 | static-candidate+pointer | pad_00 | `91 00` | `00` | control/fill hypothesis |
| `0x06D1B` | やり (Yari) | 무기 | static-candidate+pointer | pad_7a | `91 7A` | `7A` | control/fill hypothesis |
| `0x06D1B` | やり (Yari) | 무기 | static-candidate+pointer | pad_ff | `91 FF` | `FF` | control/fill hypothesis |
| `0x06D1B` | やり (Yari) | 무기 | static-candidate+pointer | pad_f8f9 | `91 F8` | `F8` | control/fill hypothesis |
| `0x06D1B` | やり (Yari) | 무기 | static-candidate+pointer | preserve_tail | `91 A9` | `A9` | baseline: only first glyph byte changes |
| `0x06DE3` | おかね (Okane) | UI | static-candidate+pointer | pad_00 | `95 00 00` | `00 00` | control/fill hypothesis |
| `0x06DE3` | おかね (Okane) | UI | static-candidate+pointer | pad_7a | `95 7A 7A` | `7A 7A` | control/fill hypothesis |
| `0x06DE3` | おかね (Okane) | UI | static-candidate+pointer | pad_ff | `95 FF FF` | `FF FF` | control/fill hypothesis |
| `0x06DE3` | おかね (Okane) | UI | static-candidate+pointer | pad_f8f9 | `95 F8 F9` | `F8 F9` | control/fill hypothesis |
| `0x06DE3` | おかね (Okane) | UI | static-candidate+pointer | preserve_tail | `95 86 98` | `86 98` | baseline: only first glyph byte changes |
| `0x06FA1` | そうび (Soubi) | UI | static-candidate+pointer | pad_00 | `93 94 00` | `00` | control/fill hypothesis |
| `0x06FA1` | そうび (Soubi) | UI | static-candidate+pointer | pad_7a | `93 94 7A` | `7A` | control/fill hypothesis |
| `0x06FA1` | そうび (Soubi) | UI | static-candidate+pointer | pad_ff | `93 94 FF` | `FF` | control/fill hypothesis |
| `0x06FA1` | そうび (Soubi) | UI | static-candidate+pointer | pad_f8f9 | `93 94 F8` | `F8` | control/fill hypothesis |
| `0x06FA1` | そうび (Soubi) | UI | static-candidate+pointer | preserve_tail | `93 94 A8` | `A8` | baseline: only first glyph byte changes |
| `0x058FB` | やり (Yari) | 무기 | static-candidate | pad_00 | `91 00` | `00` | control/fill hypothesis |
| `0x058FB` | やり (Yari) | 무기 | static-candidate | pad_7a | `91 7A` | `7A` | control/fill hypothesis |
| `0x058FB` | やり (Yari) | 무기 | static-candidate | pad_ff | `91 FF` | `FF` | control/fill hypothesis |
| `0x058FB` | やり (Yari) | 무기 | static-candidate | pad_f8f9 | `91 F8` | `F8` | control/fill hypothesis |
| `0x058FB` | やり (Yari) | 무기 | static-candidate | preserve_tail | `91 A2` | `A2` | baseline: only first glyph byte changes |
| `0x06001` | やり (Yari) | 무기 | static-candidate | pad_00 | `91 00` | `00` | control/fill hypothesis |
| `0x06001` | やり (Yari) | 무기 | static-candidate | pad_7a | `91 7A` | `7A` | control/fill hypothesis |
| `0x06001` | やり (Yari) | 무기 | static-candidate | pad_ff | `91 FF` | `FF` | control/fill hypothesis |
| `0x06001` | やり (Yari) | 무기 | static-candidate | pad_f8f9 | `91 F8` | `F8` | control/fill hypothesis |
| `0x06001` | やり (Yari) | 무기 | static-candidate | preserve_tail | `91 A7` | `A7` | baseline: only first glyph byte changes |
| `0x06479` | やり (Yari) | 무기 | static-candidate | pad_00 | `91 00` | `00` | control/fill hypothesis |
| `0x06479` | やり (Yari) | 무기 | static-candidate | pad_7a | `91 7A` | `7A` | control/fill hypothesis |
| `0x06479` | やり (Yari) | 무기 | static-candidate | pad_ff | `91 FF` | `FF` | control/fill hypothesis |
| `0x06479` | やり (Yari) | 무기 | static-candidate | pad_f8f9 | `91 F8` | `F8` | control/fill hypothesis |
| `0x06479` | やり (Yari) | 무기 | static-candidate | preserve_tail | `91 A8` | `A8` | baseline: only first glyph byte changes |
| `0x065B0` | やり (Yari) | 무기 | static-candidate | pad_00 | `91 00` | `00` | control/fill hypothesis |
| `0x065B0` | やり (Yari) | 무기 | static-candidate | pad_7a | `91 7A` | `7A` | control/fill hypothesis |
| `0x065B0` | やり (Yari) | 무기 | static-candidate | pad_ff | `91 FF` | `FF` | control/fill hypothesis |
| `0x065B0` | やり (Yari) | 무기 | static-candidate | pad_f8f9 | `91 F8` | `F8` | control/fill hypothesis |
| `0x065B0` | やり (Yari) | 무기 | static-candidate | preserve_tail | `91 A9` | `A9` | baseline: only first glyph byte changes |
| `0x06605` | ちから (Chikara) | 능력치 | static-candidate | pad_00 | `87 00 00` | `00 00` | control/fill hypothesis |
| `0x06605` | ちから (Chikara) | 능력치 | static-candidate | pad_7a | `87 7A 7A` | `7A 7A` | control/fill hypothesis |
| `0x06605` | ちから (Chikara) | 능력치 | static-candidate | pad_ff | `87 FF FF` | `FF FF` | control/fill hypothesis |
| `0x06605` | ちから (Chikara) | 능력치 | static-candidate | pad_f8f9 | `87 F8 F9` | `F8 F9` | control/fill hypothesis |
| `0x06605` | ちから (Chikara) | 능력치 | static-candidate | preserve_tail | `87 88 AA` | `88 AA` | baseline: only first glyph byte changes |
| `0x06A3D` | やり (Yari) | 무기 | static-candidate | pad_00 | `91 00` | `00` | control/fill hypothesis |
| `0x06A3D` | やり (Yari) | 무기 | static-candidate | pad_7a | `91 7A` | `7A` | control/fill hypothesis |
| `0x06A3D` | やり (Yari) | 무기 | static-candidate | pad_ff | `91 FF` | `FF` | control/fill hypothesis |
| `0x06A3D` | やり (Yari) | 무기 | static-candidate | pad_f8f9 | `91 F8` | `F8` | control/fill hypothesis |
| `0x06A3D` | やり (Yari) | 무기 | static-candidate | preserve_tail | `91 A2` | `A2` | baseline: only first glyph byte changes |
| `0x06A66` | やり (Yari) | 무기 | static-candidate | pad_00 | `91 00` | `00` | control/fill hypothesis |
| `0x06A66` | やり (Yari) | 무기 | static-candidate | pad_7a | `91 7A` | `7A` | control/fill hypothesis |
| `0x06A66` | やり (Yari) | 무기 | static-candidate | pad_ff | `91 FF` | `FF` | control/fill hypothesis |
| `0x06A66` | やり (Yari) | 무기 | static-candidate | pad_f8f9 | `91 F8` | `F8` | control/fill hypothesis |
| `0x06A66` | やり (Yari) | 무기 | static-candidate | preserve_tail | `91 A2` | `A2` | baseline: only first glyph byte changes |
| `0x06B4A` | ちから (Chikara) | 능력치 | static-candidate | pad_00 | `87 00 00` | `00 00` | control/fill hypothesis |
| `0x06B4A` | ちから (Chikara) | 능력치 | static-candidate | pad_7a | `87 7A 7A` | `7A 7A` | control/fill hypothesis |
| `0x06B4A` | ちから (Chikara) | 능력치 | static-candidate | pad_ff | `87 FF FF` | `FF FF` | control/fill hypothesis |
| `0x06B4A` | ちから (Chikara) | 능력치 | static-candidate | pad_f8f9 | `87 F8 F9` | `F8 F9` | control/fill hypothesis |
| `0x06B4A` | ちから (Chikara) | 능력치 | static-candidate | preserve_tail | `87 88 AA` | `88 AA` | baseline: only first glyph byte changes |
| `0x06FDE` | やり (Yari) | 무기 | static-candidate | pad_00 | `91 00` | `00` | control/fill hypothesis |
| `0x06FDE` | やり (Yari) | 무기 | static-candidate | pad_7a | `91 7A` | `7A` | control/fill hypothesis |
| `0x06FDE` | やり (Yari) | 무기 | static-candidate | pad_ff | `91 FF` | `FF` | control/fill hypothesis |
| `0x06FDE` | やり (Yari) | 무기 | static-candidate | pad_f8f9 | `91 F8` | `F8` | control/fill hypothesis |
| `0x06FDE` | やり (Yari) | 무기 | static-candidate | preserve_tail | `91 A9` | `A9` | baseline: only first glyph byte changes |
| `0x0704F` | やり (Yari) | 무기 | static-candidate | pad_00 | `91 00` | `00` | control/fill hypothesis |
| `0x0704F` | やり (Yari) | 무기 | static-candidate | pad_7a | `91 7A` | `7A` | control/fill hypothesis |
| `0x0704F` | やり (Yari) | 무기 | static-candidate | pad_ff | `91 FF` | `FF` | control/fill hypothesis |
| `0x0704F` | やり (Yari) | 무기 | static-candidate | pad_f8f9 | `91 F8` | `F8` | control/fill hypothesis |
| `0x0704F` | やり (Yari) | 무기 | static-candidate | preserve_tail | `91 A3` | `A3` | baseline: only first glyph byte changes |

## Recommended FCEUX Check

1. Start with the runtime-confirmed target `ROM+0x071A4` (`ちから`/Chikara -> `힘`).
2. Build one experimental ROM per padding strategy from this plan.
3. In FCEUX, reach the same status screen/read-watch route that confirmed `$B192-$B19C`.
4. Accept a strategy only if the visible label renders cleanly and neighboring status fields remain intact.
5. If more than one strategy works visually, prefer the one that matches observed control/fill behavior elsewhere in the same record family.

## Notes

- `preserve_tail` is a baseline, not a final translation: it changes only the first planned glyph byte and leaves the old tail bytes.
- `pad_00`, `pad_7a`, `pad_ff`, and `pad_f8f9` are hypotheses that need screen verification before any final patch.
