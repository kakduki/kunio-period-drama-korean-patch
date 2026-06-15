#!/usr/bin/env python3
"""NES 롬 한글 패치 - 1단계: CHR 폰트 + 텍스트 구조 분석"""
import struct, os

ROM_PATH = '/tmp/rom_hack/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes'
OUT_DIR = '/tmp/rom_hack/analysis'

os.makedirs(OUT_DIR, exist_ok=True)

with open(ROM_PATH, 'rb') as f:
    data = f.read()

# 헤더
h = data[:16]
prg_size = h[4] * 16384
chr_size = h[5] * 8192
mapper = (h[6] >> 4) | (h[7] & 0xF0)
print(f"PRG: {prg_size} bytes, CHR: {chr_size} bytes, Mapper: {mapper}")

prg = data[16:16+prg_size]
chr_rom = data[16+prg_size:16+prg_size+chr_size]

# CHR ROM 분석: 8x16 폰트 타일 추출
# NES CHR: 각 타일 = 8x8 픽셀 (16 bytes), 8x16 폰트 = 2 타일 (32 bytes)
# CHR ROM에는 보통 0x000-0x7FF: 스프라이트, 0x800-0xFFF: 배경 등

# 타일 덤프
with open(f'{OUT_DIR}/chr_dump.bin', 'wb') as f:
    f.write(chr_rom)

# 폰트 영역 추정 (보통 CHR의 후반부 0x800+)
# 8x16 폰트: 각 글자 = 16 bytes (상위 8바이트 + 하위 8바이트)
# 총 256개 글자 = 4096 bytes

# CHR ROM을 16바이트 단위 타일로 나누고 시각화
tile_count = len(chr_rom) // 16
print(f"\nCHR ROM: {tile_count} 타일 (8x8)")

# 패턴 분석 - 반복되는 텍스 영역 찾기
# ASCII 텍스트 영역 스캔
import re
ascii_texts = []

for bank_start in [0, prg_size//2]:
    bank = prg[bank_start:bank_start+prg_size//2] if bank_start == 0 else prg[prg_size//2:]
    
    for m in re.finditer(rb'[\x20-\x7E]{4,}', bank):
        text = m.group().decode('ascii', errors='replace')
        if len(text) >= 4 and text.isprintable():
            ascii_texts.append((bank_start + m.start(), text))

print(f"\n=== PRG ASCII 텍스트 ===")
for offset, text in ascii_texts[:20]:
    print(f"  PRG+0x{offset:05X}: \"{text}\"")

# 특정 포인터 테이블 찾기
# MMC3: 보통 0x8000-0xFFFF 범위에서 텍스트 포인터 찾기
# 패미컴 텍스트: 보통 0x80-0xFF 범위의 가나 문자 사용
# 쿠니오 게임 특성상 Shift-JIS가 아닌 내부 인코딩 사용 가능

# 간단한 텍스트 덤프 - 일정 범위 출력
print(f"\n=== PRG 끝부분 (0xC000-0xFFFF) 분석 ===")
end_section = prg[0xC000-0x10:0x10000]  # 마지막 16KB 뱅크 (고정)
with open(f'{OUT_DIR}/bank_fixed.txt', 'w', encoding='utf-8') as f:
    for i in range(0, len(end_section), 16):
        hex_str = ' '.join(f'{b:02X}' for b in end_section[i:i+16])
        ascii_str = ''.join(chr(b) if 0x20 <= b < 0x7F else '.' for b in end_section[i:i+16])
        f.write(f"{(0xC000+i):05X}: {hex_str}  {ascii_str}\n")

print(f"Fixed bank dump saved to {OUT_DIR}/bank_fixed.txt")

# 유명한 컴프레션 패턴 확인 (쿠니오 게임은 RLE 계열 사용)
# 텍스트 시작 위치 찾기
print(f"\n=== 키워드로 텍스트 위치 검색 ===")
keywords = [b'Kunio', b'downtown', b'special', b'jidaigeki', b'zenin']
for kw in keywords:
    idx = prg.find(kw)
    while idx != -1:
        print(f"  0x{idx+16:05X}: {prg[idx:idx+len(kw)+20]}")
        idx = prg.find(kw, idx+1)

print(f"\n분석 완료. 결과: {OUT_DIR}/")
