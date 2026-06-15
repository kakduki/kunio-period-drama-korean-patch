#!/usr/bin/env python3
"""
8x16 NES 한글 폰트 생성기
게임 텍스트 전사 파일에서 필요한 한글 음절 추출 → 8x16 도트 폰트 제작
"""
import os, json, struct
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = '/tmp/kunio_korean_patch/font'
os.makedirs(OUT_DIR, exist_ok=True)

# 텍스트 전사 파일 읽기
text_path = os.path.expanduser('~/kunio_korean_patch/text_data/쿠니오_시대극_게임_일본어_텍스트_전사.md')
# 실제 파일 위치
text_path = '/Users/jeongbeomjun/쿠니오_시대극_게임_일본어_텍스트_전사.md'

# 대략적인 번역으로 필요한 한글 음절 추정
korean_texts = {
    # 메뉴/UI
    "게임 시작": "게임시작",
    "비밀번호": "비밀번호",
    "비밀번호 입력": "비밀번호입력",
    "모험": "모험",
    "대결": "대결",
    
    # 스테이터스
    "레벨": "레벨",
    "경험치": "경험치",
    "돈": "돈",
    "소지품": "소지품",
    "장비": "장비",
    "먹다": "먹다",
    "버리다": "버리다",
    "힘": "힘",
    "속도": "속도",
    "방어": "방어",
    "체력": "체력",
    "생명": "생명",
    
    # 이벤트 대사
    "승리": "승리",
    "패배": "패배",
    "도와줘": "도와줘",
    "기다려": "기다려",
    "이걸 가져가": "이걸가져가",
    "동료가 되었다": "동료가되었다",
    "레벨업": "레벨업",
    "기술을 익혔다": "기술을익혔다",
    "몸에 익혔다": "몸에익혔다",
    
    # 아이템
    "몽둥이": "몽둥이",
    "구리": "구리",
    "쇠": "쇠",
    "강철": "강철",
    "검": "검",
    "창": "창",
    "갑옷": "갑옷",
    "방패": "방패",
    "약": "약",
    "좋은": "좋은",
    "굉장한": "굉장한",
    "기의": "기의",
    "해독약": "해독약",
    "군고구마": "군고구마",
    "주먹밥": "주먹밥",
    "투시의 옷": "투시의옷",
    "달인의 안경": "달인의안경",
    "효과": "효과",
    "배": "배",
    "회피의 옷": "회피의옷",
    "봉인의 부적": "봉인의부적",
    "황금 구슬": "황금구슬",
    "은 구슬": "은구슬",
    "빨간 구슬": "빨간구슬",
    "파란 구슬": "파란구슬",
    "전설의 도구": "전설의도구",
    "수수께끼 가게": "수수께끼가게",
    "제비뽑기": "제비뽑기",
    "보물 지도": "보물지도",
    
    # 기술
    "마하 펀치": "마하펀치",
    "마하 킥": "마하킥",
    "마하 때리기": "마하때리기",
    "마하 스윙": "마하스윙",
    "스크류": "스크류",
    "니트로 어택": "니트로어택",
    "하이퍼 가드": "하이퍼가드",
    "선풍각": "선풍각",
    "워프 슛": "워프슛",
    "인간 드릴": "인간드릴",
    "인간 헬기": "인간헬기",
    "인간 어뢰": "인간어뢰",
    "자신 어뢰": "자신어뢰",
    "빅뱅": "빅뱅",
    "변신": "변신",
    "스페셜": "스페셜",
    "때리기": "때리기",
    "박치기": "박치기",
    "안마": "안마",
    
    # 보스/캐릭터
    "은팔치": "은팔치",
    "일베에": "일베에",
    "금스케": "금스케",
    "타메키치": "타메키치",
    "곤사쿠": "곤사쿠",
    "헤이시치": "헤이시치",
    "진로쿠": "진로쿠",
    "한시로": "한시로",
    "야고로": "야고로",
    "니자에몬": "니자에몬",
    "타츠이치": "타츠이치",
    "타츠지": "타츠지",
    "토라조": "토라조",
    "두목": "두목",
    "흑막": "흑막",
    "쥬키치": "쥬키치",
    "아사지로": "아사지로",
    "츠루마츠": "츠루마츠",
    "산키치": "산키치",
    "리키고로": "리키고로",
    "요노스케": "요노스케",
    "분조": "분조",
    
    # 스테이지
    "시작": "시작",
    "마을": "마을",
    "산길": "산길",
    "숲": "숲",
    "강가": "강가",
    "동굴": "동굴",
    "산 위": "산위",
    "다리": "다리",
    "지옥": "지옥",
    "누정": "누정",
    "성": "성",
    "밭": "밭",
    "등산": "등산",
    "대장간": "대장간",
    "묘지": "묘지",
    "호수": "호수",
    
    # 엔딩
    "끝": "끝",
    "엔딩": "엔딩",
    "스태프": "스태프",
    "축하합니다": "축하합니다",
    "클리어": "클리어",
    
    # 기타
    "황금벌레": "황금벌레",
    "최강": "최강",
    "이름": "이름",
    "숨겨진": "숨겨진",
    "기술": "기술",
    "공략": "공략",
    "대부자": "대부자",
    "위력": "위력",
}

