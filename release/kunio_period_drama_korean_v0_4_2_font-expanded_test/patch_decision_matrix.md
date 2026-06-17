# Patch Decision Matrix

This file ranks the remaining Korean patch decisions after the current primary candidate.

## Summary

- Current primary: **v0.4.2 font-expanded**
- Applied in primary: **10**
- Skipped from primary: **33**
- Non-overlapping broad candidates: **4**
- High-value next checks: **22**

## Rules

- Do not extend blind autoplay after stagnant_screen; switch to manual capture.
- Do not promote needs-padding-rule rows until a visual padding strategy is proven.
- Do not patch v0.4/broad overlaps until a manually reached screen identifies the correct interpretation.
- A YouTube transcript can identify expected text, but ROM offset promotion still requires byte/runtime/screen evidence.

## Highest-Value Next Checks

| priority | kind | ROM hit | expected text | Korean | screen hint | evidence/risk | next action |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10 | `conflict_needs_manual_screen` | `0x06295` | かたな | 카타나 | look for a katana/weapon item label | static-candidate+pointer / safe-equal-length | Use base ROM broad-scan dump first, then decide whether to keep v0.4.1 exclusion or replace with broad interpretation. |
| 10 | `conflict_needs_manual_screen` | `0x0631C` | かたな | 카타나 | look for a katana/weapon item label | static-candidate+pointer / safe-equal-length | Use base ROM broad-scan dump first, then decide whether to keep v0.4.1 exclusion or replace with broad interpretation. |
| 10 | `conflict_needs_manual_screen` | `0x0635A` | かたな | 카타나 | look for a katana/weapon item label | static-candidate / safe-equal-length | Use base ROM broad-scan dump first, then decide whether to keep v0.4.1 exclusion or replace with broad interpretation. |
| 10 | `local_overlap_needs_manual_screen` | `0x05644` | はし | 다리 | look for a bridge/stage/location label | static-candidate+pointer / safe-equal-length | Manually capture this exact screen; the nearby applied row may represent a different overlapping interpretation. |
| 30 | `runtime_padding_rule_blocker` | `0x071A4` | ちから | 힘 | look for a strength/status stat label | runtime-confirmed / needs-padding-rule | Test padding experiment ROMs visually on the same status screen before promoting a shortened replacement. |
| 35 | `broad_non_overlapping` | `0x0440C` | かじや | 대장간 | look for a blacksmith/shop or blacksmith-stage label | medium / safe-equal-length after screen proof | Capture on base ROM; if confirmed, extend glyph plan and build a separate v0.5 experiment. |
| 35 | `broad_non_overlapping` | `0x048F4` | たつじ | 타츠지 | look for a visible Tatsuji boss/name context | medium / safe-equal-length after screen proof | Capture on base ROM; if confirmed, extend glyph plan and build a separate v0.5 experiment. |
| 35 | `broad_non_overlapping` | `0x052A5` | たつじ | 타츠지 | look for a visible Tatsuji boss/name context | medium / safe-equal-length after screen proof | Capture on base ROM; if confirmed, extend glyph plan and build a separate v0.5 experiment. |
| 35 | `broad_non_overlapping` | `0x05BE5` | たつじ | 타츠지 | look for a visible Tatsuji boss/name context | medium / safe-equal-length after screen proof | Capture on base ROM; if confirmed, extend glyph plan and build a separate v0.5 experiment. |
| 45 | `wrong_context_or_padding_candidate` | `0x05BBA` | やり | 창 | look for a spear/weapon item label | static-candidate+pointer / needs-padding-rule | Capture the exact screen manually; previous autoplay read hits used the wrong active bank/context. |
| 45 | `wrong_context_or_padding_candidate` | `0x06001` | やり | 창 | look for a spear/weapon item label | static-candidate / needs-padding-rule | Capture the exact screen manually; previous autoplay read hits used the wrong active bank/context. |
| 45 | `wrong_context_or_padding_candidate` | `0x0602E` | そうび | 장비 | - | static-candidate+pointer / needs-padding-rule | Capture the exact screen manually; previous autoplay read hits used the wrong active bank/context. |
| 45 | `wrong_context_or_padding_candidate` | `0x06479` | やり | 창 | - | static-candidate / needs-padding-rule | Capture the exact screen manually; previous autoplay read hits used the wrong active bank/context. |
| 45 | `wrong_context_or_padding_candidate` | `0x066FB` | ちから | 힘 | - | static-candidate+pointer / needs-padding-rule | Capture the exact screen manually; previous autoplay read hits used the wrong active bank/context. |
| 45 | `wrong_context_or_padding_candidate` | `0x069C5` | やり | 창 | - | static-candidate+pointer / needs-padding-rule | Capture the exact screen manually; previous autoplay read hits used the wrong active bank/context. |
| 45 | `wrong_context_or_padding_candidate` | `0x06A3D` | やり | 창 | - | static-candidate / needs-padding-rule | Capture the exact screen manually; previous autoplay read hits used the wrong active bank/context. |
| 45 | `wrong_context_or_padding_candidate` | `0x06A66` | やり | 창 | - | static-candidate / needs-padding-rule | Capture the exact screen manually; previous autoplay read hits used the wrong active bank/context. |
| 45 | `wrong_context_or_padding_candidate` | `0x06B4A` | ちから | 힘 | - | static-candidate / needs-padding-rule | Capture the exact screen manually; previous autoplay read hits used the wrong active bank/context. |
| 45 | `wrong_context_or_padding_candidate` | `0x06BC6` | やり | 창 | - | static-candidate+pointer / needs-padding-rule | Capture the exact screen manually; previous autoplay read hits used the wrong active bank/context. |
| 45 | `wrong_context_or_padding_candidate` | `0x06BDF` | そうび | 장비 | - | static-candidate+pointer / needs-padding-rule | Capture the exact screen manually; previous autoplay read hits used the wrong active bank/context. |

