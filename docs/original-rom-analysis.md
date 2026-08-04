# Original ROM Analysis

## Format

The confirmed input is an iNES NES/Famicom image with a 16-byte header and no
trainer. Header bytes are:

```text
4E 45 53 1A 08 10 41 00 00 00 00 00 00 00 00 00
```

This declares mapper 4 (MMC3), vertical mirroring, eight 16 KiB PRG banks,
and sixteen 8 KiB CHR banks. The file size is exactly the declared 262,160
bytes.

## Hashes

| algorithm | value |
| --- | --- |
| CRC32 | `014D63C9` |
| MD5 | `0d406a85285b4de8468f0dab6aad5fe5` |
| SHA-1 | `4338c3001c5e2bf5fad0f282bfee23b79e0ad959` |
| SHA-256 | `54d79f15f60a32123e95fbf20661128a13ee0eee1941e0ff98ba7bb54343e23a` |

## Text Ownership

The English reference identifies these distinct families:

| family | ROM range | observed ownership |
| --- | --- | --- |
| renderer support / name-table setup | `0x05288-0x052C8` and `0x0561B-0x056AF` | fixed labels and pre-pointer text |
| pre-pointer text | `0x056BC-0x05D54` | FF-delimited labels and UI strings |
| pointer table | `0x05DD4-0x05FC4` | 248 little-endian CPU pointers |
| pointer dialogue | `0x05FC4-0x07767` | variable records with control bytes |
| growth UI | `0x07894-0x078AB` | separate UI renderer |
| menu labels | `0x07FB6-0x0800F` | menu/label expansion, not assumed to be code |

These are evidence-backed regions from the base/reference diff. A byte that
looks like text outside a declared owner is not patched automatically.

## Encoding and Controls

The verified dialogue path uses game tile codes rather than Shift-JIS. English
reference dialogue letters occupy `0x81-0x9A` and render through CHR Bank 7
tiles `0x181-0x19A`, with a paired lower tile at `+0x20`. Controls observed in
the records include `0x00`, `0xBB`, `0xCA`, `0xF8`, and `0xFF`. They are kept as
explicit tokens by the compiler.

Japanese byte decoding is therefore **partly unresolved**. The current
catalog stores Japanese bytes as tokens until a runtime source-read and PPU
context proves their meaning.

## Runtime Evidence

Bounded FCEUX probes prove opening dialogue, page lifecycle recovery, menu
source chains, Items action output, and gameplay entry. A natural enemy-clear
to boss route is not proven. The English reference and Korean candidate show
the same bounded combat-state trace, so additional free-running frames are not
treated as evidence.

Detailed raw evidence remains in `rom_analysis/` and the probe sources are in
`lua/`.


## Address and Integrity Rules

- The exact dump identity is established by the filename plus the recorded hashes. A cartridge revision beyond that dump identity is not inferred.
- PRG file offsets use the iNES header and PRG-bank boundaries. MMC3 runtime bank selection must be recorded alongside any CPU address.
- The confirmed pointer family is two-byte little-endian data in the declared Bank 1 CPU window. The working mapping uses CPU $8000 to file offset 0x4010; mapper state remains part of the record contract.
- Observed 0x00, 0xBB, 0xCA, 0xF8, and 0xFF values are control candidates, not universal terminators. Each record keeps them explicit until a runtime source-read proves their role.
- The iNES header has no general ROM checksum field used by this project. Cryptographic hashes are the integrity gate; generated IPS files are verified by reapplication and candidate hashes.
- No compression or decompression routine has been proven for the declared text families. Unresolved regions remain unpatched.
