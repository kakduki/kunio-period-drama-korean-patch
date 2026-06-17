# Bank 1 Offset Status

This report summarizes current offset coverage by category and patch-readiness.

## Summary

- Total Bank 1 targets: `43`
- Runtime-confirmed targets: `2`
- Watch-range targets: `8`
- Watch-range blocks: `73`
- Watch-range translation hits: `9`
- Watch-range distinct equal-length candidates: `8`

## Category Status

| group | translation categories | targets | runtime-confirmed | watch-range | safe equal-length | needs padding | missing translation categories |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| items/equipment | 무기, 방어구, 특수, 회복 | 25 | 1 | 1 | 5 | 20 | 방어구, 특수 |
| menu | 메뉴, 모드, 타이틀 | 0 | 0 | 0 | 0 | 0 | 메뉴, 모드, 타이틀 |
| UI/status | UI, 능력치, 캐릭터명 | 11 | 1 | 0 | 2 | 9 | 캐릭터명 |
| event/dialogue-related | 기술, 대사, 보스, 스테이지, 엔딩, 이벤트 | 7 | 0 | 7 | 7 | 0 | 기술, 대사, 엔딩, 이벤트 |
| other | - | 0 | 0 | 0 | 0 | 0 | - |

## Priority Offsets

### items/equipment

Runtime-confirmed:
- `0x07227` カタナ (Katana)->카타나 (무기, runtime-confirmed, safe-equal-length)
Equal-length candidates needing runtime screen confirmation:
- `0x05644` カタナ (Katana)->카타나 (무기, static-candidate+pointer, safe-equal-length)
- `0x06295` カタナ (Katana)->카타나 (무기, static-candidate+pointer, safe-equal-length)
- `0x0631C` カタナ (Katana)->카타나 (무기, static-candidate+pointer, safe-equal-length)
- `0x0635A` カタナ (Katana)->카타나 (무기, static-candidate, safe-equal-length)
Padding-rule blockers:
- `0x058FB` やり (Yari)->창 (무기, static-candidate, needs-padding-rule)
- `0x05AA3` やり (Yari)->창 (무기, static-candidate+pointer, needs-padding-rule)
- `0x05AA5` やり (Yari)->창 (무기, static-candidate+pointer, needs-padding-rule)
- `0x05BBA` やり (Yari)->창 (무기, static-candidate+pointer, needs-padding-rule; runtime hits 710, active 0)
- `0x05BDF` くすり (Kusuri)->약 (회복, static-candidate+pointer, needs-padding-rule)
- `0x05C09` やり (Yari)->창 (무기, static-candidate+pointer, needs-padding-rule)
- `0x05C69` やり (Yari)->창 (무기, static-candidate+pointer, needs-padding-rule)
- `0x06001` やり (Yari)->창 (무기, static-candidate, needs-padding-rule; runtime hits 35, active 0)

### menu

_No current targets._

### UI/status

Runtime-confirmed:
- `0x071A4` ちから (Chikara)->힘 (능력치, runtime-confirmed, needs-padding-rule; runtime hits 1797, active 11)
Equal-length candidates needing runtime screen confirmation:
- `0x0736A` ライフ (Raifu)->라이프 (UI, static-candidate+pointer, safe-equal-length; runtime hits 10429, active 0)
- `0x0739D` ライフ (Raifu)->라이프 (UI, static-candidate+pointer, safe-equal-length)
Padding-rule blockers:
- `0x0602E` そうび (Soubi)->장비 (UI, static-candidate+pointer, needs-padding-rule; runtime hits 54, active 0)
- `0x06605` ちから (Chikara)->힘 (능력치, static-candidate, needs-padding-rule)
- `0x066FB` ちから (Chikara)->힘 (능력치, static-candidate+pointer, needs-padding-rule; runtime hits 546, active 0)
- `0x06845` ちから (Chikara)->힘 (능력치, static-candidate+pointer, needs-padding-rule)
- `0x06B4A` ちから (Chikara)->힘 (능력치, static-candidate, needs-padding-rule; runtime hits 1708, active 0)
- `0x06BDF` そうび (Soubi)->장비 (UI, static-candidate+pointer, needs-padding-rule; runtime hits 72, active 0)
- `0x06DE3` おかね (Okane)->돈 (UI, static-candidate+pointer, needs-padding-rule; runtime hits 4264, active 0)

### event/dialogue-related

Equal-length candidates needing runtime screen confirmation:
- `0x0561A` はし (Hashi)->다리 (스테이지, static-candidate+pointer, safe-equal-length)
- `0x0562F` たついち (Tatsuichi)->타츠이치 (보스, static-candidate, safe-equal-length)
- `0x05643` へいしち (Heishichi)->헤이시치 (보스, static-candidate+pointer, safe-equal-length)
- `0x0569D` はし (Hashi)->다리 (스테이지, encoding-exact, safe-equal-length)
- `0x056DA` はし (Hashi)->다리 (스테이지, static-candidate, safe-equal-length)
- `0x0571C` はし (Hashi)->다리 (스테이지, static-candidate, safe-equal-length)
- `0x057D4` はし (Hashi)->다리 (스테이지, static-candidate+pointer, safe-equal-length)

### other

_No current targets._

## Current Gaps

- Menu/title/mode strings are present in `translation_data.txt`, but no Bank 1 menu-category target is currently identified.
- Event/dialogue work is still mostly static candidate evidence; no full dialogue block is runtime-confirmed yet.
- Shortened Korean replacements such as `ちから` -> `힘`, `やり` -> `창`, `そうび` -> `장비`, and `おかね` -> `돈` remain blocked on padding/terminator behavior.
- Equal-length static candidates can be used as FCEUX breakpoint/watch priorities, but should not be promoted to final patch offsets until the corresponding screen is observed.
