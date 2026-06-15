#!/usr/bin/env python3
"""
쿠니오 시대극 - CHR ROM에서 실제 게임 폰트 추출 + 8x16 한글 폰트 생성
"""
from PIL import Image
import os

ROM_PATH = '/tmp/rom_hack/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes'
OUT_DIR = '/tmp/rom_hack/font'
os.makedirs(OUT_DIR, exist_ok=True)

with open(ROM_PATH, 'rb') as f:
    data = f.read()

chr_rom = data[16+131072:]  # CHR ROM: 131072 bytes

print("=" * 60)
print("CHR ROM 폰트 분석 및 8x16 한글 폰트 준비")
print("=" * 60)

# CHR 16개 뱅크를 개별 이미지로 저장
for bank in range(16):
    bank_data = chr_rom[bank*8192:(bank+1)*8192]
    
    # 2bpp NES 타일로 렌더링
    # CHR 8KB = 512 타일 (8x8) 또는 256 타일 (8x16)
    # 8x16 폰트로 보면: 32bytes/char, 256 chars/bank
    
    img_8x16 = Image.new('RGB', (8*16, 16*16), (255, 255, 255))
    px = img_8x16.load()
    
    for char_idx in range(256):
        base = char_idx * 32
        if base + 32 > len(bank_data):
            break
        
        cx = (char_idx % 16) * 8
        cy = (char_idx // 16) * 16
        
        for row in range(16):
            byte_plane0 = bank_data[base + row]
            byte_plane1 = bank_data[base + row + 16] if row < 16 else 0
            
            for col in range(8):
                bit0 = (byte_plane0 >> (7 - col)) & 1
                bit1 = (byte_plane1 >> (7 - col)) & 1
                pixel = bit0 | (bit1 << 1)
                
                # NES 컬러: 0=투명/하양, 1=밝은회색, 2=어두운회색, 3=검정
                colors = [(255,255,255), (200,200,200), (120,120,120), (0,0,0)]
                px[cx + col, cy + row] = colors[min(pixel, 3)]
    
    img_8x16.save(f'{OUT_DIR}/chr_bank_{bank:02d}_8x16.png')
    
    # 8x8 타일(16바이트)로도 저장
    img_8x8 = Image.new('RGB', (8*32, 8*16), (255, 255, 255))
    px8 = img_8x8.load()
    
    for tile_idx in range(512):
        base = tile_idx * 16
        if base + 16 > len(bank_data):
            break
        
        tx = (tile_idx % 32) * 8
        ty = (tile_idx // 32) * 8
        
        for row in range(8):
            byte_p0 = bank_data[base + row]
            byte_p1 = bank_data[base + 8 + row] if base + 8 + row < len(bank_data) else 0
            
            for col in range(8):
                bit0 = (byte_p0 >> (7 - col)) & 1
                bit1 = (byte_p1 >> (7 - col)) & 1
                pixel = bit0 | (bit1 << 1)
                colors = [(255,255,255), (200,200,200), (120,120,120), (0,0,0)]
                px8[tx + col, ty + row] = colors[min(pixel, 3)]
    
    img_8x8.save(f'{OUT_DIR}/chr_bank_{bank:02d}_8x8.png')

print("CHR 뱅크 이미지 생성 완료 (16개 x 2형식)")

# 폰트 영역 식별: Bank 5,6,7 에 주로 폰트/스프라이트
# Bank 4-7 = 배경/텍스트 폰트 영역 (게임마다 다름)

# 게임 내 문자 매핑 추정
# 쿠니오 게임은 보통 Bank 4-5 영역에 폰트 데이터
# 실제 게임에 사용되는 문자 확인을 위해 빈도 분석

print("\n=== 각 Bank의 8x16 폰트 사용량 분석 ===")
for bank in range(16):
    bank_data = chr_rom[bank*8192:(bank+1)*8192]
    # 비어있지 않은 타일 수
    used_tiles = 0
    for char_idx in range(256):
        base = char_idx * 32
        total = sum(bank_data[base:base+32])
        if total > 0 and total < 255*32:
            used_tiles += 1
    print(f"  Bank {bank:02d}: {used_tiles}/256 타일 사용")
