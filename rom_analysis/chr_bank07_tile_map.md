# CHR bank 07 tile map

This is a structured export of the current visually identified font map.

- CHR ROM starts at `ROM+0x20010`.
- Rendered CHR bank `07` covers `ROM+0x2E010-0x3000F`.
- Tile offsets below are bank-relative 8x8 CHR tile indexes.
- `prg_plus_0x7a_byte` is the byte expected by the current hypothesis: `PRG byte + 0x7A = CHR tile low byte`.

## hiragana

| tile | glyph | PRG byte (+0x7A) | bank offset | ROM offset | nonzero | sha1_16 |
| --- | --- | --- | --- | --- | ---: | --- |
| `0x101` | あ | `0x87` | `0x1010` | `0x2F020` | 15 | `0906cd5a8aca157b` |
| `0x102` | い | `0x88` | `0x1020` | `0x2F030` | 14 | `031621355e7d96ff` |
| `0x103` | う | `0x89` | `0x1030` | `0x2F040` | 14 | `ece63c2b2ba7d1a8` |
| `0x104` | え | `0x8A` | `0x1040` | `0x2F050` | 14 | `ee535b1c00a5ccbb` |
| `0x105` | お | `0x8B` | `0x1050` | `0x2F060` | 15 | `764e3664f643b682` |
| `0x106` | か | `0x8C` | `0x1060` | `0x2F070` | 15 | `53b466c583530d3e` |
| `0x107` | き | `0x8D` | `0x1070` | `0x2F080` | 15 | `855359141aa217ad` |
| `0x108` | く | `0x8E` | `0x1080` | `0x2F090` | 15 | `cfb17d02bbafbcef` |
| `0x109` | け | `0x8F` | `0x1090` | `0x2F0A0` | 15 | `af05d7c4b4186820` |
| `0x10A` | こ | `0x90` | `0x10A0` | `0x2F0B0` | 13 | `db76662196b607a8` |
| `0x10B` | さ | `0x91` | `0x10B0` | `0x2F0C0` | 15 | `a21ebdc9c0afb5be` |
| `0x10C` | し | `0x92` | `0x10C0` | `0x2F0D0` | 15 | `db3f402452c50beb` |
| `0x10D` | す | `0x93` | `0x10D0` | `0x2F0E0` | 15 | `bdd68fe1c1f20e07` |
| `0x10E` | せ | `0x94` | `0x10E0` | `0x2F0F0` | 15 | `8c0cf8bf61136fa4` |
| `0x10F` | そ | `0x95` | `0x10F0` | `0x2F100` | 15 | `2368a99ddfb372f0` |
| `0x110` | た | `0x96` | `0x1100` | `0x2F110` | 15 | `d352b9eb5ed38696` |
| `0x111` | ち | `0x97` | `0x1110` | `0x2F120` | 15 | `d08900ee5437d7b1` |
| `0x112` | つ | `0x98` | `0x1120` | `0x2F130` | 14 | `f02622f1713838f4` |
| `0x113` | て | `0x99` | `0x1130` | `0x2F140` | 15 | `867c65c915955ec8` |
| `0x114` | と | `0x9A` | `0x1140` | `0x2F150` | 15 | `73483710c4420f1e` |
| `0x115` | な | `0x9B` | `0x1150` | `0x2F160` | 15 | `367689680cec7d04` |
| `0x116` | に | `0x9C` | `0x1160` | `0x2F170` | 14 | `b856752d32e8e350` |
| `0x117` | ぬ | `0x9D` | `0x1170` | `0x2F180` | 15 | `718eaeb064ab4cb2` |
| `0x118` | ね | `0x9E` | `0x1180` | `0x2F190` | 15 | `87860e57494ddaf1` |
| `0x119` | の | `0x9F` | `0x1190` | `0x2F1A0` | 14 | `86d689ebcfe21867` |
| `0x11A` | は | `0xA0` | `0x11A0` | `0x2F1B0` | 15 | `469d5ab4b487886b` |
| `0x11B` | ひ | `0xA1` | `0x11B0` | `0x2F1C0` | 15 | `b140aa240edc1855` |
| `0x11C` | ふ | `0xA2` | `0x11C0` | `0x2F1D0` | 14 | `786fd7068c7dcb9b` |
| `0x11D` | へ | `0xA3` | `0x11D0` | `0x2F1E0` | 13 | `dc50dc666970abf0` |
| `0x11E` | ほ | `0xA4` | `0x11E0` | `0x2F1F0` | 15 | `c371da19da1e3efe` |
| `0x120` | ま | `0xA6` | `0x1200` | `0x2F210` | 15 | `7616c27466fc740c` |
| `0x121` | み | `0xA7` | `0x1210` | `0x2F220` | 15 | `f8ee34bf7e6211d3` |
| `0x122` | む | `0xA8` | `0x1220` | `0x2F230` | 15 | `77fbabf76b3d4a38` |
| `0x123` | め | `0xA9` | `0x1230` | `0x2F240` | 15 | `2672d0f13ae20bb5` |
| `0x124` | も | `0xAA` | `0x1240` | `0x2F250` | 15 | `c581ba5e19449063` |
| `0x125` | や | `0xAB` | `0x1250` | `0x2F260` | 15 | `a7ebd38491943321` |
| `0x126` | ゆ | `0xAC` | `0x1260` | `0x2F270` | 15 | `d7d175f2c92a94c4` |
| `0x127` | よ | `0xAD` | `0x1270` | `0x2F280` | 15 | `42b52708b18e77d3` |
| `0x128` | ら | `0xAE` | `0x1280` | `0x2F290` | 15 | `7d063e8640c2716c` |
| `0x129` | り | `0xAF` | `0x1290` | `0x2F2A0` | 15 | `80a9d905b502145e` |
| `0x12A` | る | `0xB0` | `0x12A0` | `0x2F2B0` | 15 | `39fb99a95daeff91` |
| `0x12B` | れ | `0xB1` | `0x12B0` | `0x2F2C0` | 15 | `e473c62dbd5e66cb` |
| `0x12C` | ろ | `0xB2` | `0x12C0` | `0x2F2D0` | 15 | `7d469d4088de5308` |
| `0x12D` | わ | `0xB3` | `0x12D0` | `0x2F2E0` | 15 | `b7cb4e031f77f4e4` |
| `0x12E` | を | `0xB4` | `0x12E0` | `0x2F2F0` | 15 | `ebcaa6156991edcf` |
| `0x12F` | ん | `0xB5` | `0x12F0` | `0x2F300` | 13 | `4efa7c01f246167c` |

