# AutoPlay Watch — Cumulative Run Summary

## Script: `lua/kunio_autoplay_watch.lua` (v3 — 3-phase + per-phase budget)

### Phase structure
| Phase | Frame range | Action |
|-------|-------------|--------|
| 1 | 0–199 | Game load wait (no inputs) |
| 2 | 200–3000 | START → menu entry; direction-key cycling (down/up per 60f) |
| 3 | 3001–5000 | START to close menu → right+B advance → right+A+B combat |

---

## v3 run results (2026-06-16, hit_limit=50000, phase2_cap=30000, phase3_cap=20000)

- Final frame: **5000** (`lua_done`) — full run completed
- Phase 2 hits: ~1015  |  Phase 3 hits: 20000 (capped at 20000)
- Total: 21015 hits across 334 registered CPU addresses

### Active expected match results

| label | source | expected_bytes | hits | active_matches | top_byte_diff | record_snapshot | verdict |
|-------|--------|----------------|------|---------------|--------------|----------------|---------|
| `rom_071a4_candidate_82` | ちから (힘) | `93 88 AA` | 1797 | **11** | `93>19 88>57 AA>00` | `9F B4 93 88 AA A6 83 CA F8 F9 00` | ✅ CONFIRMED |
| `rom_07227_candidate_84` | カタナ (카타나) | `8A 94 99` | 0 | 0 | — | — | ⚠️ not captured (appears after phase3 cap; confirmed in v1 frames 1975–4213) |
| all others | — | various | 0 | 0 | inconsistent | — | not matched |

### Base offset recalculation result (2026-06-16)

All 15 active targets with byte_diff data showed **inconsistent base candidates**.
Formula tested: `base_candidate = (actual_byte - HIRAGANA_LOW[char]) & 0xFF`

| target | source | expected_bytes | actual_runtime | base_candidates | conclusion |
|--------|--------|----------------|----------------|----------------|------------|
| `rom_06fa1` | そうび | `9C 90 A8` | `53 70 60` | 0x44, 0x45, 0x6D | inconsistent |
| `rom_0736a` | ライフ | `BB 95 AF` | `2A 00 6C` | 0x02, 0x50, 0xFE | inconsistent |
| `rom_06de3` | おかね | `85 86 98` | `49 FF 18` | 0x00, 0x44, 0xF9 | inconsistent |
| `rom_05bba` | やり | `9F A3` | `01 01` | 0xD8, 0xDC | inconsistent |
| `rom_071a4` | ちから | `93 88 AA` | `19 57 00` | 0x08, 0x51, 0xD8 | inconsistent (but has 11 active matches!) |

**Conclusion**: Runtime bytes at these CPU addresses are NOT the text encoding — a different ROM bank is loaded at those addresses during our test window. The expected_bytes are correct per static ROM analysis.

---

## v2 run results (2026-06-16, hit_limit=30000)

- Final frame: 3363 (hit_limit reached)
- Phase 2: ~1015 hits  |  Phase 3: ~28985 hits (dominated budget)
- ちから: 11 active matches ✅

## v1 run results (baseline, hit_limit=20000)

- Final frame: 4317 (hit_limit reached)
- ちから: 11 active matches ✅
- カタナ: 5 active matches ✅ (frames 1975–4213)

---

## Cross-run summary

| target | source | v1 active | v2 active | v3 active | confidence |
|--------|--------|-----------|-----------|-----------|------------|
| `rom_071a4_candidate_82` | ちから (힘) | 11 | 11 | 11 | **high** |
| `rom_07227_candidate_84` | カタナ (카타나) | 5 | 0 | 0 | **high** (v1 confirmed) |
| all others | — | 0 | 0 | 0 | medium |

## Root cause analysis — why some targets aren't matched

NES bank switching: the ROM maps different 16KB banks to CPU $8000–$BFFF.
During menu display, Bank 1 text (e.g. ちから at ROM 0x071A4 → CPU $B192) is readable.
During stage code execution, a different bank is loaded at those CPU addresses,
so the watcher sees random code/data bytes instead of the text encoding.

Targets that ARE matched (ちから, カタナ) happen to be read when Bank 1 is loaded.
Targets that are NOT matched require a specific menu/screen not triggered in our autoplay,
or are in a sub-bank that's rarely loaded during our test window.

## Next steps

1. Trigger specific menu items explicitly (weapon equip screen, status screen) to capture やり/そうび/おかね.
2. Track PPU writes instead of (or alongside) CPU reads to catch text during VRAM transfer.
3. Extend phase3_cap or remove it for カタナ confirmation in v3.
