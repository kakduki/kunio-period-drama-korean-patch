

# Opening Pointer 185 Base Probe

## Contract

- Base: Japanese ROM MD5 `0d406a85285b4de8468f0dab6aad5fe5`
- Pointer table entry: `PTR-185`, ROM `0x05F46`
- Base record: ROM `0x07208`, CPU `$B1F8-$B206`, PRG Bank 1
- Expected source bytes: `85 8A 94 BB 81 B4 CA 00 8A 99 9B 94 9A CB FF`
- Route: proven title/menu path plus exactly three bounded `B` acknowledgement windows at frames `900-909`, `1110-1119`, and `1520-1529`
- Frame ceiling: `1900`
- State writes: none

## Result

The bounded FCEUX run produced:

```text
frame=1691
registered=15
source-read hits=15
active_expected_match=true
target_match=true
screenshot=true
final_reason=lua_done
```

The source record is therefore `PASS` for pointer ownership, PRG-bank context,
and bounded opening-route reachability. The Japanese source semantics are still
represented by the reviewed pointer draft (`오코토 이 사람은`) and English
structural reference; the native Korean visual gate remains `UNKNOWN` until a
Korean candidate capture is reviewed.

Raw artifacts were produced under `C:\tmp\opening_ptr_185_base_probe`.
