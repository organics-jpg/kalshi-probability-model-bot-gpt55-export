# Tail-Calibrated Physics Interval Probe

Generated UTC: `20260502_184017Z`

## Scope

- Research-only scan; no orders are submitted and no bot files are modified.
- Inflates realized-volatility terminal Brownian sigma before converting margin to probability.
- Uses only physics-side scores for side choice; book probability is not a chooser or model feature.
- Tests the same policy on the current live heartbeat interval ledger and independent v21 passive websocket interval ledger.
- Unit of volume is recurring BTC 15-minute markets.

## Data

- Current intervals: 156; rows: 18034
- V21 intervals: 221; rows: 6554
- Tail-calibrated policies scanned: 8100
- Policies preserving 80% coverage on both captures/splits: 2159
- Policies passing 95% / 80% on both captures: 0
- Policies with 95% Wilson lower bound on both captures: 0
- Nondegenerate both-capture target passes: 0

## Top Shared Policies

| rank | policy | current acc/cov | v21 acc/cov | min split acc | min split cov | max median ask | ask=100 max | both target | nondeg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---|
| 1 | `tail=tail_p_rv_15m_300; tail_p_rv_15m_300>=0.6; ask<=95; sec>=60; gate=adverse15<=10` | 85.51%/88.46% | 84.78%/83.26% | 83.33% | 80.00% | 86.0 | 0 | False | True |
| 2 | `tail=tail_p_rv_60m_100; tail_p_rv_60m_100>=0.75; ask<=95; sec>=60; gate=none` | 85.00%/89.74% | 85.42%/86.88% | 83.33% | 80.00% | 85.0 | 0 | False | True |
| 3 | `tail=tail_p_rv_60m_100; tail_p_rv_60m_100>=0.75; ask<=95; sec>=60; gate=spread<=4` | 85.00%/89.74% | 85.42%/86.88% | 83.33% | 80.00% | 85.0 | 0 | False | True |
| 4 | `tail=tail_p_rv_60m_100; tail_p_rv_60m_100>=0.75; ask<=95; sec>=60; gate=margin_rv15>=0` | 85.00%/89.74% | 85.42%/86.88% | 83.33% | 80.00% | 85.0 | 0 | False | True |
| 5 | `tail=tail_p_rv_15m_200; tail_p_rv_15m_200>=0.65; ask<=95; sec>=60; gate=adverse15<=10` | 85.29%/87.18% | 84.62%/82.35% | 83.02% | 80.00% | 86.0 | 0 | False | True |
| 6 | `tail=tail_p_rv_15m_200; tail_p_rv_15m_200>=0.65; ask<=95; sec>=60; gate=none` | 84.89%/89.10% | 84.13%/85.52% | 81.48% | 82.22% | 86.0 | 0 | False | True |
| 7 | `tail=tail_p_rv_15m_200; tail_p_rv_15m_200>=0.65; ask<=95; sec>=60; gate=spread<=4` | 84.89%/89.10% | 84.13%/85.52% | 81.48% | 82.22% | 86.0 | 0 | False | True |
| 8 | `tail=tail_p_rv_15m_200; tail_p_rv_15m_200>=0.65; ask<=95; sec>=60; gate=margin_rv15>=0` | 84.89%/89.10% | 84.13%/85.52% | 81.48% | 82.22% | 86.0 | 0 | False | True |
| 9 | `tail=tail_p_rv_15m_300; tail_p_rv_15m_300>=0.6; ask<=95; sec>=60; gate=none` | 85.21%/91.03% | 84.29%/86.43% | 81.48% | 82.22% | 86.0 | 0 | False | True |
| 10 | `tail=tail_p_rv_15m_300; tail_p_rv_15m_300>=0.6; ask<=95; sec>=60; gate=spread<=4` | 85.21%/91.03% | 84.29%/86.43% | 81.48% | 82.22% | 86.0 | 0 | False | True |
| 11 | `tail=tail_p_rv_15m_300; tail_p_rv_15m_300>=0.6; ask<=95; sec>=60; gate=margin_rv15>=0` | 85.21%/91.03% | 84.29%/86.43% | 81.48% | 82.22% | 86.0 | 0 | False | True |
| 12 | `tail=tail_p_rv_60m_150; tail_p_rv_60m_150>=0.65; ask<=95; sec>=120; gate=adverse15<=10` | 83.33%/88.46% | 83.68%/85.97% | 81.48% | 81.25% | 83.0 | 0 | False | True |
| 13 | `tail=tail_p_rv_60m_150; tail_p_rv_60m_150>=0.65; ask<=95; sec>=60; gate=adverse15<=10` | 84.03%/92.31% | 83.25%/89.14% | 81.20% | 82.22% | 84.0 | 0 | False | True |
| 14 | `tail=tail_p_rv_15m_100; tail_p_rv_15m_100>=0.75; ask<=95; sec>=120; gate=none` | 83.80%/91.03% | 83.42%/90.05% | 80.83% | 84.38% | 82.0 | 0 | False | True |
| 15 | `tail=tail_p_rv_15m_100; tail_p_rv_15m_100>=0.75; ask<=95; sec>=120; gate=spread<=4` | 83.80%/91.03% | 83.42%/90.05% | 80.83% | 84.38% | 82.0 | 0 | False | True |

## Read

- No tail-calibrated physics-only policy cleared the 95% accuracy / 80% recurring-market target on both captures.
- Best shared 80%-coverage row had min split accuracy 83.33% and max median ask 86.0c.
- Tail inflation is a useful prior audit, but it does not by itself solve the high-volume physics frontier.
