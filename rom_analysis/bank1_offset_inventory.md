# Bank 1 Text Offset Inventory

This inventory consolidates the current Bank 1 translation candidates with runtime read-watch evidence.

- Source targets: `rom_analysis\bank1_watch_targets.json`
- Supplemental watch-range candidates: generated from `translation_data.txt` hits inside `ROM+0x05610-0x05810`
- Watch range: `ROM+0x05610-ROM+0x05810`
- Total targets: **43**
- Runtime-confirmed targets: **2**
- Targets inside watch range: **8**

Evidence levels:

- `runtime-confirmed`: FCEUX read-watch or preserved runtime evidence saw the expected bytes active in memory.
- `encoding-exact`: exact `plus-0x7A` encoding match, but without active runtime read evidence yet.
- `static-candidate+pointer`: translation-data match plus at least one raw pointer reference.
- `static-candidate`: translation-data match only; use as breakpoint/search target.

## Runtime-confirmed offsets

| evidence | ROM hit | record ROM | CPU range | category | Japanese | Korean | mode/base | bytes | decoded record | runtime |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| runtime-confirmed | `0x071A4` | `0x071A2-0x071AC` | `$B192-$B19C` | 능력치 | ちから | 힘 | shifted-low/`0x82` | `93 88 AA` | `へ<B4>ちからもあ<CA><F8><F9>` | 1797 hits, active 11, frames 478-3301 |
| runtime-confirmed | `0x07227` | `0x07226-0x0722A` | `$B216-$B21A` | 무기 | カタナ | 카타나 | shifted-low/`0x84` | `8A 94 99` | `あかたな` | - |

## Watch range: ROM+0x05610-0x05810

| evidence | ROM hit | record ROM | CPU range | category | Japanese | Korean | mode/base | bytes | decoded record | runtime |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| static-candidate+pointer | `0x0561A` | `0x055CE-0x0561F` | `$95BE-$960F` | 스테이지 | はし | 다리 | shifted-low/`0x7C` | `96 88` | `<7B><15>は<15>は<15>は<15>は<15>は<15>は<15>は<15>は<15>は<15>は<05><7B...` | - |
| static-candidate | `0x0562F` | `0x0562A-0x05633` | `$961A-$9623` | 보스 | たついち | 타츠이치 | shifted-low/`0x80` | `90 92 82 91` | `<0C><B6>うきちたついち` | - |
| static-candidate+pointer | `0x05643` | `0x05643-0x05647` | `$9633-$9637` | 보스 | へいしち | 헤이시치 | shifted-low/`0x80` | `9D 82 8C 91` | `へいしち` | - |
| static-candidate+pointer | `0x05644` | `0x05643-0x05647` | `$9633-$9637` | 무기 | カタナ | 카타나 | shifted-low/`0x7C` | `82 8C 91` | `みかたな` | - |
| encoding-exact | `0x0569D` | `0x0569C-0x0569F` | `$968C-$968F` | 스테이지 | はし | 다리 | plus-0x7A/`0x7A` | `A0 92` | `<85>はし` | - |
| static-candidate | `0x056DA` | `0x056D5-0x056DE` | `$96C5-$96CE` | 스테이지 | はし | 다리 | shifted-low/`0x80` | `9A 8C` | `は<07>のすけはし<0F>う` | - |
| static-candidate | `0x0571C` | `0x05716-0x05724` | `$9706-$9714` | 스테이지 | はし | 다리 | shifted-low/`0x78` | `92 84` | `にそ<0A><AB>さをはしれ<AE>ふれよは` | - |
| static-candidate+pointer | `0x057D4` | `0x057D4-0x057D8` | `$97C4-$97C8` | 스테이지 | はし | 다리 | shifted-low/`0x8C` | `A6 98` | `はしあ<89>` | - |

## UI/status

