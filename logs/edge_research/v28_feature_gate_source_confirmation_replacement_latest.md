# v28 Feature-Gate Source Confirmation Replacement

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:15:14.093669+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Replacement freeze UTC: `2026-05-07T09:04:18.363119+00:00`

## Interpretation

- Research-only source-confirmation replacement audit; no live bot changes or orders.
- The rule is observable, but the exit overlay estimate has a market/side entry-price basis caveat.
- Diagnostic best adjusted net 550.25c, row source share 0.36363636363636365, replacements 2, blockers ['row_reconstructed_share_gt_35pct', 'diagnostic_prefreeze', 'rescue_overlay_not_independently_frozen', 'exit_artifact_market_side_basis_caveat', 'diagnostic_replacement_audit'].

## Rule

- `replace_when`: selected row has abs_d<0.65, ask<0.65, p_side<0.85
- `replacement_required`: same market/side row with abs_d>=0.95, ask>=0.75, p_side>=0.88, recross<=0.35
- `rank`: highest p_side, abs_d, ask, then lower recross

## Lanes

| lane | strict | denominator | replacements | base source | repl source | base entry net | repl entry net | best adjusted rescue net | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `diagnostic_prefreeze_context` | False | 82 | 2 | 0.394 | 0.364 | 408.750 | 371.750 | 550.250 | row_reconstructed_share_gt_35pct, diagnostic_prefreeze, rescue_overlay_not_independently_frozen, exit_artifact_market_side_basis_caveat, diagnostic_replacement_audit |
| `post_confirmation_replacement_birth` | True | 33 | 0 | 0.414 | 0.414 | 93.750 | 93.750 | 317.250 | settled_lt_30, row_reconstructed_share_gt_35pct, exit_artifact_market_side_basis_caveat, post_birth_replacement_watch |

## diagnostic_prefreeze_context Replacements

| market | old source | old net | old abs_d | old ask | old p_side | new source | new net | new abs_d | new ask | new p_side | weighted delta |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY062130-30 | rejected_actionable | -65.000 | 0.624 | 0.610 | 0.768 | approved_entry | -78.000 | 0.999 | 0.760 | 0.888 | -13.000 |
| KXBTC15M-26MAY062315-15 | rejected_actionable | 39.000 | 0.576 | 0.570 | 0.752 | approved_entry | 15.000 | 1.139 | 0.840 | 0.916 | -24.000 |

## post_confirmation_replacement_birth Replacements

| market | old source | old net | old abs_d | old ask | old p_side | new source | new net | new abs_d | new ask | new p_side | weighted delta |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
