# OpenEmu 2.4.1 — macOS 12 runtime verification

## Conclusion

OpenEmu 2.4.1 is a working **visual NES runtime** on this Intel macOS 12.7.6 host. The Japanese `kunio.nes` ROM imported and its rendered title frame was captured.

This replaces neither FCEUX Lua automation nor emulator debugger memory/nametable tracing. It is suitable now for visible-scene baseline capture and manual save-state work.

## Source and install

- Publisher release: `https://github.com/OpenEmu/OpenEmu/releases/download/v2.4.1/OpenEmu_2.4.1.zip`
- Downloaded ZIP SHA-256: `521ca1305c012d38f6f907f50399fefbf4e45a9bb8d9d4063157ffca78b217d4`
- Intel executable minimum OS from `LC_BUILD_VERSION`: `10.14.4`
- Installed app: `/Users/jeongbeomjun/Applications/OpenEmu-2.4.1.app`
- Target ROM: `rom/kunio.nes`

## Render verification

1. OpenEmu initial onboarding completed with the default selected cores.
2. The target ROM was imported. OpenEmu displayed: `The game “kunio” was imported.`
3. Selecting **Play Game** created a live `OpenEmuHelperApp` process and rendered the title screen.
4. The screen visibly shows the Japanese title logo and `© 1991 TECHNOS JAPAN CORP.`

## Evidence files

| File | SHA-256 | Meaning |
|---|---|---|
| `rom-import-confirmed.png` | `573825f4d767f0e929b3159f42a50b68c208fc01c2a124fefdeb695c502206c0` | ROM import confirmation dialog |
| `japanese-rom-title-rendered.png` | `11f3b665a5d19ffbd364223b3f81c35e2997085e60a5c4818fb291afa660b4db` | Live Japanese title-screen render |

## Boundary

Do not claim repeatable scene timing, RAM byte mapping, nametable data, or trace artifacts from this OpenEmu proof. Those still require a debugger-capable route or an independently designed visual capture protocol.
