# v28 Recross-Escape Sample Plan

Forward-evidence runway for the p52 recross-escape selector plus +5pp FV overlay.

- Candidate: `p52_recross_escape_opp240_oppedge5_keep_plus05_probability`
- Freeze timestamp UTC: `2026-05-06T00:57:12.867086+00:00`
- Forward denominator: `146`
- Excluded in-progress markets: `1`

## Selector Evidence

- Raw p52 baseline entries/settled/W-L/net: `143/143/83-60/-947.000000c`
- Recross selector entries/settled/W-L/net: `143/143/84-59/-753.000000c`
- Coverage: `97.945205`
- Net/Brier vs raw p52: `194.000000c` / `-0.002374`
- Modes: `{'base': 117, 'danger_follow_opposite': 5, 'danger_keep_high_edge': 2, 'danger_no_opposite_keep': 19}`

## FV Overlay Evidence

- Raw probability settled/Brier/logloss: `143` / `0.220043` / `0.621369`
- +5 probability settled/Brier/logloss: `143` / `0.228642` / `0.636169`
- +5 deltas Brier/logloss/ECE: `0.008599` / `0.014801` / `0.038587`

## Remaining Runway

- Settled rows to 30: `0`
- Current pending rows: `0`
- Additional settled rows after pending to 30: `0`
- Future clean denominator to 30: `0`
- Actual entries needed for simulated share <=35%: `240`
- Misses needed to reduce current high coverage to <=90%: `13`
- Miss budget after 30 before coverage <70%: `58`

## Current Blockers

- FV blockers: `coverage_too_high, net_not_positive`
- Execution blockers: `simulated_share_gt_0.35, coverage_too_high, net_not_positive`

## Acceptance Conditions

- at least 30 settled forward rows
- coverage remains between 70% and 90%
- net P&L stays positive versus raw p52 on the same future denominator
- plus05 Brier and logloss deltas versus raw probability remain negative
- simulated/rejected-actionable share falls to <=35% before any live promotion
