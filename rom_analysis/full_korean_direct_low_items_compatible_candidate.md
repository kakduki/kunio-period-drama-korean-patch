# Full Direct-Low Korean Candidate

This candidate preserves the English patch's direct-low 8x8 renderer contract and replaces every extracted direct-low label with a bounded Korean label.

- Input candidate MD5: `d062b19d23050cd4e148e22fbfff57b7`.
- Candidate MD5: `b453fdef1c17ca3875fbd48b31454b5f`.
- Direct-low runs: `120`.
- Korean glyphs allocated: `77`; reserved low codes: `0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x38`.
- IPS records: `494`; IPS round trip is checked by the builder.
- Runtime/screen status: pending bounded per-context proof.
- Release status: `NOT_READY`.

## Sample Rows

| bank | ROM offset | English | Korean | new bytes |
| ---: | --- | --- | --- | --- |
| 1 | `0x07897` | GROWTH | 성장 | `01 02 00 00 00 00` |
| 1 | `0x0789E` | RATES | 비 | `03 00 00 00 00` |
| 1 | `0x078A4` | LEFTEND | 끝 | `04 00 00 00 00 00 00` |
| 3 | `0x0FC31` | NONE | 공 | `05 00 00 00` |
| 4 | `0x136DA` | TECHNOS | 기술사 | `06 07 08 00 00 00 00` |
| 4 | `0x136E2` | JAPAN | 일 | `09 00 00 00 00` |
| 4 | `0x136E8` | CORP | 회사 | `0A 08 00 00` |
| 4 | `0x13AE3` | PLAYER | 선수 | `0B 0C 00 00 00 00` |
| 4 | `0x13AEB` | PLAYER | 선수 | `0B 0C 00 00 00 00` |
| 6 | `0x1A2EF` | MENU | 메 | `0D 00 00 00` |
| 6 | `0x1A778` | FOOD | 밥 | `0E 00 00 00` |
| 6 | `0x1A786` | HEALER | 치료 | `0F 10 00 00 00 00` |
| 6 | `0x1A790` | TECH | 기술 | `06 07 00 00` |
| 6 | `0x1A798` | FOOD | 밥 | `0E 00 00 00` |
| 6 | `0x1A7A0` | SHOP | 가게 | `11 12 00 00` |
| 6 | `0x1A7A6` | CHANCE | 기회 | `06 0A 00 00 00 00` |
| 6 | `0x1A7B0` | FOOD | 밥 | `0E 00 00 00` |
| 6 | `0x1A7BA` | SHOPBUNZO | 분조가게 | `13 14 11 12 00 00 00 00 00` |
| 6 | `0x1A7CA` | SHOP | 가게 | `11 12 00 00` |
| 6 | `0x1A7D0` | FOOD | 밥 | `0E 00 00 00` |
| 6 | `0x1A7DA` | SHOP | 가게 | `11 12 00 00` |
| 6 | `0x1A7E2` | SHOP | 가게 | `11 12 00 00` |
| 6 | `0x1A7EA` | SHOP | 가게 | `11 12 00 00` |
| 6 | `0x1A7F2` | SHOP | 가게 | `11 12 00 00` |
| 6 | `0x1A7FA` | SHOP | 가게 | `11 12 00 00` |
| 6 | `0x1A802` | SHOP | 가게 | `11 12 00 00` |
| 6 | `0x1A80A` | SHOP | 가게 | `11 12 00 00` |
| 6 | `0x1A812` | SHOP | 가게 | `11 12 00 00` |
| 6 | `0x1A81A` | SHOP | 가게 | `11 12 00 00` |
| 6 | `0x1A822` | SHOP | 가게 | `11 12 00 00` |
| 6 | `0x1A82A` | SHOP | 가게 | `11 12 00 00` |
| 6 | `0x1A832` | SHOP | 가게 | `11 12 00 00` |
| 6 | `0x1A83A` | SHOP | 가게 | `11 12 00 00` |
| 6 | `0x1A842` | SHOP | 가게 | `11 12 00 00` |
| 6 | `0x1A84A` | SHOP | 가게 | `11 12 00 00` |
| 6 | `0x1A852` | SHOP | 가게 | `11 12 00 00` |
| 6 | `0x1BB4A` | SAVED | 장 | `02 00 00 00 00` |
| 7 | `0x1C914` | FIST | 주먹 | `15 16 00 00` |
| 7 | `0x1C920` | KICK | 타 | `17 00 00 00` |
| 7 | `0x1C937` | TORP | 어뢰 | `18 19 00 00` |

## Gate

- Build and byte-scope proof: PASS if the JSON report exists and IPS round trip succeeds.
- Exact screen proof: UNKNOWN until each shared Bank 7 context is captured.
- This candidate does not replace the relocated pointer-dialogue records; it composes with the current full pointer/menu candidate.
