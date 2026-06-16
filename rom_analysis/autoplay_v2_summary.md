# AutoPlay Watch v2 Summary

## Script: `lua/kunio_autoplay_watch.lua` (v2 — 3-phase)

### Phase structure
| Phase | Frame range | Action |
|-------|-------------|--------|
| 1 | 0–199 | Game load wait (no inputs) |
| 2 | 200–3000 | START → menu entry; direction-key cycling (down/up per 60f) to sweep menu items |
| 3 | 3001–5000 | START to close menu → right+B advance → right+A+B combat |

### Run parameters
- `MAX_FRAMES`: 5000
- `HIT_LIMIT`: 30000 (reached at frame **3363**)
- Targets: 36 (from `kunio_bank1_targets.lua`)
- New column `byte_diff`: shows `=XX` (match) or `EX>AC` (expected→actual) per expected byte

---

## v2 run results (2026-06-16)

- Final frame: 3363 (hit_limit reached at phase 3 start)
- Phase 2 hits: ~1015 (frames 200–3000, menu navigation)
- Phase 3 hits: ~28985 (frames 3001–3363, stage advance — dominated hit budget)
- Registered CPU addresses: 334

### Active expected match results

| label | source | expected_bytes | hits | active_matches | top_byte_diff | record_snapshot | verdict |
|-------|--------|----------------|------|---------------|--------------|----------------|---------|
| `rom_071a4_candidate_82` | ちから (힘) | `93 88 AA` | 2647 | **11** | `93>19 88>57 AA>00` | `9F B4 93 88 AA A6 83 CA F8 F9 00` | ✅ CONFIRMED |
| `rom_07227_candidate_84` | カタナ (카타나) | `8A 94 99` | 0 (v2) | 0 | — | — | ⚠️ not seen in v2 (phase 3 hit budget exhausted; confirmed in v1) |

> **Note:** `rom_07227_candidate_84` appeared at frames 1975–4213 in v1, but v2 hit_limit was reached at frame 3363 before phase 3 could capture those reads.

### Byte diff analysis (offset mismatch candidates)

Targets with 0 active matches but high hit count — actual runtime bytes vs expected:

| label | source | expected_bytes | top_byte_diff | actual_at_runtime | note |
|-------|--------|----------------|--------------|------------------|------|
| `rom_0736a_candidate_93` | ライフ (라이프) | `BB 95 AF` | `BB>2A 95>00 AF>6C` | `2A 00 6C` | base offset likely off |
| `rom_06de3_candidate_80` | おかね (돈) | `85 86 98` | `85>49 86>FF 98>18` | `49 FF 18` | base offset likely off |
| `rom_06fa1_candidate_8d` | そうび (장비) | `9C 90 A8` | `9C>53 90>70 A8>60` | `53 70 60` | base offset likely off |
| `rom_06b4a_candidate_82` | ちから (힘, alt) | `93 88 AA` | `93>F0 88>08 AA>C8` | `F0 08 C8` | wrong address range |
| `rom_066fb_candidate_82` | ちから (힘, alt) | `93 88 AA` | `93>03 88>70 AA>6B` | `03 70 6B` | wrong address range |
| `rom_05bba_candidate_7a` | やり (창) | `9F A3` | `9F>01 A3>01` | `01 01` | all-zero/init at read time |

### v2 vs v1 comparison

| metric | v1 | v2 |
|--------|----|----|
| Final frame | 4317 | 3363 |
| Hit limit | 20000 | 30000 |
| Active matches: ちから | 11 | 11 |
| Active matches: カタナ | 5 | 0 (budget exhausted) |
| New confirmed targets | — | none |
| byte_diff column | no | yes |

### Conclusion

- **ちから (`rom_071a4_candidate_82`)**: Consistently confirmed across v1 and v2 with 11 active matches. CPU record `$B192-$B19C` contains `93 88 AA` at the correct times.
- **カタナ (`rom_07227_candidate_84`)**: Confirmed in v1 (5 matches, frames 1975–4213). Not captured in v2 because phase 3 stage-advance reads dominated the hit budget. Confidence stays **high**.
- **やり / そうび / おかね / ライフ**: No active matches. `byte_diff` shows the expected bytes are consistently wrong at the record addresses — base offset re-estimation required for these targets.

### Recommended next steps

1. Extend hit_limit or split into two focused runs: phase 2 only (menu) vs phase 3 only (stage).
2. For ライフ/おかね/そうび: re-derive expected bytes from the actual runtime bytes (`2A 00 6C`, `49 FF 18`, `53 70 60`) — search ROM for those byte sequences near the current candidate addresses.
3. For やり: the CPU record shows `01 01` (all init/zero) — the ROM address may only be read during specific weapon equip events, not general menu navigation.
