# 쿠니오 시대극 한국어 패치 프로젝트

Kunio Kun no Jidaigeki Dayo Zenin Shuugou! 일본판을 대상으로 하는 한국어 패치
분석/빌드 저장소다. ROM 파일과 제3자 영어 IPS는 저장소에 넣지 않는다.

## 현재 기준

전체 작업 순서는 KOREAN_PATCH_RESTART_PLAN.md와
KOREAN_PATCH_ARCHITECTURE.md가 기준이다.

- 영어 패치의 문장이나 바이너리를 복사하지 않고, 포인터/글꼴/재배치 구조만
  참고한다.
- 일반 autoplay로 게임을 진행하며 화면을 찾지 않는다.
- 한글 16x16 오프닝 한 레코드는 기술 증명으로 통과했지만, 최종 패치나
  대량 번역본은 아니다.
- Bank 8 동적 CHR 페이지 전환은 두 가지 제한 후보에서 실패했으므로, 고정 PRG
  코드 공간을 별도로 증명하기 전에는 번역 후보에 사용하지 않는다.
- 기존 v0.4.x ROM/IPS 후보는 과거 실험 자료다. 현재 릴리스 기준이 아니다.

## 영어 패치에서 얻은 확정 구조

- 주요 대사 포인터 테이블: ROM 0x05DD4-0x05FC3, 248개 엔트리
- 주요 대사 데이터: PRG Bank 1
- 확인된 영어 대사 코드: 0x81-0x9A
- 확인된 대사 글꼴 위치: 물리 CHR Bank 7의 0x181-0x19A
- 긴 영어 대사는 포인터를 재지정하여 다른 Bank 1 레코드 공간으로 이동

세부 구현 지도는 rom_analysis/english_patch_implementation_map.md를, 원시
분석 근거는 rom_analysis/english_patch_reference.md와
rom_analysis/english_script_reference.md를 본다.

## 현재 기술 증명

오프닝 pointer 182에서 다음 문구를 16x16 한글로 표시했다.

    쿠니마사: 어서 움직여!
    분조 두목이 큰일이야!

이 후보는 47/47 대상 읽기 일치, frame 883 캡처, lua_done을 기록했다. 다만
18개 글자와 로컬 콜론 타일을 쓰는 한 장면 증명일 뿐이다. 전체 글꼴 용량,
다음 레코드, 메뉴/상태/아이템/이벤트 렌더러는 아직 별도 과제다.

근거:

- rom_analysis/opening_dialogue_16x16_speaker_separator_proof.md
- rom_analysis/opening_dialogue_16x16_speaker_separator_proof_capture/analysis.md
- rom_analysis/dialogue_glyph_capacity_plan.md
- rom_analysis/font_readability_gate.md

## 다음 작업

1. 영어 포인터 구조와 일본판 원문 토큰을 기반으로 대사 카탈로그를 완성한다.
2. 검증된 고정 Bank 7 글꼴 팔레트로 표현 가능한 오프닝 대사 1-2개를
   파일럿으로 빌드한다.
3. 대상 레코드/화면만 확인하는 짧은 FCEUX 증명으로 PASS, FAIL, UNKNOWN을
   기록한다.
4. 동적 CHR 페이지는 마지막 고정 PRG 뱅크의 안전한 코드 공간 또는 코드
   재배치를 먼저 증명한 뒤에만 재검토한다.
5. 오프닝, 메뉴, 상태/아이템, 이벤트를 서로 다른 렌더러 가족으로 검증한다.

## 빠른 검사

개발 환경에서 전체 정적 검사를 실행한다.

    python scripts/run_project_checks.py

영어 IPS가 로컬에 있을 때만 구조 자료를 다시 생성한다. 이 명령은 IPS를
메모리에서 읽을 뿐, 영어 ROM이나 IPS를 저장소에 복사하지 않는다.

    python scripts/extract_english_reference_script.py --reference-ips C:/path/to/TSe-v10.ips

FCEUX 실행 규칙과 전용 검증 명령은 FCEUX_LUA_AUTOMATION.md를 따른다.

## 레거시 증거 대시보드

이전 v0.4.x 실험의 current patch status, next FCEUX manual capture target, open release gates는 아래 문서에 남아 있다. 이들은 과거 후보의 검증 큐를 보존하는
참고 자료이며, 새 한국어 패치 작업 순서를 대신하지 않는다.

- rom_analysis/patch_progress_dashboard.md
- rom_analysis/candidate_pipeline/release_gate_action_plan.md

## 폴더

    font/          한글 글꼴 소스와 CHR 관련 자료
    lua/           대상별 FCEUX Lua 스크립트
    output/        로컬 생성 ROM/IPS, Git 제외
    rom/           개인 보유 기준 ROM, Git 제외
    rom_analysis/  분석 결과, 증거, 구현 지도
    scripts/       분석/빌드/검증 도구
    text_data/     원문 토큰, 전사, 한국어 번역 입력

## Current Development Candidate

The current bounded candidate combines the three verified opening records with
the Korean main-menu labels. ROM and IPS files stay local and are ignored by Git.

    python scripts/build_korean_development_candidate.py
    python scripts/analyze_korean_development_candidate.py
    python scripts/run_project_checks.py

Runtime evidence is recorded in
`rom_analysis/korean_development_candidate_runtime.md`. This is a development
soft-gate candidate, not a final release: Items text, later dialogue, combat
progression, and release-wide CHR sharing still require separate proof.

The from-zero work order is documented in `KOREAN_PATCH_FROM_ZERO_PLAN.md`.
The complete English-guided Bank 1 pointer worklist is generated into
`rom_analysis/pointer_dialogue_catalog.tsv` (248 rows). English text in that
catalog is structural reference only; Korean translation still requires
Japanese context, renderer ownership, and bounded screen evidence.

The first non-opening pointer batch is built by
`scripts/build_pointer_dialogue_batch_candidate.py`. It covers pointer 2 and
pointer 3, relocates pointer 3 from `$A012` to `$A011`, and keeps its runtime
gate `UNKNOWN` until an early-boss state can be entered without blind autoplay.

## Manual Real-Time Translation

The repository also includes a manual-play overlay for practical use while the
native patch is still under development. It does not autoplay or loop the
opening screen:

```powershell
python scripts/run_realtime_overlay.py --rom "rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes"
```

Known verified records are shown from `translation/realtime_overlay.csv`.
Unknown records can be sent to an optional translator command, but are logged
as `AI_UNCHECKED` and are never inserted into a ROM automatically.

## Reproducible Pipeline

The confirmed base is the Japanese NES/Famicom iNES image with mapper 4 (MMC3), 262,160 bytes, no trainer, and vertical mirroring.

- CRC32: `014D63C9`
- MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- SHA-1: `4338c3001c5e2bf5fad0f282bfee23b79e0ad959`
- SHA-256: `54d79f15f60a32123e95fbf20661128a13ee0eee1941e0ff98ba7bb54343e23a`

The local English reference is the `TSe-v10.ips` IPS. Its creator/license terms are not established by the local file metadata, so it is used only as a structural reference; its translation text, patched ROM, code, and graphics are not redistributed.

Build a candidate and an independently generated IPS from the exact base:

```powershell
python build.py --input "rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" --output "$env:TEMP\kunio-test.nes" --patch-output "$env:TEMP\kunio-development.ips" --report "$env:TEMP\kunio-build.json" --force
```

Read the requirement-specific status in `docs/project-status.md`, `docs/test-guide.md`, and `tests/known-issues.md`. Development status remains `NOT_READY` until the full dialogue, natural event/boss route, and release visual gates are proven.