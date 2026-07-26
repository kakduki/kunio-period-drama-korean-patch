# Opening MMC3/PPU Mapping Trace

Status: PASS

- Final Lua reason: lua_done
- Capture frame: 883
- Callback counts: {'mapper_select': 18130, 'mapper_data': 18130, 'ppu_control': 4093}

## Recurring Writer PCs

These are CPU program-counter samples taken at register writes. They identify
candidate mapper-update routines; they do not by themselves authorize a hook.

| write kind | CPU PC | writes |
| --- | --- | ---: |
| mmc3 select | 0xFF3F | 4233 |
| mmc3 select | 0xFF50 | 4233 |
| mmc3 select | 0xFEDD | 2069 |
| mmc3 select | 0xFEEC | 2069 |
| mmc3 select | 0xEDDE | 1368 |
| mmc3 select | 0xFEFC | 842 |
| mmc3 select | 0xFF0C | 842 |
| mmc3 select | 0xFF1C | 842 |
| mmc3 select | 0xFF2C | 842 |
| mmc3 select | 0xED56 | 819 |
| mmc3 data | 0xFF49 | 4233 |
| mmc3 data | 0xFF5C | 4233 |
| mmc3 data | 0xFEE3 | 2069 |
| mmc3 data | 0xFEF2 | 2069 |
| mmc3 data | 0xEDE2 | 1368 |
| mmc3 data | 0xFF02 | 842 |
| mmc3 data | 0xFF12 | 842 |
| mmc3 data | 0xFF22 | 842 |
| mmc3 data | 0xFF32 | 842 |
| mmc3 data | 0xED5C | 819 |
| ppu control | 0xDD6E | 1503 |
| ppu control | 0xEDB8 | 1368 |
| ppu control | 0xFDC9 | 685 |
| ppu control | 0xD6C9 | 459 |
| ppu control | 0xFED4 | 12 |
| ppu control | 0xFDDA | 12 |
| ppu control | 0xFD8B | 12 |
| ppu control | 0xFF86 | 12 |
| ppu control | 0xE8E4 | 9 |
| ppu control | 0xE923 | 9 |
| ppu control | 0xFEC8 | 8 |
| ppu control | 0xDDD4 | 6 |
- MMC3 control: 0x07; CHR mode: 0
- PPUCTRL: 0x8C; background pattern base: 0x0000
- Reference slots 0x81 and 0x9A match expected Bank 8 physical tiles: False

## CHR Windows

| PPU window | 1 KiB CHR bank | physical 8 KiB CHR bank |
| --- | ---: | ---: |
| 0x0000-0x03FF | 60 | 7 |
| 0x0400-0x07FF | 61 | 7 |
| 0x0800-0x0BFF | 62 | 7 |
| 0x0C00-0x0FFF | 63 | 7 |
| 0x1000-0x13FF | 48 | 6 |
| 0x1400-0x17FF | 49 | 6 |
| 0x1800-0x1BFF | 50 | 6 |
| 0x1C00-0x1FFF | 51 | 6 |

## Reference Dialogue Codes

| code | PPU pattern address | PPU window | 1 KiB CHR bank | physical Bank/tile |
| --- | --- | --- | ---: | --- |
| 0x81 | 0x0810 | 0x0800-0x0BFF | 62 | Bank 7, tile 0x181 |
| 0x9A | 0x09A0 | 0x0800-0x0BFF | 62 | Bank 7, tile 0x19A |

This proves the opening screen's mapped CHR state only. A different scene
or a new font page still requires its own mapper-state evidence.
