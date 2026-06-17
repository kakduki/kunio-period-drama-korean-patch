# Batch46 Text Readiness

This report reclassifies the broad-scan capture queue against the largest currently buildable font expansion.

## Summary

- Queued hits: **60**
- Batch46 added glyphs: **46**
- Font-ready after v0.4.2: **27**
- Font-ready after batch46: **27**
- Newly font-ready after batch46: **0**
- Screen-proof candidates after batch46: **7**
- New screen-proof candidates after batch46: **0**

## New Font-Ready Rows

| priority | confidence | ROM | romaji | bytes | glyphs | blockers |
| ---: | --- | --- | --- | ---: | ---: | --- |

## Screen-Proof Candidates

| priority | confidence | ROM | romaji | korean | planned bytes | screen hint |
| ---: | --- | --- | --- | --- | --- | --- |
| 10 | high | `0x06294` | Heishichi | 헤이시치 | `0x8D 0x8E 0x8F 0x90` | look for a visible Heishichi name/dialogue context |
| 10 | high | `0x06359` | Heishichi | 헤이시치 | `0x8D 0x8E 0x8F 0x90` | look for a visible Heishichi name/dialogue context |
| 10 | high | `0x0631B` | Heishichi | 헤이시치 | `0x8D 0x8E 0x8F 0x90` | look for a visible Heishichi name/dialogue context |
| 15 | medium | `0x052A5` | Tatsuji | 타츠지 | `0x89 0x98 0xA1` | look for a visible Tatsuji boss/name context |
| 15 | medium | `0x0440C` | Kajiya | 대장간 | `0xB5 0x93 0xAB` | look for a blacksmith/shop or blacksmith-stage label |
| 15 | medium | `0x05BE5` | Tatsuji | 타츠지 | `0x89 0x98 0xA1` | look for a visible Tatsuji boss/name context |
| 15 | medium | `0x048F4` | Tatsuji | 타츠지 | `0x89 0x98 0xA1` | look for a visible Tatsuji boss/name context |

## Rule

- Do not promote rows from font readiness alone.
- A row can move into a patch only after manual CPU-read evidence and visible screen-context proof agree.
- Rows blocked by length mismatch still need a padding/control-code rule before patching.
