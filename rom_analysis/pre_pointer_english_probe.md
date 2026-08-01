# English Pre-Pointer Probe

This note records a bounded runtime probe of the English reference IPS. It is
an ownership and reachability result, not release approval.

## Target

- English reference: `C:\tmp\kunio_english_reference.nes`
- English record: ROM offset `0x05BDF`
- English bytes: `88 89 94 85 FF` (`THICK` in the reference code pool)
- Static MMC3 mapping observed: CPU `$9BCF` when the containing 8 KiB PRG
  bank is visible
- Reference record family: pre-pointer text, not the verified pointer-dialogue
  table

## Bounded Results

| Probe | Result | Meaning |
| --- | --- | --- |
| Live CPU-map scan, frames 0-1800 | PASS | `THICK` appeared at CPU `$9BCF` from frame 280 onward while the source bank was mapped. |
| Narrow CPU read watcher, frames 0-1800 | NO_MATCH | The target bytes were not observed as a direct CPU read in the selected route. |
| Menu context probe, frames 0-1906 | UNKNOWN | The route produced a screen/PPU capture, but reads at `$9BD0-$9BD5` returned runtime value `03`, not the English label bytes. |
| Korean patch action | DEFERRED | No pre-pointer byte replacement is authorized until a display path is identified. |

## Interpretation

The English IPS proves that the pre-pointer region contains translated static
labels, but it does not prove that every label is used by the first menu route
or that the region shares the pointer-dialogue renderer. The CPU window is
also bank-switched: a file offset can be visible at one frame and a different
bank can occupy the same CPU address later.

The correct next action is a targeted item/status route or a manual breakpoint
on the relevant screen. Until then, keep this family separate from the
verified direct-low menu labels and relocated pointer dialogue records.

## Reproduction

- `lua/kunio_pre_pointer_scan.lua` scans the four PRG windows without assuming
  a permanent MMC3 mapping.
- `lua/kunio_pre_pointer_targets.lua` and
  `lua/kunio_pre_pointer_window_targets.lua` provide narrow read-watch targets.
- The generated capture folders are local evidence and are intentionally not
  release inputs.
