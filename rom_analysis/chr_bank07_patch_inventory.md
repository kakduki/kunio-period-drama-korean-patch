# CHR Bank 07 Patch Inventory

This maps the current Korean font patch slots onto the original CHR Bank 07 tile space.

- CHR ROM starts at `0x20010`.
- CHR Bank 07 range: `0x2E010-0x3000F`.
- Patch tile range: `0x101-0x1B5`.
- Patch slots: **181**
- Changed patch slots in generated v0.1 ROM: **181**
- Changed patch bytes in generated v0.1 ROM: **2433**

## Patch Slots

| # | tile | ROM offset | PRG byte (+0x7A) | original | patched glyph | changed bytes |
| ---: | --- | --- | --- | --- | --- | ---: |
| 0 | `0x101` | `0x2F020` | `0x87` | あ | ! | 15 |
| 1 | `0x102` | `0x2F030` | `0x88` | い | ( | 14 |
| 2 | `0x103` | `0x2F040` | `0x89` | う | ) | 14 |
| 3 | `0x104` | `0x2F050` | `0x8A` | え | , | 14 |
| 4 | `0x105` | `0x2F060` | `0x8B` | お | - | 15 |
| 5 | `0x106` | `0x2F070` | `0x8C` | か | . | 15 |
| 6 | `0x107` | `0x2F080` | `0x8D` | き | / | 15 |
| 7 | `0x108` | `0x2F090` | `0x8E` | く | 0 | 15 |
| 8 | `0x109` | `0x2F0A0` | `0x8F` | け | 1 | 15 |
| 9 | `0x10A` | `0x2F0B0` | `0x90` | こ | 2 | 13 |
| 10 | `0x10B` | `0x2F0C0` | `0x91` | さ | 3 | 15 |
| 11 | `0x10C` | `0x2F0D0` | `0x92` | し | 4 | 15 |
| 12 | `0x10D` | `0x2F0E0` | `0x93` | す | 5 | 15 |
| 13 | `0x10E` | `0x2F0F0` | `0x94` | せ | 6 | 15 |
| 14 | `0x10F` | `0x2F100` | `0x95` | そ | 7 | 15 |
| 15 | `0x110` | `0x2F110` | `0x96` | た | 8 | 15 |
| 16 | `0x111` | `0x2F120` | `0x97` | ち | 9 | 15 |
| 17 | `0x112` | `0x2F130` | `0x98` | つ | : | 14 |
| 18 | `0x113` | `0x2F140` | `0x99` | て | ; | 15 |
| 19 | `0x114` | `0x2F150` | `0x9A` | と | ? | 15 |
| 20 | `0x115` | `0x2F160` | `0x9B` | な | A | 15 |
| 21 | `0x116` | `0x2F170` | `0x9C` | に | B | 14 |
| 22 | `0x117` | `0x2F180` | `0x9D` | ぬ | C | 15 |
| 23 | `0x118` | `0x2F190` | `0x9E` | ね | D | 15 |
| 24 | `0x119` | `0x2F1A0` | `0x9F` | の | E | 14 |
| 25 | `0x11A` | `0x2F1B0` | `0xA0` | は | F | 15 |
| 26 | `0x11B` | `0x2F1C0` | `0xA1` | ひ | G | 15 |
| 27 | `0x11C` | `0x2F1D0` | `0xA2` | ふ | H | 14 |
| 28 | `0x11D` | `0x2F1E0` | `0xA3` | へ | I | 13 |
| 29 | `0x11E` | `0x2F1F0` | `0xA4` | ほ | J | 15 |
| 30 | `0x11F` | `0x2F200` | `0xA5` | patch-slot-unmapped-original | K | 15 |
| 31 | `0x120` | `0x2F210` | `0xA6` | ま | L | 15 |
| 32 | `0x121` | `0x2F220` | `0xA7` | み | M | 15 |
| 33 | `0x122` | `0x2F230` | `0xA8` | む | N | 15 |
| 34 | `0x123` | `0x2F240` | `0xA9` | め | O | 15 |
| 35 | `0x124` | `0x2F250` | `0xAA` | も | P | 15 |
| 36 | `0x125` | `0x2F260` | `0xAB` | や | Q | 15 |
| 37 | `0x126` | `0x2F270` | `0xAC` | ゆ | R | 15 |
| 38 | `0x127` | `0x2F280` | `0xAD` | よ | S | 15 |
| 39 | `0x128` | `0x2F290` | `0xAE` | ら | T | 15 |
| 40 | `0x129` | `0x2F2A0` | `0xAF` | り | U | 15 |
| 41 | `0x12A` | `0x2F2B0` | `0xB0` | る | V | 15 |
| 42 | `0x12B` | `0x2F2C0` | `0xB1` | れ | W | 15 |
| 43 | `0x12C` | `0x2F2D0` | `0xB2` | ろ | X | 15 |
| 44 | `0x12D` | `0x2F2E0` | `0xB3` | わ | Y | 15 |
| 45 | `0x12E` | `0x2F2F0` | `0xB4` | を | Z | 15 |
| 46 | `0x12F` | `0x2F300` | `0xB5` | ん | a | 13 |
| 47 | `0x130` | `0x2F310` | `0xB6` | patch-slot-unmapped-original | b | 12 |
| 48 | `0x131` | `0x2F320` | `0xB7` | patch-slot-unmapped-original | c | 12 |
| 49 | `0x132` | `0x2F330` | `0xB8` | patch-slot-unmapped-original | d | 12 |
| 50 | `0x133` | `0x2F340` | `0xB9` | patch-slot-unmapped-original | e | 13 |
| 51 | `0x134` | `0x2F350` | `0xBA` | patch-slot-unmapped-original | f | 12 |
| 52 | `0x135` | `0x2F360` | `0xBB` | patch-slot-unmapped-original | g | 13 |
| 53 | `0x136` | `0x2F370` | `0xBC` | patch-slot-unmapped-original | h | 13 |
| 54 | `0x137` | `0x2F380` | `0xBD` | patch-slot-unmapped-original | i | 13 |
| 55 | `0x138` | `0x2F390` | `0xBE` | patch-slot-unmapped-original | j | 10 |
| 56 | `0x139` | `0x2F3A0` | `0xBF` | patch-slot-unmapped-original | k | 12 |
| 57 | `0x13A` | `0x2F3B0` | `0xC0` | patch-slot-unmapped-original | l | 5 |
| 58 | `0x13B` | `0x2F3C0` | `0xC1` | patch-slot-unmapped-original | m | 8 |
| 59 | `0x13C` | `0x2F3D0` | `0xC2` | patch-slot-unmapped-original | n | 15 |
| 60 | `0x13D` | `0x2F3E0` | `0xC3` | patch-slot-unmapped-original | o | 15 |
| 61 | `0x13E` | `0x2F3F0` | `0xC4` | patch-slot-unmapped-original | p | 15 |
| 62 | `0x13F` | `0x2F400` | `0xC5` | patch-slot-unmapped-original | q | 15 |
| 63 | `0x140` | `0x2F410` | `0xC6` | patch-slot-unmapped-original | r | 16 |
| 64 | `0x141` | `0x2F420` | `0xC7` | patch-slot-unmapped-original | s | 14 |
| 65 | `0x142` | `0x2F430` | `0xC8` | patch-slot-unmapped-original | t | 15 |
| 66 | `0x143` | `0x2F440` | `0xC9` | patch-slot-unmapped-original | u | 14 |
| 67 | `0x144` | `0x2F450` | `0xCA` | patch-slot-unmapped-original | v | 14 |
| 68 | `0x145` | `0x2F460` | `0xCB` | patch-slot-unmapped-original | w | 14 |
| 69 | `0x146` | `0x2F470` | `0xCC` | patch-slot-unmapped-original | x | 14 |
| 70 | `0x147` | `0x2F480` | `0xCD` | patch-slot-unmapped-original | y | 14 |
| 71 | `0x148` | `0x2F490` | `0xCE` | patch-slot-unmapped-original | z | 14 |
| 72 | `0x149` | `0x2F4A0` | `0xCF` | patch-slot-unmapped-original | ~ | 12 |
| 73 | `0x14A` | `0x2F4B0` | `0xD0` | patch-slot-unmapped-original | 가 | 13 |
| 74 | `0x14B` | `0x2F4C0` | `0xD1` | patch-slot-unmapped-original | 각 | 13 |
| 75 | `0x14C` | `0x2F4D0` | `0xD2` | patch-slot-unmapped-original | 간 | 15 |
| 76 | `0x14D` | `0x2F4E0` | `0xD3` | patch-slot-unmapped-original | 갑 | 9 |
| 77 | `0x14E` | `0x2F4F0` | `0xD4` | patch-slot-unmapped-original | 강 | 13 |
| 78 | `0x14F` | `0x2F500` | `0xD5` | patch-slot-unmapped-original | 걸 | 9 |
| 79 | `0x150` | `0x2F510` | `0xD6` | patch-slot-unmapped-original | 검 | 15 |
| 80 | `0x151` | `0x2F520` | `0xD7` | patch-slot-unmapped-original | 게 | 15 |
| 81 | `0x152` | `0x2F530` | `0xD8` | patch-slot-unmapped-original | 겨 | 15 |
| 82 | `0x153` | `0x2F540` | `0xD9` | patch-slot-unmapped-original | 결 | 15 |
| 83 | `0x154` | `0x2F550` | `0xDA` | patch-slot-unmapped-original | 경 | 14 |
| 84 | `0x155` | `0x2F560` | `0xDB` | patch-slot-unmapped-original | 고 | 13 |
| 85 | `0x156` | `0x2F570` | `0xDC` | patch-slot-unmapped-original | 곤 | 12 |
| 86 | `0x157` | `0x2F580` | `0xDD` | patch-slot-unmapped-original | 공 | 12 |
| 87 | `0x158` | `0x2F590` | `0xDE` | patch-slot-unmapped-original | 과 | 15 |
| 88 | `0x159` | `0x2F5A0` | `0xDF` | patch-slot-unmapped-original | 굉 | 15 |
| 89 | `0x15A` | `0x2F5B0` | `0xE0` | patch-slot-unmapped-original | 구 | 6 |
| 90 | `0x15B` | `0x2F5C0` | `0xE1` | patch-slot-unmapped-original | 군 | 6 |
| 91 | `0x15C` | `0x2F5D0` | `0xE2` | patch-slot-unmapped-original | 굴 | 9 |
| 92 | `0x15D` | `0x2F5E0` | `0xE3` | patch-slot-unmapped-original | 금 | 10 |
| 93 | `0x15E` | `0x2F5F0` | `0xE4` | patch-slot-unmapped-original | 기 | 13 |
| 94 | `0x15F` | `0x2F600` | `0xE5` | patch-slot-unmapped-original | 길 | 12 |
| 95 | `0x160` | `0x2F610` | `0xE6` | patch-slot-unmapped-original | 께 | 15 |
| 96 | `0x161` | `0x2F620` | `0xE7` | patch-slot-unmapped-original | 끝 | 11 |
| 97 | `0x162` | `0x2F630` | `0xE8` | patch-slot-unmapped-original | 끼 | 15 |
| 98 | `0x163` | `0x2F640` | `0xE9` | patch-slot-unmapped-original | 노 | 13 |
| 99 | `0x164` | `0x2F650` | `0xEA` | patch-slot-unmapped-original | 누 | 13 |
| 100 | `0x165` | `0x2F660` | `0xEB` | patch-slot-unmapped-original | 니 | 15 |
| 101 | `0x166` | `0x2F670` | `0xEC` | patch-slot-unmapped-original | 다 | 15 |
| 102 | `0x167` | `0x2F680` | `0xED` | patch-slot-unmapped-original | 달 | 14 |
| 103 | `0x168` | `0x2F690` | `0xEE` | patch-slot-unmapped-original | 대 | 13 |
| 104 | `0x169` | `0x2F6A0` | `0xEF` | patch-slot-unmapped-original | 도 | 12 |
| 105 | `0x16A` | `0x2F6B0` | `0xF0` | patch-slot-unmapped-original | 독 | 11 |
| 106 | `0x16B` | `0x2F6C0` | `0xF1` | patch-slot-unmapped-original | 돈 | 14 |
| 107 | `0x16C` | `0x2F6D0` | `0xF2` | patch-slot-unmapped-original | 동 | 10 |
| 108 | `0x16D` | `0x2F6E0` | `0xF3` | patch-slot-unmapped-original | 되 | 15 |
| 109 | `0x16E` | `0x2F6F0` | `0xF4` | patch-slot-unmapped-original | 두 | 16 |
| 110 | `0x16F` | `0x2F700` | `0xF5` | patch-slot-unmapped-original | 둥 | 16 |
| 111 | `0x170` | `0x2F710` | `0xF6` | patch-slot-unmapped-original | 드 | 10 |
| 112 | `0x171` | `0x2F720` | `0xF7` | patch-slot-unmapped-original | 등 | 7 |
| 113 | `0x172` | `0x2F730` | `0xF8` | patch-slot-unmapped-original | 딩 | 14 |
| 114 | `0x173` | `0x2F740` | `0xF9` | patch-slot-unmapped-original | 때 | 14 |
| 115 | `0x174` | `0x2F750` | `0xFA` | patch-slot-unmapped-original | 라 | 14 |
| 116 | `0x175` | `0x2F760` | `0xFB` | patch-slot-unmapped-original | 란 | 16 |
| 117 | `0x176` | `0x2F770` | `0xFC` | patch-slot-unmapped-original | 략 | 16 |
| 118 | `0x177` | `0x2F780` | `0xFD` | patch-slot-unmapped-original | 레 | 16 |
| 119 | `0x178` | `0x2F790` | `0xFE` | patch-slot-unmapped-original | 려 | 15 |
| 120 | `0x179` | `0x2F7A0` | `0xFF` | patch-slot-unmapped-original | 력 | 14 |
| 121 | `0x17A` | `0x2F7B0` | `0x00` | patch-slot-unmapped-original | 로 | 5 |
| 122 | `0x17B` | `0x2F7C0` | `0x01` | patch-slot-unmapped-original | 뢰 | 13 |
| 123 | `0x17C` | `0x2F7D0` | `0x02` | patch-slot-unmapped-original | 료 | 11 |
| 124 | `0x17D` | `0x2F7E0` | `0x03` | patch-slot-unmapped-original | 루 | 6 |
| 125 | `0x17E` | `0x2F7F0` | `0x04` | patch-slot-unmapped-original | 류 | 14 |
| 126 | `0x17F` | `0x2F800` | `0x05` | patch-slot-unmapped-original | 름 | 9 |
| 127 | `0x180` | `0x2F810` | `0x06` | patch-slot-unmapped-original | 리 | 16 |
| 128 | `0x181` | `0x2F820` | `0x07` | patch-slot-unmapped-original | 릴 | 14 |
| 129 | `0x182` | `0x2F830` | `0x08` | patch-slot-unmapped-original | 마 | 13 |
| 130 | `0x183` | `0x2F840` | `0x09` | patch-slot-unmapped-original | 막 | 13 |
| 131 | `0x184` | `0x2F850` | `0x0A` | patch-slot-unmapped-original | 먹 | 13 |
| 132 | `0x185` | `0x2F860` | `0x0B` | patch-slot-unmapped-original | 메 | 14 |
| 133 | `0x186` | `0x2F870` | `0x0C` | patch-slot-unmapped-original | 명 | 14 |
| 134 | `0x187` | `0x2F880` | `0x0D` | patch-slot-unmapped-original | 모 | 14 |
| 135 | `0x188` | `0x2F890` | `0x0E` | patch-slot-unmapped-original | 목 | 14 |
| 136 | `0x189` | `0x2F8A0` | `0x0F` | patch-slot-unmapped-original | 몬 | 14 |
| 137 | `0x18A` | `0x2F8B0` | `0x10` | patch-slot-unmapped-original | 몸 | 11 |
| 138 | `0x18B` | `0x2F8C0` | `0x11` | patch-slot-unmapped-original | 몽 | 14 |
| 139 | `0x18C` | `0x2F8D0` | `0x12` | patch-slot-unmapped-original | 묘 | 14 |
| 140 | `0x18D` | `0x2F8E0` | `0x13` | patch-slot-unmapped-original | 물 | 14 |
| 141 | `0x18E` | `0x2F8F0` | `0x14` | patch-slot-unmapped-original | 밀 | 14 |
| 142 | `0x18F` | `0x2F900` | `0x15` | patch-slot-unmapped-original | 박 | 14 |
| 143 | `0x190` | `0x2F910` | `0x16` | patch-slot-unmapped-original | 밥 | 14 |
| 144 | `0x191` | `0x2F920` | `0x17` | patch-slot-unmapped-original | 방 | 14 |
| 145 | `0x192` | `0x2F930` | `0x18` | patch-slot-unmapped-original | 밭 | 13 |
| 146 | `0x193` | `0x2F940` | `0x19` | patch-slot-unmapped-original | 배 | 14 |
| 147 | `0x194` | `0x2F950` | `0x1A` | patch-slot-unmapped-original | 뱅 | 14 |
| 148 | `0x195` | `0x2F960` | `0x1B` | patch-slot-unmapped-original | 버 | 14 |
| 149 | `0x196` | `0x2F970` | `0x1C` | patch-slot-unmapped-original | 번 | 13 |
| 150 | `0x197` | `0x2F980` | `0x1D` | patch-slot-unmapped-original | 벌 | 14 |
| 151 | `0x198` | `0x2F990` | `0x1E` | patch-slot-unmapped-original | 베 | 14 |
| 152 | `0x199` | `0x2F9A0` | `0x1F` | patch-slot-unmapped-original | 벨 | 13 |
| 153 | `0x19A` | `0x2F9B0` | `0x20` | patch-slot-unmapped-original | 변 | 14 |
| 154 | `0x19B` | `0x2F9C0` | `0x21` | patch-slot-unmapped-original | 보 | 14 |
| 155 | `0x19C` | `0x2F9D0` | `0x22` | patch-slot-unmapped-original | 봉 | 13 |
| 156 | `0x19D` | `0x2F9E0` | `0x23` | patch-slot-unmapped-original | 부 | 11 |
| 157 | `0x19E` | `0x2F9F0` | `0x24` | patch-slot-unmapped-original | 분 | 14 |
| 158 | `0x19F` | `0x2FA00` | `0x25` | patch-slot-unmapped-original | 비 | 14 |
| 159 | `0x1A0` | `0x2FA10` | `0x26` | patch-slot-unmapped-original | 빅 | 14 |
| 160 | `0x1A1` | `0x2FA20` | `0x27` | patch-slot-unmapped-original | 빨 | 14 |
| 161 | `0x1A2` | `0x2FA30` | `0x28` | patch-slot-unmapped-original | 뽑 | 14 |
| 162 | `0x1A3` | `0x2FA40` | `0x29` | patch-slot-unmapped-original | 사 | 14 |
| 163 | `0x1A4` | `0x2FA50` | `0x2A` | patch-slot-unmapped-original | 산 | 14 |
| 164 | `0x1A5` | `0x2FA60` | `0x2B` | patch-slot-unmapped-original | 생 | 14 |
| 165 | `0x1A6` | `0x2FA70` | `0x2C` | patch-slot-unmapped-original | 선 | 14 |
| 166 | `0x1A7` | `0x2FA80` | `0x2D` | patch-slot-unmapped-original | 설 | 14 |
| 167 | `0x1A8` | `0x2FA90` | `0x2E` | patch-slot-unmapped-original | 성 | 14 |
| 168 | `0x1A9` | `0x2FAA0` | `0x2F` | patch-slot-unmapped-original | 셜 | 14 |
| 169 | `0x1AA` | `0x2FAB0` | `0x30` | patch-slot-unmapped-original | 소 | 14 |
| 170 | `0x1AB` | `0x2FAC0` | `0x31` | patch-slot-unmapped-original | 속 | 14 |
| 171 | `0x1AC` | `0x2FAD0` | `0x32` | patch-slot-unmapped-original | 쇠 | 14 |
| 172 | `0x1AD` | `0x2FAE0` | `0x33` | patch-slot-unmapped-original | 수 | 14 |
| 173 | `0x1AE` | `0x2FAF0` | `0x34` | patch-slot-unmapped-original | 술 | 14 |
| 174 | `0x1AF` | `0x2FB00` | `0x35` | patch-slot-unmapped-original | 숨 | 12 |
| 175 | `0x1B0` | `0x2FB10` | `0x36` | patch-slot-unmapped-original | 숲 | 11 |
| 176 | `0x1B1` | `0x2FB20` | `0x37` | patch-slot-unmapped-original | 슛 | 11 |
| 177 | `0x1B2` | `0x2FB30` | `0x38` | patch-slot-unmapped-original | 스 | 10 |
| 178 | `0x1B3` | `0x2FB40` | `0x39` | patch-slot-unmapped-original | 슬 | 12 |
| 179 | `0x1B4` | `0x2FB50` | `0x3A` | patch-slot-unmapped-original | 승 | 10 |
| 180 | `0x1B5` | `0x2FB60` | `0x3B` | patch-slot-unmapped-original | 시 | 11 |