| evidence | ROM hit | record ROM | CPU range | category | Japanese | Korean | mode/base | bytes | decoded record | runtime |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| runtime-confirmed | `0x071A4` | `0x071A2-0x071AC` | `$B192-$B19C` | 능력치 | ちから | 힘 | shifted-low/`0x82` | `93 88 AA` | `へ<B4>ちからもあ<CA><F8><F9>` | 1797 hits, active 11, frames 478-3301 |
| static-candidate+pointer | `0x0602E` | `0x0602A-0x0603B` | `$A01A-$A02B` | UI | そうび | 장비 | shifted-low/`0x8D` | `9C 90 A8` | `てる<83>くそうひ<08>て<06><82>ぬ<8C>うさ<F8><F9>` | 54 hits, active 0, frames 3165-3182 |
| static-candidate | `0x06605` | `0x065FE-0x06608` | `$A5EE-$A5F8` | 능력치 | ちから | 힘 | shifted-low/`0x82` | `93 88 AA` | `<14>されあきつ<B4>ちから` | - |
| static-candidate+pointer | `0x066FB` | `0x066FA-0x06702` | `$A6EA-$A6F2` | 능력치 | ちから | 힘 | shifted-low/`0x82` | `93 88 AA` | `こちからに<B2>えを` | 546 hits, active 0, frames 854-3300 |
| static-candidate+pointer | `0x06845` | `0x0683E-0x06848` | `$A82E-$A838` | 능력치 | ちから | 힘 | shifted-low/`0x82` | `93 88 AA` | `<81><B4>ことへえこちから` | - |
| static-candidate | `0x06B4A` | `0x06B42-0x06B4F` | `$AB32-$AB3F` | 능력치 | ちから | 힘 | shifted-low/`0x82` | `93 88 AA` | `<81><B4>これたらち<B4>ちから<B4><CA>` | 1708 hits, active 0, frames 3161-3301 |
| static-candidate+pointer | `0x06BDF` | `0x06BDB-0x06BE3` | `$ABCB-$ABD3` | UI | そうび | 장비 | shifted-low/`0x8D` | `9C 90 A8` | `<81>よ<8C>はそうひ<06>` | 72 hits, active 0, frames 3161-3165 |
| static-candidate+pointer | `0x06DE3` | `0x06DE1-0x06DE7` | `$ADD1-$ADD7` | UI | おかね | 돈 | shifted-low/`0x80` | `85 86 98` | `<F0><BB>おかね<06>` | 4264 hits, active 0, frames 3165-3300 |
| static-candidate+pointer | `0x06FA1` | `0x06FA1-0x06FAA` | `$AF91-$AF9A` | UI | そうび | 장비 | shifted-low/`0x8D` | `9C 90 A8` | `そうひ<08>て<13><CB><F8><F9>` | 1117 hits, active 0, frames 724-3301 |
| static-candidate+pointer | `0x0736A` | `0x07369-0x0736E` | `$B359-$B35E` | UI | ライフ | 라이프 | shifted-low/`0x93` | `BB 95 AF` | `<F0>らいふ<CB>` | 10429 hits, active 0, frames 3165-3301 |
| static-candidate+pointer | `0x0739D` | `0x0739C-0x073A1` | `$B38C-$B391` | UI | ライフ | 라이프 | shifted-low/`0x93` | `BB 95 AF` | `<F0>らいふ<CA>` | - |

## items/equipment

