# Large Artifact Sample

- Source path: `logs/edge_research/v28_candidate_watchlist_latest.json`
- Export artifact: `logs/edge_research/v28_candidate_watchlist_latest.json.gz`
- Original bytes: `106087284`
- Original sha256: `c57c13b3b8ff9c9ccdbc6cb70da1b7f950db4716fe4d1cce51de4aa053495817`
- Approximate newline count: `2710318`

## First Lines

    {
      "avoid_watch": {
        "reason": "Cheap low-probability/near-boundary expansion keeps producing losses in forward rows.",
        "status": "do_not_promote"
      },
      "entry_watch": {
        "anti_overfit_freeze_audit_summary": {
          "all_clear": true,
          "fail_count": 0,
          "interpretation": [
            "Pass means the artifact has a frozen state/report relationship suitable for continued forward monitoring.",
            "Watch means the artifact is diagnostic or dynamic-ranked and should not be treated as promotion evidence by itself.",
            "Fail means a report/state mismatch or missing freeze metadata needs attention before relying on the artifact."
          ],
          "purpose": "Catch candidate-selection drift and dynamic-best leakage before interpreting forward evidence.",
          "rows": [
            {
              "artifact": "v28_target_coverage_fv_overlay_validator",
              "checks": [
                {

## Last Lines

            "policy": "no_same_side_reentry",
            "settled": 116,
            "trades": 116,
            "wins": 62
          },
          {
            "delta_vs_current_cents": -329.0,
            "gross_cents": 494.0,
            "hold_cents": 1332.0,
            "losses": 47,
            "markets": 107,
            "policy": "first_entry_per_market",
            "settled": 107,
            "trades": 107,
            "wins": 57
          }
        ],
        "status": "shadow_only"
      }
    }
