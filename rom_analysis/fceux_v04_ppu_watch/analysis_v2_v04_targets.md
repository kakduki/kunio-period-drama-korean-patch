# PPU Write Watch Analysis v2

Input: `rom_analysis\fceux_v04_ppu_watch`
Targets: `rom_analysis\v04_equal_length_fceux_targets.json`

- Frames captured: **88**
- Targets loaded: **13**
- Unique target byte sequences: **5**
- Decode glyphs: **82**

## Matched Targets

| phase | label | expected_bytes |
| ---: | --- | --- |
| 2 | `v04_watch_rom_0561a_스테이지_7c` | `8B 8C` |
| 2 | `v04_watch_rom_0569d_스테이지_7a` | `8B 8C` |
| 2 | `v04_watch_rom_056da_스테이지_80` | `8B 8C` |
| 2 | `v04_watch_rom_0571c_스테이지_78` | `8B 8C` |
| 2 | `v04_watch_rom_057d4_스테이지_8c` | `8B 8C` |

**Matched: 5 / 13**

## Ambiguity Notes

- Some matched targets share the same byte sequence. A PPU stream match proves that byte sequence was written, but does not by itself distinguish which ROM offset produced it.

| byte sequence | matched labels |
| --- | --- |
| `8B 8C` | `v04_watch_rom_0561a_스테이지_7c`, `v04_watch_rom_0569d_스테이지_7a`, `v04_watch_rom_056da_스테이지_80`, `v04_watch_rom_0571c_스테이지_78`, `v04_watch_rom_057d4_스테이지_8c` |

## Representative Screen: Frame 437

| vram_base | len | decoded |
| --- | ---: | --- |
| `$2480` | 8 | <82><83><D8><D9>おかきく |
| `$24A0` | 8 | しす<E8><E9>Zに<82><83> |
| `$24C0` | 8 | ゆよ<D8><D9><02><02>しす |
| `$24E0` | 8 | <02><02><E8><E9>おかきく |
| `$2500` | 8 | や<CF><D8><D9>Zに<82><83> |
| `$2520` | 8 | <BB><BC><E8><E9><02><02>しす |
| `$2540` | 8 | <CC><CD><D8><D9><CE><CF><02><02> |
| `$2560` | 8 | <2A><2A><E8><E9><2A><2A><2A><2A> |
| `$2580` | 8 | <50><50><D8><D9>ねの<50><50> |
| `$25A0` | 8 | <01><01><D4><D5><84>え<1A><1A> |
| `$25C0` | 3 | <5E><5F><5E> |
| `$25C4` | 4 | <84>え<EA><EB> |
| `$25E4` | 4 | な<BF><FA><FB> |
| `$2600` | 8 | <58><0F><38><0F><2D><07><07><07> |
| `$2620` | 8 | <1F><1F>2<1F><3D><08><03><08> |
| `$2640` | 8 | <60><2F><2F><2F><3D><03><09><03> |
| `$2660` | 8 | J<3F><3F>ろ7<0A><0A><0A> |
| `$2680` | 8 | 9<0D><0E>わ<10><11><10><11> |
| `$26A0` | 8 | <0B><1D><1E><0B><20><21><20>B |
| `$26C3` | 5 | <0C><62><62><14><15> |
| `$26E3` | 5 | <1C><14><15>QQ |