| evidence | ROM hit | record ROM | CPU range | category | Japanese | Korean | mode/base | bytes | decoded record | runtime |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| runtime-confirmed | `0x07227` | `0x07226-0x0722A` | `$B216-$B21A` | 무기 | カタナ | 카타나 | shifted-low/`0x84` | `8A 94 99` | `あかたな` | - |
| static-candidate+pointer | `0x05644` | `0x05643-0x05647` | `$9633-$9637` | 무기 | カタナ | 카타나 | shifted-low/`0x7C` | `82 8C 91` | `みかたな` | - |
| static-candidate | `0x058FB` | `0x058FB-0x058FF` | `$98EB-$98EF` | 무기 | やり | 창 | shifted-low/`0x79` | `9E A2` | `やりつそ` | - |
| static-candidate+pointer | `0x05AA3` | `0x05AA0-0x05AA7` | `$9A90-$9A97` | 무기 | やり | 창 | shifted-low/`0x77` | `9C A0` | `ら<B4>めやりやり` | - |
| static-candidate+pointer | `0x05AA5` | `0x05AA0-0x05AA7` | `$9A90-$9A97` | 무기 | やり | 창 | shifted-low/`0x77` | `9C A0` | `ら<B4>めやりやり` | - |
| static-candidate+pointer | `0x05BBA` | `0x05BB5-0x05BBD` | `$9BA5-$9BAD` | 무기 | やり | 창 | shifted-low/`0x7A` | `9F A3` | `むねけ<99>さやりを` | 710 hits, active 0, frames 259-3111 |
| static-candidate+pointer | `0x05BDF` | `0x05BDD-0x05BE3` | `$9BCD-$9BD3` | 회복 | くすり | 약 | shifted-low/`0x7A` | `82 87 A3` | `にしくすり<99>` | - |
| static-candidate+pointer | `0x05C09` | `0x05C04-0x05C0C` | `$9BF4-$9BFC` | 무기 | やり | 창 | shifted-low/`0x7A` | `9F A3` | `ひをに<99>さやりを` | - |
| static-candidate+pointer | `0x05C69` | `0x05C64-0x05C6C` | `$9C54-$9C5C` | 무기 | やり | 창 | shifted-low/`0x7A` | `9F A3` | `ち<AE>すぬさやりを` | - |
| static-candidate | `0x06001` | `0x05FFB-0x06008` | `$9FEB-$9FF8` | 무기 | やり | 창 | shifted-low/`0x7E` | `A3 A7` | `せ<B7>お<1C>せなやりえゆそ<0E><CA>` | 35 hits, active 0, frames 3165-3182 |
| static-candidate+pointer | `0x06295` | `0x06294-0x0629E` | `$A284-$A28E` | 무기 | カタナ | 카타나 | shifted-low/`0x7C` | `82 8C 91` | `みかたなへおはさは<B5>` | - |
| static-candidate+pointer | `0x0631C` | `0x06319-0x06324` | `$A309-$A314` | 무기 | カタナ | 카타나 | shifted-low/`0x7C` | `82 8C 91` | `<F0><BB>みかたなへおはさは` | - |
| static-candidate | `0x0635A` | `0x06359-0x06362` | `$A349-$A352` | 무기 | カタナ | 카타나 | shifted-low/`0x7C` | `82 8C 91` | `みかたな<13><0A><0B><AE>ち` | - |
| static-candidate | `0x06479` | `0x06478-0x06481` | `$A468-$A471` | 무기 | やり | 창 | shifted-low/`0x7F` | `A4 A8` | `ひやりやまうぬくけ` | 3 hits, active 0, frames 3167-3180 |
| static-candidate | `0x065B0` | `0x065B0-0x065B6` | `$A5A0-$A5A6` | 무기 | やり | 창 | shifted-low/`0x80` | `A5 A9` | `やりせね<B2><CA>` | - |
| static-candidate+pointer | `0x06839` | `0x06832-0x0683D` | `$A822-$A82D` | 무기 | やり | 창 | shifted-low/`0x7E` | `A3 A7` | `そさ<10>てすせなやりお<0E>` | - |
| static-candidate+pointer | `0x068C3` | `0x068B9-0x068C5` | `$A8A9-$A8B5` | 무기 | やり | 창 | shifted-low/`0x71` | `96 9A` | `<F0><BB>たは<0C><AB>つらつ<A7>やり` | - |
| static-candidate+pointer | `0x0691E` | `0x0691E-0x06923` | `$A90E-$A913` | 무기 | やり | 창 | shifted-low/`0x80` | `A5 A9` | `やりして<CA>` | - |
| static-candidate+pointer | `0x069C5` | `0x069C5-0x069CC` | `$A9B5-$A9BC` | 무기 | やり | 창 | shifted-low/`0x79` | `9E A2` | `やりはれ<A9><0E><CA>` | 16 hits, active 0, frames 3161-3165 |
| static-candidate | `0x06A3D` | `0x06A3D-0x06A46` | `$AA2D-$AA36` | 무기 | やり | 창 | shifted-low/`0x79` | `9E A2` | `やりはれ<A9><0E><CB><F8><F9>` | 40 hits, active 0, frames 3161-3165 |
| static-candidate | `0x06A66` | `0x06A66-0x06A6D` | `$AA56-$AA5D` | 무기 | やり | 창 | shifted-low/`0x79` | `9E A2` | `やりはれ<A9><0E><CA>` | 64 hits, active 0, frames 3161-3165 |
| static-candidate+pointer | `0x06BC6` | `0x06BBF-0x06BCA` | `$ABAF-$ABBA` | 무기 | やり | 창 | shifted-low/`0x7B` | `A0 A4` | `<FB><04><BB>よけ<14>ほやり<09>ひ` | 160 hits, active 0, frames 3161-3165 |
| static-candidate+pointer | `0x06D1B` | `0x06D19-0x06D22` | `$AD09-$AD12` | 무기 | やり | 창 | shifted-low/`0x80` | `A5 A9` | `<F0><BB>やりしても<B4>て` | - |
| static-candidate | `0x06FDE` | `0x06FDE-0x06FE5` | `$AFCE-$AFD5` | 무기 | やり | 창 | shifted-low/`0x80` | `A5 A9` | `やりせね<B2><CA><CA>` | - |
| static-candidate | `0x0704F` | `0x0704E-0x07053` | `$B03E-$B043` | 무기 | やり | 창 | shifted-low/`0x7A` | `9F A3` | `さやりを<13>` | - |

