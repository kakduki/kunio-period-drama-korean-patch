#!/usr/bin/env python3
import re

with open('/tmp/rom_hack/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes', 'rb') as f:
    data = f.read()

prg = data[16:131088]  # PRG ROM

# ASCII 문자열 찾기
print("=== ASCII 문자열 ===")
ascii_pattern = re.compile(rb'[\x20-\x7E]{4,}')
matches = list(ascii_pattern.finditer(prg))
for m in matches[:30]:
    offset = m.start()
    text = m.group().decode('ascii', errors='replace')
    print(f'  PRG+0x{offset:05X}: "{text}"')

print()

# Shift-JIS 텍스트 영역 찾기
print("=== Shift-JIS 텍스트 ===")
sjis_regions = []
i = 0
while i < len(prg):
    b = prg[i]
    # SJIS lead byte
    if (0x81 <= b <= 0x9F) or (0xE0 <= b <= 0xEF):
        if i + 1 < len(prg):
            b2 = prg[i+1]
            if 0x40 <= b2 <= 0xFC:
                if not sjis_regions or sjis_regions[-1][1] != i - 1:
                    sjis_regions.append([i, i+1])
                else:
                    sjis_regions[-1][1] = i+1
                i += 2
                continue
    i += 1

count = 0
for s, e in sjis_regions:
    length = e - s + 1
    if length >= 6:  # 3자 이상 일본어
        raw = prg[s:e+1]
        try:
            text = raw.decode('shift-jis')
            if any('\u3040' <= c <= '\u309F' or '\u30A0' <= c <= '\u30FF' or '\u4E00' <= c <= '\u9FFF' for c in text):
                print(f'  PRG+0x{s+16:05X} ({length:3d}bytes): {text}')
                count += 1
                if count >= 40:
                    break
        except:
            pass

print(f"\nTotal SJIS text regions found: {count}")
print(f"PRG ROM size: {len(prg)} bytes")
