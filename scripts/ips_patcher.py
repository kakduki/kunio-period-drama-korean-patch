#!/usr/bin/env python3
"""
IPS (International Patching System) 패치 생성기
- 원본 ROM → 수정된 ROM의 차이를 .ips 파일로 생성
- CHR 폰트 교체 지원
- PRG 텍스트 패치 지원
"""
import os, struct, hashlib

class IPSPatcher:
    def __init__(self, rom_path):
        with open(rom_path, 'rb') as f:
            self.original = bytearray(f.read())
        self.patched = bytearray(self.original)
        self.records = []  # (offset, data)
    
    def patch_bytes(self, offset, data):
        """특정 ROM 오프셋에 바이트 패치"""
        if offset < 0 or offset + len(data) > len(self.patched):
            raise ValueError(f"Invalid patch offset 0x{offset:06X}")
        
        old_data = bytes(self.patched[offset:offset+len(data)])
        if old_data == data:
            return  # 이미 같음
        
        self.patched[offset:offset+len(data)] = data
        self.records.append((offset, data))
    
    def patch_chr_font(self, bank, font_data, char_map):
        """CHR ROM 뱅크에 한글 폰트 교체"""
        chr_start = 16 + 131072  # 헤더(16) + PRG(131072)
        bank_offset = chr_start + bank * 8192
        
        for char_idx, char_bytes in font_data.items():
            offset = bank_offset + char_idx * 32
            if offset + 32 > len(self.patched):
                continue
            self.patch_bytes(offset, char_bytes)
    
    def generate_ips(self, output_path):
        """IPS 파일 생성"""
        if not self.records:
            print("변경 사항 없음")
            return
        
        with open(output_path, 'wb') as f:
            f.write(b'PATCH')
            
            for offset, data in self.records:
                # RLE 압축 여부 확인 (같은 바이트 3회 이상 반복)
                if len(data) >= 3 and len(set(data)) == 1:
                    # RLE 인코딩
                    remaining = len(data)
                    pos = 0
                    while remaining > 0:
                        chunk = min(remaining, 0xFFFF)  # 최대 64KB
                        f.write(struct.pack('>I', offset + pos)[1:])  # 3바이트 오프셋
                        f.write(struct.pack('>H', chunk))  # 길이
                        f.write(bytes([data[0]]))  # RLE 바이트
                        pos += chunk
                        remaining -= chunk
                else:
                    # 일반 기록
                    remaining = len(data)
                    pos = 0
                    while remaining > 0:
                        chunk = min(remaining, 0xFFFF)
                        f.write(struct.pack('>I', offset + pos)[1:])  # 3바이트 오프셋
                        f.write(struct.pack('>H', chunk))  # 길이
                        f.write(bytes(data[pos:pos+chunk]))
                        pos += chunk
                        remaining -= chunk
            
            f.write(b'EOF')
        
        # ROM 체크섬
        original_hash = hashlib.md5(self.original).hexdigest()
        patched_hash = hashlib.md5(self.patched).hexdigest()
        
        print(f"IPS 패치 생성: {output_path}")
        print(f"  패치 레코드: {len(self.records)}개")
        print(f"  원본 MD5: {original_hash}")
        print(f"  패치 MD5: {patched_hash}")
        
        # 수정된 ROM도 저장
        rom_name = os.path.splitext(os.path.basename(output_path))[0]
        rom_out = os.path.join(os.path.dirname(output_path), f'{rom_name}.nes')
        with open(rom_out, 'wb') as f:
            f.write(self.patched)
        print(f"  패치 ROM: {rom_out}")
    
    def apply_ips(self, ips_path, output_rom_path):
        """IPS 파일을 원본 ROM에 적용"""
        result = bytearray(self.original)
        
        with open(ips_path, 'rb') as f:
            data = f.read()
        
        if data[:5] != b'PATCH':
            raise ValueError("Invalid IPS file")
        
        if data[-3:] != b'EOF':
            raise ValueError("Invalid IPS file (no EOF marker)")
        
        pos = 5
        record_count = 0
        while pos < len(data) - 3:
            if data[pos:pos+3] == b'EOF':
                break
            
            offset = (data[pos] << 16) | (data[pos+1] << 8) | data[pos+2]
            pos += 3
            
            length = (data[pos] << 8) | data[pos+1]
            pos += 2
            
            if length == 0:
                # RLE
                rle_size = (data[pos] << 8) | data[pos+1]
                pos += 2
                rle_byte = data[pos]
                pos += 1
                
                for i in range(rle_size):
                    if offset + i < len(result):
                        result[offset + i] = rle_byte
            else:
                for i in range(length):
                    if offset + i < len(result):
                        result[offset + i] = data[pos + i]
                pos += length
            
            record_count += 1
        
        with open(output_rom_path, 'wb') as f:
            f.write(result)
        
        print(f"IPS 적용 완료: {record_count}개 레코드")
        print(f"  출력: {output_rom_path}")
        return output_rom_path


if __name__ == '__main__':
    import sys
    
    ROM_PATH = '/tmp/rom_hack/Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes'
    OUT_DIR = '/tmp/kunio_korean_patch/output'
    os.makedirs(OUT_DIR, exist_ok=True)
    
    # 사용법
    print("=" * 60)
    print("NES 한글패치 IPS 생성기")
    print("=" * 60)
    print(f"\n원본 ROM: {ROM_PATH}")
    print(f"\n사용법:")
    print(f"  python {sys.argv[0]}")  # 현재 모드: 분석 모드
    print(f"\n윈도우 Codex가 분석 결과를 rom_analysis/ 에 넣으면:")
    print(f"  1. translations/translation_data.txt 로 번역 적용")
    print(f"  2. font/korean_font_8x16.bin 으로 CHR 폰트 교체")
    print(f"  3. output/kunio_korean_v1.ips 생성")
    
    # 테스트: 원본 ROM 로드
    patcher = IPSPatcher(ROM_PATH)
    print(f"\n원본 ROM 크기: {len(patcher.original)} bytes")
    print(f"IPS 생성기 준비 완료")
