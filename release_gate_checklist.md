# Release Gate Checklist

Status: **NOT_READY_FOR_RELEASE**

| gate | status | evidence / reason |
| --- | --- | --- |
| Base ROM identity | PASS | MD5 matches the verified Japanese base. |
| English structural reference | PASS | Recorded IPS SHA-256; used only for structure. |
| Scoped three-record build | PASS | 129 declared changed spans; 0 escaped bytes; range guard protects pointer 185. |
| Bounded boot and target reads | PASS | 182 frame 883 `32/32`; 183 frame 1093 `25/25`; 184 frame 1399 `23/23`; all `lua_done`. |
| Native Korean readability | PASS | Three native 16x16 opening screenshots reviewed. |
| Japanese source context | PASS | Pointer 184 base-ROM capture is recorded; prior opening records already had context evidence. |
| Menu, status, item/shop, event/boss renderers | UNKNOWN | Separate renderer/context families require their own target routes. |
| Release-wide Korean glyph capacity | UNKNOWN | Current 20-glyph allocation is scene-local. |
| Full translated script | NOT_STARTED | Bulk translation is intentionally blocked until family-by-family evidence exists. |
| Release package | BLOCKED | Requires all high-risk families and release checks to pass. |

Development uses soft gates, so static or exploratory candidates may be built
without manual visual evidence. Release promotion requires the unresolved
high-risk rows to become `PASS`.
