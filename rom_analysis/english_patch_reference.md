# English Patch Reference Analysis

This report compares the public `Technos Samurai: Downtown Special v1.00` IPS
with the verified Japanese base ROM. The third-party IPS and patched ROM are not stored in this repository.

## Identity

- Base ROM: `Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`
- Base size: `262160` bytes
- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Base SHA-1: `4338c3001c5e2bf5fad0f282bfee23b79e0ad959`
- Base payload SHA-1 (without iNES header): `e42b77a11280eb0c99d654cd08b8933fa8ddb999`
- Reference IPS: `TSe-v10.ips`
- Reference IPS SHA-256: `cb6ea2fdbf82e974c474f4ea0d489f7c65647c94de899caf2a6b8c089f202dad`
- Official archive index: `https://www.dynamic-designs.us/downloads.shtml`
- Patch database entry: `https://romhackplaza.org/translations/downtown-special-kunio-kun-no-jidaigeki-dayo-zenin-shuugou-english-translation-nes/`
- Patched size: `262160` bytes
- Patched MD5: `63e1d902807981f524af97748cd99500`
- Patched SHA-1: `74a83909bb4a0786b5dec3b4411099ccf154ca27`
- Patched payload SHA-1 (without iNES header): `cc3033c255b020babdb636439942f315ee7f6dd3`

## Structural Result

- IPS records: `99` (`0` RLE)
- IPS payload bytes: `14551`
- Actual changed bytes: `12582`
- Contiguous changed spans: `1170`
- PRG changed bytes: `10295`
- CHR changed bytes: `2286`
- Header changed bytes: `1`
- ROM size changed: `no`
- New printable ASCII runs in changed PRG data: `23`
- English tile-code runs decoded from changed PRG data: `120`
- English dialogue-code runs decoded from changed PRG data: `722`

The English patch proves that this game can hold a complete translated script without
expanding the ROM. Its own readme states that text was replaced and pointers were recalculated;
the PRG changes below provide the map for recovering those text blocks and pointer tables.

## Changed Banks

| region | bank | changed bytes | spans | first ROM offset | last ROM offset |
| --- | ---: | ---: | ---: | --- | --- |
| PRG | 1 | 7934 | 526 | `0x05288` | `0x0800E` |
| PRG | 3 | 5 | 1 | `0x0FC31` | `0x0FC35` |
| PRG | 4 | 1013 | 107 | `0x136B8` | `0x13E6E` |
| PRG | 6 | 221 | 17 | `0x1A2EF` | `0x1BB84` |
| PRG | 7 | 1122 | 144 | `0x1C841` | `0x1F33D` |
| CHR | 1 | 8 | 1 | `0x22340` | `0x22347` |
| CHR | 2 | 281 | 48 | `0x24038` | `0x246CE` |
| CHR | 7 | 1900 | 299 | `0x2F028` | `0x2FFBD` |
| CHR | 12 | 30 | 17 | `0x38C1E` | `0x38D63` |
| CHR | 15 | 67 | 9 | `0x3EB0B` | `0x3FB68` |

## Bank 1 IPS Records

These seven records are the primary script/pointer reverse-engineering targets.

| ROM range | bytes | actual changed | working classification |
| --- | ---: | ---: | --- |
| `0x05288-0x052C6` | 63 | 27 | text/render support data |
| `0x0561B-0x056AF` | 149 | 135 | dialogue/name table |
| `0x056BC-0x05D53` | 1688 | 1470 | dialogue text block 1 |
| `0x05DD4-0x07766` | 6547 | 6208 | pointer table plus dialogue text block 2 |
| `0x07894-0x078AA` | 23 | 20 | growth-rate UI text |
| `0x07FB6-0x07FEC` | 55 | 52 | inserted menu/label text |
| `0x07FF7-0x0800E` | 24 | 22 | inserted menu/label text |

## Header Difference

| offset | base | patched | note |
| --- | --- | --- | --- |
| `0x00006` | `0x41` | `0x43` | iNES flags 6 changes mirroring bit; do not copy until its runtime need is understood |

## Largest Changed Spans

| region | bank | ROM range | bytes |
| --- | ---: | --- | ---: |
| PRG | 7 | `0x1CADF-0x1CBB6` | 216 |
| PRG | 1 | `0x060BA-0x06189` | 208 |
| PRG | 1 | `0x062B1-0x06361` | 177 |
| PRG | 1 | `0x06AA3-0x06B40` | 158 |
| PRG | 1 | `0x06D28-0x06DBB` | 148 |
| PRG | 4 | `0x137AC-0x1383F` | 148 |
| PRG | 1 | `0x0636A-0x063FC` | 147 |
| PRG | 1 | `0x05AB7-0x05B42` | 140 |
| PRG | 6 | `0x1A7D6-0x1A85D` | 136 |
| PRG | 1 | `0x07507-0x07589` | 131 |
| PRG | 1 | `0x0722C-0x072AA` | 127 |
| PRG | 1 | `0x05C3A-0x05CB7` | 126 |
| PRG | 1 | `0x05B61-0x05BDB` | 123 |
| PRG | 1 | `0x07439-0x074AE` | 118 |
| PRG | 7 | `0x1C97F-0x1C9F1` | 115 |
| PRG | 1 | `0x06FF7-0x07062` | 108 |
| PRG | 1 | `0x076FE-0x07766` | 105 |
| PRG | 1 | `0x06C37-0x06C9E` | 104 |
| PRG | 1 | `0x06947-0x069AD` | 103 |
| PRG | 1 | `0x07199-0x071FC` | 100 |

## Decoded English Tile Runs

The patched CHR Bank 7 sheet maps tile `0x100` to blank and tiles `0x101-0x11A`
to `A-Z`. The reference ROM contains direct-low text bytes `0x00-0x1A`, including
the verified anchors `BUNZO = 02 15 0E 1A 0F` and `SHOP = 13 08 0F 10`.
These runs are therefore stronger text anchors than plain ASCII scans.

