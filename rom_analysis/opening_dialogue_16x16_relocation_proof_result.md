# Opening Dialogue Relocation Proof Result

Status: **PRIMARY_RECORD_PASS_NEIGHBOR_RUNTIME_UNKNOWN**

| check | result | evidence |
| --- | --- | --- |
| Base ROM identity | PASS | MD5 `0d406a85285b4de8468f0dab6aad5fe5` |
| Candidate build scope | PASS | `88` changed spans; `0` escaped bytes |
| Pointer 182 runtime record | PASS | 45 of 45 target reads match `$B1A6-$B1D2` |
| Bounded emulator completion | PASS | frame 883, `lua_done` |
| Primary opening screen | PASS | readable 16x16 Korean text; no visible background/UI damage |
| Pointer 183 static preservation | PASS | `$B1CB` -> `$BFE6`; original 21-byte record copied to ROM `0x07FF6` |
| Pointer 183 native screen | UNKNOWN | this capture intentionally stops before that later dialogue context |

The candidate ROM is local and ignored. The checked-in evidence is the catalog,
builder, target table, reports, screenshot, and capture metadata. The English
patch supplies structural reference only; it is not redistributed or applied as
a Korean translation source.

The next proof must not extend the opening autoplay duration. It should reach
pointer 183 through a deterministic context route, save state, or debug state
and then perform a separate bounded capture.
