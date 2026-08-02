# Pre-Pointer Expansion Runtime Gate

- Result: FAIL.
- Failure class: ROUTE_REGRESSION_OR_FALSE_POSITIVE_DATA_OWNERSHIP.
- Candidate MD5: 0ce9eba51a46ec437aacdda25576b7d5.
- Candidate build changed 22 additional rows and allocated 27 new glyphs.

| run | unique screens | combat evidence | final reason |
| --- | ---: | --- | --- |
| baseline pointer-owner candidate | 24 | True | lua_done |
| expanded pre-pointer candidate | 5 | False | lua_done |

## Decision

Keep the existing pointer-owner candidate as the runnable baseline; quarantine this expansion until each row has runtime ownership evidence.

The failed run is evidence that fixed FF-delimited bytes are not automatically safe text. The next promotion unit must have a source-owner read and screen-context match before it is included in the runnable candidate.
