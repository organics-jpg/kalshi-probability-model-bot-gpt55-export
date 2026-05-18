# v28 Feature-Gate Coverage Size-Shrink Runway

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:06:11.865191+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Refreshed live net: `-463c`

## Interpretation

- Runway is count-gate math only; it does not promote the candidate or prove future PnL.
- post_feature_freeze_entry: no tested clean-row scenario clears count gates.
- post_feature_freeze_bridge: no tested clean-row scenario clears count gates.

## post_feature_freeze_entry

- Policy: `repair_eighth`
- Current entries/denominator: `66/82`
- Current W/L/net/coverage: `54/12` / `423.500c` / `80.488%`
- Row/exposure reconstructed share: `0.394/0.208`
- Clean selected rows needed for source gate: `9`
- Weighted cushion surplus above 300c: `123.500c`
- Delta versus refreshed live net: `886.500c`
- Full-weight wins needed to tie live: `0`
- First viable count-gate scenario: `none`

### Coverage If Future Markets Are Missed

| missed markets | no new selected coverage | with 2 clean selected coverage |
|---:|---:|---:|
| 0 | 80.488% | 80.952% |
| 1 | 79.518% | 80.000% |
| 2 | 78.571% | 79.070% |
| 3 | 77.647% | 78.161% |
| 4 | 76.744% | 77.273% |
| 5 | 75.862% | 76.404% |
| 6 | 75.000% | 75.556% |
| 7 | 74.157% | 74.725% |

## post_feature_freeze_bridge

- Policy: `repair_eighth`
- Current entries/denominator: `66/82`
- Current W/L/net/coverage: `54/12` / `423.500c` / `80.488%`
- Row/exposure reconstructed share: `0.394/0.208`
- Clean selected rows needed for source gate: `9`
- Weighted cushion surplus above 300c: `123.500c`
- Delta versus refreshed live net: `886.500c`
- Full-weight wins needed to tie live: `0`
- First viable count-gate scenario: `none`

### Coverage If Future Markets Are Missed

| missed markets | no new selected coverage | with 2 clean selected coverage |
|---:|---:|---:|
| 0 | 80.488% | 80.952% |
| 1 | 79.518% | 80.000% |
| 2 | 78.571% | 79.070% |
| 3 | 77.647% | 78.161% |
| 4 | 76.744% | 77.273% |
| 5 | 75.862% | 76.404% |
| 6 | 75.000% | 75.556% |
| 7 | 74.157% | 74.725% |
