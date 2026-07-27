# Main Menu Cursor Probe

Status: **UNKNOWN**

A bounded post-template probe held `right` for frames 1900-1911 and captured
frame 1925. The original background selector tile (`0x7E` at row 25, column 1)
was absent in that capture, but the OAM dump did not expose a stable replacement
cursor position. The change may include selector blinking or a state transition.

This result does not alter the candidate ROM or invalidate the main-menu soft-gate
PASS. Cursor movement and menu return remain release-gate work, to be tested with
another explicitly targeted state capture rather than repeated gameplay automation.
