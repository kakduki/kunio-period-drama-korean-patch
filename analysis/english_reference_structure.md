# Technos Samurai v1.0 — English-reference structural map

## Verified identity

| Item | Value |
|---|---|
| Base ROM MD5 | `0d406a85285b4de8468f0dab6aad5fe5` |
| Base ROM size | `262,160` bytes |
| IPS SHA-256 | `cb6ea2fdbf82e974c474f4ea0d489f7c65647c94de899caf2a6b8c089f202dad` |
| IPS records | `99` |
| Patched ROM MD5 | `63e1d902807981f524af97748cd99500` |

The reference is archived at `reference/technos-samurai-v1/`. It was fetched by range requests from Archive.org, not recreated from a third-party ROM.

## Physical change map

| Region | Changed bytes | Meaning that is proven |
|---|---:|---|
| iNES header | 1 | Header byte `0x06` changes `0x41 → 0x43` |
| PRG-ROM | 10,295 | Text, pointer, and/or renderer-related changes exist; subcategories require runtime proof |
| CHR-ROM | 2,286 | Glyph/icon/palette-related tile data changes exist |

The header change preserves **mapper 4** (high nibble stays `0x4`) and changes iNES flag-6 bit 1 from clear to set: **four-screen mirroring**. This is a compatibility-relevant reference fact, not a Korean-patch change instruction.

## Concentrated changed regions

### PRG (8 KiB physical bank)

| Bank | Changed bytes | Physical file offset = `0x10 + bank×0x2000` |
|---:|---:|---|
| 3 | 5,916 | 8 KiB PRG bank |
| 2 | 2,018 | 8 KiB PRG bank |
| 14 | 1,079 | 8 KiB PRG bank |
| 9 | 1,013 | 8 KiB PRG bank |
| 13 | 221 | 8 KiB PRG bank |

### CHR (1 KiB physical bank)

| Bank | Changed bytes | Physical file offset = `0x20010 + bank×0x400` |
|---:|---:|---|
| 62 | 794 | 1 KiB CHR bank |
| 63 | 495 | 1 KiB CHR bank |
| 60 | 464 | 1 KiB CHR bank |
| 16 | 184 | 1 KiB CHR bank |
| 61 | 147 | 1 KiB CHR bank |
| 17 | 97 | 1 KiB CHR bank |
| 126 | 53 | 1 KiB CHR bank |

## What can be reused now

1. **CHR bank 60–63 is the highest-value font/icon comparison target.** It contains 1,900 of 2,286 changed CHR bytes. Compare its tile inventory against the base before designing Korean glyph capacity.
2. **PRG banks 2–3 are the primary text/pointer candidate region.** They contain 7,934 of 10,295 changed PRG bytes. They are candidates only; the live `$2006/$2007` trace must prove the pointer path.
3. **PRG bank 14 is a separate high-value candidate** (1,079 bytes) and should not be assumed to be dialogue data just because it changed.
4. The English patch is an **architectural reference**, not an overlay: Korean v0.4.x remains untouched and each claimed structure must be re-proven against the Japanese base at runtime.

## Explicit non-conclusions

- A physical PRG diff cannot identify a pointer table by itself.
- A CHR diff cannot establish which PPU bank a scene uses.
- The four-screen header flag must be treated as part of the English patch's runtime contract until emulator evidence explains it.

## Reproduction

```bash
python3 scripts/fetch_technos_samurai_reference.py
python3 scripts/analyze_technos_samurai_ips.py
python3 -m py_compile scripts/fetch_technos_samurai_reference.py scripts/analyze_technos_samurai_ips.py
```

Machine-readable map: `analysis/english_reference_structure.json`.
