# FCEUX Bank 1 read-watch summary

Input directory: `rom_analysis\fceux_bank1_watch_test`

Command:

```powershell
python scripts/run_fceux_lua_analysis.py --lua-script lua/kunio_autoplay_watch.lua --frames 5000 --timeout 120 --final-output rom_analysis/fceux_bank1_watch_test --clean-output --no-dump-hex --no-dump-bin
```

## Run result

- Final frame: `4317`
- Final reason: `hit_limit`
- Registered watched CPU addresses: `334`
- Total read hits: `20000`
- Callback detail: `callback_mode=true;target_source=generated;targets=36`

## Observed labels

| label | category | ROM hit | CPU record range | hits | first frame | last frame | unique CPU addrs | active expected matches | expected bytes in context | evidence context |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `rom_0736a_candidate_93` | UI | `ROM+0x0736A` | `$B359-$B35E` | 5534 | 4164 | 4317 | 6 | 0 | no | `60 AD A2 7A 29 10 F0 1C` |
| `rom_06de3_candidate_80` | UI | `ROM+0x06DE3` | `$ADD1-$ADD7` | 4903 | 4164 | 4316 | 7 | 0 | no | `00 0E A3 7A 38 6E A3 7A` |
| `rom_06b4a_candidate_82` | 능력치 | `ROM+0x06B4A` | `$AB32-$AB3F` | 1872 | 4160 | 4315 | 14 | 0 | no | `E8 60 A9 30 20 33 E3 B0` |
| `rom_071a4_candidate_82` | 능력치 | `ROM+0x071A4` | `$B192-$B19C` | 1769 | 358 | 4316 | 11 | 11 | yes | `82 00 9F B4 93 88 AA A6` |
| `rom_05c09_candidate_7a` | 무기 | `ROM+0x05C09` | `$9BF4-$9BFC` | 1264 | 1030 | 4164 | 8 | 0 | no | `03 03 00 00 03 03 03 03` |
| `rom_06fa1_candidate_8d` | UI | `ROM+0x06FA1` | `$AF91-$AF9A` | 1046 | 604 | 4317 | 10 | 0 | no | `7F 43 CA 02 C4 46 C5 FF` |
| `rom_05bba_candidate_7a` | 무기 | `ROM+0x05BBA` | `$9BA5-$9BAD` | 1000 | 159 | 4110 | 6 | 0 | no | `01 01 01 01 40 40 40 40` |
| `rom_05bdf_candidate_7a` | 회복 | `ROM+0x05BDF` | `$9BCD-$9BD3` | 668 | 1051 | 1943 | 4 | 0 | no | `00 00 03 03 03 03 03 03` |
| `rom_06839_candidate_7e` | 무기 | `ROM+0x06839` | `$A822-$A82D` | 642 | 4165 | 4315 | 12 | 0 | no | `68 60 48 55 77 29 7F F0` |
| `rom_066fb_candidate_82` | 능력치 | `ROM+0x066FB` | `$A6EA-$A6F2` | 539 | 2053 | 4316 | 9 | 0 | no | `C0 A6 03 70 6B 69 70 C9` |
| `rom_06bc6_candidate_7b` | 무기 | `ROM+0x06BC6` | `$ABAF-$ABBA` | 160 | 4160 | 4164 | 12 | 0 | no | `71 C8 BD F4 AB 99 1D 71` |
| `rom_06845_candidate_82` | 능력치 | `ROM+0x06845` | `$A82E-$A838` | 146 | 4165 | 4315 | 6 | 0 | no | `F0 04 68 95 77 60 68 60` |
| `rom_06fde_candidate_80` | 무기 | `ROM+0x06FDE` | `$AFCE-$AFD5` | 138 | 4167 | 4213 | 6 | 0 | no | `25 03 B5 E8 29 08 F0 11` |
| `rom_07227_candidate_84` | 무기 | `ROM+0x07227` | `$B216-$B21A` | 97 | 1975 | 4213 | 5 | 5 | yes | `AF 00 85 8A 94 99 00 82` |
| `rom_06a66_candidate_79` | 무기 | `ROM+0x06A66` | `$AA56-$AA5D` | 72 | 4160 | 4164 | 8 | 0 | no | `9D 1D 71 E8 A9 08 9D 1D` |
| `rom_06bdf_candidate_8d` | UI | `ROM+0x06BDF` | `$ABCB-$ABD3` | 72 | 4160 | 4164 | 9 | 0 | no | `71 C8 BD F4 AB 38 E9 20` |
| `rom_06a3d_candidate_79` | 무기 | `ROM+0x06A3D` | `$AA2D-$AA36` | 47 | 4160 | 4164 | 10 | 0 | no | `85 1C 4A 4A 4A 4A 85 1A` |
| `rom_069c5_candidate_79` | 무기 | `ROM+0x069C5` | `$A9B5-$A9BC` | 16 | 4160 | 4164 | 8 | 0 | no | `06 AE E3 7A CA 8E A0 06` |
| `rom_0602e_candidate_8d` | UI | `ROM+0x0602E` | `$A01A-$A02B` | 15 | 4164 | 4164 | 15 | 0 | no | `65 9F CD 6A AE DB 0A 1E` |

## Details

