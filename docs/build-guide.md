# Build Guide

The build starts from a clean, legally owned Japanese base ROM. It never modifies the input in place and never requires the original ROM or an English-applied ROM to be committed.

## Minimal reproducible build

```powershell
python build.py --input "rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" --output "build\korean_test_game.nes" --force
```

The default IPS is the current pointer candidate patch. The command writes a JSON report beside the output. A default build is expected to reproduce the known candidate hash; a custom IPS is still recorded as a development candidate and is not release approval.

## Development tools

```powershell
python tools/extract_text.py --rom "rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes"
python tools/compare_original_english.py --rom "rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" --ips "tools\reference\TSe-v10.ips"
python tools/font_builder.py --codepoints CFE0,B2C8 --output "$env:TEMP\kunio-font.bin"
python tools/insert_text.py --rom "rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" --output-dir "$env:TEMP\kunio-pointer-candidate"
```

These commands produce analysis or candidate artifacts only. They do not create a final release ROM.

## Analysis Tools

Use the analysis wrappers with an external temporary output directory. They report evidence and do not promote unresolved bytes to patchable text.

- apply_reference_patch.py: safe external IPS copy
- binary_diff.py: JSON, CSV, and Markdown changed-region report
- find_changed_regions.py: contiguous span report
- string_scanner.py: unresolved byte candidates
- pointer_scanner.py: explicit little-endian bank-context table
- font_region_analyzer.py: CHR and trailing expansion report
