#!/usr/bin/env python3
"""PRG ROM 텍스트 영역 전체 탐색"""
import re
from rom_utils import find_rom_path

with open(find_rom_path(), 'rb') as f:
    data = f.read()

prg = data[16:16+131072]

# PRG를 8KB 뱅크로 (MMC3)
print("=== PRG 뱅크별 텍스트 영역 ===")
for bank_num in range(8):
    bank_data = prg[bank_num*16384:(bank_num+1)*16384]
    
    text_regions = []
    i = 0
    while i < len(bank_data):
        b = bank_data[i]
        # ASCII printable + NES 내부 문자 코드 범위
        if (b >= 0x20 and b <= 0x7E) or b >= 0x80:
            if not text_regions or text_regions[-1][1] != i - 1:
                text_regions.append([i, i])
            else:
                text_regions[-1][1] = i
        i += 1
    
    long_regions = [(s, e, e-s+1) for s, e in text_regions if e - s >= 6]
    print(f'\nBank {bank_num} (0x{(bank_num*16384+16):05X}): {len(long_regions)} 텍스트 영역')
    for s, e, l in long_regions[:15]:
        raw = bank_data[s:e+1]
        hex_str = ' '.join(f'{b:02X}' for b in raw[:20])
        print(f'  0x{(s+16+bank_num*16384):05X} ({l:3d}bytes): {hex_str}')
