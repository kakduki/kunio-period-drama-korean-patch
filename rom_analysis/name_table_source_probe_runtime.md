# Name-Table Source Probe Runtime

- Runtime status: PASS_SOURCE_OWNER_AND_PPU
- Visual status: PASS_SCREEN_CAPTURE_AVAILABLE
- Release status: NOT_READY
- Target PPU addresses: 2043, 2044, 2045, 2046
- Base sequence: 88969F8B
- Test sequence: 81828182
- Candidate test frames: 1886, 1906, 1914, 1918, 1922, 1926, 1930, 1934, 1938, 1942, 1946, 1950, 1954, 1971, 1975
- Candidate original frames: -
- Owner hit(s): 0x3FB32

## Probe Results

| offset | test frames | original frames | result |
| --- | --- | --- | --- |
| 0x0561B | - | 1886, 1906, 1914, 1918, 1922, 1926, 1930, 1934, 1938, 1942, 1946, 1950, 1954, 1971, 1975 | NO_MATCH |
| 0x071B6 | - | 1886, 1906, 1914, 1918, 1922, 1926, 1930, 1934, 1938, 1942, 1946, 1950, 1954, 1971, 1975 | NO_MATCH |
| 0x071DF | - | 1886, 1906, 1914, 1918, 1922, 1926, 1930, 1934, 1938, 1942, 1946, 1950, 1954, 1971, 1975 | NO_MATCH |
| 0x071F0 | - | 1886, 1906, 1914, 1918, 1922, 1926, 1930, 1934, 1938, 1942, 1946, 1950, 1954, 1971, 1975 | NO_MATCH |
| 0x07242 | - | 1886, 1906, 1914, 1918, 1922, 1926, 1930, 1934, 1938, 1942, 1946, 1950, 1954, 1971, 1975 | NO_MATCH |
| 0x07267 | - | 1886, 1906, 1914, 1918, 1922, 1926, 1930, 1934, 1938, 1942, 1946, 1950, 1954, 1971, 1975 | NO_MATCH |
| 0x07288 | - | 1886, 1906, 1914, 1918, 1922, 1926, 1930, 1934, 1938, 1942, 1946, 1950, 1954, 1971, 1975 | NO_MATCH |
| 0x072F7 | - | 1886, 1906, 1914, 1918, 1922, 1926, 1930, 1934, 1938, 1942, 1946, 1950, 1954, 1971, 1975 | NO_MATCH |
| 0x3FB32 | 1886, 1906, 1914, 1918, 1922, 1926, 1930, 1934, 1938, 1942, 1946, 1950, 1954, 1971, 1975 | - | OWNER_MATCH |

## Interpretation

- The English patch's static Bank 1 name-table block is not sufficient to identify the live natural-route source.
- The bounded differential probe identifies physical ROM offset 0x3FB32 as the only tested owner of the target sequence.
- The corrected candidate changes that sequence to 81 82 81 82 and uses CHR Bank 7 tiles 0x181-0x184 for the test glyphs.
- The captured screen is evidence for one renderer context only; release-wide translation remains open.
