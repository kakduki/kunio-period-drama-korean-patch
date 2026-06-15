# 쿠니오군의 시대극이다 전원집합! 한글패치 프로젝트

## 개요
다운타운 스페셜 くにおくんの時代劇だよ全員集合! (1991, 테크노스재팬)의 한글 패치 제작

## 장비
- 호스트: macOS 12.7 Monterey (분석/스크립트 제작)
- 디버거: Windows PC (FCEUX 디버거)
- AI: Codex CLI (Windows), Hermes Agent (macOS)

## 디렉토리 구조
```
kunio_korean_patch/
├── scripts/          # Python 분석 도구
│   ├── analyze_rom.py        # 기본 ROM 구조 분석
│   ├── analyze_chr.py        # CHR ROM 분석
│   ├── analyze_chr_font.py   # CHR 폰트 추출
│   ├── extract_text.py       # 텍스트 추출
│   ├── find_text.py          # 텍스트 영역 검색
│   └── disasm_6502.py        # 6502 디스어셈블러
├── text_data/
│   └── 쿠니오_시대극_게임_일본어_텍스트_전사.md  # 150개 항목 텍스트
├── font/             # CHR 폰트 이미지
├── rom_analysis/     # 분석 결과 (TODO)
└── output/           # 최종 패치 (TODO)
```

## ROM 정보
- 파일: Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes
- 크기: 262,160 bytes (NES 2.0)
- PRG: 131,072 bytes (8 x 16KB banks, Mapper 4 / MMC3)
- CHR: 131,072 bytes (16 x 8KB banks)
- MD5: 0d406a85285b4de8468f0dab6aad5fe5

## 텍스트 분석 현황
### 완료
- 게임 텍스트 150+ 항목 전사 (일본어 원문 + 한글 번역 준비)
- CHR 16개 뱅크 폰트 이미지 추출
- 6502 디스어셈블러 제작

### 필요한 분석 (Windows FCEUX 디버거 필요)
1. 텍스트 포인터 테이블 위치 확인
2. 게임 내부 문자 인코딩 테이블 (CHR 타일 번호 ↔ 문자 코드)
3. 텍스트 압축 알고리즘 파악
4. 각 텍스트 블록의 ROM 오프셋

## 작업 플로우
```
macOS (여기)                Windows (Codex)
    │                            │
    ├─ 스크립트/데이터 GitHub push ─→ pull + FCEUX 디버거
    │                            ├─ 텍스트 포인터 분석
    │                            ├─ CHR 폰트 매핑 확인
    │                            └─ 결과 push ─┐
    │                                            │
    ←────── GitHub pull ────────────────────────┘
    ├─ 번역 데이터 준비
    ├─ 8x16 한글 폰트 제작
    └─ IPS 패치 생성
```

## 윈도우 Codex CLI 사용법
```bash
# 1. 저장소 클론
git clone <repo-url> kunio_korean_patch
cd kunio_korean_patch

# 2. Python 스크립트 실행
python scripts/extract_text.py

# 3. FCEUX 디버거로 분석
# FCEUX 실행 → ROM 열기 → Debug > Trace Logger
# 게임 플레이 중 텍스트 나오는 순간 메모리 덤프
# 결과를 rom_analysis/ 에 저장
```

## 참고 링크
- YouTube 필살기 정리: https://www.youtube.com/watch?v=VID
- YouTube 풀플레이 (2h): https://www.youtube.com/watch?v=VID
- CHR 뱅크 이미지: font/*.png
