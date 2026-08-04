# Translation Style Guide

- Translate from the Japanese source when the scene is confirmed. Use the English patch only to understand structure, width, and control flow.
- Keep names consistent with `glossary.csv` and do not silently change a confirmed name.
- Prefer concise natural Korean because the original renderer has fixed line and page limits.
- Preserve control codes, wait markers, speaker cues, and terminators exactly unless a test proves a controlled replacement.
- Avoid adding punctuation or spacing that causes a line to overflow its measured tile width.
- Record uncertainty in `notes` and leave the row `UNKNOWN`; do not fill gaps by guessing from byte patterns.
- UI labels should be short and action-oriented. Dialogue may be natural Korean, but the speaker and scene must be known first.