| ROM offset | PRG bank | length | changed ratio | decoded text | bytes |
| --- | ---: | ---: | ---: | --- | --- |
| `0x07897` | 1 | 6 | 1.000 | `GROWTH` | `07 12 0F 17 14 08` |
| `0x0789E` | 1 | 5 | 1.000 | `RATES` | `12 01 14 05 13` |
| `0x078A4` | 1 | 7 | 0.857 | `LEFTEND` | `0C 05 06 14 05 0E 04` |
| `0x0FC31` | 3 | 4 | 1.000 | `NONE` | `0E 0F 0E 05` |
| `0x136DA` | 4 | 7 | 1.000 | `TECHNOS` | `14 05 03 08 0E 0F 13` |
| `0x136E2` | 4 | 5 | 1.000 | `JAPAN` | `0A 01 10 01 0E` |
| `0x136E8` | 4 | 4 | 1.000 | `CORP` | `03 0F 12 10` |
| `0x13AE3` | 4 | 6 | 1.000 | `PLAYER` | `10 0C 01 19 05 12` |
| `0x13AEB` | 4 | 6 | 1.000 | `PLAYER` | `10 0C 01 19 05 12` |
| `0x1A2EF` | 6 | 4 | 1.000 | `MENU` | `0D 05 0E 15` |
| `0x1A778` | 6 | 4 | 1.000 | `FOOD` | `06 0F 0F 04` |
| `0x1A786` | 6 | 6 | 1.000 | `HEALER` | `08 05 01 0C 05 12` |
| `0x1A790` | 6 | 4 | 1.000 | `TECH` | `14 05 03 08` |
| `0x1A798` | 6 | 4 | 1.000 | `FOOD` | `06 0F 0F 04` |
| `0x1A7A0` | 6 | 4 | 1.000 | `SHOP` | `13 08 0F 10` |
| `0x1A7A6` | 6 | 6 | 1.000 | `CHANCE` | `03 08 01 0E 03 05` |
| `0x1A7B0` | 6 | 4 | 1.000 | `FOOD` | `06 0F 0F 04` |
| `0x1A7BA` | 6 | 9 | 1.000 | `SHOPBUNZO` | `13 08 0F 10 02 15 0E 1A 0F` |
| `0x1A7CA` | 6 | 4 | 1.000 | `SHOP` | `13 08 0F 10` |
| `0x1A7D0` | 6 | 4 | 1.000 | `FOOD` | `06 0F 0F 04` |
| `0x1A7DA` | 6 | 4 | 1.000 | `SHOP` | `13 08 0F 10` |
| `0x1A7E2` | 6 | 4 | 1.000 | `SHOP` | `13 08 0F 10` |
| `0x1A7EA` | 6 | 4 | 1.000 | `SHOP` | `13 08 0F 10` |
| `0x1A7F2` | 6 | 4 | 1.000 | `SHOP` | `13 08 0F 10` |
| `0x1A7FA` | 6 | 4 | 1.000 | `SHOP` | `13 08 0F 10` |
| `0x1A802` | 6 | 4 | 1.000 | `SHOP` | `13 08 0F 10` |
| `0x1A80A` | 6 | 4 | 1.000 | `SHOP` | `13 08 0F 10` |
| `0x1A812` | 6 | 4 | 1.000 | `SHOP` | `13 08 0F 10` |
| `0x1A81A` | 6 | 4 | 1.000 | `SHOP` | `13 08 0F 10` |
| `0x1A822` | 6 | 4 | 1.000 | `SHOP` | `13 08 0F 10` |
| `0x1A82A` | 6 | 4 | 1.000 | `SHOP` | `13 08 0F 10` |
| `0x1A832` | 6 | 4 | 1.000 | `SHOP` | `13 08 0F 10` |
| `0x1A83A` | 6 | 4 | 1.000 | `SHOP` | `13 08 0F 10` |
| `0x1A842` | 6 | 4 | 1.000 | `SHOP` | `13 08 0F 10` |
| `0x1A84A` | 6 | 4 | 1.000 | `SHOP` | `13 08 0F 10` |
| `0x1A852` | 6 | 4 | 1.000 | `SHOP` | `13 08 0F 10` |
| `0x1BB4A` | 6 | 5 | 1.000 | `SAVED` | `13 01 16 05 04` |
| `0x1C914` | 7 | 4 | 1.000 | `FIST` | `06 09 13 14` |
| `0x1C920` | 7 | 4 | 1.000 | `KICK` | `0B 09 03 0B` |
| `0x1C937` | 7 | 4 | 1.000 | `TORP` | `14 0F 12 10` |
| `0x1C943` | 7 | 6 | 0.833 | `ATTACK` | `01 14 14 01 03 0B` |
| `0x1C951` | 7 | 4 | 1.000 | `FUMI` | `06 15 0D 09` |
| `0x1C95D` | 7 | 5 | 1.000 | `GUARD` | `07 15 01 12 04` |
| `0x1C968` | 7 | 5 | 1.000 | `SCREW` | `13 03 12 05 17` |
| `0x1C973` | 7 | 7 | 0.857 | `TORNADO` | `14 0F 12 0E 01 04 0F` |
| `0x1C982` | 7 | 4 | 1.000 | `TORP` | `14 0F 12 10` |
| `0x1C98C` | 7 | 8 | 1.000 | `HELICPTR` | `08 05 0C 09 03 10 14 12` |
| `0x1C99A` | 7 | 5 | 1.000 | `DRILL` | `04 12 09 0C 0C` |
| `0x1C9A5` | 7 | 4 | 1.000 | `SLAP` | `13 0C 01 10` |
| `0x1C9B2` | 7 | 5 | 1.000 | `DAGGR` | `04 01 07 07 12` |
| `0x1C9C0` | 7 | 8 | 1.000 | `HEADBUTT` | `08 05 01 04 02 15 14 14` |
| `0x1C9CE` | 7 | 8 | 1.000 | `BMPKNART` | `02 0D 10 0B 0E 01 12 14` |
| `0x1C9DE` | 7 | 4 | 1.000 | `FIST` | `06 09 13 14` |
| `0x1C9EB` | 7 | 4 | 1.000 | `KICK` | `0B 09 03 0B` |
| `0x1C9F6` | 7 | 5 | 1.000 | `SCREW` | `13 03 12 05 17` |
| `0x1CA02` | 7 | 7 | 0.857 | `MASSAGE` | `0D 01 13 13 01 07 05` |
| `0x1CA0F` | 7 | 7 | 1.000 | `BIGBANG` | `02 09 07 02 01 0E 07` |
| `0x1CA1C` | 7 | 8 | 1.000 | `WARPSHOT` | `17 01 12 10 13 08 0F 14` |
| `0x1CA2A` | 7 | 7 | 1.000 | `DEFLECT` | `04 05 06 0C 05 03 14` |
| `0x1CA39` | 7 | 6 | 1.000 | `KIUKIU` | `0B 09 15 0B 09 15` |
| `0x1CA47` | 7 | 5 | 1.000 | `SWING` | `13 17 09 0E 07` |
| `0x1CA52` | 7 | 6 | 1.000 | `PICKLE` | `10 09 03 0B 0C 05` |
| `0x1CA5E` | 7 | 4 | 1.000 | `MEAL` | `0D 05 01 0C` |
| `0x1CA68` | 7 | 4 | 1.000 | `SOBA` | `13 0F 02 01` |
| `0x1CA72` | 7 | 4 | 1.000 | `UDON` | `15 04 0F 0E` |
| `0x1CA7C` | 7 | 4 | 1.000 | `SOUP` | `13 0F 15 10` |
| `0x1CA8F` | 7 | 4 | 1.000 | `FISH` | `06 09 13 08` |
| `0x1CA99` | 7 | 7 | 0.857 | `TENPURA` | `14 05 0E 10 15 12 01` |
| `0x1CAA6` | 7 | 5 | 1.000 | `DANGO` | `04 01 0E 07 0F` |
| `0x1CAB1` | 7 | 8 | 1.000 | `RICEBALL` | `12 09 03 05 02 01 0C 0C` |
| `0x1CABF` | 7 | 6 | 1.000 | `MANJUU` | `0D 01 0E 0A 15 15` |
| `0x1CACB` | 7 | 5 | 1.000 | `SUSHI` | `13 15 13 08 09` |
| `0x1CAD6` | 7 | 5 | 1.000 | `SALVE` | `13 01 0C 16 05` |
| `0x1CAE1` | 7 | 8 | 1.000 | `POULTICE` | `10 0F 15 0C 14 09 03 05` |
| `0x1CAEF` | 7 | 5 | 1.000 | `TONIC` | `14 0F 0E 09 03` |
| `0x1CAFB` | 7 | 6 | 1.000 | `TOYAMA` | `14 0F 19 01 0D 01` |
| `0x1CB07` | 7 | 6 | 1.000 | `ELIXIR` | `05 0C 09 18 09 12` |
| `0x1CB14` | 7 | 6 | 1.000 | `COTTON` | `03 0F 14 14 0F 0E` |
| `0x1CB21` | 7 | 6 | 1.000 | `COTTON` | `03 0F 14 14 0F 0E` |
| `0x1CB2E` | 7 | 4 | 1.000 | `LONG` | `0C 0F 0E 07` |
| `0x1CB39` | 7 | 7 | 1.000 | `OBSCENE` | `0F 02 13 03 05 0E 05` |
| `0x1CB47` | 7 | 6 | 1.000 | `COMMON` | `03 0F 0D 0D 0F 0E` |
| `0x1CB54` | 7 | 4 | 1.000 | `WIDE` | `17 09 04 05` |
| `0x1CB5F` | 7 | 5 | 1.000 | `THICK` | `14 08 09 03 0B` |
| `0x1CB6B` | 7 | 5 | 1.000 | `WHITE` | `17 08 09 14 05` |
| `0x1CB81` | 7 | 6 | 1.000 | `PRICEY` | `10 12 09 03 05 19` |
| `0x1CB8E` | 7 | 4 | 1.000 | `SILK` | `13 09 0C 0B` |
| `0x1CB99` | 7 | 4 | 1.000 | `SILK` | `13 09 0C 0B` |
| `0x1CBA4` | 7 | 5 | 1.000 | `THICK` | `14 08 09 03 0B` |
| `0x1CBB0` | 7 | 5 | 1.000 | `SAUCY` | `13 01 15 03 19` |
| `0x1CBBC` | 7 | 6 | 1.000 | `NARITA` | `0E 01 12 09 14 01` |
| `0x1CBD3` | 7 | 4 | 1.000 | `SOFT` | `13 0F 06 14` |
| `0x1CBDE` | 7 | 4 | 1.000 | `WOOL` | `17 0F 0F 0C` |
| `0x1CBEC` | 7 | 7 | 1.000 | `TWISTED` | `14 17 09 13 14 05 04` |
| `0x1CBFA` | 7 | 6 | 1.000 | `PONGEE` | `10 0F 0E 07 05 05` |
| `0x1CC06` | 7 | 8 | 1.000 | `DOUBLEUP` | `04 0F 15 02 0C 05 15 10` |
| `0x1CC15` | 7 | 4 | 1.000 | `SNOW` | `13 0E 0F 17` |
| `0x1CC20` | 7 | 6 | 1.000 | `SPIKED` | `13 10 09 0B 05 04` |
| `0x1CC2D` | 7 | 5 | 1.000 | `CAMEL` | `03 01 0D 05 0C` |
| `0x1CC39` | 7 | 5 | 1.000 | `KAPPA` | `0B 01 10 10 01` |
| `0x1CC45` | 7 | 5 | 1.000 | `MAGIC` | `0D 01 07 09 03` |
| `0x1CC51` | 7 | 5 | 1.000 | `SANKI` | `13 01 0E 0B 09` |
| `0x1CC60` | 7 | 4 | 1.000 | `CRSR` | `03 12 13 12` |
| `0x1CC6B` | 7 | 7 | 1.000 | `MYSTERY` | `0D 19 13 14 05 12 19` |
| `0x1CC78` | 7 | 8 | 1.000 | `GOODTIME` | `07 0F 0F 04 14 09 0D 05` |
| `0x1CC88` | 7 | 6 | 1.000 | `EFFECT` | `05 06 06 05 03 14` |
| `0x1CC95` | 7 | 6 | 1.000 | `MASTER` | `0D 01 13 14 05 12` |
| `0x1CCA2` | 7 | 4 | 0.750 | `JUMP` | `0A 15 0D 10` |
| `0x1CCB7` | 7 | 5 | 1.000 | `ABET` | `00 01 02 05 14` |
| `0x1CCBF` | 7 | 4 | 1.000 | `STAY` | `13 14 01 19` |
| `0x1CCC4` | 7 | 6 | 1.000 | `ANONE` | `00 01 0E 0F 0E 05` |
| `0x1CCCB` | 7 | 4 | 1.000 | `EXIT` | `05 18 09 14` |
| `0x1CCD4` | 7 | 4 | 1.000 | `HALF` | `08 01 0C 06` |
| `0x1CCE5` | 7 | 4 | 1.000 | `ALLY` | `01 0C 0C 19` |
| `0x1CCEA` | 7 | 6 | 1.000 | `STATUS` | `13 14 01 14 15 13` |
| `0x1CCF1` | 7 | 4 | 1.000 | `ALLY` | `01 0C 0C 19` |
| `0x1CCF6` | 7 | 4 | 1.000 | `TECH` | `14 05 03 08` |
| `0x1CCFB` | 7 | 5 | 1.000 | `SETUP` | `13 05 14 15 10` |
| `0x1CD01` | 7 | 6 | 0.833 | `SETTNG` | `13 05 14 14 0E 07` |
| `0x1CD08` | 7 | 4 | 1.000 | `SAVE` | `13 01 16 05` |

