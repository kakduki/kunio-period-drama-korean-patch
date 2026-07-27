# Opening Font Runtime Mapping Audit

Status: FAIL

- Candidate source codes: 34
- Candidate declared font targets: 68
- Runtime emitted tile rows audited: 67
- Rows with incomplete mapper state: 0
- Runtime mappings passing: 0
- Runtime mappings failing: 67

The candidate changes a different physical CHR tile for at least one tile
that the runtime actually emits. The affected source range must not be
used as a release-capable Korean font allocation.

| source | emitted | runtime bank/tile | runtime ROM | candidate ROM | reason |
| --- | --- | --- | --- | --- | --- |
| 0x81 | 0x81 | Bank 8 / 0x181 | 0x31820 | 0x2F820 | declared candidate target differs from runtime physical tile |
| 0x81 | 0xA1 | Bank 8 / 0x1A1 | 0x31A20 | 0x2FA20 | declared candidate target differs from runtime physical tile |
| 0x82 | 0x82 | Bank 8 / 0x182 | 0x31830 | 0x2F830 | declared candidate target differs from runtime physical tile |
| 0x82 | 0xA2 | Bank 8 / 0x1A2 | 0x31A30 | 0x2FA30 | declared candidate target differs from runtime physical tile |
| 0x83 | 0x83 | Bank 8 / 0x183 | 0x31840 | 0x2F840 | declared candidate target differs from runtime physical tile |
| 0x83 | 0xA3 | Bank 8 / 0x1A3 | 0x31A40 | 0x2FA40 | declared candidate target differs from runtime physical tile |
| 0x84 | 0x84 | Bank 8 / 0x184 | 0x31850 | 0x2F850 | declared candidate target differs from runtime physical tile |
| 0x84 | 0xA4 | Bank 8 / 0x1A4 | 0x31A50 | 0x2FA50 | declared candidate target differs from runtime physical tile |
| 0x85 | 0x85 | Bank 8 / 0x185 | 0x31860 | 0x2F860 | declared candidate target differs from runtime physical tile |
| 0x85 | 0xA5 | Bank 8 / 0x1A5 | 0x31A60 | 0x2FA60 | declared candidate target differs from runtime physical tile |
| 0x86 | 0x86 | Bank 8 / 0x186 | 0x31870 | 0x2F870 | declared candidate target differs from runtime physical tile |
| 0x86 | 0xA6 | Bank 8 / 0x1A6 | 0x31A70 | 0x2FA70 | declared candidate target differs from runtime physical tile |
| 0x87 | 0x87 | Bank 8 / 0x187 | 0x31880 | 0x2F880 | declared candidate target differs from runtime physical tile |
| 0x87 | 0xA7 | Bank 8 / 0x1A7 | 0x31A80 | 0x2FA80 | declared candidate target differs from runtime physical tile |
| 0x88 | 0x88 | Bank 8 / 0x188 | 0x31890 | 0x2F890 | declared candidate target differs from runtime physical tile |
| 0x88 | 0xA8 | Bank 8 / 0x1A8 | 0x31A90 | 0x2FA90 | declared candidate target differs from runtime physical tile |
| 0x89 | 0x89 | Bank 8 / 0x189 | 0x318A0 | 0x2F8A0 | declared candidate target differs from runtime physical tile |
| 0x89 | 0xA9 | Bank 8 / 0x1A9 | 0x31AA0 | 0x2FAA0 | declared candidate target differs from runtime physical tile |
| 0x8A | 0x8A | Bank 8 / 0x18A | 0x318B0 | 0x2F8B0 | declared candidate target differs from runtime physical tile |
| 0x8A | 0xAA | Bank 8 / 0x1AA | 0x31AB0 | 0x2FAB0 | declared candidate target differs from runtime physical tile |
| 0x8B | 0x8B | Bank 8 / 0x18B | 0x318C0 | 0x2F8C0 | declared candidate target differs from runtime physical tile |
| 0x8B | 0xAB | Bank 8 / 0x1AB | 0x31AC0 | 0x2FAC0 | declared candidate target differs from runtime physical tile |
| 0x8C | 0x8C | Bank 8 / 0x18C | 0x318D0 | 0x2F8D0 | declared candidate target differs from runtime physical tile |
| 0x8C | 0xAC | Bank 8 / 0x1AC | 0x31AD0 | 0x2FAD0 | declared candidate target differs from runtime physical tile |
| 0x8D | 0x8D | Bank 8 / 0x18D | 0x318E0 | 0x2F8E0 | declared candidate target differs from runtime physical tile |
| 0x8D | 0xAD | Bank 8 / 0x1AD | 0x31AE0 | 0x2FAE0 | declared candidate target differs from runtime physical tile |
| 0x8E | 0x8E | Bank 8 / 0x18E | 0x318F0 | 0x2F8F0 | declared candidate target differs from runtime physical tile |
| 0x8E | 0xAE | Bank 8 / 0x1AE | 0x31AF0 | 0x2FAF0 | declared candidate target differs from runtime physical tile |
| 0x8F | 0x8F | Bank 8 / 0x18F | 0x31900 | 0x2F900 | declared candidate target differs from runtime physical tile |
| 0x8F | 0xAF | Bank 8 / 0x1AF | 0x31B00 | 0x2FB00 | declared candidate target differs from runtime physical tile |
| 0x90 | 0x90 | Bank 8 / 0x190 | 0x31910 | 0x2F910 | declared candidate target differs from runtime physical tile |
| 0x90 | 0xB0 | Bank 8 / 0x1B0 | 0x31B10 | 0x2FB10 | declared candidate target differs from runtime physical tile |
| 0x91 | 0x91 | Bank 8 / 0x191 | 0x31920 | 0x2F920 | declared candidate target differs from runtime physical tile |
| 0x92 | 0x92 | Bank 8 / 0x192 | 0x31930 | 0x2F930 | declared candidate target differs from runtime physical tile |
| 0x92 | 0xB2 | Bank 8 / 0x1B2 | 0x31B30 | 0x2FB30 | declared candidate target differs from runtime physical tile |
| 0x93 | 0x93 | Bank 8 / 0x193 | 0x31940 | 0x2F940 | declared candidate target differs from runtime physical tile |
| 0x93 | 0xB3 | Bank 8 / 0x1B3 | 0x31B40 | 0x2FB40 | declared candidate target differs from runtime physical tile |
| 0x94 | 0x94 | Bank 8 / 0x194 | 0x31950 | 0x2F950 | declared candidate target differs from runtime physical tile |
| 0x94 | 0xB4 | Bank 8 / 0x1B4 | 0x31B50 | 0x2FB50 | declared candidate target differs from runtime physical tile |
| 0x95 | 0x95 | Bank 8 / 0x195 | 0x31960 | 0x2F960 | declared candidate target differs from runtime physical tile |
| 0x95 | 0xB5 | Bank 8 / 0x1B5 | 0x31B60 | 0x2FB60 | declared candidate target differs from runtime physical tile |
| 0x96 | 0x96 | Bank 8 / 0x196 | 0x31970 | 0x2F970 | declared candidate target differs from runtime physical tile |
| 0x96 | 0xB6 | Bank 8 / 0x1B6 | 0x31B70 | 0x2FB70 | declared candidate target differs from runtime physical tile |
| 0x97 | 0x97 | Bank 8 / 0x197 | 0x31980 | 0x2F980 | declared candidate target differs from runtime physical tile |
| 0x97 | 0xB7 | Bank 8 / 0x1B7 | 0x31B80 | 0x2FB80 | declared candidate target differs from runtime physical tile |
| 0x98 | 0x98 | Bank 8 / 0x198 | 0x31990 | 0x2F990 | declared candidate target differs from runtime physical tile |
| 0x98 | 0xB8 | Bank 8 / 0x1B8 | 0x31B90 | 0x2FB90 | declared candidate target differs from runtime physical tile |
| 0x99 | 0x99 | Bank 8 / 0x199 | 0x319A0 | 0x2F9A0 | declared candidate target differs from runtime physical tile |
| 0x99 | 0xB9 | Bank 8 / 0x1B9 | 0x31BA0 | 0x2FBA0 | declared candidate target differs from runtime physical tile |
| 0x9A | 0x9A | Bank 8 / 0x19A | 0x319B0 | 0x2F9B0 | declared candidate target differs from runtime physical tile |
| 0x9A | 0xBA | Bank 8 / 0x1BA | 0x31BB0 | 0x2FBB0 | declared candidate target differs from runtime physical tile |
| 0xC0 | 0xC0 | Bank 8 / 0x1C0 | 0x31C10 | 0x2FC10 | declared candidate target differs from runtime physical tile |
| 0xC0 | 0xE0 | Bank 8 / 0x1E0 | 0x31E10 | 0x2FE10 | declared candidate target differs from runtime physical tile |
| 0xC1 | 0xC1 | Bank 8 / 0x1C1 | 0x31C20 | 0x2FC20 | declared candidate target differs from runtime physical tile |
| 0xC1 | 0xE1 | Bank 8 / 0x1E1 | 0x31E20 | 0x2FE20 | declared candidate target differs from runtime physical tile |
| 0xC2 | 0xC2 | Bank 8 / 0x1C2 | 0x31C30 | 0x2FC30 | declared candidate target differs from runtime physical tile |
| 0xC2 | 0xE2 | Bank 8 / 0x1E2 | 0x31E30 | 0x2FE30 | declared candidate target differs from runtime physical tile |
| 0xC3 | 0xC3 | Bank 8 / 0x1C3 | 0x31C40 | 0x2FC40 | declared candidate target differs from runtime physical tile |
| 0xC3 | 0xE3 | Bank 8 / 0x1E3 | 0x31E40 | 0x2FE40 | declared candidate target differs from runtime physical tile |
| 0xC4 | 0xC4 | Bank 8 / 0x1C4 | 0x31C50 | 0x2FC50 | declared candidate target differs from runtime physical tile |
| 0xC4 | 0xE4 | Bank 8 / 0x1E4 | 0x31E50 | 0x2FE50 | declared candidate target differs from runtime physical tile |
| 0xC5 | 0xC5 | Bank 8 / 0x1C5 | 0x31C60 | 0x2FC60 | declared candidate target differs from runtime physical tile |
| 0xC5 | 0xE5 | Bank 8 / 0x1E5 | 0x31E60 | 0x2FE60 | declared candidate target differs from runtime physical tile |
| 0xC6 | 0xC6 | Bank 8 / 0x1C6 | 0x31C70 | 0x2FC70 | declared candidate target differs from runtime physical tile |
| 0xC6 | 0xE6 | Bank 8 / 0x1E6 | 0x31E70 | 0x2FE70 | declared candidate target differs from runtime physical tile |
| 0xC7 | 0xC7 | Bank 8 / 0x1C7 | 0x31C80 | 0x2FC80 | declared candidate target differs from runtime physical tile |
| 0xC7 | 0xE7 | Bank 8 / 0x1E7 | 0x31E80 | 0x2FE80 | declared candidate target differs from runtime physical tile |
