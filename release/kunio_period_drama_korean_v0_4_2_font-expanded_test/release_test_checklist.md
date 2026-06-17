# Release Test Checklist

Use this as the short path through the current manual-test bundle.

## 1. Apply The Primary IPS

- Required base ROM MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Primary IPS: `output\kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.ips`
- Expected patched MD5: `ea11dc002a1a7b07682ce00a754b1a61`

Repository command:

```powershell
python scripts/apply_primary_patch.py --output output/kunio_period_drama_korean_v0.4.2_test_applied.nes
python scripts/verify_primary_patch.py
```

Bundle-only command:

```powershell
python apply_ips_standalone.py C:\path\to\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes
```

## 2. Manual Screens To Check First

Do not keep blind autoplay running on the title/first screen. Use these targets as concrete manual destinations.

| # | ROM | expected text | Korean | CPU guess | proof status | screen hint |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `0x06294` | へいしち | 헤이시치 | `$A284` | `needs_manual_capture` | look for a visible Heishichi name/dialogue context |
| 2 | `0x0631B` | へいしち | 헤이시치 | `$A30B` | `needs_manual_capture` | look for a visible Heishichi name/dialogue context |
| 3 | `0x06359` | へいしち | 헤이시치 | `$A349` | `needs_manual_capture` | look for a visible Heishichi name/dialogue context |
| 4 | `0x048F4` | たつじ | 타츠지 | `$88E4` | `needs_manual_capture` | look for a visible Tatsuji boss/name context |
| 5 | `0x052A5` | たつじ | 타츠지 | `$9295` | `needs_manual_capture` | look for a visible Tatsuji boss/name context |
| 6 | `0x05BE5` | たつじ | 타츠지 | `$9BD5` | `needs_manual_capture` | look for a visible Tatsuji boss/name context |
| 7 | `0x0440C` | かじや | 대장간 | `$83FC` | `needs_manual_capture` | look for a blacksmith/shop or blacksmith-stage label |

## 3. Capture Evidence

For broad v0.4.3 candidates, open the base Japanese ROM, manually reach the target screen, then run:

```text
lua/kunio_manual_broad_scan_dump.lua
```

Then summarize and refresh the status reports:

```powershell
python scripts/analyze_broad_scan_manual_dump.py
python scripts/generate_v043_proof_status.py
python scripts/generate_manual_dump_inventory.py
```

## 4. Record Visual Review

Only after the visible screen matches the intended row:

```powershell
python scripts/record_visual_review.py 0x0440C --confirm --screen-context "blacksmith label visible"
python scripts/build_v043_from_broad_scan_proof.py
```

## Rule

- YouTube/transcription order helps choose screens, but does not approve ROM offsets.
- v0.4.3 needs both CPU-read proof and explicit visual-context confirmation.
- ROM files are local artifacts only and must not be distributed.
