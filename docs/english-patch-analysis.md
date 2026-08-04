# English Patch Analysis

## Reference Identity

| item | value |
| --- | --- |
| patch | `TSe-v10.ips` reference IPS |
| format | IPS |
| patch size | 15,054 bytes |
| patch CRC32 | `AD38FC51` |
| patch MD5 | `a2e39323e9a94a5fdb4716b2eb533db3` |
| patch SHA-1 | `05b3be449ed1e9a5c294550c4bf6e830bc5b6bb6` |
| patch SHA-256 | `cb6ea2fdbf82e974c474f4ea0d489f7c65647c94de899caf2a6b8c089f202dad` |
| required base MD5 | `0d406a85285b4de8468f0dab6aad5fe5` |
| IPS records | 99 |
| changed bytes | 12,582 |
| changed PRG / CHR bytes | 10,295 / 2,286 |
| ROM size change | none |

## Changed Areas

The reference changes renderer support, pre-pointer text, the 248-entry
pointer table, pointer records, growth UI, menu labels, and 181 physical CHR
tiles. The complete range map is in
`rom_analysis/english_patch_implementation_map.md`; record-level data is in
`rom_analysis/english_patch_record_map.csv`.

## What the Reference Solves

1. Variable-length pointer records are relocated and their little-endian
   pointers are updated.
2. English dialogue codes `0x81-0x9A` are paired with CHR Bank 7 tiles
   `0x181-0x19A` and their lower tiles.
3. Non-letter control tokens are preserved while payload text changes.
4. Pre-pointer, menu, and pointer renderers are treated as separate families.

The runtime CPU bytes at `$8205-$820C` are identical between Japanese,
English, and the current Korean candidate (`85 11 B1 07 45 1E 85 12`). This
supports a data/pointer/font/renderer ownership model rather than a wholesale
gameplay rewrite.

## Korean Reuse Decision

Reusable: pointer relocation, control-skeleton preservation, paired dialogue
tiles, renderer-family separation, and changed-byte/IPS audits.

Not copied: English text, English-applied ROM data, unverified code bytes, or
a global Korean font overwrite. Korean uses a catalog allocator, appended
development CHR pages, and isolated pools where mapper evidence requires it.
Rows that overflow a proven pool are quarantined.

## Limits

The English patch does not provide a stage warp or boss-clear cheat. Identical
bounded runs of the English reference and Korean candidate both ended with
`lua_done` at frame 3,600, 11 unique screens, and the same `$7A02` decrement
trace, with no confirmed boss transition.


## Attribution and Reuse

- Reference title: Technos Samurai: Downtown Special v1.00 / TSe-v10.ips.
- Patch creator: not identified in the local IPS metadata; do not infer authorship from byte changes.
- Source references are recorded in om_analysis/english_patch_reference.md.
- License and reuse terms: not established from the local file. This repository uses the IPS only as a local structural reference and does not include its patched ROM, source code, graphics, or full English script.
- The Korean implementation is rebuilt from the verified Japanese base with independent data, font, and patch generation.
