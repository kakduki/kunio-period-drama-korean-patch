# v0.4.3 Broad Verified Gate Report

- Verdict: **no candidate built; manual CPU-read and visual-context evidence is incomplete**
- Summary status: `no_manual_broad_scan_dump_records`
- Active CPU-read matches: **0**
- Approved visual reviews: **0**
- Applied rows: **0**
- Skipped rows: **7**
- Proof packet: `rom_analysis\v042_manual_proof_packet.json`
- Broad summary: `rom_analysis\manual_screen_dump_broad_scan\summary.json`
- Visual review: `rom_analysis\manual_screen_dump_broad_scan\visual_review.json`

## Applied Rows

_No v0.4.3 rows are approved yet._

## Skipped Rows

| ROM | expected text | Korean | screen hint | reason |
| --- | --- | --- | --- | --- |
| `0x0440C` | かじや | 대장간 | look for a blacksmith/shop or blacksmith-stage label | visual_context_confirmed is not true |
| `0x048F4` | たつじ | 타츠지 | look for a visible Tatsuji boss/name context | visual_context_confirmed is not true |
| `0x052A5` | たつじ | 타츠지 | look for a visible Tatsuji boss/name context | visual_context_confirmed is not true |
| `0x05BE5` | たつじ | 타츠지 | look for a visible Tatsuji boss/name context | visual_context_confirmed is not true |
| `0x06294` | へいしち | 헤이시치 | look for a visible Heishichi name/dialogue context | visual_context_confirmed is not true |
| `0x0631B` | へいしち | 헤이시치 | look for a visible Heishichi name/dialogue context | visual_context_confirmed is not true |
| `0x06359` | へいしち | 헤이시치 | look for a visible Heishichi name/dialogue context | visual_context_confirmed is not true |

## Gate Rule

- A row needs both `active_original_byte_match=true` in the broad-scan summary and `visual_context_confirmed=true` in the visual review file.
- Preview IPS results do not bypass this gate; they only help compare real screens.
- If this report says no candidate was built, keep using v0.4.2 as the primary patch.
