# Opening Dialogue Korean Proof Candidate

Status: **CANDIDATE_BUILT_NOT_VISUALLY_VERIFIED**

This is a one-record proof build, not a release patch. It deliberately
updates a real opening dialogue record at its original pointer and length.

## Source

- Pointer index: `182`
- Pointer ROM offset: `0x05F40` (unchanged)
- Record ROM offset: `0x071B6`
- Japanese source: くにまさ『はやくしねぇかい！ ぶんぞう親分がてぇへんなんでえ！』
- English reference: KUNIO: HURRY, SLUG! MR. BUNZO'S IN TROUBLE!
- Korean proof: 쿠니마사: 서둘러! 분조 두목이 큰일이야!

## Safety Invariants

- Original and candidate record length: `37` bytes.
- No dialogue pointer table bytes change.
- Font changes are restricted to Bank 7 physical tiles `0x181-0x191` with reserved `0x18A-0x18B` skipped.
- Changed-byte spans: `16`; escaped bytes: `0`.

## Result

- Base MD5: `0d406a85285b4de8468f0dab6aad5fe5`
- Candidate MD5: `b7e0d83c820f4368646ce42e171e97f5`
- IPS: `C:\Users\kakdu\OneDrive\문서\자산관리\kunio-period-drama-korean-patch\output\kunio_period_drama_korean_opening_dialogue_proof.ips`
- ROM: `C:\Users\kakdu\OneDrive\문서\자산관리\kunio-period-drama-korean-patch\output\kunio_period_drama_korean_opening_dialogue_proof.nes`

Visual verification is still required, but it must target the opening scene
directly; this candidate must not be used as a reason to resume blind autoplay.