## Full Matrix

| priority | status | kind | ROM hit | expected text | label | bytes | reason |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10 | skipped | `conflict_needs_manual_screen` | `0x06295` | かたな -> 카타나 | `rom_06295_candidate_7c` | `82 8C 91` | safe equal-length item/equipment candidate; needs screen proof |
| 10 | skipped | `conflict_needs_manual_screen` | `0x0631C` | かたな -> 카타나 | `rom_0631c_candidate_7c` | `82 8C 91` | safe equal-length item/equipment candidate; needs screen proof |
| 10 | skipped | `conflict_needs_manual_screen` | `0x0635A` | かたな -> 카타나 | `rom_0635a_candidate_7c` | `82 8C 91` | safe equal-length item/equipment candidate; needs screen proof |
| 10 | skipped | `local_overlap_needs_manual_screen` | `0x05644` | はし -> 다리 | `rom_05644_candidate_7c` | `82 8C 91` | safe equal-length item/equipment candidate; needs screen proof |
| 15 | applied | `applied` | `0x0736A` | ライフ -> 라이프 | `rom_0736a_candidate_93` | `BB 95 AF -> 96 8E 97` | safe equal-length UI/status candidate; needs screen proof |
| 15 | applied | `applied` | `0x0739D` | ライフ -> 라이프 | `rom_0739d_candidate_93` | `BB 95 AF -> 96 8E 97` | safe equal-length UI/status candidate; needs screen proof |
| 20 | applied | `applied` | `0x0561A` | はし -> 다리 | `watch_rom_0561a_스테이지_7c` | `96 88 -> 8B 8C` | safe equal-length event/dialogue candidate; needs screen proof |
| 20 | applied | `applied` | `0x0562F` | たついち -> 타츠이치 | `watch_rom_0562f_보스_80` | `90 92 82 91 -> 89 98 8E 90` | safe equal-length event/dialogue candidate; needs screen proof |
| 20 | applied | `applied` | `0x05643` | へいしち -> 헤이시치 | `watch_rom_05643_보스_80` | `9D 82 8C 91 -> 8D 8E 8F 90` | safe equal-length event/dialogue candidate; needs screen proof |
| 20 | applied | `applied` | `0x0569D` | はし -> 다리 | `watch_rom_0569d_스테이지_7a` | `A0 92 -> 8B 8C` | safe equal-length event/dialogue candidate; needs screen proof |
| 20 | applied | `applied` | `0x056DA` | はし -> 다리 | `watch_rom_056da_스테이지_80` | `9A 8C -> 8B 8C` | safe equal-length event/dialogue candidate; needs screen proof |
| 20 | applied | `applied` | `0x0571C` | はし -> 다리 | `watch_rom_0571c_스테이지_78` | `92 84 -> 8B 8C` | safe equal-length event/dialogue candidate; needs screen proof |
| 20 | applied | `applied` | `0x057D4` | はし -> 다리 | `watch_rom_057d4_스테이지_8c` | `A6 98 -> 8B 8C` | safe equal-length event/dialogue candidate; needs screen proof |
| 25 | applied | `applied` | `0x07227` | かたな -> 카타나 | `rom_07227_candidate_84` | `8A 94 99 -> 88 89 8A` | applied candidate still needs visual proof |
| 30 | skipped | `runtime_padding_rule_blocker` | `0x071A4` | ちから -> 힘 | `rom_071a4_candidate_82` | `93 88 AA` | runtime-confirmed shortened replacement; needs visual padding rule |
| 35 | broad_candidate | `broad_non_overlapping` | `0x0440C` | かじや -> 대장간 | `broad_0x0440C` | `CA D0 E9` | non-overlapping broad-scan candidate; not in v0.4.1 yet |
| 35 | broad_candidate | `broad_non_overlapping` | `0x048F4` | たつじ -> 타츠지 | `broad_0x048F4` | `07 09 03` | non-overlapping broad-scan candidate; not in v0.4.1 yet |
| 35 | broad_candidate | `broad_non_overlapping` | `0x052A5` | たつじ -> 타츠지 | `broad_0x052A5` | `82 84 7E` | non-overlapping broad-scan candidate; not in v0.4.1 yet |
| 35 | broad_candidate | `broad_non_overlapping` | `0x05BE5` | たつじ -> 타츠지 | `broad_0x05BE5` | `97 99 93` | non-overlapping broad-scan candidate; not in v0.4.1 yet |
| 45 | skipped | `wrong_context_or_padding_candidate` | `0x05BBA` | やり -> 창 | `rom_05bba_candidate_7a` | `9F A3` | runtime address hit but wrong active bank/context; capture exact screen |
| 45 | skipped | `wrong_context_or_padding_candidate` | `0x06001` | やり -> 창 | `rom_06001_candidate_7e` | `A3 A7` | runtime address hit but wrong active bank/context; capture exact screen |
| 45 | skipped | `wrong_context_or_padding_candidate` | `0x0602E` | そうび -> 장비 | `rom_0602e_candidate_8d` | `9C 90 A8` | runtime address hit but wrong active bank/context; capture exact screen |
| 45 | skipped | `wrong_context_or_padding_candidate` | `0x06479` | やり -> 창 | `rom_06479_candidate_7f` | `A4 A8` | runtime address hit but wrong active bank/context; capture exact screen |
| 45 | skipped | `wrong_context_or_padding_candidate` | `0x066FB` | ちから -> 힘 | `rom_066fb_candidate_82` | `93 88 AA` | runtime address hit but wrong active bank/context; capture exact screen |
| 45 | skipped | `wrong_context_or_padding_candidate` | `0x069C5` | やり -> 창 | `rom_069c5_candidate_79` | `9E A2` | runtime address hit but wrong active bank/context; capture exact screen |
| 45 | skipped | `wrong_context_or_padding_candidate` | `0x06A3D` | やり -> 창 | `rom_06a3d_candidate_79` | `9E A2` | runtime address hit but wrong active bank/context; capture exact screen |
| 45 | skipped | `wrong_context_or_padding_candidate` | `0x06A66` | やり -> 창 | `rom_06a66_candidate_79` | `9E A2` | runtime address hit but wrong active bank/context; capture exact screen |
| 45 | skipped | `wrong_context_or_padding_candidate` | `0x06B4A` | ちから -> 힘 | `rom_06b4a_candidate_82` | `93 88 AA` | runtime address hit but wrong active bank/context; capture exact screen |
| 45 | skipped | `wrong_context_or_padding_candidate` | `0x06BC6` | やり -> 창 | `rom_06bc6_candidate_7b` | `A0 A4` | runtime address hit but wrong active bank/context; capture exact screen |
| 45 | skipped | `wrong_context_or_padding_candidate` | `0x06BDF` | そうび -> 장비 | `rom_06bdf_candidate_8d` | `9C 90 A8` | runtime address hit but wrong active bank/context; capture exact screen |
| 45 | skipped | `wrong_context_or_padding_candidate` | `0x06DE3` | おかね -> 돈 | `rom_06de3_candidate_80` | `85 86 98` | runtime address hit but wrong active bank/context; capture exact screen |
| 45 | skipped | `wrong_context_or_padding_candidate` | `0x06FA1` | そうび -> 장비 | `rom_06fa1_candidate_8d` | `9C 90 A8` | runtime address hit but wrong active bank/context; capture exact screen |
| 80 | skipped | `padding_rule_blocker` | `0x058FB` | やり -> 창 | `rom_058fb_candidate_79` | `` | patch risk 'needs-padding-rule' not selected |
| 80 | skipped | `padding_rule_blocker` | `0x05AA3` | やり -> 창 | `rom_05aa3_candidate_77` | `` | patch risk 'needs-padding-rule' not selected |
| 80 | skipped | `padding_rule_blocker` | `0x05AA5` | やり -> 창 | `rom_05aa5_candidate_77` | `` | patch risk 'needs-padding-rule' not selected |
| 80 | skipped | `padding_rule_blocker` | `0x05BDF` | くすり -> 약 | `rom_05bdf_candidate_7a` | `` | patch risk 'needs-padding-rule' not selected |
| 80 | skipped | `padding_rule_blocker` | `0x05C09` | やり -> 창 | `rom_05c09_candidate_7a` | `` | patch risk 'needs-padding-rule' not selected |
| 80 | skipped | `padding_rule_blocker` | `0x05C69` | やり -> 창 | `rom_05c69_candidate_7a` | `` | patch risk 'needs-padding-rule' not selected |
| 80 | skipped | `padding_rule_blocker` | `0x065B0` | やり -> 창 | `rom_065b0_candidate_80` | `` | patch risk 'needs-padding-rule' not selected |
| 80 | skipped | `padding_rule_blocker` | `0x06605` | ちから -> 힘 | `rom_06605_candidate_82` | `` | patch risk 'needs-padding-rule' not selected |
| 80 | skipped | `padding_rule_blocker` | `0x06839` | やり -> 창 | `rom_06839_candidate_7e` | `` | patch risk 'needs-padding-rule' not selected |
| 80 | skipped | `padding_rule_blocker` | `0x06845` | ちから -> 힘 | `rom_06845_candidate_82` | `` | patch risk 'needs-padding-rule' not selected |
| 80 | skipped | `padding_rule_blocker` | `0x068C3` | やり -> 창 | `rom_068c3_candidate_71` | `` | patch risk 'needs-padding-rule' not selected |
| 80 | skipped | `padding_rule_blocker` | `0x0691E` | やり -> 창 | `rom_0691e_candidate_80` | `` | patch risk 'needs-padding-rule' not selected |
| 80 | skipped | `padding_rule_blocker` | `0x06D1B` | やり -> 창 | `rom_06d1b_candidate_80` | `` | patch risk 'needs-padding-rule' not selected |
| 80 | skipped | `padding_rule_blocker` | `0x06FDE` | やり -> 창 | `rom_06fde_candidate_80` | `` | patch risk 'needs-padding-rule' not selected |
| 80 | skipped | `padding_rule_blocker` | `0x0704F` | やり -> 창 | `rom_0704f_candidate_7a` | `` | patch risk 'needs-padding-rule' not selected |