## digit

| tile | glyph | PRG byte (+0x7A) | bank offset | ROM offset | nonzero | sha1_16 |
| --- | --- | --- | --- | --- | ---: | --- |
| `0x1C0` | 0 | `0x46` | `0x1C00` | `0x2FC10` | 14 | `e2f765dcfad096d2` |
| `0x1C1` | 1 | `0x47` | `0x1C10` | `0x2FC20` | 14 | `772030630cdeb139` |
| `0x1C2` | 2 | `0x48` | `0x1C20` | `0x2FC30` | 14 | `e09045e4cdbbfbf7` |
| `0x1C3` | 3 | `0x49` | `0x1C30` | `0x2FC40` | 14 | `d376071f3a5dc2bd` |
| `0x1C4` | 4 | `0x4A` | `0x1C40` | `0x2FC50` | 14 | `1c5da0b43b931d57` |
| `0x1C5` | 5 | `0x4B` | `0x1C50` | `0x2FC60` | 14 | `15ae1ee050a602d6` |
| `0x1C6` | 6 | `0x4C` | `0x1C60` | `0x2FC70` | 14 | `2c0a09f6d6defdbe` |
| `0x1C7` | 7 | `0x4D` | `0x1C70` | `0x2FC80` | 14 | `39eac6ef520f05a5` |
| `0x1C8` | 8 | `0x4E` | `0x1C80` | `0x2FC90` | 14 | `de0c20ed3537ecc3` |
| `0x1C9` | 9 | `0x4F` | `0x1C90` | `0x2FCA0` | 14 | `1da056b1137bfe6b` |

