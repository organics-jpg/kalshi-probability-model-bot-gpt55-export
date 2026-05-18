# v28 Dual-Lane Live-Readiness Runway

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-11T03:47:38.120642+00:00`
- Decision: `no_live_test`
- Freeze UTC/local: `2026-05-07T13:00:17.363339+00:00` / `2026-05-07T09:00:17.363339-04:00`
- Live baseline: `-256c ($-2.56)`
- Strict replay status: `due_now_or_running`
- Earliest 30-window local time: `2026-05-07T16:30:17.363339-04:00`

## Runway

- Windows remaining to minimum sample: `0`
- Own-freeze settled rows still needed: `16`
- At 30 rows, max reconstructed/rejected rows allowed: `10`
- Net needed for full-loss cushion gate: `251c ($2.51)`
- Net needed to beat refreshed live baseline: `0c ($0.00)`
- Hard blockers: `own_freeze_settled_lt_30, own_freeze_full_loss_cushion_lt_3`

## Collection

- Post-freeze events/entries/markets: `2842` / `26` / `15`
- Settled/pending exit-clock rows: `26` / `0`

## Preview Reads

| preview | entries | settled | W/L | coverage | net | avg settled | recon | neg edge | ineligible | cushion | read |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| post-freeze sidecar feature preview | 12 | 12 | 11/1 | 66.67% | 304c ($3.04) | 25c ($0.25) | 0.00% | 0 | 0 | 3 | `clean_approved_positive_preview` |
| post-freeze primary sizing-pocket risk proxy | 16 | 16 | 4/12 | 88.89% | -40c ($-0.40) | -2c ($-0.03) | 100.00% | 11 | 16 | 0 | `source_quality_risk_preview` |

## Interpretation

- This is a runway report, not a live-test approval.
- The dedicated dual-lane watch loop is keeping the inputs fresh while the strict own-freeze scorer waits for the sample clock.
- The sidecar preview is the constructive signal right now; the primary sizing-pocket proxy is a caution flag, not the actual parent-fill selection.
- A live-test review cannot start until the own-freeze promotion score has at least 30 settled strict-forward rows and clears every gate.
