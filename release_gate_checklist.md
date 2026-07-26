# Release Gate Checklist

Status: **NOT_READY_FOR_RELEASE**

| gate | status | evidence / reason |
| --- | --- | --- |
| Base ROM identity | PASS | MD5 matches the verified Japanese base. |
| English structural reference | PASS | Official IPS SHA-256 matches the recorded reference. |
| Scoped pointer-182 build | PASS | 106 declared changed spans; 0 escaped bytes. |
| Bounded boot and target reads | PASS | Frame 883, 38/38 matching reads, lua_done. |
| Native Korean readability | PASS | One opening screenshot reviewed at 16x16. |
| Pointer 183 own screen | UNKNOWN | Static relocation only; no independent capture. |
| Menu, status, item, event renderers | UNKNOWN | Separate renderer/context families. |
| Release-wide Korean glyph capacity | UNKNOWN | Current 15-glyph allocation is scene-local. |
| Full translated script | NOT_STARTED | No bulk translation is authorized. |
| Release package | BLOCKED | Requires all high-risk context families and release checks. |

Development candidates may continue through soft gates. Release promotion
requires the unresolved high-risk rows to become PASS.
