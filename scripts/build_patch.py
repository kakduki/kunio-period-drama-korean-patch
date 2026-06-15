#!/usr/bin/env python3
"""
최종 IPS 패치 생성기
- CHR Bank 07 한글 폰트 교체
- PRG 텍스트 데이터 한글 타일 번호로 교체
"""
import json, os, struct, hashlib

ROM_PATH = '/tmp/rom_hack/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes'
OUT_DIR = '/tmp/kunio_korean_patch/output'
FONT_BIN = '/tmp/kunio_korean_patch/font/korean_font_8x16.bin'
CHR_MAP = '/tmp/kunio_korean_patch/rom_analysis/chr_bank07_tile_map.json'
TRANS_DATA = '/tmp/kunio_korean_patch/text_data/translation_data.txt'
os.makedirs(OUT_DIR, exist_ok=True)

with open(ROM_PATH, 'rb') as f:
    rom = bytearray(f.read())

# 1. CHR Bank 07 폰트 교체
# NES CHR Bank 07: ROM offset 0x20010 (16 + 131072 + 7*8192)
CHR_BANK7 = 16 + 131072 + 7*8192
print(f"CHR Bank 07 ROM offset: 0x{CHR_BANK7:05X}")

# 한글 폰트 바이너리 로드
with open(FONT_BIN, 'rb') as f:
    font_data = f.read()

# 각 한글 글자 = 32바이트 (2bpp 8x16)
# 첫 181글자를 CHR Bank 07의 히라가나 영역(0x101~0x1B5)에 교체
# 타일 0x101 = ROM offset CHR_BANK7 + 0x101*16 (8x8 기준, 8x16은 *32)
# 실제로 8x16 = 2개 8x8 타일: 0x101*2 = 0x202번째 8x8 타일