## menu

_No targets in this group yet._

## event/dialogue-related

| evidence | ROM hit | record ROM | CPU range | category | Japanese | Korean | mode/base | bytes | decoded record | runtime |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| static-candidate+pointer | `0x0561A` | `0x055CE-0x0561F` | `$95BE-$960F` | 스테이지 | はし | 다리 | shifted-low/`0x7C` | `96 88` | `<7B><15>は<15>は<15>は<15>は<15>は<15>は<15>は<15>は<15>は<15>は<05><7B...` | - |
| static-candidate | `0x0562F` | `0x0562A-0x05633` | `$961A-$9623` | 보스 | たついち | 타츠이치 | shifted-low/`0x80` | `90 92 82 91` | `<0C><B6>うきちたついち` | - |
| static-candidate+pointer | `0x05643` | `0x05643-0x05647` | `$9633-$9637` | 보스 | へいしち | 헤이시치 | shifted-low/`0x80` | `9D 82 8C 91` | `へいしち` | - |
| encoding-exact | `0x0569D` | `0x0569C-0x0569F` | `$968C-$968F` | 스테이지 | はし | 다리 | plus-0x7A/`0x7A` | `A0 92` | `<85>はし` | - |
| static-candidate | `0x056DA` | `0x056D5-0x056DE` | `$96C5-$96CE` | 스테이지 | はし | 다리 | shifted-low/`0x80` | `9A 8C` | `は<07>のすけはし<0F>う` | - |
| static-candidate | `0x0571C` | `0x05716-0x05724` | `$9706-$9714` | 스테이지 | はし | 다리 | shifted-low/`0x78` | `92 84` | `にそ<0A><AB>さをはしれ<AE>ふれよは` | - |
| static-candidate+pointer | `0x057D4` | `0x057D4-0x057D8` | `$97C4-$97C8` | 스테이지 | はし | 다리 | shifted-low/`0x8C` | `A6 98` | `はしあ<89>` | - |

## other

_No targets in this group yet._

## Gaps

- No menu-category target is currently present in `bank1_watch_targets.json`; menu labels still need broader capture or refined translation matching.
- Event/dialogue evidence is still static candidate evidence only. The current watch range contains boss/stage/name-like strings, but no fully runtime-confirmed event dialogue block yet.
- Several read hits without active expected-byte matches (`rom_05bba_candidate_7a`, `rom_06fa1_candidate_8d`) are deliberately not promoted to confirmed offsets.
