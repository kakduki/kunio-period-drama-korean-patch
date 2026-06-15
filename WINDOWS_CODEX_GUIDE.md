# 윈도우 Codex CLI 실행 가이드

## 필요한 것
1. Windows PC
2. Python 3.x 설치
3. FCEUX 설치 (http://www.fceux.com/)
4. Codex CLI
5. 롬 파일 (직접 준비)

## 분석 순서

### 1단계: 텍스트 추출 스크립트 실행
```bash
cd kunio_korean_patch
# 롬 파일을 rom/ 폴더에 넣고
python scripts/extract_text.py
```

### 2단계: FCEUX 디버거로 텍스트 포인터 확인
1. FCEUX 실행 → File > Open → 롬 파일 열기
2. Debug > Trace Logger
3. Log to File: trace.log (체크)
4. 게임 실행 → 대화/메뉴 화면까지 진행
5. Debug > Name Table Viewer / PPU Viewer 열기
6. 텍스트가 화면에 표시될 때 PPU 메모리 덤프
7. Debug > Hex Editor → 0x6000-0x7FFF 영역 확인 (CHR ROM 매핑)

### 3단계: 결과 저장
분석 결과를 rom_analysis/ 폴더에 저장
```bash
# trace.log와 메모리 덤프를 rom_analysis/로 복사
cp trace.log rom_analysis/
# PPU/메모리 덤프 결과 작성
```

### 4단계: GitHub에 push
```bash
git add rom_analysis/
git commit -m "Windows FCEUX 분석 결과"
git push
```

## 스크립트 설명
- `scripts/extract_text.py` - PRG ROM에서 텍스트 영역 검색
- `scripts/disasm_6502.py` - 6502 CPU 코드 디스어셈블
- `scripts/analyze_chr_font.py` - CHR 폰트 시각화
- `scripts/find_text.py` - 텍스트 블록 위치 찾기