# 모든 한글 음절 수집
all_chars = set()
for text in korean_texts.values():
    for ch in text:
        if '\uAC00' <= ch <= '\uD7A3':  # 한글 음절
            all_chars.add(ch)
        elif ch.isalnum() or ch in '!?.,-~ ':  # 숫자/기호
            all_chars.add(ch)

# ASCII + 숫자 + 기호 추가
for ch in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!?.,-~/():;':
    all_chars.add(ch)

print(f"필요한 한글 음절 + 기호: {len(all_chars)}개")

# 시스템 폰트로 8x16 도트 렌더링
# macOS: /System/Library/Fonts/AppleSDGothicNeo.ttc
# Linux: /usr/share/fonts/truetype/nanum/NanumGothic.ttf

font_paths = [
    '/System/Library/Fonts/AppleSDGothicNeo.ttc',
    '/System/Library/Fonts/Supplemental/AppleGothic.ttf',
    '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
    '/usr/share/fonts/truetype/d2coding/D2Coding.ttf',
]

font = None
for fp in font_paths:
    if os.path.exists(fp):
        try:
            font = ImageFont.truetype(fp, 14)  # 8x16에 맞게 14pt
            print(f"폰트 로드: {fp}")
            break
        except:
            continue

if not font:
    print("시스템 폰트 없음. 기본 폰트 사용")
    font = ImageFont.load_default()

# 8x16 도트 폰트 생성
# NES 포맷: 1비트/픽셀, 8x16 = 16바이트
# 0=투명, 1=검정

font_data = {}
img_preview = Image.new('RGB', (8*32, 16*16), (255, 255, 255))
px = img_preview.load()

sorted_chars = sorted(all_chars)
for idx, ch in enumerate(sorted_chars):
    if idx >= 512:  # 최대 512자
        break
    
    # 각 글자를 14pt로 렌더링
    char_img = Image.new('1', (8, 16), 0)  # 1비트, 흰색 배경
    draw = ImageDraw.Draw(char_img)
    
    # 폰트로 그리기 (중앙 정렬)
    bbox = draw.textbbox((0, 0), ch, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (8 - tw) // 2 - bbox[0]
    y = (16 - th) // 2 - bbox[1]
    draw.text((x, y), ch, font=font, fill=255)
    
    # NES CHR 포맷으로 변환: 1비트/픽셀
    bytes_16 = bytearray(32)  # 2bpp NES = 32bytes/8x16타일
    
    for row in range(16):
        byte_p0 = 0
        byte_p1 = 0
        for col in range(8):
            pixel = char_img.getpixel((col, row))
            if pixel > 128:
                byte_p0 |= (1 << (7 - col))
        bytes_16[row] = byte_p0
        # 2bpp: plane 1은 0 (흑백)
        bytes_16[row + 16] = byte_p1
    
    font_data[ch] = bytes_16
    
    # 미리보기 이미지
    cx = (idx % 32) * 8
    cy = (idx // 32) * 16
    for row in range(16):
        b = bytes_16[row]
        for col in range(8):
            if b & (1 << (7 - col)):
                px[cx + col, cy + row] = (0, 0, 0)
            else:
                px[cx + col, cy + row] = (255, 255, 255)

# 미리보기 저장
img_preview.save(f'{OUT_DIR}/korean_8x16_preview.png')
print(f"폰트 미리보기: {OUT_DIR}/korean_8x16_preview.png")

# CHR ROM 교체용 데이터 저장
with open(f'{OUT_DIR}/korean_font_8x16.bin', 'wb') as f:
    for ch in sorted_chars:
        if ch in font_data:
            f.write(font_data[ch])

# 문자→인덱스 매핑 저장
mapping = {ch: i for i, ch in enumerate(sorted_chars)}
with open(f'{OUT_DIR}/char_map.json', 'w', encoding='utf-8') as f:
    json.dump({'sorted': sorted_chars, 'count': len(sorted_chars)}, f, ensure_ascii=False, indent=2)

print(f"\n폰트 생성 완료!")
print(f"  전체 글자: {len(sorted_chars)}개")
print(f"  바이너리 크기: {len(sorted_chars) * 32} bytes")
print(f"  CHR 뱅크 사용량: {len(sorted_chars) / 256:.1f} 뱅크")