## latin_upper

| tile | glyph | PRG byte (+0x7A) | bank offset | ROM offset | nonzero | sha1_16 |
| --- | --- | --- | --- | --- | ---: | --- |
| `0x1E1` | A | `0x67` | `0x1E10` | `0x2FE20` | 14 | `1a4c7626126d1423` |
| `0x1E2` | B | `0x68` | `0x1E20` | `0x2FE30` | 14 | `afb7937a7f85f88b` |
| `0x1E3` | C | `0x69` | `0x1E30` | `0x2FE40` | 14 | `6fdaaa4d856cae13` |
| `0x1E4` | D | `0x6A` | `0x1E40` | `0x2FE50` | 14 | `f61a70ae34599fb2` |
| `0x1E5` | E | `0x6B` | `0x1E50` | `0x2FE60` | 14 | `7defddfb23e5ee15` |
| `0x1E6` | F | `0x6C` | `0x1E60` | `0x2FE70` | 14 | `cc02714a1d11e6a6` |
| `0x1E7` | G | `0x6D` | `0x1E70` | `0x2FE80` | 14 | `556eb1ca9423f210` |
| `0x1E8` | H | `0x6E` | `0x1E80` | `0x2FE90` | 14 | `9988869a72b2b38a` |
| `0x1E9` | I | `0x6F` | `0x1E90` | `0x2FEA0` | 14 | `7d0c9aa8d1a95452` |
| `0x1EA` | J | `0x70` | `0x1EA0` | `0x2FEB0` | 14 | `5d9f261f6f5109a7` |
| `0x1EB` | K | `0x71` | `0x1EB0` | `0x2FEC0` | 14 | `c34428a23ae7798f` |
| `0x1EC` | L | `0x72` | `0x1EC0` | `0x2FED0` | 14 | `95cf28bc807f9259` |
| `0x1ED` | M | `0x73` | `0x1ED0` | `0x2FEE0` | 14 | `94f6051fc4867990` |
| `0x1EE` | N | `0x74` | `0x1EE0` | `0x2FEF0` | 14 | `5c4cce699e2b489c` |
| `0x1EF` | O | `0x75` | `0x1EF0` | `0x2FF00` | 14 | `abe3729082421185` |
| `0x1F0` | P | `0x76` | `0x1F00` | `0x2FF10` | 14 | `5debb405247a115a` |
| `0x1F1` | Q | `0x77` | `0x1F10` | `0x2FF20` | 14 | `1b3579e2d6119415` |
| `0x1F2` | R | `0x78` | `0x1F20` | `0x2FF30` | 14 | `7f802948dbe85f9f` |
| `0x1F3` | S | `0x79` | `0x1F30` | `0x2FF40` | 14 | `86106cf229d5de53` |
| `0x1F4` | T | `0x7A` | `0x1F40` | `0x2FF50` | 14 | `701e345496936555` |
| `0x1F5` | U | `0x7B` | `0x1F50` | `0x2FF60` | 14 | `2c1ea39848446ef7` |
| `0x1F6` | V | `0x7C` | `0x1F60` | `0x2FF70` | 14 | `019d3cf42da6d003` |
| `0x1F7` | W | `0x7D` | `0x1F70` | `0x2FF80` | 14 | `e29f82f616d93a2d` |
| `0x1F8` | X | `0x7E` | `0x1F80` | `0x2FF90` | 14 | `3ee0154de1be0773` |
| `0x1F9` | Y | `0x7F` | `0x1F90` | `0x2FFA0` | 14 | `89e56113281dee1e` |
| `0x1FA` | Z | `0x80` | `0x1FA0` | `0x2FFB0` | 14 | `a5d69f017ab2a143` |

## Notes

- This export does not prove every glyph is used by the text renderer; it records the current CHR-bank visual mapping used by the ROM text scans.
- Runtime FCEUX traces still need to connect PRG reads to PPU tile writes for final patch confidence.
