# Korean targets × English-reference structural correlation

> Decision rule: this report replaces menu-loop observation with a reproducible physical-diff check. “Structurally supported” means only that the verified English patch also changes the exact Japanese PRG span. It is **not** a pointer, CPU-read, visual, or release proof.

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- English IPS SHA-256: `cb6ea2fdbf82e974c474f4ea0d489f7c65647c94de899caf2a6b8c089f202dad`
- English IPS records: **99**
- Classifications: `{'unrelated_to_english_reference': 2, 'structurally_supported': 5}`

| task | target file offset | source → Korean | static result | English run IDs | runtime/release |
|---:|---|---|---|---|---|
| 1 | `0x0440C` | かじや → 대장간 | `unrelated_to_english_reference` | — | required / no |
| 2 | `0x048F4` | たつじ → 타츠지 | `unrelated_to_english_reference` | — | required / no |
| 3 | `0x052A5` | たつじ → 타츠지 | `structurally_supported` | 5 | required / no |
| 4 | `0x05BE5` | たつじ → 타츠지 | `structurally_supported` | 173 | required / no |
| 5 | `0x06294` | へいしち → 헤이시치 | `structurally_supported` | 392 | required / no |
| 6 | `0x0631B` | へいしち → 헤이시치 | `structurally_supported` | 395 | required / no |
| 7 | `0x06359` | へいしち → 헤이시치 | `structurally_supported` | 395 | required / no |

## Interpretation

- **Supported rows are prioritization candidates, not patch-ready rows.** They show that the historical English patch altered the same PRG span, so these offsets deserve code/pointer analysis before unrelated targets.
- **Unrelated rows are not rejected.** They simply cannot borrow structural confidence from the English IPS and must wait for another static route or a debugger-capable runtime trace.
- No Korean IPS/ROM was generated or modified by this analysis.