| label | top CPU addresses | top values | expected bytes | record snapshot evidence |
| --- | --- | --- | --- | --- |
| `rom_0736a_candidate_93` | `$B35B`:1727, `$B35C`:1727, `$B35D`:1727, `$B359`:140 | `00`:1721, `6C`:1654, `2E`:1654, `A2`:73 | `BB 95 AF` | `no: A2 7A 29 10 F0 1C` |
| `rom_06de3_candidate_80` | `$ADD6`:1089, `$ADD7`:1089, `$ADD1`:545, `$ADD2`:545 | `C9`:1088, `50`:1088, `49`:544, `FF`:544 | `85 86 98` | `no: A3 7A 38 6E A3 7A EE` |
| `rom_06b4a_candidate_82` | `$AB34`:169, `$AB35`:169, `$AB36`:169, `$AB37`:147 | `04`:289, `0A`:288, `71`:168, `C8`:144 | `93 88 AA` | `no: 9D 1D 71 E8 60 A9 30 20 33 E3 B0 FB A9 01` |
| `rom_071a4_candidate_82` | `$B192`:187, `$B193`:187, `$B194`:187, `$B195`:187 | `57`:288, `00`:145, `19`:144, `4A`:144 | `93 88 AA` | `yes: 9F B4 93 88 AA A6 83 CA F8 F9 00` |
| `rom_05c09_candidate_7a` | `$9BF4`:315, `$9BF5`:315, `$9BF6`:315, `$9BF7`:315 | `03`:629, `00`:628, `C3`:1, `9D`:1 | `9F A3` | `no: 00 00 03 03 03 03 03 40 00` |
| `rom_06fa1_candidate_8d` | `$AF95`:175, `$AF96`:175, `$AF97`:175, `$AF98`:165 | `C5`:102, `FF`:102, `01`:102, `CE`:93 | `9C 90 A8` | `no: CA 02 C4 46 C5 FF 01 CE 3C 95` |
| `rom_05bba_candidate_7a` | `$9BA5`:278, `$9BA6`:278, `$9BA9`:119, `$9BAA`:119 | `01`:1000 | `9F A3` | `no: 01 01 01 01 01 01 40 40 40` |
| `rom_05bdf_candidate_7a` | `$9BD0`:167, `$9BD1`:167, `$9BD2`:167, `$9BD3`:167 | `03`:668 | `82 87 A3` | `no: 00 00 00 03 03 03 03` |
| `rom_06839_candidate_7e` | `$A827`:72, `$A828`:72, `$A829`:72, `$A82A`:72 | `48`:72, `55`:72, `77`:72, `29`:72 | `A3 A7` | `no: 95 50 60 68 60 48 55 77 29 7F F0 04` |
| `rom_066fb_candidate_82` | `$A6EA`:252, `$A6EB`:36, `$A6EC`:36, `$A6ED`:36 | `A7`:216, `70`:72, `C9`:72, `6B`:71 | `93 88 AA` | `no: 03 70 6B 69 70 C9 6E C9 6B` |
| `rom_06bc6_candidate_7b` | `$ABB9`:40, `$ABBA`:40, `$ABAF`:8, `$ABB0`:8 | `B5`:40, `1A`:40, `AB`:16, `BD`:8 | `A0 A4` | `no: BD F4 AB 99 1D 71 C8 20 E5 AB B5 1A` |
| `rom_06845_candidate_82` | `$A832`:71, `$A833`:71, `$A82E`:1, `$A82F`:1 | `68`:72, `60`:72, `95`:1, `77`:1 | `93 88 AA` | `no: 68 95 77 60 68 60 B5 77 29 7F 95` |
| `rom_06fde_candidate_80` | `$AFCE`:23, `$AFCF`:23, `$AFD0`:23, `$AFD1`:23 | `B5`:23, `E8`:23, `29`:23, `08`:23 | `A5 A9` | `no: B5 E8 29 08 F0 11 BD 2D` |
| `rom_07227_candidate_84` | `$B217`:24, `$B218`:24, `$B219`:24, `$B21A`:24 | `A9`:23, `80`:23, `9D`:23, `4D`:23 | `8A 94 99` | `yes: 85 8A 94 99 00` |
| `rom_06a66_candidate_79` | `$AA56`:9, `$AA57`:9, `$AA58`:9, `$AA59`:9 | `71`:16, `E8`:16, `A9`:8, `08`:8 | `9E A2` | `no: 71 E8 A9 08 9D 1D 71 E8` |
| `rom_06bdf_candidate_8d` | `$ABCB`:8, `$ABCC`:8, `$ABCD`:8, `$ABCE`:8 | `BD`:8, `F4`:8, `AB`:8, `38`:8 | `9C 90 A8` | `no: BD F4 AB 38 E9 20 99 1D 71` |
| `rom_06a3d_candidate_79` | `$AA2D`:5, `$AA2E`:5, `$AA2F`:5, `$AA30`:5 | `4A`:16, `85`:8, `1A`:4, `A9`:4 | `9E A2` | `no: 4A 4A 4A 4A 85 1A A9 01 85 1B` |
| `rom_069c5_candidate_79` | `$A9B5`:2, `$A9B6`:2, `$A9B7`:2, `$A9B8`:2 | `E3`:2, `7A`:2, `CA`:2, `8E`:2 | `9E A2` | `no: E3 7A CA 8E A0 06 20 37` |
| `rom_0602e_candidate_8d` | `$A01D`:1, `$A01E`:1, `$A01F`:1, `$A020`:1 | `CD`:1, `6A`:1, `AE`:1, `DB`:1 | `9C 90 A8` | `no: D0 65 9F CD 6A AE DB 0A 1E 78 D8 00 C4 54 C7 C8 D1 4D` |

## Notes

- A hit means the emulator read a watched CPU address while the Lua watcher was active.
- `active expected matches` counts hits where the watched CPU record currently contained the expected byte sequence.
- A context match is stronger evidence because the surrounding bytes include the translation candidate's expected byte sequence.
- This still needs to be paired with screen state/PPU writes before treating every candidate as final patch text.
