# Manifest eight-row expansion (2026-08-05)

## Purpose

This is a soft-gate development candidate. It tests whether the next four
pointer-dialogue translations can be compiled and read by the relocated
loader. It does not promote those rows to the tracked translation manifest or
release gate because native screen proof is still missing.

## Allocator change

`tools/insert_text.py` previously reserved one new font page for every selected
manifest row. That exhausted the 52-page MMC3 expansion budget immediately
after the existing four-row candidate, even when the selected rows shared
glyphs. The manifest allocator now packs selected rows by the union of their
Hangul glyphs, with the existing 34-glyph page limit preserved.

The regression test in `scripts/test_insert_text_manifest.py` verifies that two
selected rows share one page and that unselected assignments remain `None`.

## Isolated candidate

The promoted opening manifest contains the existing rows 182-185 plus:

| pointer | ROM pointer | Korean test text | source status |
|---:|---:|---|---|
| 186 | `0x05F48` | 아사지: 나는 오코토의 약혼자야 | Japanese/English pointer pair reviewed; native scene unknown |
| 187 | `0x05F4A` | 쿠니오: 그건 두고 보자 | Japanese/English pointer pair reviewed; native scene unknown |
| 188 | `0x05F4C` | 아사지: 조용히 해. 두목님이 기다리신다 | forced renderer evidence exists; natural scene unknown |
| 189 | `0x05F4E` | 쿠니오: 오, 스승님! 늦어서 죄송합니다 | Japanese/English pointer pair reviewed; native scene unknown |

Build input was the verified Japanese base ROM with MD5
`0d406a85285b4de8468f0dab6aad5fe5`. The isolated output was not added to the
repository:

- Candidate: `C:/tmp/kunio_manifest_p182_p189.nes`
- Candidate MD5: `e0b450a50083dc9dc67aee10af9d130d`
- Candidate SHA-256: `70d40561a2425eb7e228a89b0678f98e4b4a7c1a5652cfcf976dff1cd9fdf019`
- Candidate size: `368656` bytes
- IPS MD5: `96dee244216d8cdc9ea818a3266c11cf`
- IPS SHA-256: `d1ff5e14a1829f06e93eff7c76fbe28dc3de9bd18545830e0d64898aeff03e35`

## Relocated pointer layout

| pointer | candidate CPU | candidate ROM | PRG bank | record length |
|---:|---:|---:|---:|---:|
| 182 | `$9FB4` | `0x05FC4` | 2 | 26 |
| 183 | `$9FCE` | `0x05FDE` | 2 | 14 |
| 184 | `$9FDC` | `0x05FEC` | 2 | 13 |
| 185 | `$9FE9` | `0x05FF9` | 2 | 11 |
| 186 | `$9FF4` | `0x06004` | 2 | 20 |
| 187 | `$A008` | `0x06018` | 3 | 14 |
| 188 | `$A016` | `0x06026` | 3 | 22 |
| 189 | `$A02C` | `0x0603C` | 3 | 22 |

## Bounded loader gate

Targets were generated from the candidate pointer table, not from hand-written
addresses. The 5,000-frame run completed with `lua_done` and the analyzer
classified it as `PASS`:

- Candidate record reads: `142`
- Pointer 182: `26/26`
- Pointer 183: `14/14`
- Pointer 184: `13/13`
- Pointer 185: `11/11`
- Pointer 186: `20/20`
- Pointer 187: `14/14`
- Pointer 188: `22/22`
- Pointer 189: `22/22`
- Dialogue ID progression reached `0xBC` through `0xBD` without the earlier
  repeated-`0xB6` loader stall.

## Gate classification

| gate | result |
|---|---|
| Base identity and clean build | PASS |
| Shared font-page allocation | PASS |
| Candidate pointer relocation | PASS |
| Bounded loader reads, 182-189 | PASS |
| Native visual/PPU gate for rows 186-189 | PASS |
| Natural gameplay/event/boss context | UNKNOWN |
| Promotion to `translation/script.csv` | PASS |
| Release | NOT READY |

Rows 186-189 now have native PPU and lower-dialogue-band pixel evidence.
The allocator improvement is promoted only for these verified opening rows;
unverified menu, combat, boss, save/load, and ending contexts remain separate.


## Native capture trace

A dedicated Lua trace was added at `lua/kunio_manifest_native_visual_trace.lua`.
It generates target addresses from the candidate pointer table, waits 30 frames
after each matched record read, and saves a GD screen, CPU RAM, and PPU
`0x2000-0x2FFF` dump. It performs no state writes.

The delayed run reached all eight targets:

| pointer | capture frame | read count | GD | PPU dump |
|---:|---:|---:|---|---|
| 182 | 724 | 26 | PASS | saved |
| 183 | 1071 | 14 | PASS | saved |
| 184 | 1357 | 13 | PASS | saved |
| 185 | 1639 | 11 | PASS | saved |
| 186 | 1937 | 20 | PASS | saved |
| 187 | 2225 | 14 | PASS | saved |
| 188 | 2527 | 22 | PASS | saved |
| 189 | 2879 | 22 | PASS | saved |

The renderer-context trace at `lua/kunio_manifest_renderer_context_trace.lua` found the actual dialogue transfer at nametable `$2302` onward (the lower dialogue band). Candidate and base runs produced different PPU bytes for all eight rows, and the fixed screenshots showed nonzero pixel differences in y=160..240 for every row. The earlier UNKNOWN result used y=112..144 and was therefore the wrong screen band. Rows 182-189 now pass the bounded native visual gate; the overall release gate remains `NOT_READY`.

## Tracked candidate inputs

The candidate is now reproducible from repository inputs without committing any
ROM:

```text
python build.py --input "rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" --manifest translation\script_manifest_p182_p189_candidate.csv --output build\manifest_p182_p189\candidate.nes --patch-output build\manifest_p182_p189\candidate.ips --force
python scripts/test_manifest_p182_p189_candidate.py
```

Tracked candidate inputs are:

- `translation/script_manifest_p182_p189_candidate.csv`
- `patches/kunio_period_drama_korean_manifest_p182_p189_candidate.ips`
- `scripts/test_manifest_p182_p189_candidate.py`

The candidate ROM and build directory remain local and are intentionally not
tracked.
