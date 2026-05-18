# v28 Source-Aware FV Robustness Audit

Research-only perturbation audit for the source-aware FV overlay.

- Overlay: `source_aware_approved_book_target_logit125_p60_only`
- Settled: `285`
- Full Brier/logloss delta vs raw: `-0.000479/-0.023376`
- Leave-one-market failures: `12`
- Dominant market Brier-delta share: `7.336170`
- Blockers: `leave_one_market_failure, single_market_contribution_gt_50pct`

## Current Read

- Full source-aware overlay Brier/logloss deltas are -0.00047867059736544926/-0.02337638854671964.
- Leave-one-market failures: 12.
- Largest single-market absolute Brier-delta contribution share is 733.62%.
- Source slice approved_entry best overlay is book_probability with expected source-aware rank 2.
- Source slice rejected_actionable best overlay is book_probability with expected source-aware rank 5.

## Source Slices

| source | settled | best overlay | source-aware rank | d brier | d logloss |
|---|---:|---|---:|---:|---:|
| approved_entry | 180 | `book_probability` | 2 | -0.003466 | -0.042302 |
| rejected_actionable | 105 | `book_probability` | 5 | 0.004642 | 0.009067 |

## Top Market Contributions

| market | contribution | kept d brier |
|---|---:|---:|
| `KXBTC15M-26MAY051715-15` | 0.003512 | 0.003033 |
| `KXBTC15M-26MAY060330-30` | 0.003244 | 0.002765 |
| `KXBTC15M-26MAY052245-45` | 0.002245 | 0.001767 |
| `KXBTC15M-26MAY070015-15` | 0.001543 | 0.001064 |
| `KXBTC15M-26MAY060745-45` | 0.001284 | 0.000806 |
| `KXBTC15M-26MAY060945-45` | -0.001134 | -0.001613 |
| `KXBTC15M-26MAY052045-45` | 0.000812 | 0.000334 |
| `KXBTC15M-26MAY060215-15` | 0.000809 | 0.000330 |
| `KXBTC15M-26MAY062130-30` | 0.000741 | 0.000262 |
| `KXBTC15M-26MAY061015-15` | -0.000730 | -0.001209 |

## Leave-One-Market

