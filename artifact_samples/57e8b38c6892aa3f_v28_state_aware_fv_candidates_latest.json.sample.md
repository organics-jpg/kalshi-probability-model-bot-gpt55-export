# Large Artifact Sample

- Source path: `logs/edge_research/v28_state_aware_fv_candidates_latest.json`
- Export artifact: `logs/edge_research/v28_state_aware_fv_candidates_latest.json.gz`
- Original bytes: `42006932`
- Original sha256: `a7a31a54e51c356ba0142825d18a46fa2ba82248cf66d8948653ec01caa27c33`
- Approximate newline count: `1224548`

## First Lines

    {
      "observation_count": 6798,
      "rows": [
        {
          "book_p": 0.81,
          "brier": 0.017589390625,
          "candidate": "v28_raw",
          "gross_cents": 36,
          "is_first_market_observation": true,
          "is_first_market_side_observation": true,
          "market": "KXBTC15M-26MAY051300-00",
          "market_observation_index": 0,
          "market_side_observation_index": 0,
          "outcome": 1.0,
          "outlier_share": null,
          "p": 0.867375,
          "raw_v28_p": 0.867375,
          "side": "yes",
          "source": "approved_entry",
          "spectral_tag": "insufficient_history",

## Last Lines

              "avg_p": 0.5436903352830188,
              "brier_minus_v28_raw": -0.0046067788748099525,
              "candidate": "repeated_side_book_anchor",
              "count": 6625,
              "gross_cents": -4056.0,
              "win_rate": 0.542188679245283
            },
            {
              "avg_brier": 0.16980646655174866,
              "avg_p": 0.5404188789433962,
              "brier_minus_v28_raw": 0.0,
              "candidate": "v28_raw",
              "count": 6625,
              "gross_cents": -4056.0,
              "win_rate": 0.542188679245283
            }
          ]
        }
      }
    }