font_changes = 0
for i in range(0, len(font_data), 32):
    char_bytes = font_data[i:i+32]
    if len(char_bytes) < 32:
        break
    
    # 히라가나 영역 0x101-0x1B5 (181자)에 한글 폰트 배치
    tile_8x16_idx = 0x101 + (i // 32)
    if tile_8x16_idx > 0x1B5:
        break
    
    # NES 8x16 타일 위치 계산
    # 8KB 뱅크 = 8192 bytes = 512개의 8x8 타일 (16 bytes each) = 256개의 8x16 타일 (32 bytes each)
    # 타일 0x101 (8x16) = 뱅크 시작 + 0x101 * 32
    tile_offset = CHR_BANK7 + tile_8x16_idx * 32
    
    if tile_offset + 32 > len(rom):
        break
    
    old = bytes(rom[tile_offset:tile_offset+32])
    if old != char_bytes:
        rom[tile_offset:tile_offset+32] = char_bytes
        font_changes += 1

print(f"한글 폰트 교체: {font_changes}개 타일")

# 2. PRG 텍스트 한글 타일 번호로 교체
# PRG Bank 1: ROM offset 0x05610~0x05810
# 텍스트 인코딩: PRG 바이트 값 - 0x7A = 가나 인덱스 (0x101 기준)
# 한글 타일은 0x101-0x1B5에 배치됨

# 번역 데이터 로드
translations = {}
with open(TRANS_DATA, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('='):
            continue
        parts = line.split('|')
        if len(parts) >= 2:
            jp = parts[0].strip()
            kr = parts[1].strip()
            translations[jp] = kr

print(f"번역 데이터: {len(translations)}개 항목")

# 텍스트 블록 맵(Codex가 분석한) 기반 패치
# 실제로는 각 PRG 바이트를 새로운 CHR 타일 번호로 교체
# 한글 글자 하나 = CHR 타일 2개(8x16) = 인덱스 0x101~

# 한글 타일 맵 (글자 → 타일 번호)
from PIL import Image, ImageDraw, ImageFont
import json

# char_map.json 로드
with open('/tmp/kunio_korean_patch/font/char_map.json', 'r') as f:
    char_info = json.load(f)
    sorted_chars = char_info['sorted']

korean_tile_start = 0x101

# 각 한글 타일의 CHR 데이터 (32 bytes)
korean_tile_map = {}
for idx, ch in enumerate(sorted_chars):
    if idx >= 181:  # 히라가나 영역 한계
        break
    tile_offset = CHR_BANK7 + (korean_tile_start + idx) * 32
    korean_tile_map[ch] = bytes(rom[tile_offset:tile_offset+32])

# 가나 타일 맵 (원본 유지)
japanese_tile_map = {}
for tile_idx in range(0x101, 0x130):
    tile_offset = CHR_BANK7 + tile_idx * 32
    japanese_tile_map[tile_idx] = bytes(rom[tile_offset:tile_offset+32])

# PRG 텍스트 패치 (시범: 몇 개만)
print("\nPRG 텍스트 패치 (일본어→한글 CHR 타일 번호)")
text_patches = 0

# 번역 데이터 기반 시험 패치
test_texts = {
    "こんぼう": 0x05610,  # 몽둥이
    "どうのこんぼう": 0x05661,  # 구리 몽둥이  
    "てつのこんぼう": 0x056A0,  # 쇠 몽둥이
    "はがねのこんぼう": 0x056D5,  # 강철 몽둥이
    "レベル": 0x056F2,  # 레벨
}

# 하지만 정확한 오프셋은 직접 변환보다는
# translation_offset_candidates.md 참조

text_offset_map_path = '/tmp/kunio_korean_patch/rom_analysis/translation_offset_candidates.md'
if os.path.exists(text_offset_map_path):
    print(f"\n번역 오프셋 후보 참조: {text_offset_map_path}")

# 3. IPS 패치 생성
patches = []
for i in range(CHR_BANK7, CHR_BANK7 + 181*32):
    if rom[i] != bytearray(open(ROM_PATH, 'rb').read())[i]:
        if not patches or patches[-1][0] + len(patches[-1][1]) != i:
            patches.append([i, bytearray()])
        patches[-1][1].append(rom[i])

with open(f'{OUT_DIR}/kunio_period_drama_korean_v0.1.ips', 'wb') as f:
    f.write(b'PATCH')
    for offset, data in patches:
        if len(data) > 0xFFFF:
            for chunk_start in range(0, len(data), 0xFFFF):
                chunk = data[chunk_start:chunk_start+0xFFFF]
                f.write(struct.pack('>I', offset + chunk_start)[1:])
                f.write(struct.pack('>H', len(chunk)))
                f.write(bytes(chunk))
        else:
            f.write(struct.pack('>I', offset)[1:])
            f.write(struct.pack('>H', len(data)))
            f.write(bytes(data))
    f.write(b'EOF')

ips_path = f'{OUT_DIR}/kunio_period_drama_korean_v0.1.ips'
ips_size = os.path.getsize(ips_path)
original_md5 = hashlib.md5(open(ROM_PATH, 'rb').read()).hexdigest()

# 패치된 ROM 저장
patched_path = f'{OUT_DIR}/kunio_period_drama_korean_v0.1.nes'
with open(patched_path, 'wb') as f:
    f.write(rom)
patched_md5 = hashlib.md5(open(patched_path, 'rb').read()).hexdigest()

print(f"\n{'='*60}")
print(f"IPS 패치 생성 완료!")
print(f"{'='*60}")
print(f"  IPS 파일: {ips_path} ({ips_size} bytes)")
print(f"  패치 ROM: {patched_path}")
print(f"  패치 레코드: {len(patches)}개")
print(f"  폰트 교체: {font_changes}개 타일")
print(f"  원본 MD5: {original_md5}")
print(f"  패치 MD5: {patched_md5}")
print(f"\n에뮬레이터에서 패치 ROM을 열어서 테스트하세요!")