## Decoded English Dialogue Runs

The dialogue/name path uses CHR tiles `0x181-0x19A`, encoded as
`A=0x81` through `Z=0x9A`, with `0xFF` acting as a separator/control byte.
The first reference block at `0x0561B` includes the names `KUNIO`, `RIKI`, and `BUNZO`;
sentence data begins at `0x056BC`.

| ROM offset | PRG bank | length | changed ratio | decoded text | bytes |
| --- | ---: | ---: | ---: | --- | --- |
| `0x052A8` | 1 | 4 | 1.000 | `EVEN` | `85 96 85 8E` |
| `0x052B8` | 1 | 4 | 1.000 | `EVEN` | `85 96 85 8E` |
| `0x0561A` | 1 | 111 | 0.901 | `VKUNIORIKI BUNZOJUUKITSUI TATSUYAGO JINROHEISIKINSUTAME GONSAGINPAICHI ROKU TSUU ASAJIYONO TORA HAN NIZAEHEIRU` | `96 8B 95 8E 89 8F 92 89 8B 89 FF 82 95 8E 9A 8F 8A 95 95 8B 89 94 93 95 89 FF 94 81 94 93 95 99 81 87 8F FF 8A 89 8E 92 8F 88 85 89 93 89 8B 89 8E 93 95 94 81 8D 85 FF 87 8F 8E 93 81 87 89 8E 90 81 89 83 88 89 FF 92 8F 8B 95 FF 94 93 95 95 FF 81 93 81 8A 89 99 8F 8E 8F FF 94 8F 92 81 FF 88 81 8E FF FF 8E 89 9A 81 85 88 85 89 92 95` |
| `0x0568C` | 1 | 36 | 0.889 | `OBINAMATSUOKOTO OMON RAO SANKI` | `FF 8F 82 89 8E 81 8D 81 94 93 95 8F 8B 8F 94 8F FF FF FF FF FF 8F 8D 8F 8E FF 92 81 8F FF FF 93 81 8E 8B 89` |
| `0x056BB` | 1 | 801 | 0.905 | `VYUKI ITOKISAKI TAMO SAIZOHAGI HASHIKOSU HANSUKOUE HIRA HIDE ASHI BEN SAITAMOEMOMURA SADA SEKI YOTSUTOMO KUMA WATA URAE TOME ONOKIYATA ISORORIHEICHIE SUMI SHIN MUNE GENSUOISA HEMO YOTA KAME TAKI HISA SAHEIKISU NORI KOUKISUEMATAKE UMEMABOBU YUUE YOSHIRIHE HACHIDEZOUKUMI TARO URASAYONE SHIMATERU SUYA MORI ISHI SAKU URAJISHIBAJMGQ SHIROJUNZOINETAAKIZOYURI SUTE SHUU EBINOCHIJIATSU KANA SUKE GOSU TSUNOKIKU TOSHITSUKIOBISAYASU KENGOMANSIKATSUSONO GOSA TOUBEZENE OMENOMOCHISHOU INGO NEHA TEMA MOHE SOME KAMO MATA UKI GORO KOTA TSUDAINOSUUMETAUSUKEMANGONENKIKURO TEHA SENBESENPAHOME TAHA KICHINETA TAGO MANPEKETA KUNKIMOMO TANE HEKO MATAAMEHEIMASU UNJI MONO DENSUUMESIMAGO RAHA MOHEISENROCHOU KAN KANPAIMOHAMINO KANTAFUNE KANSUSUJI SICHIUSHI ROHEIKOME GOBEEZENJISUNE KINE SUZU INEMOHATA UNOMAYAENONEKI` | `96 99 95 8B 89 FF 89 94 8F 8B 89 93 81 8B 89 FF 94 81 8D 8F FF 93 81 89 9A 8F 88 81 87 89 FF 88 81 93 88 89 8B 8F 93 95 FF 88 81 8E 93 95 8B 8F 95 85 FF 88 89 92 81 FF 88 89 84 85 FF 81 93 88 89 FF 82 85 8E FF FF 93 81 89 94 81 8D 8F 85 8D 8F 8D 95 92 81 FF 93 81 84 81 FF 93 85 8B 89 FF 99 8F 94 93 95 94 8F 8D 8F FF 8B 95 8D 81 FF 97 81 94 81 FF 95 92 81 85 FF 94 8F 8D 85 FF 8F 8E 8F 8B 89 99 81 94 81 FF 89 93 8F 92 8F 92 89 88 85 89 83 88 89 85 FF 93 95 8D 89 FF 93 88 89 8E FF 8D 95 8E 85 FF 87 85 8E 93 95 8F 89 93 81 FF 88 85 8D 8F FF 99 8F 94 81 FF 8B 81 8D 85 FF 94 81 8B 89 FF 88 89 93 81 FF 93 81 88 85 89 8B 89 93 95 FF 8E 8F 92 89 FF 8B 8F 95 8B 89 93 95 85 8D 81 94 81 8B 85 FF 95 8D 85 8D 81 82 8F 82 95 FF 99 95 95 85 FF 99 8F 93 88 89 92 89 88 85 FF 88 81 83 88 89 84 85 9A 8F 95 8B 95 8D 89 FF 94 81 92 8F FF 95 92 81 93 81 99 8F 8E 85 FF 93 88 89 8D 81 94 85 92 95 FF 93 95 99 81 FF 8D 8F 92 89 FF 89 93 88 89 FF 93 81 8B 95 FF 95 92 81 8A 89 93 88 89 82 81 8A 8D 87 91 FF 93 88 89 92 8F 8A 95 8E 9A 8F 89 8E 85 94 81 81 8B 89 9A 8F 99 95 92 89 FF 93 95 94 85 FF 93 88 95 95 FF 85 82 89 8E 8F 83 88 89 8A 89 81 94 93 95 FF 8B 81 8E 81 FF 93 95 8B 85 FF 87 8F 93 95 FF 94 93 95 8E 8F 8B 89 8B 95 FF 94 8F 93 88 89 94 93 95 8B 89 8F 82 89 93 81 99 81 93 95 FF 8B 85 8E 87 8F 8D 81 8E 93 89 8B 81 94 93 95 93 8F 8E 8F FF 87 8F 93 81 FF 94 8F 95 82 85 9A 85 8E 85 FF 8F 8D 85 8E 8F 8D 8F 83 88 89 93 88 8F 95 FF 89 8E 87 8F FF 8E 85 88 81 FF 94 85 8D 81 FF 8D 8F 88 85 FF 93 8F 8D 85 FF 8B 81 8D 8F FF 8D 81 94 81 FF 95 8B 89 FF FF 87 8F 92 8F FF 8B 8F 94 81 FF 94 93 95 84 81 89 8E 8F 93 95 95 8D 85 94 81 95 93 95 8B 85 8D 81 8E 87 8F 8E 85 8E 8B 89 8B 95 92 8F FF 94 85 88 81 FF 93 85 8E 82 85 93 85 8E 90 81 88 8F 8D 85 FF 94 81 88 81 FF 8B 89 83 88 89 8E 85 94 81 FF 94 81 87 8F FF 8D 81 8E 90 85 8B 85 94 81 FF 8B 95 8E 8B 89 8D 8F 8D 8F FF 94 81 8E 85 FF 88 85 8B 8F FF 8D 81 94 81 81 8D 85 88 85 89 8D 81 93 95 FF 95 8E 8A 89 FF 8D 8F 8E 8F FF 84 85 8E 93 95 95 8D 85 93 89 8D 81 87 8F FF 92 81 88 81 FF 8D 8F 88 85 89 93 85 8E 92 8F 83 88 8F 95 FF 8B 81 8E FF FF 8B 81 8E 90 81 89 8D 8F 88 81 8D 89 8E 8F FF 8B 81 8E 94 81 86 95 8E 85 FF 8B 81 8E 93 95 93 95 8A 89 FF 93 89 83 88 89 95 93 88 89 FF 92 8F 88 85 89 8B 8F 8D 85 FF 87 8F 82 85 85 9A 85 8E 8A 89 93 95 8E 85 FF 8B 89 8E 85 FF 93 95 9A 95 FF 89 8E 85 8D 8F 88 81 94 81 FF 95 8E 8F 8D 81 99 81 85 8E 8F 8E 85 8B 89 FF` |
| `0x05A7C` | 1 | 6 | 0.833 | `FIST M` | `86 89 93 94 FF 8D` |
| `0x05A83` | 1 | 6 | 0.833 | `KICK M` | `8B 89 83 8B FF 8D` |
| `0x05A8A` | 1 | 5 | 0.800 | `WPN E` | `97 90 8E FF 85` |
| `0x05A90` | 1 | 6 | 1.000 | `TORP N` | `94 8F 92 90 FF 8E` |
| `0x05A97` | 1 | 8 | 0.875 | `ATTACK M` | `81 94 94 81 83 8B FF 8D` |
| `0x05AA0` | 1 | 6 | 1.000 | `FUMI H` | `86 95 8D 89 FF 88` |
| `0x05AA7` | 1 | 21 | 0.952 | `GUARD SCREW TORNADO S` | `87 95 81 92 84 FF 93 83 92 85 97 FF 94 8F 92 8E 81 84 8F FF 93` |
| `0x05ABD` | 1 | 24 | 1.000 | `TORP HELICPTR DRILL SLAP` | `94 8F 92 90 FF 88 85 8C 89 83 90 94 92 FF 84 92 89 8C 8C FF 93 8C 81 90` |
| `0x05AD6` | 1 | 8 | 1.000 | `SP DAGGR` | `93 90 FF 84 81 87 87 92` |
| `0x05ADF` | 1 | 22 | 1.000 | `SP HEADBUTT BMPKNART M` | `93 90 FF 88 85 81 84 82 95 94 94 FF 82 8D 90 8B 8E 81 92 94 FF 8D` |
| `0x05AF6` | 1 | 4 | 1.000 | `FIST` | `86 89 93 94` |
| `0x05AFE` | 1 | 4 | 1.000 | `KICK` | `8B 89 83 8B` |
| `0x05B03` | 1 | 6 | 1.000 | `SCREW` | `FF 93 83 92 85 97` |
| `0x05B0A` | 1 | 35 | 1.000 | `MASSAGE BIGBANG WARPSHOT DEFLECT M` | `FF 8D 81 93 93 81 87 85 FF 82 89 87 82 81 8E 87 FF 97 81 92 90 93 88 8F 94 FF 84 85 86 8C 85 83 94 FF 8D` |
| `0x05B2E` | 1 | 8 | 1.000 | `KIUKIU M` | `8B 89 95 8B 89 95 FF 8D` |
| `0x05B37` | 1 | 99 | 0.960 | `SWING PICKLE MEAL SOBA UDON SOUP IMO FISH TENPURA DANGO RICEBALL MANJUU SUSHI SALVE POULTICE TONIC` | `93 97 89 8E 87 FF 90 89 83 8B 8C 85 FF 8D 85 81 8C FF 93 8F 82 81 FF 95 84 8F 8E FF 93 8F 95 90 FF 89 8D 8F FF 86 89 93 88 FF 94 85 8E 90 95 92 81 FF 84 81 8E 87 8F FF 92 89 83 85 82 81 8C 8C FF 8D 81 8E 8A 95 95 FF 93 95 93 88 89 FF 93 81 8C 96 85 FF 90 8F 95 8C 94 89 83 85 FF 94 8F 8E 89 83 FF` |
| `0x05B9B` | 1 | 14 | 1.000 | `TOYAMA ELIXIR` | `94 8F 99 81 8D 81 FF 85 8C 89 98 89 92 FF` |
| `0x05BAA` | 1 | 7 | 1.000 | `COTTON` | `83 8F 94 94 8F 8E FF` |
| `0x05BB2` | 1 | 7 | 1.000 | `COTTON` | `83 8F 94 94 8F 8E FF` |
| `0x05BBA` | 1 | 5 | 1.000 | `LONG` | `8C 8F 8E 87 FF` |
| `0x05BC0` | 1 | 8 | 1.000 | `OBSCENE` | `8F 82 93 83 85 8E 85 FF` |
| `0x05BC9` | 1 | 7 | 1.000 | `COMMON` | `83 8F 8D 8D 8F 8E FF` |
| `0x05BD1` | 1 | 5 | 1.000 | `WIDE` | `97 89 84 85 FF` |
| `0x05BD7` | 1 | 6 | 0.833 | `THICK` | `94 88 89 83 8B FF` |
| `0x05BDE` | 1 | 6 | 0.833 | `WHITE` | `97 88 89 94 85 FF` |
| `0x05BE5` | 1 | 4 | 1.000 | `SUN` | `93 95 8E FF` |
| `0x05BEA` | 1 | 7 | 1.000 | `PRICEY` | `90 92 89 83 85 99 FF` |
| `0x05BF2` | 1 | 5 | 1.000 | `SILK` | `93 89 8C 8B FF` |
| `0x05BF8` | 1 | 6 | 1.000 | `SILK` | `93 89 8C 8B FF FF` |
| `0x05BFF` | 1 | 6 | 1.000 | `THICK` | `94 88 89 83 8B FF` |
| `0x05C06` | 1 | 6 | 1.000 | `SAUCY` | `93 81 95 83 99 FF` |
| `0x05C0D` | 1 | 7 | 1.000 | `NARITA` | `8E 81 92 89 94 81 FF` |
| `0x05C15` | 1 | 4 | 0.750 | `JET` | `8A 85 94 FF` |
| `0x05C1A` | 1 | 5 | 1.000 | `SOFT` | `93 8F 86 94 FF` |
| `0x05C20` | 1 | 5 | 1.000 | `WOOL` | `97 8F 8F 8C FF` |
| `0x05C26` | 1 | 8 | 1.000 | `TWISTED` | `94 97 89 93 94 85 84 FF` |
| `0x05C2F` | 1 | 16 | 0.938 | `PONGEE DOUBLEUP` | `90 8F 8E 87 85 85 FF 84 8F 95 82 8C 85 95 90 FF` |
| `0x05C40` | 1 | 5 | 1.000 | `SNOW` | `93 8E 8F 97 FF` |
| `0x05C46` | 1 | 7 | 1.000 | `SPIKED` | `93 90 89 8B 85 84 FF` |
| `0x05C4E` | 1 | 6 | 1.000 | `CAMEL` | `83 81 8D 85 8C FF` |
| `0x05C55` | 1 | 6 | 1.000 | `KAPPA` | `8B 81 90 90 81 FF` |
| `0x05C5C` | 1 | 6 | 1.000 | `MAGIC` | `8D 81 87 89 83 FF` |
| `0x05C63` | 1 | 9 | 1.000 | `SANKI MAP` | `93 81 8E 8B 89 FF 8D 81 90` |
| `0x05C6D` | 1 | 5 | 1.000 | `CRSR` | `83 92 93 92 FF` |
| `0x05C73` | 1 | 17 | 1.000 | `MYSTERY GOODTIME` | `8D 99 93 94 85 92 99 FF 87 8F 8F 84 94 89 8D 85 FF` |
| `0x05C86` | 1 | 7 | 1.000 | `EFFECT` | `85 86 86 85 83 94 FF` |
| `0x05C8E` | 1 | 7 | 1.000 | `MASTER` | `8D 81 93 94 85 92 FF` |
| `0x05C96` | 1 | 4 | 1.000 | `JUMP` | `8A 95 8D 90` |
| `0x05C9D` | 1 | 8 | 1.000 | `KAPPA` | `8B 81 90 90 81 FF FF FF` |
| `0x05CA6` | 1 | 19 | 0.947 | `CAMEL RAINCOAT` | `83 81 8D 85 8C FF 92 81 89 8E 83 8F 81 94 FF FF FF FF FF` |
| `0x05CD1` | 1 | 50 | 0.960 | `STAM VIT PUNCH KICK WPN THROW AGI WILL DEF STR MAX` | `93 94 81 8D FF 96 89 94 FF 90 95 8E 83 88 FF 8B 89 83 8B FF 97 90 8E FF 94 88 92 8F 97 FF 81 87 89 FF 97 89 8C 8C FF 84 85 86 FF 93 94 92 FF 8D 81 98` |
| `0x05D04` | 1 | 7 | 0.857 | `VIT MAX` | `96 89 94 FF 8D 81 98` |
| `0x05FC6` | 1 | 4 | 1.000 | `NAME` | `8E 81 8D 85` |
| `0x05FCE` | 1 | 5 | 1.000 | `GINPA` | `87 89 8E 90 81` |
| `0x05FD5` | 1 | 4 | 1.000 | `THIS` | `94 88 89 93` |
| `0x05FE0` | 1 | 4 | 1.000 | `TURF` | `94 95 92 86` |
| `0x05FEC` | 1 | 5 | 1.000 | `FIGHT` | `86 89 87 88 94` |
| `0x06000` | 1 | 7 | 1.000 | `LETTING` | `8C 85 94 94 89 8E 87` |
| `0x0600C` | 1 | 4 | 1.000 | `PASS` | `90 81 93 93` |
| `0x06015` | 1 | 4 | 1.000 | `HOLY` | `88 8F 8C 99` |
| `0x0601A` | 1 | 4 | 1.000 | `SHIT` | `93 88 89 94` |
| `0x0602D` | 1 | 4 | 1.000 | `MEET` | `8D 85 85 94` |
| `0x06032` | 1 | 5 | 1.000 | `AGAIN` | `81 87 81 89 8E` |
| `0x0603C` | 1 | 8 | 1.000 | `REMEMBER` | `92 85 8D 85 8D 82 85 92` |
| `0x06045` | 1 | 5 | 1.000 | `THOSE` | `94 88 8F 93 85` |
| `0x0604B` | 1 | 5 | 1.000 | `DUDES` | `84 95 84 85 93` |
| `0x06052` | 1 | 4 | 1.000 | `THEY` | `94 88 85 99` |
| `0x0605E` | 1 | 4 | 1.000 | `ONES` | `8F 8E 85 93` |
| `0x06073` | 1 | 4 | 1.000 | `BEAT` | `82 85 81 94` |
| `0x0607B` | 1 | 4 | 0.750 | `BOYS` | `82 8F 99 93` |
| `0x06088` | 1 | 5 | 1.000 | `FIGHT` | `86 89 87 88 94` |
| `0x0608E` | 1 | 4 | 1.000 | `LIKE` | `8C 89 8B 85` |
| `0x0609D` | 1 | 6 | 1.000 | `PLEASE` | `90 8C 85 81 93 85` |
| `0x060AB` | 1 | 4 | 1.000 | `JOIN` | `8A 8F 89 8E` |
| `0x060C1` | 1 | 6 | 1.000 | `NOTHIN` | `8E 8F 94 88 89 8E` |
| `0x060D4` | 1 | 4 | 1.000 | `COME` | `83 8F 8D 85` |
| `0x060DD` | 1 | 6 | 1.000 | `BUNZO` | `FF 82 95 8E 9A 8F` |
| `0x060E5` | 1 | 6 | 1.000 | `PLEASE` | `90 8C 85 81 93 85` |
| `0x060EC` | 1 | 5 | 1.000 | `HURRY` | `88 95 92 92 99` |
| `0x060F8` | 1 | 4 | 1.000 | `GIVE` | `87 89 96 85` |
| `0x0610C` | 1 | 4 | 1.000 | `GOOD` | `87 8F 8F 84` |
| `0x06114` | 1 | 7 | 1.000 | `LEARNED` | `8C 85 81 92 8E 85 84` |
| `0x0611E` | 1 | 9 | 1.000 | `TECHNIQUE` | `94 85 83 88 8E 89 91 95 85` |
| `0x06136` | 1 | 4 | 1.000 | `SEEN` | `93 85 85 8E` |
| `0x0613B` | 1 | 6 | 1.000 | `NOTHIN` | `8E 8F 94 88 89 8E` |
| `0x06151` | 1 | 5 | 1.000 | `LEMME` | `8C 85 8D 8D 85` |
| `0x06157` | 1 | 4 | 1.000 | `KICK` | `8B 89 83 8B` |
| `0x06164` | 1 | 6 | 1.000 | `THANKS` | `94 88 81 8E 8B 93` |
| `0x06171` | 1 | 5 | 1.000 | `ICHI` | `FF 89 83 88 89` |
| `0x06184` | 1 | 4 | 1.000 | `GUYS` | `87 95 99 93` |
| `0x0618A` | 1 | 6 | 0.833 | `ANYWAY` | `81 8E 99 97 81 99` |
| `0x06191` | 1 | 5 | 1.000 | `ROKU` | `FF 92 8F 8B 95` |
| `0x061A0` | 1 | 5 | 1.000 | `ROKU` | `FF 92 8F 8B 95` |
| `0x061A7` | 1 | 5 | 1.000 | `AARGH` | `81 81 92 87 88` |
| `0x061B0` | 1 | 4 | 1.000 | `LOST` | `8C 8F 93 94` |
| `0x061D5` | 1 | 4 | 1.000 | `HURT` | `88 95 92 94` |
| `0x061DA` | 1 | 5 | 1.000 | `WOMEN` | `97 8F 8D 85 8E` |
| `0x061E4` | 1 | 4 | 1.000 | `WHAT` | `97 88 81 94` |
| `0x061EC` | 1 | 4 | 1.000 | `BEAT` | `82 85 81 94` |
| `0x061F1` | 1 | 4 | 0.750 | `THEM` | `94 88 85 8D` |
| `0x061FA` | 1 | 4 | 0.750 | `BEEG` | `82 85 85 87` |
| `0x061FF` | 1 | 4 | 1.000 | `BOSS` | `82 8F 93 93` |
| `0x06204` | 1 | 5 | 1.000 | `JINRO` | `8A 89 8E 92 8F` |
| `0x0620A` | 1 | 4 | 1.000 | `SENT` | `93 85 8E 94` |
| `0x06215` | 1 | 4 | 1.000 | `KICK` | `8B 89 83 8B` |
| `0x0621A` | 1 | 4 | 1.000 | `YOUR` | `99 8F 95 92` |
| `0x0621F` | 1 | 5 | 1.000 | `BUTTS` | `82 95 94 94 93` |
| `0x0622D` | 1 | 5 | 1.000 | `GONNA` | `87 8F 8E 8E 81` |
| `0x06233` | 1 | 4 | 1.000 | `KICK` | `8B 89 83 8B` |
| `0x06238` | 1 | 4 | 1.000 | `YOUR` | `99 8F 95 92` |
| `0x0623D` | 1 | 5 | 1.000 | `ASSES` | `81 93 93 85 93` |
| `0x06252` | 1 | 5 | 0.800 | `CHINA` | `83 88 89 8E 81` |
| `0x0625C` | 1 | 5 | 1.000 | `JINRO` | `8A 89 8E 92 8F` |
| `0x06262` | 1 | 4 | 1.000 | `WILL` | `97 89 8C 8C` |
| `0x06281` | 1 | 4 | 1.000 | `BEEG` | `82 85 85 87` |
| `0x06286` | 1 | 4 | 1.000 | `BOSS` | `82 8F 93 93` |
| `0x06294` | 1 | 4 | 1.000 | `SHOW` | `93 88 8F 97` |
| `0x06299` | 1 | 5 | 1.000 | `THESE` | `94 88 85 93 85` |
| `0x0629F` | 1 | 6 | 1.000 | `LOSERS` | `8C 8F 93 85 92 93` |
| `0x062A8` | 1 | 5 | 1.000 | `THING` | `94 88 89 8E 87` |
| `0x062B9` | 1 | 4 | 1.000 | `JEEZ` | `8A 85 85 9A` |
| `0x062C6` | 1 | 5 | 1.000 | `TOUGH` | `94 8F 95 87 88` |
| `0x062D1` | 1 | 5 | 1.000 | `HEISI` | `88 85 89 93 89` |
| `0x062D7` | 1 | 4 | 1.000 | `WILL` | `97 89 8C 8C` |
| `0x062DC` | 1 | 5 | 1.000 | `CRUSH` | `83 92 95 93 88` |
| `0x062EB` | 1 | 4 | 1.000 | `NYAH` | `8E 99 81 88` |
| `0x062F1` | 1 | 5 | 1.000 | `LATER` | `8C 81 94 85 92` |
| `0x06307` | 1 | 5 | 1.000 | `THOSE` | `94 88 8F 93 85` |
| `0x06315` | 1 | 5 | 1.000 | `ASSES` | `81 93 93 85 93` |
| `0x06323` | 1 | 5 | 1.000 | `KINSU` | `8B 89 8E 93 95` |
| `0x06330` | 1 | 6 | 1.000 | `BOOGIE` | `82 8F 8F 87 89 85` |
| `0x0633B` | 1 | 4 | 1.000 | `DAMN` | `84 81 8D 8E` |
| `0x06357` | 1 | 5 | 1.000 | `WRONG` | `97 92 8F 8E 87` |
| `0x0635D` | 1 | 4 | 1.000 | `SIDE` | `93 89 84 85` |
| `0x0636A` | 1 | 5 | 1.000 | `GONNA` | `87 8F 8E 8E 81` |
| `0x06370` | 1 | 4 | 1.000 | `TELL` | `94 85 8C 8C` |
| `0x06378` | 1 | 7 | 1.000 | `BROTHER` | `82 92 8F 94 88 85 92` |
| `0x06381` | 1 | 5 | 1.000 | `HEISI` | `88 85 89 93 89` |
| `0x0638B` | 1 | 5 | 1.000 | `CATCH` | `83 81 94 83 88` |
| `0x063AC` | 1 | 5 | 1.000 | `HEISI` | `88 85 89 93 89` |
| `0x063B6` | 1 | 4 | 1.000 | `GAWD` | `87 81 97 84` |
| `0x063C3` | 1 | 5 | 1.000 | `TOUGH` | `94 8F 95 87 88` |
| `0x063CD` | 1 | 4 | 1.000 | `BEEG` | `82 85 85 87` |
| `0x063D2` | 1 | 4 | 1.000 | `BOSS` | `82 8F 93 93` |
| `0x063D7` | 1 | 5 | 1.000 | `JINRO` | `8A 89 8E 92 8F` |
| `0x063DD` | 1 | 4 | 1.000 | `WILL` | `97 89 8C 8C` |
| `0x063F6` | 1 | 4 | 1.000 | `RUN` | `92 95 8E FF` |
| `0x063FD` | 1 | 5 | 0.800 | `FIGHT` | `86 89 87 88 94` |
| `0x06412` | 1 | 4 | 1.000 | `WORK` | `97 8F 92 8B` |
| `0x06421` | 1 | 7 | 0.857 | `THOUGHT` | `94 88 8F 95 87 88 94` |
| `0x0642D` | 1 | 6 | 1.000 | `SERVED` | `93 85 92 96 85 84` |
| `0x06434` | 1 | 4 | 1.000 | `TORA` | `94 8F 92 81` |
| `0x0643D` | 1 | 5 | 1.000 | `SORRY` | `93 8F 92 92 99` |
| `0x0644D` | 1 | 5 | 1.000 | `GIMME` | `87 89 8D 8D 85` |
| `0x06455` | 1 | 5 | 1.000 | `BREAK` | `82 92 85 81 8B` |
| `0x0645F` | 1 | 4 | 1.000 | `TAKE` | `94 81 8B 85` |
| `0x06467` | 1 | 4 | 1.000 | `WITH` | `97 89 94 88` |
| `0x06474` | 1 | 4 | 1.000 | `PHEW` | `90 88 85 97` |
| `0x0647E` | 1 | 4 | 1.000 | `NEED` | `8E 85 85 84` |
| `0x06485` | 1 | 4 | 1.000 | `BATH` | `82 81 94 88` |
| `0x0649F` | 1 | 4 | 1.000 | `HERE` | `88 85 92 85` |
| `0x064A8` | 1 | 4 | 1.000 | `TAKE` | `94 81 8B 85` |
| `0x064AD` | 1 | 4 | 1.000 | `THIS` | `94 88 89 93` |
| `0x064B2` | 1 | 6 | 1.000 | `KANPOU` | `8B 81 8E 90 8F 95` |
| `0x064C7` | 1 | 4 | 1.000 | `CURE` | `83 95 92 85` |
| `0x064D7` | 1 | 4 | 1.000 | `TORA` | `94 8F 92 81` |
| `0x064DE` | 1 | 4 | 1.000 | `HOLY` | `88 8F 8C 99` |
| `0x064E3` | 1 | 5 | 0.800 | `GUARD` | `87 95 81 92 84` |
| `0x064EA` | 1 | 7 | 1.000 | `PREPARE` | `90 92 85 90 81 92 85` |
| `0x064F6` | 1 | 6 | 1.000 | `HEAVEN` | `88 85 81 96 85 8E` |
| `0x064FF` | 1 | 5 | 1.000 | `WRATH` | `97 92 81 94 88` |
| `0x06510` | 1 | 4 | 0.750 | `WHAT` | `97 88 81 94` |
| `0x06519` | 1 | 5 | 0.800 | `LOUSY` | `8C 8F 95 93 99` |
| `0x0651F` | 1 | 10 | 1.000 | `FOREIGNERS` | `86 8F 92 85 89 87 8E 85 92 93` |
| `0x0652B` | 1 | 4 | 1.000 | `YOUR` | `99 8F 95 92` |
| `0x06538` | 1 | 5 | 1.000 | `SUCKS` | `93 95 83 8B 93` |
| `0x06547` | 1 | 5 | 1.000 | `GIMME` | `87 89 8D 8D 85` |
| `0x0654F` | 1 | 5 | 1.000 | `BREAK` | `82 92 85 81 8B` |
| `0x0655A` | 1 | 7 | 1.000 | `BYGONES` | `82 99 87 8F 8E 85 93` |
| `0x06565` | 1 | 7 | 1.000 | `BYGONES` | `82 99 87 8F 8E 85 93` |
| `0x06571` | 1 | 5 | 1.000 | `LATER` | `8C 81 94 85 92` |
| `0x06580` | 1 | 6 | 1.000 | `HEEHEE` | `88 85 85 88 85 85` |
| `0x0658C` | 1 | 7 | 1.000 | `NOTHING` | `8E 8F 94 88 89 8E 87` |
| `0x06594` | 1 | 8 | 1.000 | `PERSONAL` | `90 85 92 93 8F 8E 81 8C` |
| `0x0659E` | 1 | 5 | 1.000 | `SORRY` | `93 8F 92 92 99` |
| `0x065AC` | 1 | 4 | 1.000 | `WORK` | `97 8F 92 8B` |
| `0x065B9` | 1 | 4 | 1.000 | `WELL` | `97 85 8C 8C` |
| `0x065C1` | 1 | 4 | 1.000 | `HAVE` | `88 81 96 85` |
| `0x065C6` | 1 | 4 | 1.000 | `SOME` | `93 8F 8D 85` |
| `0x065CB` | 1 | 4 | 1.000 | `NEWS` | `8E 85 97 93` |
| `0x065D4` | 1 | 4 | 0.750 | `TORA` | `94 8F 92 81` |
| `0x065D9` | 1 | 4 | 1.000 | `TOOK` | `94 8F 8F 8B` |
| `0x065E2` | 1 | 4 | 1.000 | `GIRL` | `87 89 92 8C` |
| `0x065F6` | 1 | 4 | 1.000 | `WITH` | `97 89 94 88` |
| `0x06604` | 1 | 7 | 0.857 | `INSTEAD` | `89 8E 93 94 85 81 84` |

