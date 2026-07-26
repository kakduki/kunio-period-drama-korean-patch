# Release Gate Checklist

Status: **NOT_READY_FOR_RELEASE**

| gate | status | evidence / reason |
| --- | --- | --- |
| Base ROM identity | PASS | MD5 matches the verified Japanese base. |
| English structural reference | PASS | Official IPS SHA-256 matches the recorded reference. |
| Scoped two-record build | PASS | 126 declared changed spans; 0 escaped bytes. |
| Bounded boot and target reads | PASS | Pointer 182 frame 883, 33/33; pointer 183 frame 1095, 25/25; both `lua_done`. |
| Native Korean readability | PASS | Two opening screenshots reviewed at native 16x16. |
| Pointer 183 own screen | PASS | Independent bounded capture at frame 1095 with matching relocated record. |
| Menu, status, item, event renderers | UNKNOWN | Separate renderer/context families. |
| Release-wide Korean glyph capacity | UNKNOWN | Current 19-glyph allocation is scene-local. |
| Full translated script | NOT_STARTED | No bulk translation is authorized. |
| Release package | BLOCKED | Requires all high-risk context families and release checks. |

Development candidates may continue through soft gates. Release promotion
requires the unresolved high-risk rows to become PASS.
