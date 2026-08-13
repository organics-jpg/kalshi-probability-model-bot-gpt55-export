# BTC15M sequential informed-flow screen

**Research-only result. The overall EDGE search remains active.**

## Mechanism

Use outcome-conditioned KXBTC15M taker-flow likelihoods, optionally augmented by KXBTCPERP marked flow, as a sequential posterior correction to the contemporaneous binary-market probability. Orders are admitted only after a fixed latency against exact visible 100-contract depth.

## Frozen development contract

- Historical model training: July 27–29, 2026 dense one-second KXBTC15M tape (288 markets; 259,200 rows).
- Development: July 31 and August 1.
- Validation: August 2 and August 3.
- Sealed lockbox: August 9–10; labels were not opened.
- Quantity: 100 contracts, exactly $100 face notional per market.
- Execution: first causal snapshot after 1, 2, or 3 seconds; full 100-contract VWAP required; 1-cent adverse stress; exact fee function; hold to settlement; one position per market.
- Search: historical offset-logit, beta/binomial likelihood, Gaussian likelihood, binary-flow, perp-flow, and combined-flow paths; six schedules; seven edge thresholds; three latencies.

## Result

- Candidate implementations: **5,544**
- Candidates with trades in both development and validation: **5,320**
- Full passers: **0**

### Strongest minimum point-estimate candidate

`gauss:z_30:scale=0.5:seq600_60:edge=0.07:lat=2s`

```json
{
  "train": {
    "annual_after_best_2h_removed": 48949.65540618557,
    "annual_after_best_day_removed": 28261.60592164949,
    "annual_after_top10pct_winners_removed": -18611.839175257704,
    "annual_net": 133479.13994226806,
    "chronological_half_annual": [312608.3588571429, -49381.93770000001],
    "lcb_annual_2h_cluster_t": -179291.35699036779,
    "net_pnl": 369.50561000000005,
    "source_markets": 97,
    "trades": 53
  },
  "validation": {
    "annual_after_best_2h_removed": 31442.559999999994,
    "annual_after_best_day_removed": -35187.94666666666,
    "annual_after_top10pct_winners_removed": -16619.34222222223,
    "annual_net": 77729.10222222221,
    "chronological_half_annual": [-57068.82352941176, 214538.93731343278],
    "lcb_annual_2h_cluster_t": -92132.77152677916,
    "net_pnl": 299.46999999999997,
    "source_markets": 135,
    "trades": 49
  }
}
```

This rule reached a development annualized point estimate above $100,000, but validation was only about $77,700 and its validation 2-hour clustered lower bound, best-day removal, and top-winner removal were all negative.

### Validation-leading candidate

`beta10:cap=30:anchor120:edge=0.015:lat=1s`

```json
{
  "train": {
    "annual_net": -3734.9786226804076,
    "lcb_annual_2h_cluster_t": -138526.56601232392,
    "net_pnl": -10.339409999999987,
    "source_markets": 97,
    "trades": 42
  },
  "validation": {
    "annual_after_best_2h_removed": 72922.19043555556,
    "annual_after_best_day_removed": 42691.15530666667,
    "annual_after_top10pct_winners_removed": 13852.537102222228,
    "annual_net": 101810.7237688889,
    "chronological_half_annual": [117369.73150588236, 86019.49203582092],
    "lcb_annual_2h_cluster_t": 2562.990455578116,
    "net_pnl": 392.25022,
    "source_markets": 135,
    "trades": 45
  }
}
```

The validation-leading rule exceeded a $100,000 point estimate on validation but was negative on development.

## Decision

The sequential informed-flow family is closed without a lockbox touch. Threshold retunes, sign inversions, and minor window changes do not constitute new mechanisms.

## Provenance

```json
{
  "feature_builder_commit": "960f91a206e58f88e78669b09e0b6716078f904e",
  "feature_artifact_id": 9169858469,
  "feature_artifact_digest": "sha256:610fd3a68838058dc6b4a7bf9fcf6c7a4a0e8d1d9e09801e89e2fd8bfa911067",
  "source_data_commit": "e45c6a9b851e2f61872b1e2b36b354b56eceaa70",
  "source_tick_rows": 259200,
  "source_tick_markets": 288,
  "live_feature_rows": 172351,
  "dev_join_rows": 151102,
  "lockbox_feature_rows": 21249,
  "lockbox_labels_sealed_sha256": "944a7506fd522bba3ed3f474da45cd87dcf9c4e4118e2468c7c5b2b0b4d8d494",
  "lockbox_labels_opened": false,
  "discovery_script_sha256": "9a18967bca3385105919f618ebeee70874e578273b033ef5b6b775dca600185d",
  "full_result_sha256": "5f32a286d687e2099a45dc3e1d3caf198194e7d1af16703134680f1b538b0261"
}
```

Frozen search specification SHA-256: `2c229db38ae3c467e4f55db7115eec082bb5a5aeacd16524327eac9a4c67239e`
