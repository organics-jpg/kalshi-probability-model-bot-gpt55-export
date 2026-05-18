# v28 Successor Live P&L Research Decision Log

## Bootstrap Policy v002

- Policy id: `v28s_live_pnl_midband_no_fade_yes_v019`
- Policy hash: `5bf8d66dbe2b31e01d38abe8a0238e68`
- Decision: `continue_collecting_future_live_rows`
- Reason: the lab can produce policy rows, label joins, fee-aware paired P&L, source checks, capture health, and readiness output.

## Fee Model Note

- Fill model status: `explicit_assumption_report`
- Official fee source URLs are recorded in the fill-model audit.
- Capture health status: `pass_scaffold`

## Problem-Solving Research

- Problem: v018 converted v17's too-cheap YES fade into a narrow 75c-80c expensive-confirmed band, but it still produced no entries over two finalized live-forward markets. Fresh labels showed the earliest tradable fade rows at 65c-74c also won, while later 80s/90s rows remained too expensive or too close to close.
- Implemented: the smallest inspectable replacement keeps the same cross-side fade trigger and one-entry cap, lowers only the YES ask floor from 75c to 65c, and keeps the 80c ceiling. Diagnostic one-entry-per-market replay over joined rows favored the 65c-80c, 5c-signal band over broader 80s/90s expansions: +79c across 14 diagnostic entries and +66c across the two newly labeled v018 primary markets, while 65c-85c/90c variants were roughly flat to negative diagnostically. This is not promotion evidence; it is only the reason to freeze v019 before collecting new primary rows.
- Solution families considered: one-entry-per-market hard exposure cap, risk-constrained or fractional Kelly sizing, conformal risk-controlled abstention, book/FV disagreement confirmation before entry, Brownian-bridge or first-passage recross filters, late-window cheap-tail hazard filters

## Research Sources

- https://arxiv.org/abs/2603.24704
- https://arxiv.org/abs/2208.12084
- https://arxiv.org/abs/2604.11577
- https://arxiv.org/abs/1603.06183
- https://arxiv.org/abs/0708.3562
- https://arxiv.org/abs/0811.2629
- https://aclanthology.org/2021.acl-long.84/