| removed market | kept settled | best overlay | source-aware rank | d brier | d logloss | pass |
|---|---:|---|---:|---:|---:|---:|
| `KXBTC15M-26MAY051300-00` | 284 | `book_probability` | 3 | -0.000546 | -0.023700 | True |
| `KXBTC15M-26MAY051330-30` | 284 | `book_probability` | 3 | -0.000543 | -0.023705 | True |
| `KXBTC15M-26MAY051545-45` | 284 | `book_probability` | 3 | -0.000623 | -0.023907 | True |
| `KXBTC15M-26MAY051615-15` | 283 | `book_probability` | 3 | -0.000601 | -0.023517 | True |
| `KXBTC15M-26MAY051715-15` | 282 | `book_probability` | 4 | 0.003033 | -0.013487 | False |
| `KXBTC15M-26MAY051745-45` | 283 | `book_probability` | 3 | -0.000675 | -0.024201 | True |
| `KXBTC15M-26MAY051800-00` | 283 | `book_probability` | 3 | -0.000648 | -0.024109 | True |
| `KXBTC15M-26MAY051815-15` | 284 | `book_probability` | 3 | -0.000153 | -0.022243 | True |
| `KXBTC15M-26MAY051830-30` | 284 | `book_probability` | 3 | -0.000097 | -0.022066 | True |
| `KXBTC15M-26MAY051845-45` | 284 | `book_probability` | 3 | -0.000571 | -0.023774 | True |
| `KXBTC15M-26MAY051900-00` | 284 | `book_probability` | 3 | -0.000567 | -0.023779 | True |
| `KXBTC15M-26MAY051915-15` | 284 | `book_probability` | 3 | -0.000544 | -0.023708 | True |
| `KXBTC15M-26MAY051945-45` | 283 | `book_probability` | 3 | -0.000590 | -0.023962 | True |
| `KXBTC15M-26MAY052000-00` | 284 | `book_probability` | 3 | -0.000398 | -0.023268 | True |
| `KXBTC15M-26MAY052015-15` | 283 | `book_probability` | 3 | -0.000533 | -0.023785 | True |
| `KXBTC15M-26MAY052030-30` | 284 | `book_probability` | 3 | -0.000480 | -0.023459 | True |
| `KXBTC15M-26MAY052045-45` | 283 | `book_probability` | 4 | 0.000334 | -0.020271 | False |
| `KXBTC15M-26MAY052100-00` | 281 | `book_probability` | 3 | -0.000761 | -0.024153 | True |
| `KXBTC15M-26MAY052115-15` | 283 | `book_probability` | 3 | -0.000641 | -0.024207 | True |
| `KXBTC15M-26MAY052130-30` | 284 | `book_probability` | 3 | -0.000427 | -0.023254 | True |
| `KXBTC15M-26MAY052145-45` | 283 | `book_probability` | 3 | -0.000510 | -0.023696 | True |
| `KXBTC15M-26MAY052200-00` | 284 | `book_probability` | 3 | -0.000557 | -0.023720 | True |
| `KXBTC15M-26MAY052215-15` | 283 | `book_probability` | 3 | -0.000476 | -0.023543 | True |
| `KXBTC15M-26MAY052230-30` | 284 | `book_probability` | 3 | -0.000400 | -0.023243 | True |
| `KXBTC15M-26MAY052245-45` | 283 | `book_probability` | 4 | 0.001767 | -0.016913 | False |
| `KXBTC15M-26MAY052300-00` | 283 | `book_probability` | 3 | -0.000595 | -0.024093 | True |
| `KXBTC15M-26MAY052315-15` | 283 | `book_probability` | 3 | -0.000644 | -0.024167 | True |
| `KXBTC15M-26MAY052330-30` | 284 | `book_probability` | 3 | -0.000652 | -0.023852 | True |
| `KXBTC15M-26MAY052345-45` | 284 | `book_probability` | 3 | -0.000403 | -0.023287 | True |
| `KXBTC15M-26MAY060030-30` | 284 | `book_probability` | 3 | -0.000604 | -0.023724 | True |
| `KXBTC15M-26MAY060045-45` | 282 | `book_probability` | 3 | -0.000561 | -0.023931 | True |
| `KXBTC15M-26MAY060100-00` | 283 | `book_probability` | 3 | -0.000882 | -0.024930 | True |
| `KXBTC15M-26MAY060130-30` | 284 | `book_probability` | 3 | -0.000408 | -0.023304 | True |
| `KXBTC15M-26MAY060145-45` | 284 | `book_probability` | 3 | -0.000517 | -0.023675 | True |
| `KXBTC15M-26MAY060200-00` | 282 | `book_probability` | 3 | -0.000554 | -0.023992 | True |
| `KXBTC15M-26MAY060215-15` | 281 | `book_probability` | 4 | 0.000330 | -0.020692 | False |
| `KXBTC15M-26MAY060230-30` | 284 | `book_probability` | 3 | -0.000529 | -0.023666 | True |
| `KXBTC15M-26MAY060245-45` | 281 | `book_probability` | 3 | -0.001004 | -0.025278 | True |
| `KXBTC15M-26MAY060300-00` | 280 | `book_probability` | 3 | -0.000713 | -0.024765 | True |
| `KXBTC15M-26MAY060315-15` | 284 | `book_probability` | 3 | -0.000521 | -0.023658 | True |
| `KXBTC15M-26MAY060330-30` | 282 | `book_probability` | 4 | 0.002765 | 0.005235 | False |
| `KXBTC15M-26MAY060345-45` | 283 | `book_probability` | 3 | -0.000613 | -0.024023 | True |
| `KXBTC15M-26MAY060415-15` | 284 | `book_probability` | 3 | -0.000397 | -0.023261 | True |
| `KXBTC15M-26MAY060445-45` | 283 | `book_probability` | 3 | -0.000655 | -0.024060 | True |
| `KXBTC15M-26MAY060500-00` | 283 | `book_probability` | 3 | -0.000795 | -0.024465 | True |
| `KXBTC15M-26MAY060515-15` | 282 | `book_probability` | 3 | -0.000784 | -0.024650 | True |
| `KXBTC15M-26MAY060530-30` | 283 | `book_probability` | 3 | -0.000601 | -0.023961 | True |
| `KXBTC15M-26MAY060545-45` | 283 | `book_probability` | 3 | -0.000647 | -0.024064 | True |
| `KXBTC15M-26MAY060600-00` | 283 | `book_probability` | 3 | -0.000579 | -0.023852 | True |
| `KXBTC15M-26MAY060615-15` | 283 | `book_probability` | 3 | -0.000659 | -0.024190 | True |
| `KXBTC15M-26MAY060630-30` | 282 | `book_probability` | 3 | -0.000800 | -0.024560 | True |
| `KXBTC15M-26MAY060645-45` | 281 | `book_probability` | 3 | -0.000729 | -0.024580 | True |
| `KXBTC15M-26MAY060700-00` | 281 | `book_probability` | 3 | -0.000484 | -0.023393 | True |
| `KXBTC15M-26MAY060715-15` | 283 | `book_probability` | 3 | -0.000585 | -0.024025 | True |
| `KXBTC15M-26MAY060730-30` | 283 | `book_probability` | 3 | -0.000537 | -0.023784 | True |
| `KXBTC15M-26MAY060745-45` | 283 | `book_probability` | 4 | 0.000806 | -0.019569 | False |
| `KXBTC15M-26MAY060800-00` | 282 | `book_probability` | 3 | -0.000914 | -0.024882 | True |
| `KXBTC15M-26MAY060815-15` | 284 | `book_probability` | 3 | -0.000567 | -0.023758 | True |
| `KXBTC15M-26MAY060830-30` | 283 | `book_probability` | 3 | -0.000734 | -0.024256 | True |
| `KXBTC15M-26MAY060900-00` | 281 | `book_probability` | 4 | 0.000107 | -0.021641 | False |
| `KXBTC15M-26MAY060915-15` | 282 | `book_probability` | 3 | -0.000782 | -0.024565 | True |
| `KXBTC15M-26MAY060930-30` | 280 | `book_probability` | 3 | -0.001167 | -0.025844 | True |
| `KXBTC15M-26MAY060945-45` | 280 | `book_probability` | 3 | -0.001613 | -0.026883 | True |
| `KXBTC15M-26MAY061000-00` | 284 | `book_probability` | 3 | -0.000837 | -0.024423 | True |
| `KXBTC15M-26MAY061015-15` | 281 | `book_probability` | 3 | -0.001209 | -0.025813 | True |
| `KXBTC15M-26MAY061030-30` | 281 | `book_probability` | 3 | -0.000771 | -0.024713 | True |
| `KXBTC15M-26MAY061045-45` | 282 | `book_probability` | 3 | -0.000717 | -0.024342 | True |
| `KXBTC15M-26MAY061100-00` | 282 | `book_probability` | 3 | -0.000858 | -0.024793 | True |
| `KXBTC15M-26MAY061130-30` | 283 | `book_probability` | 3 | -0.000489 | -0.023684 | True |
| `KXBTC15M-26MAY061200-00` | 283 | `book_probability` | 3 | -0.000500 | -0.023584 | True |
| `KXBTC15M-26MAY061230-30` | 284 | `book_probability` | 3 | -0.000677 | -0.023928 | True |
| `KXBTC15M-26MAY061300-00` | 284 | `book_probability` | 3 | -0.000124 | -0.022180 | True |
| `KXBTC15M-26MAY061400-00` | 283 | `book_probability` | 3 | -0.000563 | -0.024176 | True |
| `KXBTC15M-26MAY061415-15` | 284 | `book_probability` | 3 | -0.000517 | -0.023678 | True |
| `KXBTC15M-26MAY061430-30` | 284 | `book_probability` | 3 | -0.000397 | -0.023260 | True |
| `KXBTC15M-26MAY061445-45` | 282 | `book_probability` | 3 | -0.000464 | -0.023817 | True |
| `KXBTC15M-26MAY061545-45` | 284 | `book_probability` | 3 | -0.000532 | -0.023682 | True |
| `KXBTC15M-26MAY061600-00` | 284 | `book_probability` | 3 | -0.000597 | -0.023707 | True |
| `KXBTC15M-26MAY061615-15` | 283 | `book_probability` | 3 | -0.000440 | -0.023541 | True |
| `KXBTC15M-26MAY061630-30` | 284 | `book_probability` | 3 | -0.000404 | -0.023291 | True |
| `KXBTC15M-26MAY061645-45` | 283 | `book_probability` | 3 | -0.000533 | -0.023743 | True |
| `KXBTC15M-26MAY061700-00` | 284 | `book_probability` | 3 | -0.000480 | -0.023459 | True |
| `KXBTC15M-26MAY061715-15` | 284 | `book_probability` | 3 | -0.000622 | -0.023770 | True |
| `KXBTC15M-26MAY061730-30` | 284 | `book_probability` | 3 | -0.000397 | -0.023265 | True |
| `KXBTC15M-26MAY061745-45` | 284 | `book_probability` | 3 | -0.000480 | -0.023459 | True |
| `KXBTC15M-26MAY061800-00` | 283 | `book_probability` | 3 | -0.000746 | -0.024366 | True |
| `KXBTC15M-26MAY061815-15` | 283 | `book_probability` | 3 | -0.000500 | -0.023758 | True |
| `KXBTC15M-26MAY061830-30` | 283 | `book_probability` | 3 | -0.000515 | -0.023762 | True |
| `KXBTC15M-26MAY061900-00` | 283 | `book_probability` | 3 | -0.000510 | -0.023753 | True |
| `KXBTC15M-26MAY061915-15` | 283 | `book_probability` | 3 | -0.000560 | -0.023962 | True |
| `KXBTC15M-26MAY061930-30` | 284 | `book_probability` | 3 | -0.000480 | -0.023459 | True |
| `KXBTC15M-26MAY061945-45` | 284 | `book_probability` | 3 | -0.000480 | -0.023459 | True |
| `KXBTC15M-26MAY062000-00` | 284 | `book_probability` | 3 | -0.000480 | -0.023459 | True |
| `KXBTC15M-26MAY062015-15` | 281 | `book_probability` | 4 | 0.000046 | -0.019829 | False |
| `KXBTC15M-26MAY062030-30` | 283 | `book_probability` | 3 | -0.000811 | -0.024483 | True |
| `KXBTC15M-26MAY062045-45` | 283 | `book_probability` | 3 | -0.000531 | -0.023899 | True |
| `KXBTC15M-26MAY062100-00` | 281 | `book_probability` | 3 | -0.001207 | -0.025766 | True |
| `KXBTC15M-26MAY062115-15` | 282 | `book_probability` | 4 | 0.000158 | -0.022121 | False |
| `KXBTC15M-26MAY062130-30` | 283 | `book_probability` | 4 | 0.000262 | -0.020856 | False |
| `KXBTC15M-26MAY062145-45` | 284 | `book_probability` | 3 | -0.000414 | -0.023320 | True |
| `KXBTC15M-26MAY062200-00` | 284 | `book_probability` | 3 | -0.000408 | -0.023303 | True |
| `KXBTC15M-26MAY062215-15` | 282 | `book_probability` | 3 | -0.000846 | -0.024783 | True |
| `KXBTC15M-26MAY062230-30` | 284 | `book_probability` | 3 | -0.000714 | -0.024068 | True |
| `KXBTC15M-26MAY062245-45` | 283 | `book_probability` | 3 | -0.000653 | -0.024128 | True |
| `KXBTC15M-26MAY062300-00` | 283 | `book_probability` | 3 | -0.000446 | -0.023532 | True |
| `KXBTC15M-26MAY062315-15` | 283 | `book_probability` | 3 | -0.000470 | -0.023630 | True |
| `KXBTC15M-26MAY062330-30` | 284 | `book_probability` | 3 | -0.000480 | -0.023459 | True |
| `KXBTC15M-26MAY062345-45` | 284 | `book_probability` | 3 | -0.000594 | -0.023700 | True |
| `KXBTC15M-26MAY070000-00` | 283 | `book_probability` | 3 | -0.000693 | -0.024264 | True |
| `KXBTC15M-26MAY070015-15` | 284 | `book_probability` | 4 | 0.001064 | -0.016026 | False |
| `KXBTC15M-26MAY070030-30` | 283 | `book_probability` | 3 | -0.000576 | -0.023965 | True |
| `KXBTC15M-26MAY070045-45` | 284 | `book_probability` | 3 | -0.000480 | -0.023459 | True |
| `KXBTC15M-26MAY070100-00` | 284 | `book_probability` | 3 | -0.000480 | -0.023459 | True |
| `KXBTC15M-26MAY070115-15` | 283 | `book_probability` | 3 | -0.000475 | -0.023572 | True |
| `KXBTC15M-26MAY070130-30` | 284 | `book_probability` | 3 | -0.000413 | -0.023316 | True |
| `KXBTC15M-26MAY070145-45` | 284 | `book_probability` | 3 | -0.000433 | -0.023261 | True |
| `KXBTC15M-26MAY070200-00` | 284 | `book_probability` | 3 | -0.000480 | -0.023459 | True |
| `KXBTC15M-26MAY070530-30` | 284 | `book_probability` | 3 | -0.000480 | -0.023459 | True |
| `KXBTC15M-26MAY070545-45` | 283 | `book_probability` | 3 | -0.000801 | -0.024538 | True |
| `KXBTC15M-26MAY070600-00` | 284 | `book_probability` | 3 | -0.000399 | -0.023244 | True |
| `KXBTC15M-26MAY070615-15` | 284 | `book_probability` | 3 | -0.000410 | -0.023309 | True |
| `KXBTC15M-26MAY070630-30` | 284 | `book_probability` | 3 | -0.000592 | -0.023696 | True |
| `KXBTC15M-26MAY070645-45` | 283 | `book_probability` | 3 | -0.000660 | -0.024250 | True |
| `KXBTC15M-26MAY070700-00` | 284 | `book_probability` | 3 | -0.000647 | -0.023838 | True |
| `KXBTC15M-26MAY070715-15` | 284 | `book_probability` | 3 | -0.000480 | -0.023459 | True |
| `KXBTC15M-26MAY070730-30` | 284 | `book_probability` | 3 | -0.000480 | -0.023459 | True |
| `KXBTC15M-26MAY070745-45` | 283 | `book_probability` | 3 | -0.001140 | -0.025552 | True |
| `KXBTC15M-26MAY070800-00` | 284 | `book_probability` | 3 | -0.000480 | -0.023459 | True |
| `KXBTC15M-26MAY070815-15` | 283 | `book_probability` | 3 | -0.000509 | -0.023736 | True |
| `KXBTC15M-26MAY070830-30` | 281 | `book_probability` | 3 | -0.000802 | -0.024823 | True |
| `KXBTC15M-26MAY070845-45` | 284 | `book_probability` | 3 | -0.000480 | -0.023459 | True |
| `KXBTC15M-26MAY070900-00` | 284 | `book_probability` | 3 | -0.000480 | -0.023459 | True |
| `KXBTC15M-26MAY070915-15` | 283 | `book_probability` | 3 | -0.000550 | -0.023784 | True |
| `KXBTC15M-26MAY070930-30` | 284 | `book_probability` | 3 | -0.000548 | -0.023697 | True |
| `KXBTC15M-26MAY070945-45` | 283 | `book_probability` | 3 | -0.000746 | -0.024294 | True |
| `KXBTC15M-26MAY071000-00` | 283 | `book_probability` | 3 | -0.000892 | -0.024771 | True |
| `KXBTC15M-26MAY071015-15` | 281 | `book_probability` | 4 | 0.000144 | -0.021360 | False |
| `KXBTC15M-26MAY071030-30` | 282 | `book_probability` | 3 | -0.000641 | -0.024212 | True |
| `KXBTC15M-26MAY071045-45` | 283 | `book_probability` | 3 | -0.000805 | -0.024563 | True |
| `KXBTC15M-26MAY071100-00` | 284 | `book_probability` | 3 | -0.000154 | -0.022112 | True |
| `KXBTC15M-26MAY071115-15` | 283 | `book_probability` | 3 | -0.000677 | -0.024074 | True |
| `KXBTC15M-26MAY071130-30` | 284 | `book_probability` | 3 | -0.000535 | -0.023724 | True |
| `KXBTC15M-26MAY071145-45` | 283 | `book_probability` | 3 | -0.000515 | -0.023734 | True |
| `KXBTC15M-26MAY071200-00` | 283 | `book_probability` | 3 | -0.000710 | -0.024164 | True |
| `KXBTC15M-26MAY071215-15` | 282 | `book_probability` | 3 | -0.000700 | -0.024418 | True |
| `KXBTC15M-26MAY071230-30` | 281 | `book_probability` | 3 | -0.000967 | -0.025218 | True |
| `KXBTC15M-26MAY071300-00` | 284 | `book_probability` | 3 | -0.000626 | -0.023779 | True |
| `KXBTC15M-26MAY071315-15` | 282 | `book_probability` | 3 | -0.000713 | -0.024427 | True |