## New Printable PRG Runs

These are discovery anchors, not a finished script dump. Short or encoded strings may not appear here.
The current results are mostly non-language byte patterns, confirming that the English script uses
the game's custom tile encoding rather than plain ASCII.

| ROM offset | PRG bank | length | text |
| --- | ---: | ---: | --- |
| `0x0788E` | 1 | 7 | `zzzzzz6` |
| `0x13CB2` | 4 | 5 | `$5GVq` |
| `0x13D76` | 4 | 10 | `%/8?FNYbit` |
| `0x1A7B4` | 6 | 6 | `zz\\\z` |
| `0x1A7C5` | 6 | 5 | `z\\\z` |
| `0x1A7D4` | 6 | 6 | `zz\\\z` |
| `0x1A7DE` | 6 | 4 | `\\\z` |
| `0x1A7E6` | 6 | 4 | `\\\z` |
| `0x1A7EE` | 6 | 4 | `\\\z` |
| `0x1A7F6` | 6 | 4 | `\\\z` |
| `0x1A7FE` | 6 | 4 | `\\\z` |
| `0x1A806` | 6 | 4 | `\\\z` |
| `0x1A80E` | 6 | 4 | `\\\z` |
| `0x1A816` | 6 | 4 | `\\\z` |
| `0x1A81E` | 6 | 4 | `\\\z` |
| `0x1A826` | 6 | 4 | `\\\z` |
| `0x1A82E` | 6 | 4 | `\\\z` |
| `0x1A836` | 6 | 4 | `\\\z` |
| `0x1A83E` | 6 | 4 | `\\\z` |
| `0x1A846` | 6 | 4 | `\\\z` |
| `0x1A84E` | 6 | 4 | `\\\z` |
| `0x1A856` | 6 | 4 | `\\\z` |
| `0x1BB2F` | 6 | 4 | `}}}z` |

## How To Use This Reference

1. Diff each changed PRG bank against the Japanese ROM and classify text, pointer, code, and palette spans.
2. Recover the English pointer-table writes and map them back to Japanese source records.
3. Build a deterministic script extractor/inserter from those records before translating more text.
4. Reuse only structural knowledge. Do not reuse the English localization wording as the Korean translation source.
5. Treat CHR changes starting at `0x20010` as font/icon reference material.
