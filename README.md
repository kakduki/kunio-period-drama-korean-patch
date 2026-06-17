# 쿠니오 시대극 한국어 패치 프로젝트

`Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes`의 일본어 텍스트를 한국어로 바꾸기 위한 분석/패치 저장소입니다.

이 저장소에는 ROM 파일을 포함하지 않습니다. 각자 보유한 정품 기반 일본판 ROM을 `rom/` 폴더에 넣고 분석/패치 스크립트를 실행합니다.

## 현재 상태

- 기준 ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- 현재 1차 테스트 후보: `v0.4.2 font-expanded`
- 테스트 IPS: `output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.ips`
- 테스트 번들: `release/kunio_period_drama_korean_v0_4_2_font-expanded_test.zip`
- 패치 적용 후 예상 MD5: `ea11dc002a1a7b07682ce00a754b1a61`

아직 최종 패치가 아닙니다. 현재 후보는 안전한 equal-length PRG 텍스트 일부와 CHR 글리프만 적용한 수동 검증용 빌드입니다.

## 빠른 검증

```powershell
python scripts/verify_primary_patch.py
python scripts/run_project_checks.py
```

현재 테스트 IPS를 내 ROM에 적용하려면:

```powershell
python scripts/apply_primary_patch.py --output output/kunio_period_drama_korean_v0.4.2_test_applied.nes
```

생성물을 다시 만들면서 확인하려면:

```powershell
python scripts/run_project_checks.py --regen
```

## 중요한 작업 원칙

- FCEUX 자동 진행이 `stagnant_screen`을 기록하거나 첫 화면/초기 메뉴만 반복하면 즉시 중단합니다.
- `scripts/run_fceux_lua_analysis.py`는 타깃 없는 기본 autoplay를 자동으로 짧게 제한합니다. 길게 돌릴 때는 `--target-lua`로 감시 대상을 주거나 `--allow-long-autoplay`를 명시합니다.
- 유튜브 영상은 대사 흐름과 전사 참고용입니다. 실제 패치 승격은 ROM 오프셋, 바이트 매핑, 런타임 메모리, 화면 증거가 필요합니다.
- `needs-padding-rule` 항목은 화면에서 패딩/종료 규칙이 확인되기 전까지 최종 후보에 넣지 않습니다.
- v0.4/broad-scan 충돌 항목은 수동 화면 증거가 나오기 전까지 어느 쪽도 확정하지 않습니다.

## 다음에 볼 파일

- `rom_analysis/patch_decision_matrix.md`: 다음 수동 검증 우선순위
- `rom_analysis/manual_capture_cards.md`: FCEUX 앞에서 바로 따라 할 짧은 캡처 카드
- `rom_analysis/manual_capture_status.md`: 수동 덤프가 생긴 뒤 카드별 증거 상태표
- `rom_analysis/translation_glyph_coverage.md`: 전체 번역 데이터 기준 글리프 커버리지
- `rom_analysis/next_glyph_expansion_plan.md`: 다음 한글 글리프 확장 우선순위
- `rom_analysis/v042_text_promotion_readiness.md`: v0.4.2 폰트 기준 다음 텍스트 후보 준비도
- `rom_analysis/v042_manual_proof_packet.md`: 첫 화면 루프 대신 확인할 7개 base-ROM 수동 검증 과제
- `rom_analysis/primary_patch_contents.md`: 현재 primary IPS가 바꾸는 텍스트 10개, 바이트, 증거 상태
- `rom_analysis/kunio_period_drama_korean_font_expansion_v0.5_batch32_report.md`: 로컬 v0.5 글리프 확장 실험 빌드 리포트
- `rom_analysis/patch_candidate_manifest.md`: 현재 ROM/IPS 후보 목록
- `rom_analysis/manual_capture_workflow.md`: FCEUX 수동 캡처 절차
- `rom_analysis/v04_broad_candidate_conflicts.md`: v0.4와 broad-scan 충돌 목록
- `rom_analysis/prg_padding_options.md`: 짧아지는 번역의 패딩 위험 목록

## 수동 FCEUX 검증 흐름

현재 테스트 후보를 확인할 때:

```text
output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes
```

1. FCEUX에서 위 ROM을 엽니다.
2. `rom_analysis/patch_decision_matrix.md`의 상위 항목에 해당하는 화면까지 직접 진행합니다.
3. 해당 화면에서 일시정지합니다.
4. FCEUX Lua 메뉴에서 `lua/kunio_manual_v042_screen_dump.lua`를 실행합니다.
5. 덤프를 요약합니다.

```powershell
python scripts/analyze_manual_screen_dump.py --input-dir rom_analysis/manual_screen_dump_v042 --output rom_analysis/manual_screen_dump_v042/summary.md
```

broad-scan 후보를 확인할 때는 base ROM에서 화면을 열고 `lua/kunio_manual_broad_scan_dump.lua`를 사용합니다.
요약 결과는 `rom_analysis/manual_screen_dump_broad_scan/summary.md`와 `summary.json`에 저장됩니다.
화면 맥락까지 맞는 후보는 `rom_analysis/manual_screen_dump_broad_scan/visual_review.json`에서 `visual_context_confirmed`를 `true`로 바꾼 뒤 `python scripts/build_v043_from_broad_scan_proof.py`로 v0.4.3 후보를 만들 수 있습니다.

## 현재 최우선 확인 항목

`rom_analysis/patch_decision_matrix.md` 기준:

1. `0x06295`, `0x0631C`, `0x0635A`: v0.4와 broad-scan 해석이 충돌하는 항목
2. `0x05644`: 이미 적용된 근처 항목과 겹치는 local overlap
3. `0x071A4`: 런타임 확인은 됐지만 짧아지는 번역이라 패딩 규칙 검증 필요
4. `0x0440C`, `0x048F4`, `0x052A5`, `0x05BE5`: broad-scan 비충돌 후보

## 주요 스크립트

- `scripts/verify_primary_patch.py`: 현재 primary IPS가 기준 ROM에 정상 적용되는지 확인
- `scripts/apply_primary_patch.py`: 현재 primary IPS를 개인 보유 ROM에 적용
- `scripts/build_v043_from_broad_scan_proof.py`: CPU read와 화면 맥락이 둘 다 확인된 broad-scan 후보만 v0.4.3으로 승격
- `scripts/run_project_checks.py`: Python, Lua, IPS, manifest 핵심 체크
- `scripts/generate_patch_decision_matrix.py`: 다음 수동 검증 결정표 생성
- `scripts/package_primary_release.py`: ROM 없는 테스트 IPS 번들 생성
- `scripts/run_fceux_lua_analysis.py`: FCEUX Lua 자동 분석 실행기
- `scripts/analyze_manual_screen_dump.py`: 수동 화면 덤프 요약

## 저장소 구조

```text
font/          한국어 글리프와 CHR 관련 자료
lua/           FCEUX Lua 자동화 및 수동 덤프 스크립트
output/        로컬 테스트 ROM/IPS 산출물
release/       ROM 없는 테스트 배포 번들
rom/           개인 보유 ROM 위치, git 제외
rom_analysis/  분석 결과와 검증 큐
scripts/       Python 분석/빌드/검증 도구
text_data/     전사/번역 참고 자료
```
