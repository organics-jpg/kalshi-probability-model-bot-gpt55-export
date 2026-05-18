# v28 Dual-Lane Strict Replay Accounting Audit

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-11T03:46:04.938176+00:00`
- Audited file: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\probe_v28_dual_lane_own_freeze_watch.py`
- Precheck artifact: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_dual_lane_strict_replay_precheck_latest.json`
- Accounting patch verified: `True`
- Score path read: `strict_replay_sidecar_net_uses_boundary_clock_feature_gate_net`
- Precheck promotion use: `not_promotion_evidence_before_min_sample`
- Precheck windows: `59`

## Checks

| check | status |
|---|---|
| imports `feature_gate_net` | `True` |
| sidecar compaction uses `feature_gate_net(row)` | `True` |
| latest precheck has nonzero sidecar add | `True` |

## Latest Strict Precheck

| policy | settled | W/L | coverage | net | sidecar add | recon | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `post_dual_union_birth_entry_cheap_penalty025_rank_only` | 16 | 13/3 | 88.89% | 59c ($0.59) | 10c ($0.10) | 18.75% | 0 | settled_lt_30, full_loss_cushion_lt_3, does_not_beat_refreshed_live_baseline |

## Interpretation

- This audit verifies the research scorer wiring, not live readiness.
- The strict precheck remains diagnostic until the 30-settled-row own-freeze sample gate is available.
- The main remaining blocker is evidence maturity, not the sidecar PnL accounting path.
