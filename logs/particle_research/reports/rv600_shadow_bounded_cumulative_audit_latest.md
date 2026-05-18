# RV600 Bounded Cumulative Audit

- generated_utc: 2026-05-15T21:17:00+00:00
- research_only: True
- decision: cumulative_bounded_scored_with_entries
- collection_ok: True
- offline_v28_context_ok: True
- pipeline_ok: True
- labels_ok: True
- scored_ok: True

## Summary

- root_count: 40
- candidate_rows: 31480
- settled_markets: 78
- locked_total_entries: 304
- locked_total_pnl_cents: 3634.0
- best_grid_variant: `blend_90_10_max_3_entries_base_70_420_ev4`
- best_grid_accepted_entries: 100
- best_grid_distinct_markets: 34
- best_grid_selected_pnl_cents: 1700.0
- best_grid_matched_v28_delta_cents: 0.0
- best_grid_rejection: `positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct;market_drawdown_worse_than_25pct`
- best_locked_variant: `rv600_primary_max_3_entries_mid_120_420_ev12`
- best_locked_accepted_entries: 46
- best_locked_selected_pnl_cents: 696.0
- best_locked_matched_v28_delta_cents: 0.0
- best_locked_rejection: `positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct;missing_single_market_benchmark`

## Roots

| root | checkpoints | spot_ticks | spot_issues | offline_contexts | offline_issues | pipeline_contexts | pipeline_issues |
|---|---:|---:|---:|---:|---:|---:|---:|
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T195001Z` | 832 | 5302 | 0 | 830 | 2 | 776 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T202034Z` | 842 | 3916 | 0 | 840 | 2 | 810 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T205117Z` | 828 | 3490 | 0 | 826 | 2 | 817 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T211949Z` | 839 | 2706 | 0 | 837 | 2 | 823 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T215130Z` | 836 | 5298 | 0 | 834 | 2 | 784 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T222021Z` | 819 | 4341 | 0 | 817 | 2 | 727 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T230108Z` | 834 | 3594 | 0 | 832 | 2 | 805 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260513T234759Z` | 855 | 2997 | 0 | 852 | 3 | 836 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T002426Z` | 820 | 4360 | 0 | 818 | 2 | 763 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T010859Z` | 836 | 5994 | 0 | 833 | 3 | 819 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T014324Z` | 790 | 12036 | 0 | 788 | 2 | 716 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T021209Z` | 843 | 5344 | 0 | 842 | 1 | 827 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T024042Z` | 807 | 4932 | 0 | 805 | 2 | 753 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T031420Z` | 839 | 6418 | 0 | 837 | 2 | 812 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T035926Z` | 811 | 4300 | 0 | 808 | 3 | 767 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T045722Z` | 847 | 3714 | 0 | 842 | 5 | 823 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T053423Z` | 792 | 3605 | 0 | 790 | 2 | 731 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T122254Z` | 850 | 3470 | 0 | 844 | 6 | 794 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260514T130107Z` | 819 | 7400 | 0 | 817 | 2 | 781 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T024708Z` | 821 | 9133 | 0 | 818 | 3 | 764 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T032104Z` | 855 | 5314 | 0 | 853 | 2 | 853 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T034820Z` | 820 | 4784 | 0 | 818 | 2 | 789 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T045448Z` | 830 | 3837 | 0 | 828 | 2 | 751 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T053557Z` | 791 | 4360 | 0 | 790 | 1 | 719 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T063046Z` | 828 | 2714 | 0 | 827 | 1 | 783 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T071544Z` | 789 | 3245 | 0 | 788 | 1 | 743 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T080148Z` | 800 | 2961 | 0 | 799 | 1 | 706 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T083925Z` | 807 | 3815 | 0 | 805 | 2 | 761 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T091646Z` | 839 | 3817 | 0 | 838 | 1 | 830 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T100014Z` | 811 | 4634 | 0 | 810 | 1 | 763 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T105111Z` | 734 | 2846 | 0 | 733 | 1 | 665 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T113027Z` | 832 | 3034 | 0 | 831 | 1 | 831 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T143222Z` | 846 | 20224 | 0 | 843 | 3 | 809 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T151536Z` | 850 | 10251 | 0 | 848 | 2 | 818 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T160221Z` | 837 | 9359 | 0 | 835 | 2 | 824 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T164836Z` | 871 | 7767 | 0 | 869 | 2 | 866 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T173507Z` | 851 | 7885 | 0 | 849 | 2 | 849 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T182447Z` | 814 | 12586 | 0 | 811 | 3 | 744 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T190705Z` | 813 | 10088 | 0 | 810 | 3 | 795 | 0 |
| `logs\particle_research\real_shadow\rv600_next_evidence_shadow_20260515T200306Z` | 868 | 6406 | 0 | 865 | 3 | 853 | 0 |

## Interpretation

Cumulative bounded read-only evidence has accepted RV600-style entries (locked_pnl_cents=3634.0, best_grid_pnl_cents=1700.0), but the best row is still gate-rejected: positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct;market_drawdown_worse_than_25pct.
