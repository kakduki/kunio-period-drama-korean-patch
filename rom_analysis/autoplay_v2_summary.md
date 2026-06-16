# AutoPlay Watch v2 Summary

## Script: `lua/kunio_autoplay_watch.lua` (v2 — 3-phase)

### Phase structure
| Phase | Frame range | Action |
|-------|-------------|--------|
| 1 | 0–199 | Game load wait (no inputs) |
| 2 | 200–3000 | START → menu entry; direction-key cycling (down/up per 60f) to sweep menu items; extra START presses at rel≈150 and rel≈600 for sub-menus |
| 3 | 3001–5000 | START to close menu → right+B advance → right+A+B combat |

### Parameters
- `MAX_FRAMES`: 5000
- `HIT_LIMIT`: 30000
- Targets: 36 (from `kunio_bank1_targets.lua`)
- New column in `bank1_reads.tsv`: `byte_diff` — shows `=XX` (match) or `EX>AC` (expected→actual) per expected byte

---

## v1 baseline (autoplay old 5-phase, hit_limit 20000, stopped at frame 4317)

### Active expected match results

| label | source | expected_bytes | active_matches | record_snapshot | verdict |
|-------|--------|---------------|---------------|----------------|---------|
| `rom_071a4_candidate_82` | ちから (힘) | `93 88 AA` | **11** | `9F B4 93 88 AA A6 83 CA F8 F9 00` | ✅ CONFIRMED |
| `rom_07227_candidate_84` | カタナ (카타나) | `8A 94 99` | **5** | `85 8A 94 99 00` | ✅ CONFIRMED |
| all others | — | — | 0 | — | not matched |

### Unmatched high-hit targets (need base offset re-estimation)

| label | source | hits | expected_bytes | typical record snapshot |
|-------|--------|------|----------------|------------------------|
| `rom_0736a_candidate_93` | ライフ (라이프) | 5534 | `BB 95 AF` | `A2 7A 29 10 F0 1C` |
| `rom_06de3_candidate_80` | おかね (돈) | 4903 | `85 86 98` | `A3 7A 38 6E A3 7A EE` |
| `rom_06fa1_candidate_8d` | そうび (장비) | 1046 | `9C 90 A8` | `CA 02 C4 46 C5 FF 01 CE 3C 95` |
| `rom_06b4a_candidate_82` | ちから (힘) | 1872 | `93 88 AA` | `9D 1D 71 E8 60 A9 30 20 33 E3 B0 FB A9 01` |

Note: High hit count with no match suggests the CPU address range is being read (correct bank), but the expected bytes from the ROM analysis differ from what the CPU sees at runtime. The `byte_diff` column in v2 output will show per-byte delta.

---

## v2 run results

> **TODO: Fill in after running:**
> ```
> python scripts/run_fceux_lua_analysis.py \
>   --lua-script lua/kunio_autoplay_watch.lua \
>   --frames 5000 --timeout 150 \
>   --final-output rom_analysis/fceux_bank1_watch_test \
>   --clean-output --no-dump-hex --no-dump-bin
> ```
> Then:
> ```
> python scripts/summarize_bank1_watch_reads.py \
>   --input-dir rom_analysis/fceux_bank1_watch_test \
>   --output rom_analysis/fceux_bank1_watch_test/autoplay_v2_summary.md
> ```

### Per-target read hit count (v2)

| label | source | hits | first_frame | last_frame | active_expected_matches | top_byte_diff |
|-------|--------|------|-------------|------------|------------------------|--------------|
| *(pending v2 run)* | | | | | | |

### Newly confirmed targets (v2)

| label | source | record_snapshot |
|-------|--------|----------------|
| *(pending)* | | |

### Base offset adjustment needed

| label | source | expected_bytes | observed_diff |
|-------|--------|----------------|--------------|
| *(pending)* | | | |
