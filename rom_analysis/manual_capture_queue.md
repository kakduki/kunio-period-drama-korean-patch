# Manual FCEUX Capture Queue

Use this queue after manually reaching a real dialogue/menu/status screen in FCEUX.
Do not extend blind autoplay runs when the emulator is still on the opening/title screen.

Workflow:

1. Manually reach the listed kind of screen in FCEUX.
2. Run `lua/kunio_manual_screen_dump.lua` from FCEUX's Lua window.
3. Run `python scripts/analyze_manual_screen_dump.py`.
4. Promote a patch candidate only when the screen-specific evidence supports it.

## Summary

- Total targets in status report: **43**
- Queued high-value targets: **27**
- Safe equal-length targets needing screen proof: **13**
- Runtime-confirmed padding blockers: **1**
- Runtime-hit/wrong-context targets: **14**

## Queue

| priority | reason | group | source | romaji/context | Korean | ROM hit | CPU range | expected | evidence | risk |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | safe equal-length item/equipment candidate; needs screen proof | items/equipment | `カタナ` | Katana<br>4.1 무기류 | `카타나` | `0x05644` | `$9633-$9637` | `82 8C 91` | static-candidate+pointer | safe-equal-length |
| 10 | safe equal-length item/equipment candidate; needs screen proof | items/equipment | `カタナ` | Katana<br>4.1 무기류 | `카타나` | `0x06295` | `$A284-$A28E` | `82 8C 91` | static-candidate+pointer | safe-equal-length |
| 10 | safe equal-length item/equipment candidate; needs screen proof | items/equipment | `カタナ` | Katana<br>4.1 무기류 | `카타나` | `0x0631C` | `$A309-$A314` | `82 8C 91` | static-candidate+pointer | safe-equal-length |
| 10 | safe equal-length item/equipment candidate; needs screen proof | items/equipment | `カタナ` | Katana<br>4.1 무기류 | `카타나` | `0x0635A` | `$A349-$A352` | `82 8C 91` | static-candidate | safe-equal-length |
| 15 | safe equal-length UI/status candidate; needs screen proof | UI/status | `ライフ` | Raifu<br>3. 스테이터스 / UI 텍스트 | `라이프` | `0x0736A` | `$B359-$B35E` | `BB 95 AF` | static-candidate+pointer | safe-equal-length |
| 15 | safe equal-length UI/status candidate; needs screen proof | UI/status | `ライフ` | Raifu<br>3. 스테이터스 / UI 텍스트 | `라이프` | `0x0739D` | `$B38C-$B391` | `BB 95 AF` | static-candidate+pointer | safe-equal-length |
| 20 | safe equal-length event/dialogue candidate; needs screen proof | event/dialogue-related | `はし` | Hashi<br>7. 스테이지 / 지역 이름 | `다리` | `0x0561A` | `$95BE-$960F` | `96 88` | static-candidate+pointer | safe-equal-length |
| 20 | safe equal-length event/dialogue candidate; needs screen proof | event/dialogue-related | `たついち` | Tatsuichi<br>6.1 스테이지 보스 | `타츠이치` | `0x0562F` | `$961A-$9623` | `90 92 82 91` | static-candidate | safe-equal-length |
| 20 | safe equal-length event/dialogue candidate; needs screen proof | event/dialogue-related | `へいしち` | Heishichi<br>6.2 아군/조력 캐릭터 | `헤이시치` | `0x05643` | `$9633-$9637` | `9D 82 8C 91` | static-candidate+pointer | safe-equal-length |
| 20 | safe equal-length event/dialogue candidate; needs screen proof | event/dialogue-related | `はし` | Hashi<br>7. 스테이지 / 지역 이름 | `다리` | `0x0569D` | `$968C-$968F` | `A0 92` | encoding-exact | safe-equal-length |
| 20 | safe equal-length event/dialogue candidate; needs screen proof | event/dialogue-related | `はし` | Hashi<br>7. 스테이지 / 지역 이름 | `다리` | `0x056DA` | `$96C5-$96CE` | `9A 8C` | static-candidate | safe-equal-length |
| 20 | safe equal-length event/dialogue candidate; needs screen proof | event/dialogue-related | `はし` | Hashi<br>7. 스테이지 / 지역 이름 | `다리` | `0x0571C` | `$9706-$9714` | `92 84` | static-candidate | safe-equal-length |
| 20 | safe equal-length event/dialogue candidate; needs screen proof | event/dialogue-related | `はし` | Hashi<br>7. 스테이지 / 지역 이름 | `다리` | `0x057D4` | `$97C4-$97C8` | `A6 98` | static-candidate+pointer | safe-equal-length |
| 30 | runtime-confirmed shortened replacement; needs visual padding rule | UI/status | `ちから` | Chikara<br>3. 스테이터스 / UI 텍스트 | `힘` | `0x071A4` | `$B192-$B19C` | `93 88 AA` | runtime-confirmed | needs-padding-rule |
| 45 | runtime address hit but wrong active bank/context; capture exact screen | UI/status | `そうび` | Soubi<br>3. 스테이터스 / UI 텍스트 | `장비` | `0x0602E` | `$A01A-$A02B` | `9C 90 A8` | static-candidate+pointer | needs-padding-rule |
| 45 | runtime address hit but wrong active bank/context; capture exact screen | UI/status | `ちから` | Chikara<br>3. 스테이터스 / UI 텍스트 | `힘` | `0x066FB` | `$A6EA-$A6F2` | `93 88 AA` | static-candidate+pointer | needs-padding-rule |
| 45 | runtime address hit but wrong active bank/context; capture exact screen | UI/status | `ちから` | Chikara<br>3. 스테이터스 / UI 텍스트 | `힘` | `0x06B4A` | `$AB32-$AB3F` | `93 88 AA` | static-candidate | needs-padding-rule |
| 45 | runtime address hit but wrong active bank/context; capture exact screen | UI/status | `そうび` | Soubi<br>3. 스테이터스 / UI 텍스트 | `장비` | `0x06BDF` | `$ABCB-$ABD3` | `9C 90 A8` | static-candidate+pointer | needs-padding-rule |
| 45 | runtime address hit but wrong active bank/context; capture exact screen | UI/status | `おかね` | Okane<br>3. 스테이터스 / UI 텍스트 | `돈` | `0x06DE3` | `$ADD1-$ADD7` | `85 86 98` | static-candidate+pointer | needs-padding-rule |
| 45 | runtime address hit but wrong active bank/context; capture exact screen | UI/status | `そうび` | Soubi<br>3. 스테이터스 / UI 텍스트 | `장비` | `0x06FA1` | `$AF91-$AF9A` | `9C 90 A8` | static-candidate+pointer | needs-padding-rule |
| 45 | runtime address hit but wrong active bank/context; capture exact screen | items/equipment | `やり` | Yari<br>4.1 무기류 | `창` | `0x05BBA` | `$9BA5-$9BAD` | `9F A3` | static-candidate+pointer | needs-padding-rule |
| 45 | runtime address hit but wrong active bank/context; capture exact screen | items/equipment | `やり` | Yari<br>4.1 무기류 | `창` | `0x06001` | `$9FEB-$9FF8` | `A3 A7` | static-candidate | needs-padding-rule |
| 45 | runtime address hit but wrong active bank/context; capture exact screen | items/equipment | `やり` | Yari<br>4.1 무기류 | `창` | `0x06479` | `$A468-$A471` | `A4 A8` | static-candidate | needs-padding-rule |
| 45 | runtime address hit but wrong active bank/context; capture exact screen | items/equipment | `やり` | Yari<br>4.1 무기류 | `창` | `0x069C5` | `$A9B5-$A9BC` | `9E A2` | static-candidate+pointer | needs-padding-rule |
| 45 | runtime address hit but wrong active bank/context; capture exact screen | items/equipment | `やり` | Yari<br>4.1 무기류 | `창` | `0x06A3D` | `$AA2D-$AA36` | `9E A2` | static-candidate | needs-padding-rule |
| 45 | runtime address hit but wrong active bank/context; capture exact screen | items/equipment | `やり` | Yari<br>4.1 무기류 | `창` | `0x06A66` | `$AA56-$AA5D` | `9E A2` | static-candidate | needs-padding-rule |
| 45 | runtime address hit but wrong active bank/context; capture exact screen | items/equipment | `やり` | Yari<br>4.1 무기류 | `창` | `0x06BC6` | `$ABAF-$ABBA` | `A0 A4` | static-candidate+pointer | needs-padding-rule |

## Notes

- Priority 10-20 rows are the best next candidates because they are equal-length and should not need padding rules.
- Priority 30 rows are important but blocked until the exact visual padding/terminator behavior is proven.
- Priority 45 rows already produced runtime reads in earlier automation, but the active bytes did not match; these need the exact screen/context.
