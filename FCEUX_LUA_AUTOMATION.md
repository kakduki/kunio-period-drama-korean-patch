# FCEUX Lua 실행 정책

이 저장소에서 FCEUX는 게임을 자동으로 끝까지 진행시키는 도구가 아니다. 이미
정적으로 확인한 레코드, 화면, 또는 메모리 상태를 짧게 검증하는 도구다.

## 기본 규칙

1. Lua 스크립트를 명시하지 않은 실행은 거부된다.
2. legacy autoplay 스크립트는 기본적으로 거부된다.
3. legacy autoplay를 진단 목적으로 명시 허용해도 900프레임과 45초를 넘지
   못한다.
4. 모든 실제 검증 실행에는 대상 레코드 또는 캡처 조건, 최대 프레임, 최대
   시간, 종료 신호가 있어야 한다.
5. 첫 화면이나 메뉴가 반복되면 프레임을 늘리지 않는다. 그 실행은
   UNKNOWN 또는 stagnant_screen 증거로 끝낸다.

--allow-long-autoplay 옵션은 폐기되었다. 긴 게임 진행이 필요해 보일 때는
저장 상태, 디버그 상태, 또는 제한된 상태 주입을 먼저 설계한다.

## 전용 대사 검증 예시

오프닝 포인터 182의 화자 구분 후보는 아래처럼 전용 Lua와 대상 테이블을
명시해서만 실행한다.

    python scripts/run_fceux_lua_analysis.py --rom output/opening_dialogue_16x16_speaker_separator_proof/kunio_period_drama_korean_opening_dialogue_16x16_speaker_separator_proof.nes --lua-script lua/kunio_opening_dialogue_proof.lua --target-lua lua/kunio_opening_dialogue_16x16_speaker_separator_proof_target.lua --frames 920 --timeout 90 --hit-limit 5000 --final-output rom_analysis/opening_dialogue_16x16_speaker_separator_proof_capture --clean-output

이 실행은 알려진 입력 순서로 frame 883의 대사 화면만 캡처하고, 대상 바이트가
확인되면 lua_done을 기록한 뒤 FCEUX를 종료한다. 게임 플레이를 계속하지
않는다.

## Legacy 진단 실행

기존 autoplay Lua는 회귀 진단에만 남아 있다. 필요할 때도 명시적으로 다음
옵션을 써야 하며, 실행기는 하드 한도를 적용한다.

    python scripts/run_fceux_lua_analysis.py --lua-script lua/kunio_auto_dump.lua --allow-blind-autoplay

이 경로는 대사 발견이나 패치 승격의 근거가 아니다. 첫 화면 반복이 감지되면
즉시 종료하고, 다음에는 정적 대본/포인터 분석 또는 대상 화면용 전용 Lua를
사용한다.

## 결과 판정

| 결과 | 의미 |
| --- | --- |
| PASS | 대상 바이트, ROM 범위, 부팅, 네이티브 화면 문맥이 모두 맞다. |
| FAIL | 포인터, 제어 토큰, 글꼴, 부팅, 또는 화면 문맥의 오류가 확인됐다. |
| UNKNOWN | 정적 검사는 통과했으나 대상 화면 증거가 없다. |

Lua 출력의 lua_done, hit_limit, stagnant_screen은 실행 종료 이유다. 그 자체가
한국어 패치 PASS 판정은 아니다.

## 출력 파일

전용 Lua의 출력은 지정한 rom_analysis 하위 폴더에 복사된다.

- summary.tsv: 프레임과 종료 이유
- target_records.tsv 또는 opening_target_record.tsv: 대상 바이트 읽기
- analysis.json 및 analysis.md: 정적/런타임 판정
- PNG: 필요한 경우에만 남기는 네이티브 화면 증거

원시 BIN과 GD 덤프, 생성 ROM과 IPS는 Git에서 제외한다.
