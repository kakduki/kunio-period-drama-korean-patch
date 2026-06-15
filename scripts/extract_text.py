#!/usr/bin/env python3
"""
NES 쿠니오 시대극 - 포인터 기반 텍스트 추출기
MMC3 mapper 4, PRG 128KB
텍스트 포인터 찾기 + 실제 텍스트 덤프
"""
import struct, sys

ROM_PATH = '/tmp/rom_hack/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes'

with open(ROM_PATH, 'rb') as f:
    data = f.read()

# NES 6502 주소 변환
# PRG ROM 128KB = 8 x 16KB 뱅크
# CPU 매핑: 0x8000-0xFFFF (32KB 윈도우)
# MMC3: 2개 뱅크 선택 (0x8000-0x9FFF, 0xA000-0xBFFF), 0xC000-0xFFFF 고정

def prg_to_cpu(prg_offset):
    """PRG ROM 오프셋 → CPU 주소"""
    bank_num = prg_offset // 16384
    bank_offset = prg_offset % 16384
    if bank_num < 4:
        return 0x8000 + bank_offset
    else:
        return 0x8000 + bank_offset  # MMC3 매핑

def cpu_to_prg(cpu_addr, active_bank=0, second_bank=1, fixed_bank=7):
    """CPU 주소 → PRG ROM 오프셋 (뱅크 매핑 가정)"""
    if 0x8000 <= cpu_addr <= 0x9FFF:
        return active_bank * 16384 + (cpu_addr - 0x8000)
    elif 0xA000 <= cpu_addr <= 0xBFFF:
        return second_bank * 16384 + (cpu_addr - 0xA000) + 8192
    elif 0xC000 <= cpu_addr <= 0xFFFF:
        return fixed_bank * 16384 + (cpu_addr - 0xC000)
    return -1

prg = data[16:16+131072]

print("=" * 60)
print("쿠니오 시대극 - 텍스트 포인터 분석")
print("=" * 60)

# 텍스트 포인터 찾기: 
# 쿠니오 게임은 보통 0x8000-0xBFFF 영역에 텍스트 포인터 테이블이 있고
# 실제 텍스트는 0xC000-0xFFFF (고정 뱅크) 또는 다른 뱅크에 있음

# 고정 뱅크 (마지막 16KB = bank 7) 내용 확인
print("\n=== 고정 뱅크 (0xC000-0xFFFF) ===")
fixed_bank = prg[7*16384:8*16384]

# 텍스트 포인터 패턴: 6502에서 LDA (ptr),Y 같은 패턴
# 보통 포인터는 little-endian 2바이트

# 텍스트 데이터 블록 찾기
# Shift-JIS 텍스트는 0x81-0x9F, 0xE0-0xEF 범위에서 시작
print("\n=== Shift-JIS 추정 텍스트 블록 ===")
for bank in range(8):
    bank_data = prg[bank*16384:(bank+1)*16384]
    sjis_sequences = []
    i = 0
    while i < len(bank_data):
        b = bank_data[i]
        if (0x81 <= b <= 0x9F) or (0xE0 <= b <= 0xEF):
            if i + 1 < len(bank_data):
                b2 = bank_data[i+1]
                if 0x40 <= b2 <= 0xFC:
                    if not sjis_sequences or sjis_sequences[-1][1] != i - 1:
                        sjis_sequences.append([i, i+1])
                    else:
                        sjis_sequences[-1][1] = i+1
                    i += 2
                    continue
        i += 1
    
    long_seqs = [(s, e) for s, e in sjis_sequences if e - s >= 8]
    if long_seqs:
        print(f'Bank {bank} (CPU 0x{8000+bank*16384:04X}?): {len(long_seqs)} SJIS 시퀀스 (>=4 chars)')
        for s, e in long_seqs[:5]:
            raw = bank_data[s:e+1]
            try:
                text = raw.decode('shift-jis')
                addr = bank * 16384 + 16  # ROM 오프셋이 아닌 CPU 주소
                print(f'  0x{addr:05X} ({e-s+1:3d}b): {text.strip()[:40]}')
            except:
                pass

# 널 종단 문자열 검색 (0x00으로 끝나는 영문/일본어)
print("\n=== 0x00 종단 텍스트 블록 (5바이트 이상) ===")
for bank in range(8):
    bank_data = prg[bank*16384:(bank+1)*16384]
    i = 0
    count = 0
    while i < len(bank_data) and count < 20:
        b = bank_data[i]
        # 0x20-0x7F 범위 + 일본어 범위 시작
        if 0x20 <= b <= 0x7E or b >= 0x80:
            start = i
            while i < len(bank_data) and bank_data[i] != 0 and (0x20 <= bank_data[i] <= 0x7E or bank_data[i] >= 0x80):
                i += 1
            length = i - start
            if length >= 5:
                raw = bank_data[start:i]
                addr = bank * 16384 + start + 16
                # Shift-JIS로 디코딩 시도
                try:
                    text = raw.decode('shift-jis')
                    if any('\u3040' <= c <= '\u309F' or '\u30A0' <= c <= '\u30FF' or '\u4E00' <= c <= '\u9FFF' for c in text):
                        print(f'  ROM+0x{addr:05X} ({length:3d}b): {text.strip()[:50]}')
                        count += 1
                except:
                    # ASCII only
                    try:
                        text = raw.decode('ascii')
                        if text.isprintable() and any(c.isalpha() for c in text):
                            print(f'  ROM+0x{addr:05X} ({length:3d}b ASCII): {text.strip()[:50]}')
                            count += 1
                    except:
                        pass
            i += 1
        else:
            i += 1
