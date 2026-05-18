# Paired Sidecar Slice Refresh

Research-only maintenance refresh for the predeclared paired sidecar slice. By default it does not collect new snapshots, place orders, or touch live bot state.

## Summary

- generated_utc: `2026-05-13T02:02:12+00:00`
- promotion_allowed: `False`
- hypothesis_id: `blend_v28_w20_time_gt_600s_v1`
- model: `blend_v28_online_lr010_w20`
- slice: `time_to_close_band=600s_plus`
- locked_after_utc: `2026-05-12T14:44:16+00:00`
- collect_requested/status: `False` / `not_requested`
- label_refresh_requested/status: `True` / `sidecar_cycle_ready_for_external_promotion_verifier`
- aggregate rows / markets: `1410` / `68`
- pending manifests / enriched rows: `0` / `0`
- next pending market close UTC: ``
- seconds until next pending close: `None`
- online prepared rows / markets: `1410` / `68`
- slice report count: `5`
- slice fresh rows / markets: `504` / `28`
- slice rows / markets: `432` / `24`
- slice selected count: `177`
- slice selected PnL cents: `450.5`
- slice promotion_safe: `False`
- goal audit refreshed/complete: `False` / `False`

## Slice Reports

| hypothesis | model | fresh rows/markets | slice rows/markets | selected | selected pnl c | top EV pnl c | safe |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `blend_v28_w20_time_gt_600s_v1` | `blend_v28_online_lr010_w20` | `504` / `28` | `432` / `24` | `177` | `450.5` | `448.5` | `False` |
| `blend_v28_w05_time_gt_600s_v1` | `blend_v28_online_lr010_w05` | `432` / `24` | `378` / `21` | `144` | `1460.0` | `355.0` | `False` |
| `v28_control_time_gt_600s_v1` | `v28` | `432` / `24` | `378` / `21` | `153` | `1516.5` | `748.0` | `False` |
| `blend_v28_w15_candidate_v28_gap_05_15pp_v1` | `blend_v28_online_lr010_w15` | `342` / `19` | `35` / `14` | `14` | `-31.7` | `67.8` | `False` |
| `v28_control_candidate_v28_gap_05_15pp_v1` | `v28` | `342` / `19` | `35` / `14` | `16` | `-6.7` | `-64.2` | `False` |

## Pending Slice Preview

| hypothesis | model | pending fresh rows/markets | pending slice rows/markets | outcome-free |
| --- | --- | ---: | ---: | --- |
| `blend_v28_w20_time_gt_600s_v1` | `blend_v28_online_lr010_w20` | `0` / `0` | `0` / `0` | `True` |
| `blend_v28_w05_time_gt_600s_v1` | `blend_v28_online_lr010_w05` | `0` / `0` | `0` / `0` | `True` |
| `v28_control_time_gt_600s_v1` | `v28` | `0` / `0` | `0` / `0` | `True` |
| `blend_v28_w15_candidate_v28_gap_05_15pp_v1` | `blend_v28_online_lr010_w15` | `0` / `0` | `0` / `0` | `True` |
| `v28_control_candidate_v28_gap_05_15pp_v1` | `v28` | `0` / `0` | `0` / `0` | `True` |

## Read

- `slice_promotion_safe=True` would still be research evidence only; the live bot remains untouched until the broader goal audit clears.
- Post-lock rows are the only rows counted by the locked slice evaluator.
