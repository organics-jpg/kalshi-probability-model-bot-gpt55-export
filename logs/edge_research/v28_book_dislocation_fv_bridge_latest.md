# v28 Book-Dislocation FV Bridge

Research-only; no live bot changes and no orders.

- Freeze UTC: `2026-05-06T14:29:17.965829+00:00`
- Candidate: `book_dislocation_aware_escape_energy`

## Current Read

- diagnostic_existing_false_conviction_freeze: best book_dislocation_escape_energy entries/settled/coverage/net 91/91/80.53097345132744/-638.0c; ask_spikes 24, deep_discounts 21, blockers ['net_not_positive', 'reconstructed_share_gt_35pct'].
- post_freeze_candidate: best book_dislocation_escape_energy entries/settled/coverage/net 74/74/80.43478260869566/-1017.0c; ask_spikes 17, deep_discounts 19, blockers ['net_not_positive', 'reconstructed_share_gt_35pct'].
- Diagnostic results explain direction only; post-freeze rows decide whether the dislocation penalty survives.

## diagnostic_existing_false_conviction_freeze

- Future denominator: `113`

| rank | mode | entries | settled | W/L | coverage | net c | avg edge | avg escape | avg disloc | ask spikes | deep disc | approved/recon | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `book_dislocation_escape_energy` | 91 | 91 | 59/32 | 80.530973 | -638.000000 | 0.088082 | 0.342255 | 0.323958 | 24 | 21 | 8/83 | net_not_positive, reconstructed_share_gt_35pct |
| 2 | `base_escape_energy` | 91 | 91 | 60/31 | 80.530973 | -407.000000 | 0.089383 | 0.343270 | 0.322775 | 26 | 22 | 8/83 | net_not_positive, reconstructed_share_gt_35pct |

## post_freeze_candidate

- Future denominator: `92`

| rank | mode | entries | settled | W/L | coverage | net c | avg edge | avg escape | avg disloc | ask spikes | deep disc | approved/recon | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `book_dislocation_escape_energy` | 74 | 74 | 45/29 | 80.434783 | -1017.000000 | 0.097434 | 0.351954 | 0.333711 | 17 | 19 | 8/66 | net_not_positive, reconstructed_share_gt_35pct |
| 2 | `base_escape_energy` | 74 | 74 | 46/28 | 80.434783 | -822.000000 | 0.097558 | 0.352845 | 0.333183 | 18 | 20 | 8/66 | net_not_positive, reconstructed_share_gt_35pct |
