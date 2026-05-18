# v28 Dual-Lane Live-Readiness Gate

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-11T03:47:38.018343+00:00`
- Decision: `no_live_test`
- Freeze UTC: `2026-05-07T13:00:17.363339+00:00`
- Freeze local time: `2026-05-07T09:00:17.363339-04:00`
- Live baseline: `-256c ($-2.56)`
- Next action: Review missing score gates on the own-freeze union rows.

## Sample And Collection

- Possible 15m windows since freeze: `347`
- Windows remaining to 30-row gate: `0`
- Earliest possible 30-window local time: `2026-05-07T16:30:17.363339-04:00`
- Collection blocker: `none`
- Post-freeze events/entries/settled/pending: `2842` / `26` / `26` / `0`

## Evidence Layers

| layer | status | entries | W/L | coverage | net | recon | cushion | note |
|---|---|---:|---:|---:|---:|---:|---:|---|
| diagnostic pre-own-freeze | discovery only | 83 | 68/15 | 82.18% | 1842c ($18.43) | 21.69% | 18 | prior rows found the union; not live-readiness proof |
| strict/post context before own-freeze | context only | 65 | 51/13 | 84.42% | 464c ($4.64) | 33.85% | 4 | useful but still born before exact union freeze |
| post-freeze sidecar feature preview | collection health only | 12 | 11/1 | 66.67% | 304c ($3.04) | 0.00% | 3 | feature availability and early row-shape check only |
| post-freeze primary sizing-pocket proxy | risk proxy only | 16 | 4/12 | 88.89% | -40c ($-0.40) | 100.00% | 0 | sizing-pocket proxy, not actual primary selection |

- Preview observations/features: `977` observations across `18` markets; availability `{'abs_d_sigma': 977, 'ask_prob': 977, 'raw_edge': 977, 'recross_hazard_score': 977}`.
- Primary proxy note: This is only the observable sizing-pocket proxy. The actual primary lane is selected by the parent-fill composer before this pocket can shrink size.

## Own-Freeze Gate Rows

| policy | settled | W/L | coverage | net | delta live | recon | cushion | live ready | missing gates |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| `post_dual_union_birth_entry_cheap_penalty025_rank_only` | 14 | 12/2 | 77.78% | 49c ($0.49) | 305c ($3.05) | 14.29% | 0 | `False` | settled_lt_30, full_loss_cushion_lt_3 |
| `post_dual_union_birth_bridge_cheap_penalty025_rank_only` | 14 | 12/2 | 77.78% | 49c ($0.49) | 305c ($3.05) | 14.29% | 0 | `False` | settled_lt_30, full_loss_cushion_lt_3 |

## Interpretation

- This is the dual-lane-only readiness gate.
- Pre-own-freeze rows explain why the dual lane was created but cannot prove live readiness.
- The shadow feature preview checks collection health only; it is not promotion evidence.
- Diagnostic dual-lane PnL is not promotion evidence; only own-freeze rows count.
- The global controlled live-test gate remains the final arbiter before any live trade test.
