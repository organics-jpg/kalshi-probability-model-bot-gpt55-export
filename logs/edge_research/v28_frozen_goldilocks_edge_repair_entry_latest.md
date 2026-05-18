# v28 Frozen Goldilocks Edge Repair Entry

Research-only; no live bot changes and no orders.

- Freeze UTC: `2026-05-06T13:41:43.611538+00:00`
- Candidate: `skip_false_edge_phase_repair_goldilocks`
- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Live ready: `False`
- Blockers: `net_not_positive`

## Interpretation

- Diagnostic candidate has 92 entries, 92 settled, coverage 75.40983606557377, net 63.0c versus target -432.0c.
- Diagnostic delta versus target is 495.0c; danger rows removed 38, repair rows added 40.
- Frozen future candidate has 49 entries and 49 settled rows since its own freeze.
- Frozen future blockers: net_not_positive.

## Scenarios

### diagnostic_existing_forward

- Denominator: `122`
- Target entries/settled/coverage/net: `90/90/73.770492/-432.000000c`
- Danger entries/settled/net: `38/38/-732.000000c`
- Repair entries/settled/net: `40/40/-237.000000c`
- Candidate entries/settled/coverage/net: `92/92/75.409836/63.000000c`
- Delta vs target: `495.000000c`
- Needed repairs: `40`
- Blockers: `none`

### frozen_future

- Denominator: `65`
- Target entries/settled/coverage/net: `50/50/76.923077/220.000000c`
- Danger entries/settled/net: `18/18/200.000000c`
- Repair entries/settled/net: `17/17/-179.000000c`
- Candidate entries/settled/coverage/net: `49/49/75.384615/-159.000000c`
- Delta vs target: `-379.000000c`
- Needed repairs: `17`
- Blockers: `net_not_positive`

