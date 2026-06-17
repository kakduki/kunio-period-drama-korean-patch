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

## 2. Primary Screens To Check First

Do not keep blind autoplay running on the title/first screen. First verify the rows already changed by the primary IPS.

- Pending primary visual checks: **10**
- Open patched ROM: `output/kunio_period_drama_korean_prg_plan_v0.4.2_font_expanded.nes`
- Run watcher: `lua/kunio_manual_v042_capture_watch.lua`
- Press `D` only on a visible matching text/menu/status screen.

| # | ROM | romaji | human hint | Korean | evidence | screen hint |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `0x07227` | Katana | weapon/item label | 카타나 | `runtime-confirmed` | look for a katana/weapon item label |
| 2 | `0x0569D` | Hashi | stage/location label | 다리 | `encoding-exact` | look for a bridge/stage/location label |
| 3 | `0x0561A` | Hashi | stage/location label | 다리 | `static-candidate+pointer` | look for a bridge/stage/location label |
| 4 | `0x05643` | Heishichi | name/dialogue label | 헤이시치 | `static-candidate+pointer` | look for a visible Heishichi name/dialogue context |
| 5 | `0x057D4` | Hashi | stage/location label | 다리 | `static-candidate+pointer` | look for a bridge/stage/location label |
| 6 | `0x0736A` | Raifu | UI life label | 라이프 | `static-candidate+pointer` | look for a life/status UI label |
| 7 | `0x0739D` | Raifu | UI life label | 라이프 | `static-candidate+pointer` | look for a life/status UI label |

After a matched primary screen:

```powershell
python scripts/record_primary_visual_review.py 0x07227 --confirm --screen-context "katana/weapon item label visible"
python scripts/refresh_after_manual_capture.py --phase primary
```

## 3. Broad Screens For Future v0.4.3 Rows

Use these only after primary visual review, or when you are already on the matching base-ROM route.

| # | ROM | expected text | Korean | CPU guess | proof status | screen hint |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `0x06294` | へいしち | 헤이시치 | `$A284` | `needs_manual_capture` | look for a visible Heishichi name/dialogue context |
| 2 | `0x0631B` | へいしち | 헤이시치 | `$A30B` | `needs_manual_capture` | look for a visible Heishichi name/dialogue context |
| 3 | `0x06359` | へいしち | 헤이시치 | `$A349` | `needs_manual_capture` | look for a visible Heishichi name/dialogue context |
| 4 | `0x048F4` | たつじ | 타츠지 | `$88E4` | `needs_manual_capture` | look for a visible Tatsuji boss/name context |
| 5 | `0x052A5` | たつじ | 타츠지 | `$9295` | `needs_manual_capture` | look for a visible Tatsuji boss/name context |
| 6 | `0x05BE5` | たつじ | 타츠지 | `$9BD5` | `needs_manual_capture` | look for a visible Tatsuji boss/name context |
| 7 | `0x0440C` | かじや | 대장간 | `$83FC` | `needs_manual_capture` | look for a blacksmith/shop or blacksmith-stage label |

## 4. Route Watchers

Prefer these route wrappers over the all-target broad watcher. They show the active route and screen hint in the FCEUX overlay.

| route | group | watcher | targets | screen hint |
| ---: | --- | --- | ---: | --- |
| 1 | Kajiya | `lua/kunio_manual_route_kajiya_capture_watch.lua` | 1 | look for a blacksmith/shop or blacksmith-stage label |
| 2 | Tatsuji | `lua/kunio_manual_route_tatsuji_capture_watch.lua` | 3 | look for a visible Tatsuji boss/name context |
| 3 | Heishichi | `lua/kunio_manual_route_heishichi_capture_watch.lua` | 3 | look for a visible Heishichi name/dialogue context |

Recommended next run:

```text
lua/kunio_manual_route_heishichi_capture_watch.lua
```

If the visible FCEUX screen is still the title/opening screen, stop with `Q`; do not wait.

## 5. Capture Evidence

For broad v0.4.3 candidates, open the base Japanese ROM, manually reach the target screen, then run:

```text
lua/kunio_manual_broad_scan_dump.lua
```

For several manually reached candidate screens in one session, run the matching route watcher once and press `D` on each target screen. Use the all-target watcher only if the route is unclear:

```text
lua/kunio_manual_broad_scan_capture_watch.lua
```

Then summarize and refresh the status reports:

```powershell
python scripts/analyze_broad_scan_manual_dump.py
python scripts/generate_v043_proof_status.py
python scripts/generate_manual_dump_inventory.py
```

## 6. Record v0.4.3 Visual Review

Only after the visible screen matches the intended row:

```powershell
python scripts/record_visual_review.py 0x0440C --confirm --screen-context "blacksmith label visible"
python scripts/build_v043_from_broad_scan_proof.py
```

## Rule

- YouTube/transcription order helps choose screens, but does not approve ROM offsets.
- v0.4.3 needs both CPU-read proof and explicit visual-context confirmation.
- ROM files are local artifacts only and must not be distributed.
