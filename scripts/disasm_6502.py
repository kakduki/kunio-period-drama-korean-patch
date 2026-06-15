#!/usr/bin/env python3
"""
6502 디스어셈블러 + 텍스트 엔진 분석
Mapper 4 (MMC3), PRG 128KB
"""
import struct

ROM_PATH = '/tmp/rom_hack/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes'

with open(ROM_PATH, 'rb') as f:
    data = f.read()

prg = data[16:16+131072]

# 6502 opcode table (간략)
OPCODES = {
    0x20: ('JSR', 3), 0x4C: ('JMP', 3), 0x60: ('RTS', 1),
    0xA0: ('LDY', 2), 0xA2: ('LDX', 2), 0xA9: ('LDA', 2),
    0xA5: ('LDA', 2, 'zp'), 0xAD: ('LDA', 3, 'abs'),
    0xB9: ('LDA', 3, 'abs,Y'), 0xBD: ('LDA', 3, 'abs,X'),
    0x85: ('STA', 2, 'zp'), 0x8D: ('STA', 3, 'abs'),
    0x99: ('STA', 3, 'abs,Y'), 0x9D: ('STA', 3, 'abs,X'),
    0x81: ('STA', 2, '(ind,X)'), 0x91: ('STA', 2, '(ind),Y'),
    0xE8: ('INX', 1), 0xC8: ('INY', 1), 0xCA: ('DEX', 1), 0x88: ('DEY', 1),
    0xF0: ('BEQ', 2), 0xD0: ('BNE', 2), 0x90: ('BCC', 2), 0xB0: ('BCS', 2),
    0x30: ('BMI', 2), 0x10: ('BPL', 2), 0x50: ('BVC', 2), 0x70: ('BVS', 2),
    0xC9: ('CMP', 2), 0xE0: ('CPX', 2), 0xC0: ('CPY', 2),
    0x18: ('CLC', 1), 0x38: ('SEC', 1), 0x58: ('CLI', 1), 0x78: ('SEI', 1),
    0xAA: ('TAX', 1), 0xA8: ('TAY', 1), 0x8A: ('TXA', 1), 0x98: ('TYA', 1),
    0xE0: ('CPX', 2), 0xC0: ('CPY', 2),
    0xEA: ('NOP', 1), 0x00: ('BRK', 1), 0x48: ('PHA', 1), 0x68: ('PLA', 1),
    0x08: ('PHP', 1), 0x28: ('PLP', 1),
    0x09: ('ORA', 2), 0x0D: ('ORA', 3, 'abs'),
    0x29: ('AND', 2), 0x2D: ('AND', 3, 'abs'),
    0x49: ('EOR', 2), 0x4D: ('EOR', 3, 'abs'),
    0x69: ('ADC', 2), 0x6D: ('ADC', 3, 'abs'),
    0xE9: ('SBC', 2), 0xED: ('SBC', 3, 'abs'),
    0x0A: ('ASL', 1), 0x4A: ('LSR', 1), 0x2A: ('ROL', 1), 0x6A: ('ROR', 1),
    0xE6: ('INC', 2, 'zp'), 0xC6: ('DEC', 2, 'zp'),
    0xEE: ('INC', 3, 'abs'), 0xCE: ('DEC', 3, 'abs'),
    0x86: ('STX', 2, 'zp'), 0x84: ('STY', 2, 'zp'),
    0x96: ('STX', 2, 'zp,Y'), 0xA6: ('LDX', 2, 'zp'), 0xA4: ('LDY', 2, 'zp'),
    0xB6: ('LDX', 2, 'zp,Y'), 0xB4: ('LDY', 2, 'zp,X'),
}

def disasm(bank_data, base_addr, limit=0x4000):
    """6502 디스어셈블"""
    lines = []
    i = 0
    while i < len(bank_data) and i < limit:
        if i >= len(bank_data):
            break
        op = bank_data[i]
        addr = base_addr + i
        
        if op in OPCODES:
            mnemonic, size = OPCODES[op][0], OPCODES[op][1]
            extra = OPCODES[op][2] if len(OPCODES[op]) > 2 else ''
            
            if size == 1:
                lines.append(f"{addr:04X}: {mnemonic}")
            elif size == 2 and i + 1 < len(bank_data):
                operand = bank_data[i+1]
                if extra and extra.startswith('zp'):
                    lines.append(f"{addr:04X}: {mnemonic} ${operand:02X}")
                elif mnemonic in ['BEQ','BNE','BCC','BCS','BMI','BPL','BVC','BVS']:
                    # relative branch
                    target = addr + 2 + (operand if operand < 128 else operand - 256)
                    lines.append(f"{addr:04X}: {mnemonic} ${target:04X}")
                else:
                    lines.append(f"{addr:04X}: {mnemonic} #${operand:02X}")
            elif size == 3 and i + 2 < len(bank_data):
                operand = bank_data[i+1] | (bank_data[i+2] << 8)
                if mnemonic in ['JSR', 'JMP']:
                    lines.append(f"{addr:04X}: {mnemonic} ${operand:04X}")
                elif mnemonic == 'LDA' and 'abs' in extra:
                    lines.append(f"{addr:04X}: LDA ${operand:04X}")
                elif mnemonic == 'STA' and 'abs' in extra:
                    lines.append(f"{addr:04X}: STA ${operand:04X}")
                elif mnemonic == 'LDA' and 'Y' in extra:
                    lines.append(f"{addr:04X}: LDA ${operand:04X},Y")
                else:
                    lines.append(f"{addr:04X}: {mnemonic} ${operand:04X}")
            i += size
        else:
            # 데이터 바이트
            lines.append(f"{addr:04X}: .byte ${op:02X}")
            i += 1
    return lines

print("=" * 70)
print("6502 디스어셈블리 - 텍스트 출력 루틴 찾기")
print("=" * 70)

# 중요한 뱅크 분석
# MMC3: 0xC000-0xFFFF = 고정 뱅크 (마지막 16KB)
# 텍스트 처리 루틴은 보통 여기에 있음

print("\n=== 고정 뱅크 (0xC000-0xFFFF) 디스어셈블 ===")
fixed = prg[7*16384:8*16384]
asm = disasm(fixed, 0xC000, 0x4000)

# 텍스트 관련 함수 서명 검색
# 패미컴 텍스트 출력 = PPU에 타일 쓰기
# LDA $2002 (PPUSTATUS), LDA $2006 (PPUADDR), STA $2007 (PPUDATA)
# JSR $XXXX 호출 패턴

text_calls = []
for line in asm:
    # JSR $XX 찾기 (서브루틴 호출)
    if 'JSR $' in line:
        addr = int(line.split('$')[1].split(':')[0], 16)
        text_calls.append(line)

print(f"\n=== 텍스트 관련 JSR 호출 (고정 뱅크) ===")
for c in text_calls:
    print(c)

# PPU 조작 명령어 검색
print(f"\n=== PPU 조작 루틴 ===")
for i, line in enumerate(asm):
    if '$2006' in line or '$2007' in line or '$2000' in line or '$2001' in line or '$2005' in line:
        # 주변 라인 출력
        start = max(0, i-3)
        end = min(len(asm), i+3)
        for j in range(start, end):
            marker = '>>>' if j == i else '   '
            print(f"{marker} {asm[j]}")
        print()