## Reference Tiles Outside Patch Range

Digits and uppercase Latin tiles are tracked here because they are useful for decoding and should not be accidentally overwritten by the current Bank7 font patch.

| tile | ROM offset | glyph | group | changed bytes |
| --- | --- | --- | --- | ---: |
| `0x1C0` | `0x2FC10` | 0 | digit | 0 |
| `0x1C1` | `0x2FC20` | 1 | digit | 0 |
| `0x1C2` | `0x2FC30` | 2 | digit | 0 |
| `0x1C3` | `0x2FC40` | 3 | digit | 0 |
| `0x1C4` | `0x2FC50` | 4 | digit | 0 |
| `0x1C5` | `0x2FC60` | 5 | digit | 0 |
| `0x1C6` | `0x2FC70` | 6 | digit | 0 |
| `0x1C7` | `0x2FC80` | 7 | digit | 0 |
| `0x1C8` | `0x2FC90` | 8 | digit | 0 |
| `0x1C9` | `0x2FCA0` | 9 | digit | 0 |
| `0x1E1` | `0x2FE20` | A | latin_upper | 0 |
| `0x1E2` | `0x2FE30` | B | latin_upper | 0 |
| `0x1E3` | `0x2FE40` | C | latin_upper | 0 |
| `0x1E4` | `0x2FE50` | D | latin_upper | 0 |
| `0x1E5` | `0x2FE60` | E | latin_upper | 0 |
| `0x1E6` | `0x2FE70` | F | latin_upper | 0 |
| `0x1E7` | `0x2FE80` | G | latin_upper | 0 |
| `0x1E8` | `0x2FE90` | H | latin_upper | 0 |
| `0x1E9` | `0x2FEA0` | I | latin_upper | 0 |
| `0x1EA` | `0x2FEB0` | J | latin_upper | 0 |
| `0x1EB` | `0x2FEC0` | K | latin_upper | 0 |
| `0x1EC` | `0x2FED0` | L | latin_upper | 0 |
| `0x1ED` | `0x2FEE0` | M | latin_upper | 0 |
| `0x1EE` | `0x2FEF0` | N | latin_upper | 0 |
| `0x1EF` | `0x2FF00` | O | latin_upper | 0 |
| `0x1F0` | `0x2FF10` | P | latin_upper | 0 |
| `0x1F1` | `0x2FF20` | Q | latin_upper | 0 |
| `0x1F2` | `0x2FF30` | R | latin_upper | 0 |
| `0x1F3` | `0x2FF40` | S | latin_upper | 0 |
| `0x1F4` | `0x2FF50` | T | latin_upper | 0 |
| `0x1F5` | `0x2FF60` | U | latin_upper | 0 |
| `0x1F6` | `0x2FF70` | V | latin_upper | 0 |
| `0x1F7` | `0x2FF80` | W | latin_upper | 0 |
| `0x1F8` | `0x2FF90` | X | latin_upper | 0 |
| `0x1F9` | `0x2FFA0` | Y | latin_upper | 0 |
| `0x1FA` | `0x2FFB0` | Z | latin_upper | 0 |

## Notes

- The patch slots are 8x8 CHR tiles, 16 bytes each. They are not 8x16 tile indexes.
- The generated v0.1 ROM currently writes inside `0x101-0x1B5`; digits `0x1C0-0x1C9` and uppercase Latin `0x1E1-0x1FA` are left unchanged.
- PRG text bytes still need per-string encoding rules before these patched glyph slots can be used for a final translation patch.
