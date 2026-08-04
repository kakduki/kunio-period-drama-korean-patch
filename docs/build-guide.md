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
python tools/font_builder.py --characters "쿠니오" --output "$env:TEMP\kunio-font.bin"
python tools/insert_text.py --rom "rom\Kunio Kun no Jidaigeki Dayo Zenin Shuugou! (J).nes" --output-dir "$env:TEMP\kunio-pointer-candidate"
```

These commands produce analysis or candidate artifacts only. They do not create a final release ROM.
