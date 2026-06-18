# Release Gate Action Plan

This queue is generated from `release_gate_checklist.json`. It converts open FAIL/UNKNOWN gates into the next concrete evidence tasks.

## Summary

- Open gates: **3**
- Actions: **3**
- Next gate: `release-included visual proof`
- Release ready: `False`

## Actions

| priority | gate | status | failure class | phase | target | evidence needed | command |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 10 | release-included visual proof | FAIL | VISUAL_PROOF_PENDING | `primary_v042_visual_review` | `0x07227` | visible-screen capture and primary visual review confirmation | `python scripts/record_primary_visual_review.py 0x07227 --confirm --screen-context "look for a katana/weapon item label visible"` |
| 20 | high-risk/quarantined visual proof | FAIL | HIGH_RISK_VISUAL_PROOF_PENDING | `katana_quarantine_visual_proof` | `0x05644, 0x06295, 0x0631C, 0x0635A, 0x07227` | Katana/item-list screen where the intended row is visibly readable | `python scripts/record_primary_visual_review.py 0x07227 --confirm --screen-context "katana/weapon item label visible"` |
| 30 | shortened padding rule acceptance | UNKNOWN | PADDING_RULE_UNPROVEN | `padding_rule_acceptance` | `ROM+0x071A4 Chikara -> 힘` | strict PPU/visual acceptance for one of 5 v05 padding strategies | `python scripts/audit_padding_experiment_pipeline.py` |
