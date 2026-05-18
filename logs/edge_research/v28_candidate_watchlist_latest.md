# v28 Candidate Watchlist

Forward-only watchlist for the active v28 improvement goal. No candidate here is promoted.

## Current Control

- Entries: `173`
- Gross P&L: `$8.23`
- Current balance reference: `$26.40`
- Risk stop active: `True`

## Exit Watch

- Candidate: `suppress_reduce_p_hold_ge_075`
- Status: `shadow_only`
- Reason: Frozen forward validator targets probability-reduce exits that clip a still-strong held-side thesis.
- Candidate gross: `1424c`
- Delta vs current: `601c`
- Worst mark: `-172c`
- Live readiness: `False`
- Promotion status: `blocked`
- Promotion blockers: `control_risk_stop_active, readiness:exit:suppressed_loss_control_cost_negative, readiness:control_risk_stop_active`

### Frozen Reduce-Suppression Validator

- Future settled rows: `132`
- Frozen delta vs current: `337c`
- Suppressed exits: `25`
- Frozen blockers: `suppressed_loss_control_cost_negative`

### Frozen YES-Only Reduce-Suppression Validator

- Narrow side-asymmetric validator created because the full reduce-suppression evidence has not proven NO-side behavior.
- Future settled rows: `103`
- Frozen delta vs current: `112c`
- Suppressed exits: `6`
- Suppressed W/L: `5/1`
- Frozen blockers: `suppressed_losers_present, suppressed_loss_control_cost_negative`

### Reduce-Suppression Robustness

- Shadow interest: `False`
- Promotion ready: `False`
- Robustness blockers: `suppressed_loss_cost_negative, suppressed_losers_present`

### Reduce-Suppression Side Split

- Diagnostic split of the frozen reduce-suppression window; this is not promotion evidence for the fresh YES-only validator.
- `suppress_all_reduce_p_hold_ge_075`: settled `132`, delta `337c`, suppressed `25`, W/L `20/5`, loss cost `-730c`
- `suppress_yes_reduce_p_hold_ge_075`: settled `132`, delta `436c`, suppressed `12`, W/L `11/1`, loss cost `-146c`
- `suppress_no_reduce_p_hold_ge_075`: settled `132`, delta `-99c`, suppressed `13`, W/L `9/4`, loss cost `-584c`

### Exit Reduce Promotion Runway

- Defines what still has to happen before reduce-suppression can be considered.
- Rows needed for 30: `0`
- Current delta: `337c`
- Suppressed exits: `25`
- Invalidators now: `suppressed_loss_control_cost_negative, robustness_shadow_interest_false`

### Exit Book-Gap Candidates

- Tests whether soft exits should be suppressed when p_hold exceeds executable exit bid.
- Best book-gap exit policy is hold_to_settlement_control with gross 2304.0c and delta 1481.0c vs current.
- Current v28 exit gross is 823.0c over 173 trades.
- This is diagnostic only; forward promotion needs a frozen validator with future rows.
- `hold_to_settlement_control`: trades `173`, W/L `146/27`, gross/delta `2304c/1481c`, suppressed `142`, worst mark `-172c`
- `suppress_soft_gap15_or_p_hold75`: trades `173`, W/L `115/58`, gross/delta `1396c/573c`, suppressed `86`, worst mark `-172c`
- `suppress_soft_exit_hold_book_gap_ge_10pp`: trades `173`, W/L `100/73`, gross/delta `837c/14c`, suppressed `3`, worst mark `-152c`
- `current_v28_exit`: trades `173`, W/L `98/75`, gross/delta `823c/0c`, suppressed `0`, worst mark `-134c`
- `suppress_soft_exit_hold_book_gap_ge_20pp`: trades `173`, W/L `98/75`, gross/delta `823c/0c`, suppressed `0`, worst mark `-134c`

### Frozen Exit Book-Gap Suppression

- Future-only validator for suppressing soft exits when held-side FV still dominates the executable exit bid.
- Candidate: `suppress_soft_gap15_or_p_hold75`
- Future settled rows: `120`
- Frozen delta vs current: `235c`
- Suppressed exits: `59`
- Frozen blockers: `suppressed_loss_control_cost_negative`

### Active Trade Sensitivity

- Shows unresolved trades and what settlement outcomes imply for current exit value and frozen candidates.
- Active/unresolved trades: `0`
- No unresolved v28 trades currently reconstructed.

## Entry Watch

- Candidate: `book_plus_05_no_cheap_yes_boundary`
- Status: `shadow_only`
- Reason: Best current broad discovery row after removing cheap YES boundary-pull traps; frozen future validation has just started and still includes rejected-actionable rows.
- Candidate entries/resolved/settled/wins/losses: `164/164/164/92/72`
- Candidate actual/simulated rows: `31/133`
- Candidate simulated share: `81.1%`
- Candidate coverage: `90.60773480662984`
- Candidate gross: `646c`
- Baseline entries/resolved/settled/wins/losses: `107/107/107/91/16`
- Baseline gross: `494c`
- Promotion status: `blocked`
- Promotion blockers: `simulated_share_gt_35%`

### RMT Forgetting Broad Entry Watch

- These rows target roughly 70-90% market coverage and remain shadow-only.
- `v28_raw_p55_edge2`: entries `162`, settled `162`, wins/losses `108/54`, coverage `89.50276243093923`, gross/net `965c/406c`, brier `0.20693301481807408`, actual/sim `16/146`, early/late net `-205c/611c`, boot net p10/p50 `-1012c/420c`, boot p>0 `0.6365`, blockers `simulated_share_gt_35%`
- `v28_raw_p58_edge2`: entries `158`, settled `158`, wins/losses `107/51`, coverage `87.29281767955801`, gross/net `601c/62c`, brier `0.20564982716485444`, actual/sim `18/140`, early/late net `-156c/218c`, boot net p10/p50 `-1380c/49c`, boot p>0 `0.517`, blockers `simulated_share_gt_35%`
- `v28_raw_p60_edge0`: entries `162`, settled `162`, wins/losses `103/59`, coverage `89.50276243093923`, gross/net `-1096c/-1654c`, brier `0.21558763914079632`, actual/sim `21/141`, early/late net `-572c/-1082c`, boot net p10/p50 `-3067c/-1669c`, boot p>0 `0.0655`, blockers `simulated_share_gt_35%`

### Book-Favorite Edge Check

- Checks whether book-anchored candidate rows beat executable ask after estimated entry fees.
- `first_side_raw_later_book_p60_edge0` `all`: count `171`, wins/losses `103/68`, avg ask `0.6680116959064327`, realized edge vs ask `-0.065672514619883`, net `-2831c`
- `first_side_raw_later_book_p60_edge0` `mode_book_exact`: count `130`, wins/losses `79/51`, avg ask `0.6783846153846154`, realized edge vs ask `-0.07069230769230772`, net `-2205c`
- `rmt_repetition_forget_p60_edge0` `all`: count `171`, wins/losses `106/65`, avg ask `0.6780701754385965`, realized edge vs ask `-0.05818713450292401`, net `-2573c`
- `rmt_repetition_forget_p60_edge0` `mode_book_exact`: count `140`, wins/losses `85/55`, avg ask `0.6775714285714286`, realized edge vs ask `-0.07042857142857151`, net `-2376c`
- `book_ask_prior_p60_edge0` `all`: count `173`, wins/losses `107/66`, avg ask `0.67121387283237`, realized edge vs ask `-0.05271676300578043`, net `-2489c`
- `book_ask_prior_p60_edge0` `mode_book_exact`: count `173`, wins/losses `107/66`, avg ask `0.67121387283237`, realized edge vs ask `-0.05271676300578043`, net `-2489c`

### Frozen Forward Candidate Gate

- Freeze timestamp UTC: `2026-05-05T22:07:37.064896+00:00`
- Forward market denominator: `157`
- Excluded in-progress post-freeze markets: `1`
- Future candidate rows: `5306`
- `first_side_raw_later_book_p60_edge0`: entries `153`, settled `153`, wins/losses `88/65`, coverage `97.45222929936305`, net `-3318c`, brier `0.23467192757783006`, actual/sim `4/149`, fv blockers `coverage_too_high, net_not_positive`, execution blockers `simulated_share_gt_0.35, coverage_too_high, net_not_positive`
- `rmt_repetition_forget_p60_edge0`: entries `153`, settled `153`, wins/losses `91/62`, coverage `97.45222929936305`, net `-3048c`, brier `0.22999871486730228`, actual/sim `4/149`, fv blockers `coverage_too_high, net_not_positive`, execution blockers `simulated_share_gt_0.35, coverage_too_high, net_not_positive`
- `book_ask_prior_p60_edge0`: entries `155`, settled `155`, wins/losses `93/62`, coverage `98.72611464968153`, net `-2777c`, brier `0.23468322580645162`, actual/sim `3/152`, fv blockers `coverage_too_high, net_not_positive`, execution blockers `simulated_share_gt_0.35, coverage_too_high, net_not_positive`
- `v28_raw_p50_edge0`: entries `154`, settled `154`, wins/losses `87/67`, coverage `98.08917197452229`, net `-627c`, brier `0.22763813776681818`, actual/sim `8/146`, fv blockers `coverage_too_high, net_not_positive`, execution blockers `simulated_share_gt_0.35, coverage_too_high, net_not_positive`

### Frozen Threshold Challengers

- Freeze timestamp UTC: `2026-05-05T22:19:18.149284+00:00`
- Forward market denominator: `156`
- Future candidate rows: `5270`
- `first_side_raw_later_book_p58_edge0`: entries `152`, settled `152`, coverage `97.43589743589743`, net `-2557c`, brier `0.22836092462157234`, missed `4`, fv blockers `coverage_too_high, net_not_positive`, execution blockers `simulated_share_gt_0.35, coverage_too_high, net_not_positive`
- `rmt_repetition_forget_p58_edge0`: entries `152`, settled `152`, coverage `97.43589743589743`, net `-3210c`, brier `0.2301266198428339`, missed `4`, fv blockers `coverage_too_high, net_not_positive`, execution blockers `simulated_share_gt_0.35, coverage_too_high, net_not_positive`

### Frozen Timing Diagnostic

- Markets with selected rows: `157`
- `KXBTC15M-26MAY071315-15` `threshold_p58` `first_side_raw_later_book_p58_edge0`: delay `141.378957`, side `yes`, same_first `True`, p_eff `0.7`, ask `0.7`, edge `0.0`, won `True`
- `KXBTC15M-26MAY071315-15` `threshold_p58` `rmt_repetition_forget_p58_edge0`: delay `141.378957`, side `yes`, same_first `True`, p_eff `0.7`, ask `0.7`, edge `0.0`, won `True`
- `KXBTC15M-26MAY071330-30` `primary_p60` `book_ask_prior_p60_edge0`: delay `0.0`, side `no`, same_first `True`, p_eff `0.6`, ask `0.6`, edge `0.0`, won `True`
- `KXBTC15M-26MAY071330-30` `primary_p60` `v28_raw_p50_edge0`: delay `19.992339`, side `yes`, same_first `False`, p_eff `0.544206`, ask `0.52`, edge `0.02420599999999995`, won `False`
- `KXBTC15M-26MAY071330-30` `threshold_p58` `first_side_raw_later_book_p58_edge0`: delay `40.00197`, side `no`, same_first `True`, p_eff `0.58`, ask `0.58`, edge `0.0`, won `True`
- `KXBTC15M-26MAY071330-30` `threshold_p58` `rmt_repetition_forget_p58_edge0`: delay `40.00197`, side `no`, same_first `True`, p_eff `0.58`, ask `0.58`, edge `0.0`, won `True`
- `KXBTC15M-26MAY071330-30` `primary_p60` `first_side_raw_later_book_p60_edge0`: delay `80.786449`, side `no`, same_first `True`, p_eff `0.65`, ask `0.65`, edge `0.0`, won `True`
- `KXBTC15M-26MAY071330-30` `primary_p60` `rmt_repetition_forget_p60_edge0`: delay `80.786449`, side `no`, same_first `True`, p_eff `0.65`, ask `0.65`, edge `0.0`, won `True`

### Side-Flip Path Diagnostic

- Compares raw broad first entry against later/book-anchored entries when side agrees or flips.
- `first_side_raw_later_book_p60_edge0` `same_side`: count `125`, settled `125`, early wins `79`, late wins `79`, early net `39c`, late net `-1257c`, late-early `-1296c`
- `first_side_raw_later_book_p60_edge0` `side_flip`: count `44`, settled `44`, early wins `22`, late wins `22`, early net `188c`, late net `-1639c`, late-early `-1827c`
- `rmt_repetition_forget_p60_edge0` `same_side`: count `120`, settled `120`, early wins `78`, late wins `78`, early net `314c`, late net `-1089c`, late-early `-1403c`
- `rmt_repetition_forget_p60_edge0` `side_flip`: count `49`, settled `49`, early wins `23`, late wins `26`, early net `-87c`, late net `-1549c`, late-early `-1462c`
- `book_ask_prior_p60_edge0` `same_side`: count `118`, settled `118`, early wins `77`, late wins `77`, early net `410c`, late net `-944c`, late-early `-1354c`
- `book_ask_prior_p60_edge0` `side_flip`: count `52`, settled `52`, early wins `24`, late wins `28`, early net `-287c`, late net `-1476c`, late-early `-1189c`

### Side-Agreement Meta Candidate

- Discovery-only until its frozen gate accumulates future rows.
- `raw_when_same_else_first_side_p60`: entries `172`, settled `172`, coverage `95.02762430939227`, net `-1906c`, brier `0.2276797781500349`, same/raw `125`, flip/wait `44`
- `raw_when_same_else_rmt_p60`: entries `172`, settled `172`, coverage `95.02762430939227`, net `-1541c`, brier `0.22236482000402327`, same/raw `120`, flip/wait `49`

### Frozen Side-Agreement Challengers

- Freeze timestamp UTC: `2026-05-05T22:28:58.054865+00:00`
- Forward market denominator: `156`
- Future candidate rows: `306`
- `raw_when_same_else_first_side_raw_later_book_p60_edge0`: entries `150`, settled `150`, coverage `96.15384615384616`, net `-2071c`, brier `0.22915378225423336`, missed `6`, fv blockers `coverage_too_high, net_not_positive`, execution blockers `simulated_share_gt_0.35, coverage_too_high, net_not_positive`
- `raw_when_same_else_rmt_repetition_forget_p60_edge0`: entries `150`, settled `150`, coverage `96.15384615384616`, net `-1694c`, brier `0.22335529691347333`, missed `6`, fv blockers `coverage_too_high, net_not_positive`, execution blockers `simulated_share_gt_0.35, coverage_too_high, net_not_positive`

### Convex Raw-Escape Candidate

- Discovery-only until its frozen gate accumulates future rows.
- `raw_edge20_else_first_side_p60`: entries `172`, settled `172`, coverage `95.02762430939227`, net `-3438c`, brier `0.23794684986814535`, raw_escape `11`, wait `158`
- `raw_edge20_else_rmt_p60`: entries `172`, settled `172`, coverage `95.02762430939227`, net `-2907c`, brier `0.2315861060744215`, raw_escape `11`, wait `158`

### Frozen Convex Raw-Escape Challengers

- Freeze timestamp UTC: `2026-05-05T22:33:33.421286+00:00`
- Forward market denominator: `155`
- Future candidate rows: `304`
- `raw_edge20_else_first_side_raw_later_book_p60_edge0`: entries `152`, settled `152`, coverage `98.06451612903226`, net `-4099c`, brier `0.2480778028969671`, raw_escape `10`, wait `139`, fv blockers `coverage_too_high, net_not_positive`, execution blockers `simulated_share_gt_0.35, coverage_too_high, net_not_positive`
- `raw_edge20_else_rmt_repetition_forget_p60_edge0`: entries `152`, settled `152`, coverage `98.06451612903226`, net `-3556c`, brier `0.24107700258128287`, raw_escape `10`, wait `139`, fv blockers `coverage_too_high, net_not_positive`, execution blockers `simulated_share_gt_0.35, coverage_too_high, net_not_positive`

### Raw-Conviction Override Diagnostic

- Tests whether strong raw v28 executable edge should override later book/RMT side flips.
- `first_side_raw_later_book_p60_edge0:same_side`: count `125`, settled `125`, raw W/L `79/46`, raw net `37c`, alt W/L `79/46`, alt net `-1257c`, alt-raw `-1294c`
- `first_side_raw_later_book_p60_edge0:side_flip`: count `44`, settled `44`, raw W/L `22/22`, raw net `188c`, alt W/L `22/22`, alt net `-1639c`, alt-raw `-1827c`
- `rmt_repetition_forget_p60_edge0:same_side`: count `120`, settled `120`, raw W/L `78/42`, raw net `312c`, alt W/L `78/42`, alt net `-1089c`, alt-raw `-1401c`
- `rmt_repetition_forget_p60_edge0:side_flip`: count `49`, settled `49`, raw W/L `23/26`, raw net `-87c`, alt W/L `26/23`, alt net `-1549c`, alt-raw `-1462c`
- `book_ask_prior_p60_edge0:same_side`: count `118`, settled `118`, raw W/L `77/41`, raw net `408c`, alt W/L `77/41`, alt net `-944c`, alt-raw `-1352c`
- `book_ask_prior_p60_edge0:side_flip`: count `52`, settled `52`, raw W/L `24/28`, raw net `-287c`, alt W/L `28/24`, alt net `-1476c`, alt-raw `-1189c`
- Side-flip edge buckets:
  - `first_side_raw_later_book_p60_edge0:side_flip:raw_edge_ge_20pp`: settled `7`, raw net `-169c`, alt net `116c`, alt-raw `285c`
  - `first_side_raw_later_book_p60_edge0:side_flip:raw_edge_0_5pp`: settled `24`, raw net `113c`, alt net `-1179c`, alt-raw `-1292c`
  - `rmt_repetition_forget_p60_edge0:side_flip:raw_edge_ge_20pp`: settled `8`, raw net `-28c`, alt net `-16c`, alt-raw `12c`
  - `rmt_repetition_forget_p60_edge0:side_flip:raw_edge_0_5pp`: settled `25`, raw net `-5c`, alt net `-1121c`, alt-raw `-1116c`
  - `book_ask_prior_p60_edge0:side_flip:raw_edge_ge_20pp`: settled `9`, raw net `68c`, alt net `-141c`, alt-raw `-209c`
  - `book_ask_prior_p60_edge0:side_flip:raw_edge_0_5pp`: settled `28`, raw net `37c`, alt net `-1289c`, alt-raw `-1326c`

### Coverage Pressure Audit

- Scores missed forward markets after settlement to distinguish healthy abstentions from coverage mistakes.
- `v28_frozen_forward_candidates` `book_ask_prior_p60_edge0`: misses `2`, resolved `2`, pending `0`, near-miss net `8c`, saved losses `0`, missed profits `2`, negative-edge winners `0`
- `v28_frozen_forward_candidates` `first_side_raw_later_book_p60_edge0`: misses `4`, resolved `4`, pending `0`, near-miss net `-131c`, saved losses `1`, missed profits `3`, negative-edge winners `0`
- `v28_frozen_forward_candidates` `rmt_repetition_forget_p60_edge0`: misses `4`, resolved `4`, pending `0`, near-miss net `-131c`, saved losses `1`, missed profits `3`, negative-edge winners `0`
- `v28_frozen_forward_candidates` `v28_raw_p50_edge0`: misses `3`, resolved `3`, pending `0`, near-miss net `-124c`, saved losses `1`, missed profits `0`, negative-edge winners `2`

### Raw Physics Penalty Candidates

- Discovery-only physics penalties around raw v28; frozen challengers below must earn forward rows.
- `raw_expensive_friction_p52_edge0`: entries `160`, settled `160`, coverage `88.39779005524862`, net `478c`, brier `0.20687056340426874`, actual/sim `23/137`
- `raw_full_physics_friction_p50_edge0`: entries `145`, settled `145`, coverage `80.11049723756905`, net `267c`, brier `0.19853071697781377`, actual/sim `30/115`
- `raw_full_no_repeat_friction_p52_edge0`: entries `160`, settled `160`, coverage `88.39779005524862`, net `248c`, brier `0.2019768709127375`, actual/sim `27/133`
- `raw_full_physics_friction_p50_edge1`: entries `133`, settled `133`, coverage `73.48066298342542`, net `233c`, brier `0.21267640697487217`, actual/sim `25/108`
- `raw_full_physics_friction_p52_edge0`: entries `141`, settled `141`, coverage `77.90055248618785`, net `228c`, brier `0.19223500082514894`, actual/sim `31/110`
- `raw_full_no_repeat_friction_p50_edge1`: entries `154`, settled `154`, coverage `85.0828729281768`, net `152c`, brier `0.20087178377271428`, actual/sim `28/126`

### Noise-Floor Shrinkage Candidates

- Discovery-only FV candidates that shrink raw v28 toward 50 in noisy physical states instead of flipping sides.
- `noise_shrink_rmt_recency_p50_edge0`: entries `147`, settled `147`, coverage `81.21546961325967`, net `1233c`, brier `0.23150507721482877`, actual/sim `9/138`
- `noise_shrink_rmt_recency_p50_edge1`: entries `136`, settled `136`, coverage `75.13812154696133`, net `832c`, brier `0.23947440792589234`, actual/sim `7/129`
- `noise_shrink_light_p50_edge1`: entries `168`, settled `168`, coverage `92.81767955801105`, net `812c`, brier `0.20926054614098494`, actual/sim `14/154`
- `noise_shrink_full_p50_edge0`: entries `136`, settled `136`, coverage `75.13812154696133`, net `786c`, brier `0.2369739343349383`, actual/sim `7/129`
- `noise_shrink_rmt_recency_p52_edge0`: entries `132`, settled `132`, coverage `72.92817679558011`, net `781c`, brier `0.2217768094262941`, actual/sim `11/121`
- `noise_shrink_weakraw_rmt_memory_p50_edge1`: entries `170`, settled `170`, coverage `93.92265193370166`, net `725c`, brier `0.20134718376916153`, actual/sim `14/156`

### Raw Entry Calibrated Probability

- Keeps raw v28 p50 entry selection fixed and compares probability overlays on the same selected rows.
- `book_probability`: count `172`, brier `0.21744593023255815` delta `-0.006548895154377898`, logloss `0.62142053873985` delta `-0.010476170391744977`, ece `0.02982558139534884` delta `-0.03441020348837208`, net `-81c`
- `noise_shrink_light_probability`: count `172`, brier `0.22249237353325432` delta `-0.0015024518536817244`, logloss `0.6293531129061882` delta `-0.0025435962254067856`, ece `0.050837996076099` delta `-0.013397788807621921`, net `-81c`
- `raw_probability`: count `172`, brier `0.22399482538693605` delta `0.0`, logloss `0.631896709131595` delta `0.0`, ece `0.06423578488372092` delta `0.0`, net `-81c`
- `noise_shrink_full_probability`: count `172`, brier `0.22436632666587913` delta `0.00037150127894308715`, logloss `0.63672133009727` delta `0.004824620965675042`, ece `0.044420248122283526` delta `-0.019815536761437394`, net `-81c`
- `noise_shrink_rmt_recency_probability`: count `172`, brier `0.22519346821257832` delta `0.0011986428256422765`, logloss `0.6381342719787806` delta `0.006237562847185574`, ece `0.059140308459354175` delta `-0.005095476424366745`, net `-81c`
- `entry_conditioned_logit125_probability`: count `172`, brier `0.22627037424370602` delta `0.0022755488567699766`, logloss `0.634658227534248` delta `0.0027615184026530404`, ece `0.07841492663293712` delta `0.014179141749216195`, net `-81c`

### Probability Profit Bridge

- Compares settlement calibration with realized exit P&L and hold-to-settlement P&L.
- Rows/settled: `173/173`
- Overall actual/hold/exit value: `823c/2304c/-1481c`
- Overall settled win rate is 0.8439306358381503 with avg p 0.8838875953757226, actual gross 823.0c, and exit value -1481.0c.
- Worst raw/book gap bucket by actual gross is raw_above_book_15_30pp with 22 settled rows and -118.0c.
- Reentry bucket first_same_side has 116 settled rows, gross 532.0c, hold 1356.0c.
- Reentry bucket same_side_reentry has 57 settled rows, gross 291.0c, hold 948.0c.
- gap `raw_above_book_15_30pp`: settled `22`, W/L `17/5`, actual/hold/exit `-118c/426c/-544c`
- gap `raw_above_book_5_15pp`: settled `146`, W/L `127/19`, actual/hold/exit `1035c/1852c/-817c`
- gap `raw_above_book_gt_30pp`: settled `5`, W/L `2/3`, actual/hold/exit `-94c/26c/-120c`
- reentry `first_same_side`: settled `116`, W/L `97/19`, actual/hold `532c/1356c`
- reentry `same_side_reentry`: settled `57`, W/L `49/8`, actual/hold `291c/948c`

### Approved-Entry FV Overlay Validator

- FV overlay calibration on actual v28-approved entries only.
- Rows/settled: `173/173`
- Best overlay: `book_probability`
- Best approved-entry overlay by Brier is book_probability with Brier delta -0.0048166936698150475.
- Raw approved-entry calibration error is -0.03995695953757228 with win rate 0.8439306358381503 and avg p 0.8838875953757226.
- `book_probability`: settled `173`, W/L `146-27`, avg p `0.7773410404624277`, brier d `-0.0048166936698150475`, logloss d `-0.04865443082318277`
- `noise_shrink_light_probability`: settled `173`, W/L `146-27`, avg p `0.8753320000145539`, brier d `-0.0005465028547037565`, logloss d `-0.024833970136842354`
- `raw_probability`: settled `173`, W/L `146-27`, avg p `0.8838875953757226`, brier d `0.0`, logloss d `0.0`
- `entry_conditioned_plus03_probability`: settled `173`, W/L `146-27`, avg p `0.913558416184971`, brier d `0.002944633619479775`, logloss d `0.05426925365445007`
- `entry_conditioned_logit125_probability`: settled `173`, W/L `146-27`, avg p `0.9251859479005387`, brier d `0.004596640788226525`, logloss d `0.041291218855766754`

### Approved-Entry Book-Edge Actionability

- Tests whether book-vs-raw disagreement changes actual v28-approved entry decisions without relying on rejected-actionable rows.
- Future actual-approved entries: `133`
- Useful policies: `2`
- Best useful policy `skip_discount15_book_edge_lt_5pp` keeps coverage `84.21052631578948`, net `927c`, delta `226c`, skipped W/L/net `16/5/-226c`
- Scored 133 future actual-approved v28 entries from book-FV freeze 2026-05-06T06:20:06.824407+00:00.
- Keep-all control net is 701.0c with 133 settled rows.
- Useful retained-coverage policies found: 2.
- Best clean policy skip_discount15_book_edge_lt_5pp keeps coverage 84.21052631578948%, improves net by 226.0c, and skipped rows were 16/5 for -226.0c.

### Frozen Approved-Entry Book-Edge Gate

- Future-only validator for the fixed book-edge skip rule; earlier actionability rows are discovery only.
- Freeze timestamp UTC: `2026-05-06T13:10:59.879402+00:00`
- Future entries/retained settled/coverage: `88/71/80.68181818181819`
- Retained net/delta: `783c/152c`
- Skipped W/L/net: `14/3/-152c`
- Blockers: `none`

### Entry-Conditioned Posterior Diagnostic

- Checks whether the +5pp posterior lift survives across physical buckets on the fixed raw p50 entry slice.
- `all`: settled `172`, W/L `101/71`, best `book_probability`, best brier `0.21744593023255815`, plus05 delta `0.006406016572098855`
- `early_markets`: settled `86`, W/L `54/32`, best `noise_shrink_light_probability`, best brier `0.22497590749289878`, plus05 delta `0.0024814383720930255`
- `late_markets`: settled `86`, W/L `47/39`, best `book_probability`, best brier `0.2078046511627907`, plus05 delta `0.010330594772104656`
- `approved_entries`: settled `10`, W/L `10/0`, best `entry_conditioned_plus05_probability`, best brier `0.003762082003099995`, plus05 delta `-0.0078068249599000045`
- `shadow_rejected_actionable`: settled `162`, W/L `91/71`, best `book_probability`, best brier `0.22847901234567902`, plus05 delta `0.007283352469135834`
- `near_strike_abs_d_lte_025`: settled `92`, W/L `47/45`, best `book_probability`, best brier `0.24231413043478262`, plus05 delta `0.0061215250000000165`
- `away_from_strike_abs_d_gt_025`: settled `80`, W/L `54/26`, best `book_probability`, best brier `0.1888475`, plus05 delta `0.006733181880012512`
- `high_recross`: settled `165`, W/L `94/71`, best `book_probability`, best brier `0.22500727272727272`, plus05 delta `0.006995260606060594`
- `lower_recross`: settled `7`, W/L `7/0`, best `entry_conditioned_plus05_probability`, best brier `0.0039957426211428525`, plus05 delta `-0.007483307085571433`
- `spectral_dominant_factor`: settled `168`, W/L `99/69`, best `book_probability`, best brier `0.21935238095238094`, plus05 delta `0.006037755657148813`
- `raw_p_50_60`: settled `87`, W/L `46/41`, best `book_probability`, best brier `0.24021724137931036`, plus05 delta `0.003928005747126456`
- `raw_p_60_plus`: settled `85`, W/L `55/30`, best `book_probability`, best brier `0.19413882352941175`, plus05 delta `0.008942333534129376`
- `ask_lte_60`: settled `119`, W/L `58/61`, best `book_probability`, best brier `0.24602352941176472`, plus05 delta `0.010443987394958054`
- `ask_gt_60`: settled `53`, W/L `43/10`, best `entry_conditioned_plus05_probability`, best brier `0.14056939335696225`, plus05 delta `-0.0026603707471509475`

### Source-Aware FV Overlay Validator

- Tests approved-entry book anchoring plus target-coverage strong-row sharpening as one FV overlay.
- Rows/settled: `285/285`
- Approved/rejected settled: `180/105`
- Simulated share: `36.8%`
- Best overlay: `book_probability`
- Evidence blockers: `simulated_share_gt_35pct`
- Best combined FV overlay is book_probability with Brier delta -0.008784259450245635 and logloss delta -0.04014041423512027.
- Evidence mix is 180 approved settled rows and 105 target/rejected settled rows.
- Simulated/rejected share is 36.84%.
- `book_probability`: Brier/logloss d `-0.008784259450245635/-0.04014041423512027`, cal err `0.03985964912280693`
- `source_aware_approved_book_target_raw`: Brier/logloss d `-0.0021889532646526544/-0.02671694969016758`, cal err `0.010430456140350874`
- `source_aware_approved_book_target_logit125_p60_only`: Brier/logloss d `-0.00047867059736544926/-0.02337638854671964`, cal err `0.0015201404591436152`
- `raw_probability`: Brier/logloss d `0.0/0.0`, cal err `-0.05661049122807027`

### Source-Aware FV Robustness Audit

- Perturbs the candidate by removing each market and checking source slices.
- Full Brier/logloss delta: `-0.00047867059736544926/-0.02337638854671964`
- Leave-one-market failures: `12`
- Dominant market Brier-delta share: `733.6%`
- Blockers: `leave_one_market_failure, single_market_contribution_gt_50pct`
- source `approved_entry`: settled `180`, best `book_probability`, source-aware rank `2`, d brier/logloss `-0.0034658426690333533/-0.042301837009431964`
- source `rejected_actionable`: settled `105`, best `book_probability`, source-aware rank `5`, d brier/logloss `0.004642195811208116/0.00906723738935844`
- top market contribution `KXBTC15M-26MAY051715-15`: contribution `0.003511609115581238`, kept d brier `0.0030329385182157886`
- top market contribution `KXBTC15M-26MAY060330-30`: contribution `0.003243903390046099`, kept d brier `0.0027652327926806497`
- top market contribution `KXBTC15M-26MAY052245-45`: contribution `0.0022453301785405333`, kept d brier `0.001766659581175084`

### Source-Aware FV Promotion Audit

- Ready for implementation planning: `False`
- Overlay: `book_probability`
- Settled/approved/simulated/share: `285/180/105/36.8%`
- Brier/logloss delta: `-0.008784259450245635/-0.04014041423512027`
- Robustness blockers: `leave_one_market_failure, single_market_contribution_gt_50pct`
- blocker `expected_overlay_is_best`: actual `book_probability`, required `source_aware_approved_book_target_logit125_p60_only`
- blocker `simulated_share_lte_35pct`: actual `0.3684210526315789`, required `<= 0.35`
- blocker `freeze_audit_no_failures`: actual `1`, required `0`
- blocker `robustness_audit_no_blockers`: actual `['leave_one_market_failure', 'single_market_contribution_gt_50pct']`, required `none`

### Approved-Entry State Valves

- Actual-only diagnostic for same-market reentry and raw/book disagreement.
- Rows/markets: `173/107`
- Best policy: `same_side_reentry_gap_lte_15pp`
- Best actual-only state valve is same_side_reentry_gap_lte_15pp with delta 250.0c vs current approved entries.
- Control approved entries are 173 rows with gross 823.0c.
- This is diagnostic only because it is evaluated on already-approved live/shadow entries, not a frozen future promotion slice.
- `same_side_reentry_gap_lte_15pp`: entries `165`, W/L `141/24`, coverage `100.0%`, gross/delta `1073c/250c`, skipped gross `-250c`
- `same_side_reentry_gap_lte15_and_book_not_down10`: entries `165`, W/L `141/24`, coverage `100.0%`, gross/delta `1073c/250c`, skipped gross `-250c`
- `same_side_reentry_book_not_down_10pp`: entries `168`, W/L `144/24`, coverage `100.0%`, gross/delta `1045c/222c`, skipped gross `-222c`
- `raw_book_gap_lte_15pp`: entries `146`, W/L `127/19`, coverage `92.5%`, gross/delta `1035c/212c`, skipped gross `-212c`
- `raw_book_gap_lte_20pp`: entries `156`, W/L `134/22`, coverage `94.4%`, gross/delta `1001c/178c`, skipped gross `-178c`

### Frozen Approved-Entry State Valve

- Forward-only validator for the fixed same-side reentry gap valve.
- Freeze timestamp UTC: `2026-05-06T02:42:53.253731+00:00`
- Candidate entries/W-L/gross: `138/122-16/885c`
- Control entries/W-L/gross: `144/127-17/705c`
- Delta/coverage/skipped: `180c/100.0%/6`
- Blockers: `none`

### Danger-Zone Entry Valve

- Actual-only diagnostic for raw/book overconfidence and repeated same-side entries.
- Rows/markets: `173/107`
- Best policy: `skip_reentry_gap15_or_gap30`
- Best danger-zone policy is skip_reentry_gap15_or_gap30 with delta 322.0c and coverage 99.06542056074767%.
- Control gross is 823.0c over 173 entries.
- Discovery-only: this must be frozen and validated forward before promotion.
- `skip_reentry_gap15_or_gap30`: entries `161`, W/L `139/22`, coverage `99.1%`, gross/delta `1145c/322c`, skipped gross `-322c`
- `skip_raw_book_gap_gt30`: entries `168`, W/L `144/24`, coverage `99.1%`, gross/delta `917c/94c`, skipped gross `-94c`
- `current_v28_approved_all`: entries `173`, W/L `146/27`, coverage `100.0%`, gross/delta `823c/0c`, skipped gross `0c`
- `skip_reentry_or_gap30`: entries `112`, W/L `95/17`, coverage `99.1%`, gross/delta `604c/-219c`, skipped gross `219c`
- `skip_same_side_reentry`: entries `116`, W/L `97/19`, coverage `100.0%`, gross/delta `532c/-291c`, skipped gross `291c`

### Frozen Danger-Zone Entry Valve

- Forward-only validator for the fixed skip_reentry_gap15_or_gap30 rule.
- Freeze timestamp UTC: `2026-05-06T03:09:58.042066+00:00`
- Candidate entries/W-L/gross: `134/119-15/973c`
- Control entries/W-L/gross: `142/125-17/715c`
- Delta/coverage/skipped: `258c/100.0%/8`
- Blockers: `none`

### Danger-Zone FV Calibration

- Tests whether raw/book overconfidence is a probability error, not only an entry P&L problem.
- Rows/markets: `173/107`
- Best overlay: `danger_to_book`
- Best danger-zone FV overlay is danger_to_book with Brier/logloss deltas -0.011340997078595372/-0.0661185329043299.
- Danger-zone rows are 12/173 with gross -322.0c.
- Discovery-only: any useful overlay needs a frozen forward validator before promotion.
- `danger_to_book`: rows `173`, W/L `146/27`, avg p/win `0.8605982138728323/0.8439306358381503`, d brier/logloss `-0.011340997078595372/-0.0661185329043299`
- `danger_cap_gap15`: rows `173`, W/L `146/27`, avg p/win `0.871002838150289/0.8439306358381503`, d brier/logloss `-0.01045660401501157/-0.0633689292960104`
- `danger_cap_gap20`: rows `173`, W/L `146/27`, avg p/win `0.8735913063583814/0.8439306358381503`, d brier/logloss `-0.00936611321784972/-0.05968631864211782`
- `danger_halfway_to_book`: rows `173`, W/L `146/27`, avg p/win `0.8722429046242774/0.8439306358381503`, d brier/logloss `-0.008425793936114173/-0.059393549035959003`
- `book_probability`: rows `173`, W/L `146/27`, avg p/win `0.7773410404624277/0.8439306358381503`, d brier/logloss `-0.0048166936698150475/-0.04865443082318277`

### Frozen Danger-Zone FV Calibration

- Forward-only validator for fixed raw/book/danger_to_book probability overlays.
- Freeze timestamp UTC: `2026-05-06T03:14:35.467881+00:00`
- Future rows/markets/danger rows: `142/84/8`
- Best overlay: `danger_to_book`
- `danger_to_book`: rows `142`, d brier/logloss `-0.004051658561887328/-0.05274815488405854`, blockers `none`
- `raw_probability`: rows `142`, d brier/logloss `0.0/0.0`, blockers `none`
- `book_probability`: rows `142`, d brier/logloss `0.004996192972542238/-0.02616504629059274`, blockers `brier_not_better_than_raw`

### Danger-Zone Robustness Audit

- Leave-one-market-out check for the danger-zone entry valve and danger-to-book FV overlay.
- Entry robustness pass: `True`
- FV robustness pass: `True`
- Entry full-sample delta: `322c`
- FV Brier/logloss delta: `-0.011340997078595372/-0.0661185329043299`
- Leave-one failures entry/FV: `0/0`
- remove `KXBTC15M-26MAY062015-15`: entry delta `128c`, FV d brier/logloss `-0.011449548600376475/-0.06534539631428271`
- remove `KXBTC15M-26MAY051715-15`: entry delta `252c`, FV d brier/logloss `-0.0062822262930117695/-0.05273482763335363`
- remove `KXBTC15M-26MAY060800-00`: entry delta `290c`, FV d brier/logloss `-0.012057211721473685/-0.06853596427361702`

### Book-Disagreement Trajectory FV

- Tests whether raw FV should shrink toward book when book rejects the same-side thesis.
- Rows/markets/market-sides: `21031/176/350`
- View approved_only best variant is gap15_or_drawdown10 with Brier/logloss deltas -0.009376900694792453/-0.06120296241970963.
- View first_per_market_side best variant is book_probability with Brier/logloss deltas -0.015092992568571412/-0.05257090757616956.
- View last_per_market_side best variant is book_probability with Brier/logloss deltas -0.02403667592009142/-0.12451779896646292.
- View all_observations best variant is book_probability with Brier/logloss deltas -0.007492661082343172/-0.02034393845703447.
- Repeated observation views are diagnostic only; first/last per market-side are less autocorrelated.
- view `approved_only`: best `gap15_or_drawdown10` d brier/logloss `-0.009376900694792453/-0.06120296241970963`; candidate d `-0.009376900694792453/-0.06120296241970963`
- view `first_per_market_side`: best `book_probability` d brier/logloss `-0.015092992568571412/-0.05257090757616956`; candidate d `-0.004933453734482729/-0.020704827410331972`
- view `last_per_market_side`: best `book_probability` d brier/logloss `-0.02403667592009142/-0.12451779896646292`; candidate d `-0.010486568159295762/-0.055005169313760316`

### Frozen Book-Trajectory FV

- Forward-only validator for fixed gap15_or_drawdown10 FV shrinkage.
- Freeze timestamp UTC: `2026-05-06T02:47:06.099693+00:00`
- Future rows/markets/market-sides: `16371/139/278`
- view `approved_only`: rows `185`, d brier/logloss `-0.006465489121030052/-0.058536085976903574`, blockers `none`
- view `first_per_market_side`: rows `278`, d brier/logloss `-0.005829965412330246/-0.025293489455758156`, blockers `none`
- view `last_per_market_side`: rows `278`, d brier/logloss `-0.007015796044586763/-0.05085760273030587`, blockers `none`
- view `all_observations`: rows `16371`, d brier/logloss `-0.0022175152031330414/-0.006440429569180506`, blockers `none`

### Book-Trajectory Entry Projection

- Discovery-only test of whether trajectory-adjusted FV creates broad entry economics.
- Denominator markets: `176`
- Best 75-90% coverage row is gap15_or_drawdown10_p50_edge0 with coverage 87.5 and gross 556.0c.
- Raw p50 baseline has coverage 88.06818181818181 and gross 539.0c.
- This is discovery-only because projected entries use observed shadow opportunities, not actual fills.
- `gap15_or_drawdown10_p50_edge0`: entries `154`, W/L `115/39`, coverage `87.5%`, gross `556c`, avg edge `0.03762731298701298`
- `gap15_or_drawdown10_p52_edge0`: entries `153`, W/L `115/38`, coverage `86.9%`, gross `543c`, avg edge `0.0375642954248366`
- `raw_probability_p50_edge0`: entries `155`, W/L `113/42`, coverage `88.1%`, gross `539c`, avg edge `0.050319116129032254`
- `raw_probability_p52_edge0`: entries `154`, W/L `114/40`, coverage `87.5%`, gross `472c`, avg edge `0.046750071428571426`
- `gap15_or_drawdown10_p60_edge0`: entries `149`, W/L `114/35`, coverage `84.7%`, gross `156c`, avg edge `0.03981108590604027`
- `raw_probability_p60_edge0`: entries `152`, W/L `112/40`, coverage `86.4%`, gross `27c`, avg edge `0.05950922368421052`

### Frozen Pending Monitor

- Shows unresolved post-freeze rows that will affect frozen validators after settlement.
- Pending state-valve/book-trajectory rows: `0/0`
- book-trajectory pending adjusted rows in displayed tail: `0`

### Frozen Forward Scorecard

- Unified post-freeze scorecard for frozen state/FV candidates.
- State valve has 138 settled post-freeze rows with delta 180.0c.
- Danger-zone valve has 134 settled post-freeze rows with delta 258.0c.
- Book-trajectory all-observation FV delta is -0.0022175152031330414/-0.006440429569180506.
- Current v28 exits are 823.0c over 173 trades; simple exit book-gap suppressors are not better.
- State settled/gross/delta: `138/885c/180c`
- Book trajectory all-observation rows and Brier/logloss delta: `16371/-0.0022175152031330414/-0.006440429569180506`
- Control gross/hold/exit value: `823c/2304c/-1481c`

### Entry-Conditioned Lift Plateau

- Tests whether the posterior lift is broad or point-fit. +5pp remains the frozen conservative challenger.
- Best discovery lift: `-4pp`
- Improving lift values: `[-7, -6, -5, -4, -3, -2, -1]`
- lift `-4pp`: brier `0.22246741282879653`, delta `-0.0015274125581395126`, logloss delta `-0.0010140693993765382`, avg p `0.5863019593023255`
- lift `-3pp`: brier `0.22254926596833138`, delta `-0.0014455594186046639`, logloss delta `-0.0013696211569103056`, avg p `0.5963019593023255`
- lift `-5pp`: brier `0.2225855596892616`, delta `-0.0014092656976744389`, logloss delta `-0.00026243367892286873`, avg p `0.5763019593023255`
- lift `-2pp`: brier `0.22283111910786627`, delta `-0.0011637062790697816`, logloss delta `-0.0013237698806031206`, avg p `0.6063019593023256`
- lift `-6pp`: brier `0.22290370654972674`, delta `-0.001091118837209304`, logloss delta `0.0008811833985532536`, avg p `0.5663019593023256`

### Entry-Conditioned Jackknife

- Removes one market at a time and checks whether +5pp still improves calibration versus raw.
- Jackknife pass: `False`
- Failure count: `172`
- Full-sample Brier/logloss deltas: `0.006406016572098855/0.011122342497338011`
- worst removal `KXBTC15M-26MAY070815-15`: kept count `171`, brier delta `0.006720585674859697`, logloss delta `0.011743538009070353`
- worst removal `KXBTC15M-26MAY061900-00`: kept count `171`, brier delta `0.006720207312286536`, logloss delta `0.011742853923131125`
- worst removal `KXBTC15M-26MAY060715-15`: kept count `171`, brier delta `0.006720203218719301`, logloss delta `0.011742846531101248`

### Entry-Conditioned Data Quality

- Causality and row-quality audit for the raw p50 fixed entry slice.
- Data-quality pass: `True`
- Selected/unique/settled: `172/172/172`
- Approved/shadow rows: `10/162`
- Flag counts: `{}`

### Raw p52 Delta Diagnostic

- Explains what raw p52 removes from raw p50 without treating the discovery slice as promotion evidence.
- Base rows kept by p52: count `169`, settled `169`, net `-32c`, brier `0.22346650192552664`
- Actual p52 rows: count `169`, settled `169`, net `69c`, brier `0.2160618340284497`
- Skipped by p52: count `3`, settled `3`, net `-49c`, brier `0.25375704704633334`
- Changed p52 selections among kept markets: `23`
- Changed-selection net delta: `101c`
- Skipped-row tags:
  - `low_edge_lt_5pp`: count `2`, net `-2c`, brier `0.25311650548500003`
  - `high_recross`: count `3`, net `-49c`, brier `0.25375704704633334`
  - `near_strike`: count `3`, net `-49c`, brier `0.25375704704633334`
  - `long_horizon`: count `1`, net `-102c`, brier `0.260170384761`

### Raw p52 Confirmation Path

- Separates p52 waiting behavior into side flips, same-side confirmation, and pay-up paths.
- Changed paths: `23`, resolved `23`, confirm-base net `101c`, avg delay `104.71853260869565` seconds
- Avg Brier base/confirm: `0.24918775508813046/0.19477954314873913`
- `minor_wait`: count `3`, base net `294c`, confirm net `286c`, delta `-8c`
- `pay_up_for_probability_confirmation`: count `11`, base net `486c`, confirm net `223c`, delta `-263c`
- `pay_up_without_probability_confirmation`: count `1`, base net `-102c`, confirm net `-108c`, delta `-6c`
- `side_flip_confirmation`: count `8`, base net `-235c`, confirm net `143c`, delta `378c`

### Frozen Raw Physics Challengers

- Freeze timestamp UTC: `2026-05-05T22:57:17.938743+00:00`
- Forward market denominator: `154`
- Future candidate rows: `2578`
- `v28_raw_p52_edge0`: entries `150`, settled `150`, coverage `97.40259740259741`, net `-879c`, brier `0.22290984774580663`, fv blockers `coverage_too_high, net_not_positive`, execution blockers `simulated_share_gt_0.35, coverage_too_high, net_not_positive`
- `raw_fee_friction_p50_edge0`: entries `149`, settled `149`, coverage `96.75324675324676`, net `-555c`, brier `0.2170692071872886`, fv blockers `coverage_too_high, net_not_positive`, execution blockers `simulated_share_gt_0.35, coverage_too_high, net_not_positive`
- `raw_touch_friction_p50_edge0`: entries `149`, settled `149`, coverage `96.75324675324676`, net `-515c`, brier `0.21087049964792617`, fv blockers `coverage_too_high, net_not_positive`, execution blockers `simulated_share_gt_0.35, coverage_too_high, net_not_positive`

### Raw p52 Side-Flip Candidate

- Discovery-only candidate: raw p50 entries, except use p52 when it confirms the opposite side.
- `v28_raw_p50_edge0`: entries `172`, settled `172`, coverage `95.02762430939227`, net `-81c`, brier `0.22399482538693605`, modes base/sideflip `0/0`
- `v28_raw_p52_edge0`: entries `169`, settled `169`, coverage `93.37016574585635`, net `69c`, brier `0.2160618340284497`, modes base/sideflip `0/0`
- `raw_p50_else_p52_sideflip_confirm`: entries `172`, settled `172`, coverage `95.02762430939227`, net `297c`, brier `0.21994523198214536`, modes base/sideflip `164/8`

### Frozen Raw p52 Side-Flip Challenger

- Freeze timestamp UTC: `2026-05-05T23:14:05.888026+00:00`
- Forward market denominator: `153`
- Future candidate rows: `150`
- `raw_p50_else_p52_sideflip_confirm`: entries `150`, settled `150`, coverage `98.0392156862745`, net `-819c`, brier `0.22572648929082664`, modes base/sideflip `143/7`, fv blockers `coverage_too_high, net_not_positive`, execution blockers `simulated_share_gt_0.35, coverage_too_high, net_not_positive`

### Raw p52 Recross-Escape Candidate

- Discovery-only candidate: keeps broad raw p52, but weak near-strike/high-recross rows may follow a later opposite p52 confirmation with >=5pp edge.
- `v28_raw_p52_edge0_base`: entries `169`, settled `169`, coverage `93.37016574585635`, net `69c`, brier `0.2160618340284497`, modes `{'base': 169}`, boot p10/p>0 `-1450c/0.529`
- `p52_recross_escape_opp120_skip_edge5`: entries `149`, settled `149`, coverage `82.32044198895028`, net `749c`, brier `0.2045106998639866`, modes `{'base': 131, 'danger_follow_opposite': 9, 'danger_keep_high_edge': 4, 'danger_no_opposite_keep': 5}`, boot p10/p>0 `-664c/0.752`
- `p52_recross_escape_opp240_skip_edge5`: entries `152`, settled `152`, coverage `83.97790055248619`, net `330c`, brier `0.2084564772687763`, modes `{'base': 131, 'danger_follow_opposite': 14, 'danger_keep_high_edge': 4, 'danger_no_opposite_keep': 3}`, boot p10/p>0 `-1084c/0.6235`
- `p52_recross_escape_opp240_skip_edge10`: entries `149`, settled `149`, coverage `82.32044198895028`, net `224c`, brier `0.20776897810351677`, modes `{'base': 131, 'danger_follow_opposite': 14, 'danger_keep_high_edge': 4}`, boot p10/p>0 `-1215c/0.5775`
- `p52_recross_escape_opp240_oppedge5_keep`: entries `169`, settled `169`, coverage `93.37016574585635`, net `491c`, brier `0.21496096587224262`, modes `{'base': 131, 'danger_follow_opposite': 8, 'danger_keep_high_edge': 4, 'danger_no_opposite_keep': 26}`, boot p10/p>0 `-1022c/0.665`

### Frozen Raw p52 Recross-Escape Challenger

- Freeze timestamp UTC: `2026-05-06T00:57:12.867086+00:00`
- Forward market denominator: `146`
- Future candidate rows: `804`
- `v28_raw_p52_edge0_base`: entries `143`, settled `143`, coverage `97.94520547945206`, net `-947c`, brier `0.2224169008928951`, modes `{'base': 143}`, fv blockers `coverage_too_high, net_not_positive`, execution blockers `simulated_share_gt_0.35, coverage_too_high, net_not_positive`
- `p52_recross_escape_opp240_oppedge5_keep`: entries `143`, settled `143`, coverage `97.94520547945206`, net `-753c`, brier `0.22004310838604896`, modes `{'base': 117, 'danger_follow_opposite': 5, 'danger_keep_high_edge': 2, 'danger_no_opposite_keep': 19}`, fv blockers `coverage_too_high, net_not_positive`, execution blockers `simulated_share_gt_0.35, coverage_too_high, net_not_positive`

### Recross-Escape Probability Calibration

- Discovery-only fixed-row FV calibration for the recross-escape selector; P&L is unchanged.
- Policy: `p52_recross_escape_opp240_oppedge5_keep`, entries/settled `169/169`
- `raw_probability`: Brier `0.21496096587224262` delta `0.0`, logloss `0.6124233567960218` delta `0.0`, ECE `0.05918872781065087`
- `logit110_probability`: Brier `0.2155067875056291` delta `0.000545821633386484`, logloss `0.6127474599904696` delta `0.0003241031944478667`, ECE `0.04734251907553898`
- `logit125_probability`: Brier `0.2169422419193256` delta `0.0019812760470829804`, logloss `0.6151696107745921` delta `0.002746253978570312`, ECE `0.06141259017963272`
- `plus03_probability`: Brier `0.21732977445449705` delta `0.002368808582254439`, logloss `0.6161087734689641` delta `0.00368541667294231`, ECE `0.06471857988165686`
- `conservative_mode_probability`: Brier `0.21760288226514793` delta `0.0026419163929053135`, logloss `0.6170072077237277` delta `0.004583850927705968`, ECE `0.06045822485207102`
- Lift plateau: best lift `-0.02`, improving lifts `[-0.04, -0.03, -0.02, -0.01]`
- +5pp jackknife: Brier improved `0/169` slices, logloss improved `0/169`, worst Brier delta `0.005244407214291674`

### Frozen Recross-Escape Attribution

- Forward-only physical attribution for the recross-escape challenger.
- Freeze timestamp UTC: `2026-05-06T00:57:12.867086+00:00`
- Baseline entries/settled/W-L/net: `143/143/83-60/-949c`
- Challenger entries/settled/W-L/net: `143/143/84-59/-755c`
- Best settled FV overlay so far: `raw_probability` Brier `0.22004310838604896`, logloss `0.6213685752213018`
- `all`: entries `143`, settled `143`, W/L `84/59`, net `-755c`, Brier `0.22004310838604896`
- `ask:cheap_lte55`: entries `63`, settled `63`, W/L `27/36`, net `-876c`, Brier `0.26785397278138096`
- `ask:expensive_gt70`: entries `27`, settled `27`, W/L `25/2`, net `497c`, Brier `0.07325281921566666`
- `ask:mid_55_70`: entries `53`, settled `53`, W/L `32/21`, net `-376c`, Brier `0.23799128481424528`
- `edge:modest_2_5pp`: entries `37`, settled `37`, W/L `26/11`, net `315c`, Brier `0.175112115762`
- `edge:thin_lt2pp`: entries `47`, settled `47`, W/L `25/22`, net `-787c`, Brier `0.2598673800826383`
- `edge:wide_ge5pp`: entries `59`, settled `59`, W/L `33/26`, net `-283c`, Brier `0.21649575173096608`
- `mode:base`: entries `117`, settled `117`, W/L `72/45`, net `-407c`, Brier `0.21398663943076068`

### Recross-Escape Sample Plan

- Candidate: `p52_recross_escape_opp240_oppedge5_keep_plus05_probability`
- Freeze timestamp UTC: `2026-05-06T00:57:12.867086+00:00`
- Forward denominator: `146`, excluded in-progress `1`
- Settled rows to 30: `0`, pending `0`, additional after pending `0`
- Actual entries needed for simulated share <=35%: `240`
- FV blockers: `coverage_too_high, net_not_positive`
- Execution blockers: `simulated_share_gt_0.35, coverage_too_high, net_not_positive`

### Frozen Noise-Floor Shrinkage Challengers

- Freeze timestamp UTC: `2026-05-05T23:22:57.684142+00:00`
- Forward market denominator: `152`
- Future candidate rows: `2462`
- `noise_shrink_light_p50_edge1`: entries `146`, settled `146`, coverage `96.05263157894737`, net `10c`, brier `0.21553304553452313`, fv blockers `coverage_too_high`, execution blockers `simulated_share_gt_0.35, coverage_too_high`
- `noise_shrink_light_p50_edge0`: entries `149`, settled `149`, coverage `98.02631578947368`, net `-381c`, brier `0.2188775252427696`, fv blockers `coverage_too_high, net_not_positive`, execution blockers `simulated_share_gt_0.35, coverage_too_high, net_not_positive`

### Frozen Raw Entry Calibrated Probability

- Freeze timestamp UTC: `2026-05-05T23:30:17.615882+00:00`
- Forward market denominator: `152`
- Future entry rows: `150`
- `book_probability`: entries `150`, settled `150`, coverage `98.68421052631578`, brier `0.21780866666666668`, delta `-0.012290468851073322`, net `-1009c`, blockers `coverage_too_high, bucket_brier_not_better_than_raw`
- `noise_shrink_light_probability`: entries `150`, settled `150`, coverage `98.68421052631578`, brier `0.22741693678941857`, delta `-0.0026821987283214277`, net `-1009c`, blockers `coverage_too_high, bucket_brier_not_better_than_raw`
- `raw_probability`: entries `150`, settled `150`, coverage `98.68421052631578`, brier `0.23009913551774`, delta `0.0`, net `-1009c`, blockers `coverage_too_high`
- `entry_conditioned_logit125_p60_only_probability`: entries `150`, settled `150`, coverage `98.68421052631578`, brier `0.23308019377657863`, delta `0.002981058258838626`, net `-1009c`, blockers `coverage_too_high, brier_not_better_than_raw, bucket_brier_not_better_than_raw`
- `entry_conditioned_logit125_probability`: entries `150`, settled `150`, coverage `98.68421052631578`, brier `0.23344281970077232`, delta `0.003343684183032325`, net `-1009c`, blockers `coverage_too_high, brier_not_better_than_raw, bucket_brier_not_better_than_raw`
- `entry_conditioned_plus03_probability`: entries `150`, settled `150`, coverage `98.68421052631578`, brier `0.23532351238708`, delta `0.005224376869339992`, net `-1009c`, blockers `coverage_too_high, brier_not_better_than_raw, bucket_brier_not_better_than_raw`
- `entry_conditioned_plus05_probability`: entries `150`, settled `150`, coverage `98.68421052631578`, brier `0.2398028518537467`, delta `0.009703716336006696`, net `-1009c`, blockers `coverage_too_high, brier_not_better_than_raw, bucket_brier_not_better_than_raw`

### Calibrated FV Forward Monitor

- Tracks clean forward markets, pending selections, and missed markets after the calibrated-FV freeze.
- Clean forward markets: `152`
- Selected/settled/pending/missed: `150/150/0/2`
- Coverage: `98.68421052631578`
- Settled W/L net: `83/67` `-1009c`
- Calibration deltas +5 minus raw Brier/logloss: `1.4555574504010014/2.734739962832429`
- `KXBTC15M-26MAY051945-45` selected `True` close `settled` sec_to/since_close `-149848.173032` side `yes` p_raw/+5/ask `0.613944/0.6639440000000001/0.51` won `True` net `94c` brier/logloss d `-0.036105600000000015/-0.07829408979447428`
- `KXBTC15M-26MAY052000-00` selected `True` close `settled` sec_to/since_close `-148948.173032` side `no` p_raw/+5/ask `0.665463/0.7154630000000001/0.63` won `True` net `70c` brier/logloss d `-0.03095370000000003/-0.07244684657562883`
- `KXBTC15M-26MAY052015-15` selected `True` close `settled` sec_to/since_close `-148048.173032` side `no` p_raw/+5/ask `0.567861/0.617861/0.49` won `False` net `-102c` brier/logloss d `0.059286100000000064/0.1229628789840499`
- `KXBTC15M-26MAY052030-30` selected `True` close `settled` sec_to/since_close `-147148.173032` side `yes` p_raw/+5/ask `0.54078/0.5907800000000001/0.47` won `False` net `-98c` brier/logloss d `0.05657800000000007/0.11527648932546397`
- `KXBTC15M-26MAY052045-45` selected `True` close `settled` sec_to/since_close `-146248.173032` side `yes` p_raw/+5/ask `0.590266/0.640266/0.56` won `False` net `-116c` brier/logloss d `0.06152660000000004/0.13014329921308632`
- `KXBTC15M-26MAY052100-00` selected `True` close `settled` sec_to/since_close `-145348.173032` side `yes` p_raw/+5/ask `0.565554/0.615554/0.46` won `True` net `104c` brier/logloss d `-0.040944600000000025/-0.08471689361269757`
- `KXBTC15M-26MAY052115-15` selected `True` close `settled` sec_to/since_close `-144448.173032` side `yes` p_raw/+5/ask `0.571476/0.621476/0.53` won `True` net `90c` brier/logloss d `-0.04035240000000001/-0.08387480635172867`
- `KXBTC15M-26MAY052130-30` selected `True` close `settled` sec_to/since_close `-143548.173032` side `yes` p_raw/+5/ask `0.822836/0.8728360000000001/0.8` won `True` net `37c` brier/logloss d `-0.015216400000000008/-0.05899077037096018`
- `KXBTC15M-26MAY052145-45` selected `True` close `settled` sec_to/since_close `-142648.173032` side `yes` p_raw/+5/ask `0.865417/0.915417/0.83` won `True` net `32c` brier/logloss d `-0.01095830000000001/-0.056168227470494755`
- `KXBTC15M-26MAY052200-00` selected `True` close `settled` sec_to/since_close `-141748.173032` side `no` p_raw/+5/ask `0.551743/0.601743/0.52` won `False` net `-108c` brier/logloss d `0.05767430000000007/0.11826920311424549`
- `KXBTC15M-26MAY052215-15` selected `True` close `settled` sec_to/since_close `-140848.173032` side `no` p_raw/+5/ask `0.809232/0.859232/0.77` won `True` net `43c` brier/logloss d `-0.016576800000000017/-0.05995331726736511`
- `KXBTC15M-26MAY052230-30` selected `True` close `settled` sec_to/since_close `-139948.173032` side `no` p_raw/+5/ask `0.730624/0.7806240000000001/0.65` won `True` net `66c` brier/logloss d `-0.02443760000000001/-0.06619463631999467`
- `KXBTC15M-26MAY052245-45` selected `True` close `settled` sec_to/since_close `-139048.173032` side `no` p_raw/+5/ask `0.643789/0.693789/0.57` won `False` net `-118c` brier/logloss d `0.06687890000000007/0.1512488450951175`
- `KXBTC15M-26MAY052300-00` selected `True` close `settled` sec_to/since_close `-138148.173032` side `yes` p_raw/+5/ask `0.918967/0.968967/0.85` won `True` net `26c` brier/logloss d `-0.0056033000000000055/-0.05298034246864499`
- `KXBTC15M-26MAY052315-15` selected `True` close `settled` sec_to/since_close `-137248.173032` side `yes` p_raw/+5/ask `0.884999/0.934999/0.81` won `True` net `-41c` brier/logloss d `-0.009000100000000007/-0.05495894470561023`
- `KXBTC15M-26MAY052330-30` selected `True` close `settled` sec_to/since_close `-136348.173032` side `no` p_raw/+5/ask `0.659176/0.709176/0.63` won `False` net `-130c` brier/logloss d `0.06841760000000002/0.15864794180784303`
- `KXBTC15M-26MAY052345-45` selected `True` close `settled` sec_to/since_close `-135448.173032` side `no` p_raw/+5/ask `0.636767/0.686767/0.63` won `True` net `70c` brier/logloss d `-0.03382330000000003/-0.07559126736704763`
- `KXBTC15M-26MAY060000-00` selected `True` close `settled` sec_to/since_close `-134548.173032` side `no` p_raw/+5/ask `0.576655/0.6266550000000001/0.56` won `False` net `-116c` brier/logloss d `0.06016550000000004/0.12568452432714228`
- `KXBTC15M-26MAY060015-15` selected `True` close `settled` sec_to/since_close `-133648.173032` side `yes` p_raw/+5/ask `0.532782/0.582782/0.52` won `False` net `-108c` brier/logloss d `0.055778200000000056/0.11318709119851977`
- `KXBTC15M-26MAY060030-30` selected `True` close `settled` sec_to/since_close `-132748.173032` side `yes` p_raw/+5/ask `0.617077/0.667077/0.51` won `False` net `-106c` brier/logloss d `0.06420770000000009/0.1399226925709418`
- `KXBTC15M-26MAY060045-45` selected `True` close `settled` sec_to/since_close `-131848.173032` side `no` p_raw/+5/ask `0.826505/0.8765050000000001/0.79` won `True` net `39c` brier/logloss d `-0.014849500000000009/-0.05873644200202316`
- `KXBTC15M-26MAY060100-00` selected `True` close `settled` sec_to/since_close `-130948.173032` side `yes` p_raw/+5/ask `0.799928/0.849928/0.79` won `False` net `-161c` brier/logloss d `0.08249280000000014/0.28756212283047833`
- `KXBTC15M-26MAY060115-15` selected `True` close `settled` sec_to/since_close `-130048.173032` side `no` p_raw/+5/ask `0.513971/0.563971/0.51` won `True` net `94c` brier/logloss d `-0.04610290000000006/-0.09283598810634852`
- `KXBTC15M-26MAY060130-30` selected `True` close `settled` sec_to/since_close `-129148.173032` side `no` p_raw/+5/ask `0.616779/0.666779/0.59` won `True` net `78c` brier/logloss d `-0.03582210000000004/-0.07794788170253131`
- `KXBTC15M-26MAY060145-45` selected `True` close `settled` sec_to/since_close `-128248.173032` side `no` p_raw/+5/ask `0.557282/0.6072820000000001/0.55` won `True` net `86c` brier/logloss d `-0.041771800000000026/-0.08592186760539267`
- `KXBTC15M-26MAY060200-00` selected `True` close `settled` sec_to/since_close `-127348.173032` side `yes` p_raw/+5/ask `0.618277/0.668277/0.6` won `True` net `76c` brier/logloss d `-0.03567230000000003/-0.07776618114140282`
- `KXBTC15M-26MAY060215-15` selected `True` close `settled` sec_to/since_close `-126448.173032` side `yes` p_raw/+5/ask `0.583024/0.633024/0.53` won `False` net `-110c` brier/logloss d `0.060802400000000034/0.1277322153648246`
- `KXBTC15M-26MAY060230-30` selected `True` close `settled` sec_to/since_close `-125548.173032` side `no` p_raw/+5/ask `0.574094/0.624094/0.54` won `False` net `-112c` brier/logloss d `0.05990940000000006/0.12487955250929117`
- `KXBTC15M-26MAY060245-45` selected `True` close `settled` sec_to/since_close `-124648.173032` side `no` p_raw/+5/ask `0.660829/0.710829/0.65` won `False` net `-134c` brier/logloss d `0.06858290000000011/0.15948619634839956`
- `KXBTC15M-26MAY060300-00` selected `True` close `settled` sec_to/since_close `-123748.173032` side `yes` p_raw/+5/ask `0.661141/0.711141/0.64` won `True` net `68c` brier/logloss d `-0.031385900000000036/-0.07290359211271108`
- `KXBTC15M-26MAY060315-15` selected `True` close `settled` sec_to/since_close `-122848.173032` side `yes` p_raw/+5/ask `0.512365/0.562365/0.5` won `True` net `96c` brier/logloss d `-0.04626350000000004/-0.09311384359527808`
- `KXBTC15M-26MAY060330-30` selected `True` close `settled` sec_to/since_close `-121948.173032` side `no` p_raw/+5/ask `0.63088/0.68088/0.57` won `False` net `-118c` brier/logloss d `0.06558800000000004/0.14555458682829236`
- `KXBTC15M-26MAY060345-45` selected `True` close `settled` sec_to/since_close `-121048.173032` side `yes` p_raw/+5/ask `0.515105/0.5651050000000001/0.38` won `False` net `-80c` brier/logloss d `0.05401050000000007/0.10882775001206568`
- `KXBTC15M-26MAY060400-00` selected `True` close `settled` sec_to/since_close `-120148.173032` side `yes` p_raw/+5/ask `0.539723/0.589723/0.5` won `False` net `-104c` brier/logloss d `0.056472300000000086/0.11499594082930464`
- `KXBTC15M-26MAY060415-15` selected `True` close `settled` sec_to/since_close `-119248.173032` side `yes` p_raw/+5/ask `0.676831/0.726831/0.67` won `True` net `62c` brier/logloss d `-0.029816900000000035/-0.07127237731112712`
- `KXBTC15M-26MAY060430-30` selected `False` close `None` sec_to/since_close `None` side `None` p_raw/+5/ask `None/None/None` won `None` net `None` brier/logloss d `None/None`
- `KXBTC15M-26MAY060445-45` selected `True` close `settled` sec_to/since_close `-117448.173032` side `no` p_raw/+5/ask `0.636374/0.686374/0.45` won `False` net `-94c` brier/logloss d `0.06613740000000007/0.14792467369469842`
- `KXBTC15M-26MAY060500-00` selected `True` close `settled` sec_to/since_close `-116548.173032` side `no` p_raw/+5/ask `0.674136/0.724136/0.61` won `False` net `-126c` brier/logloss d `0.06991360000000002/0.1665721257586832`
- `KXBTC15M-26MAY060515-15` selected `True` close `settled` sec_to/since_close `-115648.173032` side `yes` p_raw/+5/ask `0.532512/0.582512/0.41` won `False` net `-86c` brier/logloss d `0.055751200000000056/0.11311787858723754`
- `KXBTC15M-26MAY060530-30` selected `True` close `settled` sec_to/since_close `-114748.173032` side `yes` p_raw/+5/ask `0.588889/0.638889/0.54` won `False` net `-112c` brier/logloss d `0.06138890000000008/0.12967786073058096`
- `KXBTC15M-26MAY060545-45` selected `True` close `settled` sec_to/since_close `-113848.173032` side `no` p_raw/+5/ask `0.626642/0.6766420000000001/0.44` won `False` net `-92c` brier/logloss d `0.06516420000000006/0.14377767628770055`
- `KXBTC15M-26MAY060600-00` selected `True` close `settled` sec_to/since_close `-112948.173032` side `no` p_raw/+5/ask `0.792357/0.842357/0.75` won `True` net `47c` brier/logloss d `-0.018264300000000015/-0.06119186705306043`
- `KXBTC15M-26MAY060615-15` selected `True` close `settled` sec_to/since_close `-112048.173032` side `yes` p_raw/+5/ask `0.598388/0.6483880000000001/0.57` won `True` net `41c` brier/logloss d `-0.037661200000000034/-0.08024990961261852`
- `KXBTC15M-26MAY060630-30` selected `True` close `settled` sec_to/since_close `-111148.173032` side `no` p_raw/+5/ask `0.675344/0.7253440000000001/0.66` won `False` net `-136c` brier/logloss d `0.07003440000000005/0.16724675468945915`
- `KXBTC15M-26MAY060645-45` selected `True` close `settled` sec_to/since_close `-110248.173032` side `yes` p_raw/+5/ask `0.598639/0.6486390000000001/0.59` won `True` net `78c` brier/logloss d `-0.03763610000000003/-0.08021757625754333`
- `KXBTC15M-26MAY060700-00` selected `True` close `settled` sec_to/since_close `-109348.173032` side `yes` p_raw/+5/ask `0.527819/0.5778190000000001/0.52` won `True` net `92c` brier/logloss d `-0.04471810000000004/-0.0905072489365617`
- `KXBTC15M-26MAY060715-15` selected `True` close `settled` sec_to/since_close `-108448.173032` side `yes` p_raw/+5/ask `0.501801/0.5518010000000001/0.49` won `True` net `98c` brier/logloss d `-0.047319900000000054/-0.09498384727619591`
- `KXBTC15M-26MAY060730-30` selected `True` close `settled` sec_to/since_close `-107548.173032` side `yes` p_raw/+5/ask `0.594884/0.644884/0.56` won `True` net `84c` brier/logloss d `-0.038011600000000034/-0.08070402710482949`
- `KXBTC15M-26MAY060745-45` selected `True` close `settled` sec_to/since_close `-106648.173032` side `no` p_raw/+5/ask `0.553279/0.603279/0.54` won `True` net `88c` brier/logloss d `-0.042172100000000046/-0.08651738119775654`
- `KXBTC15M-26MAY060800-00` selected `True` close `settled` sec_to/since_close `-105748.173032` side `yes` p_raw/+5/ask `0.523411/0.573411/0.47` won `True` net `102c` brier/logloss d `-0.04515890000000006/-0.09123573077486657`
- `KXBTC15M-26MAY060815-15` selected `True` close `settled` sec_to/since_close `-104848.173032` side `no` p_raw/+5/ask `0.505085/0.555085/0.49` won `True` net `98c` brier/logloss d `-0.04699150000000005/-0.0943945232294865`
- `KXBTC15M-26MAY060830-30` selected `True` close `settled` sec_to/since_close `-103948.173032` side `no` p_raw/+5/ask `0.60073/0.65073/0.59` won `False` net `-122c` brier/logloss d `0.06257300000000005/0.13379261770003692`
- `KXBTC15M-26MAY060845-45` selected `True` close `settled` sec_to/since_close `-103048.173032` side `yes` p_raw/+5/ask `0.506183/0.5561830000000001/0.5` won `False` net `-104c` brier/logloss d `0.05311830000000006/0.1067526879040741`
- `KXBTC15M-26MAY060900-00` selected `True` close `settled` sec_to/since_close `-102148.173032` side `no` p_raw/+5/ask `0.586412/0.6364120000000001/0.58` won `True` net `80c` brier/logloss d `-0.03885880000000003/-0.08182353814096288`
- `KXBTC15M-26MAY060915-15` selected `True` close `settled` sec_to/since_close `-101248.173032` side `no` p_raw/+5/ask `0.672099/0.722099/0.6` won `True` net `76c` brier/logloss d `-0.030290100000000028/-0.07175659750544827`
- `KXBTC15M-26MAY060930-30` selected `True` close `settled` sec_to/since_close `-100348.173032` side `yes` p_raw/+5/ask `0.604377/0.6543770000000001/0.6` won `False` net `-124c` brier/logloss d `0.06293770000000004/0.1351131519519918`
- `KXBTC15M-26MAY060945-45` selected `True` close `settled` sec_to/since_close `-99448.173032` side `no` p_raw/+5/ask `0.761891/0.811891/0.5` won `True` net `96c` brier/logloss d `-0.021310900000000015/-0.06356259386259058`
- `KXBTC15M-26MAY061000-00` selected `True` close `settled` sec_to/since_close `-98548.173032` side `no` p_raw/+5/ask `0.513222/0.563222/0.5` won `True` net `96c` brier/logloss d `-0.04617780000000005/-0.09296536648077547`
- `KXBTC15M-26MAY061015-15` selected `True` close `settled` sec_to/since_close `-97648.173032` side `no` p_raw/+5/ask `0.595554/0.6455540000000001/0.52` won `True` net `92c` brier/logloss d `-0.03794460000000002/-0.08061679808336153`
- `KXBTC15M-26MAY061030-30` selected `True` close `settled` sec_to/since_close `-96748.173032` side `yes` p_raw/+5/ask `0.618153/0.668153/0.61` won `True` net `74c` brier/logloss d `-0.03568470000000003/-0.07778118959458585`
- `KXBTC15M-26MAY061045-45` selected `True` close `settled` sec_to/since_close `-95848.173032` side `no` p_raw/+5/ask `0.601767/0.6517670000000001/0.57` won `False` net `-118c` brier/logloss d `0.06267670000000003/0.13416546516220385`
- `KXBTC15M-26MAY061100-00` selected `True` close `settled` sec_to/since_close `-94948.173032` side `yes` p_raw/+5/ask `0.740374/0.790374/0.74` won `False` net `-151c` brier/logloss d `0.07653740000000009/0.2139171433426852`
- `KXBTC15M-26MAY061115-15` selected `True` close `settled` sec_to/since_close `-94048.173032` side `yes` p_raw/+5/ask `0.533622/0.5836220000000001/0.52` won `False` net `-108c` brier/logloss d `0.055862200000000084/0.11340296258101346`
- `KXBTC15M-26MAY061130-30` selected `True` close `settled` sec_to/since_close `-93148.173032` side `yes` p_raw/+5/ask `0.653101/0.7031010000000001/0.65` won `True` net `66c` brier/logloss d `-0.03218990000000002/-0.07376876341036953`
- `KXBTC15M-26MAY061145-45` selected `True` close `settled` sec_to/since_close `-92248.173032` side `no` p_raw/+5/ask `0.502076/0.552076/0.49` won `True` net `98c` brier/logloss d `-0.04729240000000004/-0.09493421530427382`
- `KXBTC15M-26MAY061200-00` selected `True` close `settled` sec_to/since_close `-91348.173032` side `yes` p_raw/+5/ask `0.848576/0.898576/0.81` won `True` net `35c` brier/logloss d `-0.012642400000000008/-0.057251637574359956`
- `KXBTC15M-26MAY061215-15` selected `True` close `settled` sec_to/since_close `-90448.173032` side `no` p_raw/+5/ask `0.536898/0.586898/0.53` won `False` net `-110c` brier/logloss d `0.05618980000000007/0.11425279636529007`
- `KXBTC15M-26MAY061230-30` selected `True` close `settled` sec_to/since_close `-89548.173032` side `yes` p_raw/+5/ask `0.681329/0.731329/0.68` won `False` net `-140c` brier/logloss d `0.07063290000000011/0.17067163987649003`
- `KXBTC15M-26MAY061245-45` selected `True` close `settled` sec_to/since_close `-88648.173032` side `no` p_raw/+5/ask `0.555732/0.605732/0.52` won `False` net `-108c` brier/logloss d `0.0580732000000001/0.11939710283006677`
- `KXBTC15M-26MAY061300-00` selected `True` close `settled` sec_to/since_close `-87748.173032` side `no` p_raw/+5/ask `0.544132/0.594132/0.54` won `True` net `88c` brier/logloss d `-0.043086800000000064/-0.08790965241643667`
- `KXBTC15M-26MAY061400-00` selected `True` close `settled` sec_to/since_close `-84148.173032` side `no` p_raw/+5/ask `0.97364/0.999999/0.89` won `True` net `-11c` brier/logloss d `-0.0006948495990000027/-0.026712653517923377`
- `KXBTC15M-26MAY061415-15` selected `True` close `settled` sec_to/since_close `-83248.173032` side `no` p_raw/+5/ask `0.519091/0.569091/0.48` won `True` net `100c` brier/logloss d `-0.045590900000000045/-0.09196114605715133`
- `KXBTC15M-26MAY061430-30` selected `True` close `settled` sec_to/since_close `-82348.173032` side `yes` p_raw/+5/ask `0.678512/0.728512/0.67` won `True` net `62c` brier/logloss d `-0.02964880000000003/-0.07110193251200625`
- `KXBTC15M-26MAY061445-45` selected `True` close `settled` sec_to/since_close `-81448.173032` side `no` p_raw/+5/ask `0.724164/0.7741640000000001/0.71` won `True` net `55c` brier/logloss d `-0.02508360000000002/-0.06676585137880248`
- `KXBTC15M-26MAY061500-00` selected `True` close `settled` sec_to/since_close `-80548.173032` side `yes` p_raw/+5/ask `0.55091/0.60091/0.55` won `False` net `-114c` brier/logloss d `0.057591/0.11803635772612686`
- `KXBTC15M-26MAY061515-15` selected `True` close `settled` sec_to/since_close `-79648.173032` side `no` p_raw/+5/ask `0.518915/0.5689150000000001/0.5` won `True` net `96c` brier/logloss d `-0.045608500000000024/-0.09199094482173509`
- `KXBTC15M-26MAY061530-30` selected `True` close `settled` sec_to/since_close `-78748.173032` side `no` p_raw/+5/ask `0.548704/0.598704/0.53` won `False` net `-110c` brier/logloss d `0.057370400000000044/0.11742413389191853`
- `KXBTC15M-26MAY061545-45` selected `True` close `settled` sec_to/since_close `-77848.173032` side `no` p_raw/+5/ask `0.513617/0.563617/0.49` won `False` net `-102c` brier/logloss d `0.05386170000000001/0.10847608127020358`
- `KXBTC15M-26MAY061600-00` selected `True` close `settled` sec_to/since_close `-76948.173032` side `no` p_raw/+5/ask `0.610883/0.660883/0.6` won `False` net `-124c` brier/logloss d `0.06358830000000004/0.13753488902487243`
- `KXBTC15M-26MAY061615-15` selected `True` close `settled` sec_to/since_close `-76048.173032` side `yes` p_raw/+5/ask `0.770727/0.8207270000000001/0.74` won `True` net `49c` brier/logloss d `-0.02042730000000001/-0.06285630758238042`
- `KXBTC15M-26MAY061630-30` selected `True` close `settled` sec_to/since_close `-75148.173032` side `no` p_raw/+5/ask `0.631665/0.6816650000000001/0.63` won `True` net `70c` brier/logloss d `-0.03433350000000003/-0.07617914449551977`
- `KXBTC15M-26MAY061645-45` selected `True` close `settled` sec_to/since_close `-74248.173032` side `no` p_raw/+5/ask `0.736529/0.786529/0.71` won `True` net `55c` brier/logloss d `-0.023847100000000017/-0.06568098348546203`
- `KXBTC15M-26MAY061700-00` selected `True` close `settled` sec_to/since_close `-73348.173032` side `no` p_raw/+5/ask `0.547299/0.597299/0.49` won `False` net `-102c` brier/logloss d `0.057229900000000056/0.11703751231541726`
- `KXBTC15M-26MAY061715-15` selected `True` close `settled` sec_to/since_close `-72448.173032` side `yes` p_raw/+5/ask `0.633073/0.683073/0.5` won `False` net `-104c` brier/logloss d `0.06580730000000001/0.14649145474139535`
- `KXBTC15M-26MAY061730-30` selected `True` close `settled` sec_to/since_close `-71548.173032` side `yes` p_raw/+5/ask `0.670106/0.720106/0.63` won `True` net `70c` brier/logloss d `-0.030489400000000028/-0.07196251456967673`
- `KXBTC15M-26MAY061745-45` selected `True` close `settled` sec_to/since_close `-70648.173032` side `no` p_raw/+5/ask `0.510383/0.5603830000000001/0.14` won `False` net `-30c` brier/logloss d `0.05353830000000004/0.10771955951623058`
- `KXBTC15M-26MAY061800-00` selected `True` close `settled` sec_to/since_close `-69748.173032` side `no` p_raw/+5/ask `0.700391/0.750391/0.68` won `True` net `60c` brier/logloss d `-0.027460900000000024/-0.06895565348765648`
- `KXBTC15M-26MAY061815-15` selected `True` close `settled` sec_to/since_close `-68848.173032` side `no` p_raw/+5/ask `0.794472/0.844472/0.72` won `True` net `53c` brier/logloss d `-0.018052800000000015/-0.06103383691975445`
- `KXBTC15M-26MAY061830-30` selected `True` close `settled` sec_to/since_close `-67948.173032` side `yes` p_raw/+5/ask `0.553162/0.6031620000000001/0.23` won `False` net `-49c` brier/logloss d `0.057816200000000095/0.11866797586313049`
- `KXBTC15M-26MAY061845-45` selected `False` close `None` sec_to/since_close `None` side `None` p_raw/+5/ask `None/None/None` won `None` net `None` brier/logloss d `None/None`
- `KXBTC15M-26MAY061900-00` selected `True` close `settled` sec_to/since_close `-66148.173032` side `yes` p_raw/+5/ask `0.501794/0.551794/0.34` won `True` net `128c` brier/logloss d `-0.047320600000000046/-0.0949851113133009`
- `KXBTC15M-26MAY061915-15` selected `True` close `settled` sec_to/since_close `-65248.173032` side `no` p_raw/+5/ask `0.923342/0.973342/0.87` won `True` net `22c` brier/logloss d `-0.005165800000000003/-0.0527358139133534`
- `KXBTC15M-26MAY061930-30` selected `True` close `settled` sec_to/since_close `-64348.173032` side `yes` p_raw/+5/ask `0.551364/0.601364/0.47` won `True` net `102c` brier/logloss d `-0.04236360000000003/-0.08680520033541261`
- `KXBTC15M-26MAY061945-45` selected `True` close `settled` sec_to/since_close `-63448.173032` side `yes` p_raw/+5/ask `0.542407/0.592407/0.42` won `False` net `-88c` brier/logloss d `0.05674070000000003/0.1157110152443932`
- `KXBTC15M-26MAY062000-00` selected `True` close `settled` sec_to/since_close `-62548.173032` side `yes` p_raw/+5/ask `0.582435/0.6324350000000001/0.5` won `True` net `96c` brier/logloss d `-0.03925650000000003/-0.08235985729176631`
- `KXBTC15M-26MAY062015-15` selected `True` close `settled` sec_to/since_close `-61648.173032` side `yes` p_raw/+5/ask `0.526847/0.576847/0.51` won `False` net `-106c` brier/logloss d `0.05518470000000003/0.11168498764263901`
- `KXBTC15M-26MAY062030-30` selected `True` close `settled` sec_to/since_close `-60748.173032` side `yes` p_raw/+5/ask `0.544418/0.594418/0.32` won `False` net `-68c` brier/logloss d `0.05694180000000004/0.11625264985791739`
- `KXBTC15M-26MAY062045-45` selected `True` close `settled` sec_to/since_close `-59848.173032` side `no` p_raw/+5/ask `0.61792/0.6679200000000001/0.51` won `True` net `94c` brier/logloss d `-0.03570800000000002/-0.07780940664559549`
- `KXBTC15M-26MAY062100-00` selected `True` close `settled` sec_to/since_close `-58948.173032` side `no` p_raw/+5/ask `0.615588/0.6655880000000001/0.22` won `False` net `-47c` brier/logloss d `0.06405880000000008/0.13934112835651846`
- `KXBTC15M-26MAY062115-15` selected `True` close `settled` sec_to/since_close `-58048.173032` side `yes` p_raw/+5/ask `0.543753/0.5937530000000001/0.53` won `True` net `90c` brier/logloss d `-0.043124700000000044/-0.08796830833861224`
- `KXBTC15M-26MAY062130-30` selected `True` close `settled` sec_to/since_close `-57148.173032` side `yes` p_raw/+5/ask `0.586142/0.6361420000000001/0.41` won `True` net `114c` brier/logloss d `-0.038885800000000026/-0.08185972781806078`
- `KXBTC15M-26MAY062145-45` selected `True` close `settled` sec_to/since_close `-56248.173032` side `yes` p_raw/+5/ask `0.600378/0.650378/0.57` won `True` net `82c` brier/logloss d `-0.03746220000000003/-0.07999427547380189`
- `KXBTC15M-26MAY062200-00` selected `True` close `settled` sec_to/since_close `-55348.173032` side `no` p_raw/+5/ask `0.617816/0.6678160000000001/0.46` won `True` net `104c` brier/logloss d `-0.035718400000000025/-0.07782200799367267`
- `KXBTC15M-26MAY062215-15` selected `True` close `settled` sec_to/since_close `-54448.173032` side `no` p_raw/+5/ask `0.661831/0.711831/0.59` won `True` net `78c` brier/logloss d `-0.031316900000000036/-0.07283028735050817`
- `KXBTC15M-26MAY062230-30` selected `True` close `settled` sec_to/since_close `-53548.173032` side `yes` p_raw/+5/ask `0.718015/0.768015/0.38` won `False` net `-80c` brier/logloss d `0.07430150000000002/0.1951811636303742`
- `KXBTC15M-26MAY062245-45` selected `True` close `settled` sec_to/since_close `-52648.173032` side `no` p_raw/+5/ask `0.605951/0.6559510000000001/0.54` won `False` net `-112c` brier/logloss d `0.06309510000000007/0.13569117795743713`
- `KXBTC15M-26MAY062300-00` selected `True` close `settled` sec_to/since_close `-51748.173032` side `yes` p_raw/+5/ask `0.758354/0.808354/0.73` won `True` net `51c` brier/logloss d `-0.02166460000000002/-0.06384978629410831`
- `KXBTC15M-26MAY062315-15` selected `True` close `settled` sec_to/since_close `-50848.173032` side `no` p_raw/+5/ask `0.74458/0.7945800000000001/0.68` won `True` net `60c` brier/logloss d `-0.02304200000000002/-0.06499337214814149`
- `KXBTC15M-26MAY062330-30` selected `True` close `settled` sec_to/since_close `-49948.173032` side `yes` p_raw/+5/ask `0.546903/0.5969030000000001/0.52` won `False` net `-108c` brier/logloss d `0.05719030000000003/0.11692900282279717`
- `KXBTC15M-26MAY062345-45` selected `True` close `settled` sec_to/since_close `-49048.173032` side `no` p_raw/+5/ask `0.608623/0.6586230000000001/0.46` won `False` net `-96c` brier/logloss d `0.06336230000000004/0.1366838513854124`
- `KXBTC15M-26MAY070000-00` selected `True` close `settled` sec_to/since_close `-48148.173032` side `no` p_raw/+5/ask `0.863962/0.913962/0.78` won `True` net `0c` brier/logloss d `-0.011103800000000007/-0.05626020874216353`
- `KXBTC15M-26MAY070015-15` selected `True` close `settled` sec_to/since_close `-47248.173032` side `yes` p_raw/+5/ask `0.560075/0.610075/0.56` won `True` net `84c` brier/logloss d `-0.04149250000000004/-0.08551119709620353`
- `KXBTC15M-26MAY070030-30` selected `True` close `settled` sec_to/since_close `-46348.173032` side `no` p_raw/+5/ask `0.523605/0.573605/0.33` won `False` net `-70c` brier/logloss d `0.05486050000000009/0.11088119533995178`
- `KXBTC15M-26MAY070045-45` selected `True` close `settled` sec_to/since_close `-45448.173032` side `no` p_raw/+5/ask `0.582164/0.6321640000000001/0.48` won `True` net `100c` brier/logloss d `-0.03928360000000003/-0.08239665917654926`
- `KXBTC15M-26MAY070100-00` selected `True` close `settled` sec_to/since_close `-44548.173032` side `no` p_raw/+5/ask `0.505013/0.5550130000000001/0.22` won `False` net `-47c` brier/logloss d `0.05300130000000003/0.10648643134118696`
- `KXBTC15M-26MAY070115-15` selected `True` close `settled` sec_to/since_close `-43648.173032` side `yes` p_raw/+5/ask `0.773654/0.823654/0.72` won `True` net `53c` brier/logloss d `-0.020134600000000023/-0.06262579359397424`
- `KXBTC15M-26MAY070130-30` selected `True` close `settled` sec_to/since_close `-42748.173032` side `no` p_raw/+5/ask `0.60414/0.65414/0.59` won `True` net `78c` brier/logloss d `-0.03708600000000002/-0.07951543667077726`
- `KXBTC15M-26MAY070145-45` selected `True` close `settled` sec_to/since_close `-41848.173032` side `no` p_raw/+5/ask `0.83804/0.88804/0.81` won `True` net `35c` brier/logloss d `-0.013696000000000009/-0.05795095498290609`
- `KXBTC15M-26MAY070200-00` selected `True` close `settled` sec_to/since_close `-40948.173032` side `yes` p_raw/+5/ask `0.50571/0.55571/0.3` won `False` net `-63c` brier/logloss d `0.053071000000000035/0.1066448871054072`
- `KXBTC15M-26MAY070530-30` selected `True` close `settled` sec_to/since_close `-28348.173032` side `no` p_raw/+5/ask `0.540822/0.5908220000000001/0.48` won `True` net `100c` brier/logloss d `-0.043417800000000034/-0.08842458323309454`
- `KXBTC15M-26MAY070545-45` selected `True` close `settled` sec_to/since_close `-27448.173032` side `yes` p_raw/+5/ask `0.707647/0.7576470000000001/0.6` won `False` net `-124c` brier/logloss d `0.07326470000000007/0.18756663523590866`
- `KXBTC15M-26MAY070600-00` selected `True` close `settled` sec_to/since_close `-26548.173032` side `yes` p_raw/+5/ask `0.72396/0.7739600000000001/0.67` won `True` net `62c` brier/logloss d `-0.025104000000000008/-0.06678405042705737`
- `KXBTC15M-26MAY070615-15` selected `True` close `settled` sec_to/since_close `-25648.173032` side `no` p_raw/+5/ask `0.610872/0.660872/0.28` won `True` net `141c` brier/logloss d `-0.03641280000000002/-0.07867273051903423`
- `KXBTC15M-26MAY070630-30` selected `True` close `settled` sec_to/since_close `-24748.173032` side `yes` p_raw/+5/ask `0.606974/0.6569740000000001/0.47` won `False` net `-98c` brier/logloss d `0.06319740000000007/0.13606952139934392`
- `KXBTC15M-26MAY070645-45` selected `True` close `settled` sec_to/since_close `-23848.173032` side `yes` p_raw/+5/ask `0.895399/0.945399/0.81` won `True` net `35c` brier/logloss d `-0.00796010000000001/-0.05433763161830181`
- `KXBTC15M-26MAY070700-00` selected `True` close `settled` sec_to/since_close `-22948.173032` side `yes` p_raw/+5/ask `0.654812/0.704812/0.56` won `False` net `-116c` brier/logloss d `0.06798120000000002/0.15647675465493482`
- `KXBTC15M-26MAY070715-15` selected `True` close `settled` sec_to/since_close `-22048.173032` side `yes` p_raw/+5/ask `0.560435/0.6104350000000001/0.51` won `True` net `94c` brier/logloss d `-0.041456500000000035/-0.08545854987434204`
- `KXBTC15M-26MAY070730-30` selected `True` close `settled` sec_to/since_close `-21148.173032` side `yes` p_raw/+5/ask `0.530778/0.580778/0.46` won `False` net `-96c` brier/logloss d `0.05557780000000001/0.11267539145485539`
- `KXBTC15M-26MAY070745-45` selected `True` close `settled` sec_to/since_close `-20248.173032` side `yes` p_raw/+5/ask `0.903807/0.9538070000000001/0.68` won `True` net `32c` brier/logloss d `-0.007119300000000001/-0.05384550287845598`
- `KXBTC15M-26MAY070800-00` selected `True` close `settled` sec_to/since_close `-19348.173032` side `yes` p_raw/+5/ask `0.536385/0.586385/0.45` won `False` net `-94c` brier/logloss d `0.056138500000000036/0.11411887695987544`
- `KXBTC15M-26MAY070815-15` selected `True` close `settled` sec_to/since_close `-18448.173032` side `yes` p_raw/+5/ask `0.501147/0.551147/0.44` won `True` net `108c` brier/logloss d `-0.04738530000000002/-0.09510209000892711`
- `KXBTC15M-26MAY070830-30` selected `True` close `settled` sec_to/since_close `-17548.173032` side `yes` p_raw/+5/ask `0.514492/0.564492/0.41` won `False` net `-86c` brier/logloss d `0.05394920000000003/0.10868259963965154`
- `KXBTC15M-26MAY070845-45` selected `True` close `settled` sec_to/since_close `-16648.173032` side `yes` p_raw/+5/ask `0.596088/0.646088/0.45` won `True` net `106c` brier/logloss d `-0.03789120000000004/-0.08054741024259643`
- `KXBTC15M-26MAY070900-00` selected `True` close `settled` sec_to/since_close `-15748.173032` side `yes` p_raw/+5/ask `0.597604/0.6476040000000001/0.55` won `True` net `86c` brier/logloss d `-0.03773960000000004/-0.08035107120002422`
- `KXBTC15M-26MAY070915-15` selected `True` close `settled` sec_to/since_close `-14848.173032` side `no` p_raw/+5/ask `0.788001/0.838001/0.75` won `True` net `47c` brier/logloss d `-0.018699900000000016/-0.06151993490618665`
- `KXBTC15M-26MAY070930-30` selected `True` close `settled` sec_to/since_close `-13948.173032` side `no` p_raw/+5/ask `0.511849/0.561849/0.48` won `False` net `-100c` brier/logloss d `0.05368490000000009/0.1080611843975724`
- `KXBTC15M-26MAY070945-45` selected `True` close `settled` sec_to/since_close `-13048.173032` side `no` p_raw/+5/ask `0.532085/0.5820850000000001/0.48` won `True` net `100c` brier/logloss d `-0.04429150000000004/-0.08981323416225784`
- `KXBTC15M-26MAY071000-00` selected `True` close `settled` sec_to/since_close `-12148.173032` side `yes` p_raw/+5/ask `0.54351/0.5935100000000001/0.54` won `False` net `-112c` brier/logloss d `0.056851000000000096/0.11600746555077746`
- `KXBTC15M-26MAY071015-15` selected `True` close `settled` sec_to/since_close `-11248.173032` side `no` p_raw/+5/ask `0.609894/0.6598940000000001/0.6` won `False` net `-124c` brier/logloss d `0.06348940000000003/0.13716116333838035`
- `KXBTC15M-26MAY071030-30` selected `True` close `settled` sec_to/since_close `-10348.173032` side `no` p_raw/+5/ask `0.64638/0.69638/0.62` won `True` net `72c` brier/logloss d `-0.03286200000000003/-0.07450792222053731`
- `KXBTC15M-26MAY071045-45` selected `True` close `settled` sec_to/since_close `-9448.173032` side `yes` p_raw/+5/ask `0.557862/0.607862/0.55` won `False` net `-114c` brier/logloss d `0.05828620000000001/0.12000823188766252`
- `KXBTC15M-26MAY071100-00` selected `True` close `settled` sec_to/since_close `-8548.173032` side `no` p_raw/+5/ask `0.5788/0.6288/0.56` won `True` net `84c` brier/logloss d `-0.039620000000000044/-0.08285624635766803`
- `KXBTC15M-26MAY071115-15` selected `True` close `settled` sec_to/since_close `-7648.173032` side `no` p_raw/+5/ask `0.635838/0.6858380000000001/0.62` won `False` net `-128c` brier/logloss d `0.06608380000000003/0.1476900471418916`
- `KXBTC15M-26MAY071130-30` selected `True` close `settled` sec_to/since_close `-6748.173032` side `no` p_raw/+5/ask `0.582087/0.6320870000000001/0.58` won `True` net `80c` brier/logloss d `-0.03929130000000003/-0.08240712180486076`
- `KXBTC15M-26MAY071145-45` selected `True` close `settled` sec_to/since_close `-5848.173032` side `yes` p_raw/+5/ask `0.645637/0.6956370000000001/0.61` won `True` net `74c` brier/logloss d `-0.032936300000000016/-0.07459054621284722`
- `KXBTC15M-26MAY071200-00` selected `True` close `settled` sec_to/since_close `-4948.173032` side `yes` p_raw/+5/ask `0.606055/0.656055/0.6` won `False` net `-124c` brier/logloss d `0.06310550000000004/0.13572954477546462`
- `KXBTC15M-26MAY071215-15` selected `True` close `settled` sec_to/since_close `-4048.173032` side `yes` p_raw/+5/ask `0.509397/0.559397/0.47` won `False` net `-98c` brier/logloss d `0.05343970000000009/0.10749100352494356`
- `KXBTC15M-26MAY071230-30` selected `True` close `settled` sec_to/since_close `-3148.173032` side `no` p_raw/+5/ask `0.729882/0.7798820000000001/0.7` won `False` net `-143c` brier/logloss d `0.0754882/0.20469513436537778`
- `KXBTC15M-26MAY071245-45` selected `True` close `settled` sec_to/since_close `-2248.173032` side `yes` p_raw/+5/ask `0.559979/0.609979/0.55` won `False` net `-114c` brier/logloss d `0.05849790000000005/0.12062186921823803`
- `KXBTC15M-26MAY071300-00` selected `True` close `settled` sec_to/since_close `-1348.173032` side `yes` p_raw/+5/ask `0.63604/0.6860400000000001/0.59` won `False` net `-122c` brier/logloss d `0.06610400000000005/0.14777838222987727`
- `KXBTC15M-26MAY071315-15` selected `True` close `settled` sec_to/since_close `-448.173032` side `yes` p_raw/+5/ask `0.533442/0.583442/0.51` won `True` net `94c` brier/logloss d `-0.04415580000000005/-0.08959469780915597`
- `KXBTC15M-26MAY071330-30` selected `True` close `settled` sec_to/since_close `451.826968` side `yes` p_raw/+5/ask `0.544206/0.594206/0.52` won `False` net `-108c` brier/logloss d `0.05692060000000004/0.1161953113829346`

### Calibrated FV Sequential Evidence

- Paired forward raw-vs-+5 calibration evidence on settled selected rows.
- Status: `inconclusive_or_blocked`
- Settled rows: `150`
- Blockers: `brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative, mean_brier_delta_not_negative, mean_logloss_delta_not_negative`
- Brier mean delta negative/positive: `0.009703716336006675` `83/67`
- Logloss mean delta negative/positive: `0.018231599752216193` `83/67`

### Calibrated FV Physics Attribution

- Predeclared physics buckets for the frozen raw-entry +5pp FV overlay.
- Selected/settled/pending: `150/150/0`
- Blockers: `none`
- `all_selected`: selected `150`, settled `150`, W/L `83/67`, net `-1009c`, brier mean delta `0.009703716336006675`, logloss mean delta `0.018231599752216193`
- `settled_only`: selected `150`, settled `150`, W/L `83/67`, net `-1009c`, brier mean delta `0.009703716336006675`, logloss mean delta `0.018231599752216193`
- `spectral_dominant_factor`: selected `149`, settled `149`, W/L `83/66`, net `-903c`, brier mean delta `0.00939847483490605`, logloss mean delta `0.017604395806642886`
- `early_market_stc_gt_600`: selected `135`, settled `135`, W/L `71/64`, net `-1274c`, brier mean delta `0.01105341925925927`, logloss mean delta `0.02262611106427856`
- `ask_lte_60`: selected `105`, settled `105`, W/L `47/58`, net `-1460c`, brier mean delta `0.01484098666666668`, logloss mean delta `0.03184468070630781`
- `high_recross_hazard_gte_075`: selected `92`, settled `92`, W/L `46/46`, net `-1008c`, brier mean delta `0.010102740217391314`, logloss mean delta `0.022238755966965798`
- `raw_edge_lt_05pp`: selected `88`, settled `88`, W/L `51/37`, net `-695c`, brier mean delta `0.006331675000000006`, logloss mean delta `0.012522439945181181`
- `near_strike_abs_d_lte_025`: selected `79`, settled `79`, W/L `37/42`, net `-690c`, brier mean delta `0.010697893670886086`, logloss mean delta `0.021867368589672916`

### Calibrated FV Path Contradiction

- Compares the early raw-p50 selected side against later actual v28 approvals in the same market.
- Selected/settled rows: `150/150`
- Rows with later opposite approval: `44`
- Settled contradiction W/L for early selected side: `9/35`
- Blockers: `none`
- `KXBTC15M-26MAY051945-45` early `yes` p/ask `0.613944/0.51` won `True`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY052015-15` early `no` p/ask `0.567861/0.49` won `False`; later approvals `2`, opposite `2`, first opposite `yes` after `185.005681` sec
- `KXBTC15M-26MAY052045-45` early `yes` p/ask `0.590266/0.56` won `False`; later approvals `3`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY052100-00` early `yes` p/ask `0.565554/0.46` won `True`; later approvals `3`, opposite `1`, first opposite `no` after `131.475165` sec
- `KXBTC15M-26MAY052115-15` early `yes` p/ask `0.571476/0.53` won `True`; later approvals `2`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY052145-45` early `yes` p/ask `0.865417/0.83` won `True`; later approvals `3`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY052200-00` early `no` p/ask `0.551743/0.52` won `False`; later approvals `1`, opposite `1`, first opposite `yes` after `91.824781` sec
- `KXBTC15M-26MAY052215-15` early `no` p/ask `0.809232/0.77` won `True`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY052245-45` early `no` p/ask `0.643789/0.57` won `False`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY052300-00` early `yes` p/ask `0.918967/0.85` won `True`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY052315-15` early `yes` p/ask `0.884999/0.81` won `True`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY060045-45` early `no` p/ask `0.826505/0.79` won `True`; later approvals `2`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY060100-00` early `yes` p/ask `0.799928/0.79` won `False`; later approvals `1`, opposite `1`, first opposite `no` after `204.867824` sec
- `KXBTC15M-26MAY060145-45` early `no` p/ask `0.557282/0.55` won `True`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY060200-00` early `yes` p/ask `0.618277/0.6` won `True`; later approvals `3`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY060215-15` early `yes` p/ask `0.583024/0.53` won `False`; later approvals `3`, opposite `1`, first opposite `no` after `590.244882` sec
- `KXBTC15M-26MAY060230-30` early `no` p/ask `0.574094/0.54` won `False`; later approvals `1`, opposite `1`, first opposite `yes` after `573.058198` sec
- `KXBTC15M-26MAY060245-45` early `no` p/ask `0.660829/0.65` won `False`; later approvals `4`, opposite `4`, first opposite `yes` after `408.247407` sec
- `KXBTC15M-26MAY060300-00` early `yes` p/ask `0.661141/0.64` won `True`; later approvals `4`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY060315-15` early `yes` p/ask `0.512365/0.5` won `True`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY060330-30` early `no` p/ask `0.63088/0.57` won `False`; later approvals `2`, opposite `1`, first opposite `yes` after `472.047345` sec
- `KXBTC15M-26MAY060345-45` early `yes` p/ask `0.515105/0.38` won `False`; later approvals `1`, opposite `1`, first opposite `no` after `188.784149` sec
- `KXBTC15M-26MAY060445-45` early `no` p/ask `0.636374/0.45` won `False`; later approvals `2`, opposite `2`, first opposite `yes` after `184.821398` sec
- `KXBTC15M-26MAY060500-00` early `no` p/ask `0.674136/0.61` won `False`; later approvals `2`, opposite `2`, first opposite `yes` after `208.937945` sec
- `KXBTC15M-26MAY060515-15` early `yes` p/ask `0.532512/0.41` won `False`; later approvals `3`, opposite `3`, first opposite `no` after `46.889424` sec
- `KXBTC15M-26MAY060530-30` early `yes` p/ask `0.588889/0.54` won `False`; later approvals `1`, opposite `1`, first opposite `no` after `312.577116` sec
- `KXBTC15M-26MAY060545-45` early `no` p/ask `0.626642/0.44` won `False`; later approvals `1`, opposite `1`, first opposite `yes` after `42.732601` sec
- `KXBTC15M-26MAY060600-00` early `no` p/ask `0.792357/0.75` won `True`; later approvals `3`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY060615-15` early `yes` p/ask `0.598388/0.57` won `True`; later approvals `2`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY060630-30` early `no` p/ask `0.675344/0.66` won `False`; later approvals `2`, opposite `2`, first opposite `yes` after `325.276557` sec
- `KXBTC15M-26MAY060645-45` early `yes` p/ask `0.598639/0.59` won `True`; later approvals `3`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY060700-00` early `yes` p/ask `0.527819/0.52` won `True`; later approvals `4`, opposite `1`, first opposite `no` after `119.64695` sec
- `KXBTC15M-26MAY060715-15` early `yes` p/ask `0.501801/0.49` won `True`; later approvals `3`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY060730-30` early `yes` p/ask `0.594884/0.56` won `True`; later approvals `2`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY060745-45` early `no` p/ask `0.553279/0.54` won `True`; later approvals `2`, opposite `2`, first opposite `yes` after `356.676335` sec
- `KXBTC15M-26MAY060800-00` early `yes` p/ask `0.523411/0.47` won `True`; later approvals `2`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY060815-15` early `no` p/ask `0.505085/0.49` won `True`; later approvals `3`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY060830-30` early `no` p/ask `0.60073/0.59` won `False`; later approvals `1`, opposite `1`, first opposite `yes` after `336.85113` sec
- `KXBTC15M-26MAY060900-00` early `no` p/ask `0.586412/0.58` won `True`; later approvals `5`, opposite `3`, first opposite `yes` after `65.328264` sec
- `KXBTC15M-26MAY060915-15` early `no` p/ask `0.672099/0.6` won `True`; later approvals `3`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY060930-30` early `yes` p/ask `0.604377/0.6` won `False`; later approvals `4`, opposite `4`, first opposite `no` after `264.766303` sec
- `KXBTC15M-26MAY060945-45` early `no` p/ask `0.761891/0.5` won `True`; later approvals `4`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY061000-00` early `no` p/ask `0.513222/0.5` won `True`; later approvals `5`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY061015-15` early `no` p/ask `0.595554/0.52` won `True`; later approvals `3`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY061030-30` early `yes` p/ask `0.618153/0.61` won `True`; later approvals `3`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY061045-45` early `no` p/ask `0.601767/0.57` won `False`; later approvals `3`, opposite `3`, first opposite `yes` after `332.32828` sec
- `KXBTC15M-26MAY061100-00` early `yes` p/ask `0.740374/0.74` won `False`; later approvals `2`, opposite `2`, first opposite `no` after `207.846358` sec
- `KXBTC15M-26MAY061130-30` early `yes` p/ask `0.653101/0.65` won `True`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY061200-00` early `yes` p/ask `0.848576/0.81` won `True`; later approvals `4`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY061300-00` early `no` p/ask `0.544132/0.54` won `True`; later approvals `1`, opposite `1`, first opposite `yes` after `398.365953` sec
- `KXBTC15M-26MAY061400-00` early `no` p/ask `0.97364/0.89` won `True`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY061415-15` early `no` p/ask `0.519091/0.48` won `True`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY061445-45` early `no` p/ask `0.724164/0.71` won `True`; later approvals `2`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY061545-45` early `no` p/ask `0.513617/0.49` won `False`; later approvals `1`, opposite `1`, first opposite `yes` after `403.815909` sec
- `KXBTC15M-26MAY061615-15` early `yes` p/ask `0.770727/0.74` won `True`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY061645-45` early `no` p/ask `0.736529/0.71` won `True`; later approvals `2`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY061800-00` early `no` p/ask `0.700391/0.68` won `True`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY061815-15` early `no` p/ask `0.794472/0.72` won `True`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY061830-30` early `yes` p/ask `0.553162/0.23` won `False`; later approvals `1`, opposite `1`, first opposite `no` after `299.205587` sec
- `KXBTC15M-26MAY061900-00` early `yes` p/ask `0.501794/0.34` won `True`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY061915-15` early `no` p/ask `0.923342/0.87` won `True`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY062015-15` early `yes` p/ask `0.526847/0.51` won `False`; later approvals `3`, opposite `1`, first opposite `no` after `619.969983` sec
- `KXBTC15M-26MAY062030-30` early `yes` p/ask `0.544418/0.32` won `False`; later approvals `1`, opposite `1`, first opposite `no` after `201.175765` sec
- `KXBTC15M-26MAY062045-45` early `no` p/ask `0.61792/0.51` won `True`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY062100-00` early `no` p/ask `0.615588/0.22` won `False`; later approvals `3`, opposite `3`, first opposite `yes` after `1.074763` sec
- `KXBTC15M-26MAY062115-15` early `yes` p/ask `0.543753/0.53` won `True`; later approvals `4`, opposite `2`, first opposite `no` after `322.858332` sec
- `KXBTC15M-26MAY062130-30` early `yes` p/ask `0.586142/0.41` won `True`; later approvals `2`, opposite `2`, first opposite `no` after `125.028005` sec
- `KXBTC15M-26MAY062215-15` early `no` p/ask `0.661831/0.59` won `True`; later approvals `2`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY062245-45` early `no` p/ask `0.605951/0.54` won `False`; later approvals `2`, opposite `2`, first opposite `yes` after `139.654993` sec
- `KXBTC15M-26MAY062300-00` early `yes` p/ask `0.758354/0.73` won `True`; later approvals `2`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY062315-15` early `no` p/ask `0.74458/0.68` won `True`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY070000-00` early `no` p/ask `0.863962/0.78` won `True`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY070015-15` early `yes` p/ask `0.560075/0.56` won `True`; later approvals `1`, opposite `1`, first opposite `no` after `435.204964` sec
- `KXBTC15M-26MAY070030-30` early `no` p/ask `0.523605/0.33` won `False`; later approvals `1`, opposite `1`, first opposite `yes` after `313.097001` sec
- `KXBTC15M-26MAY070115-15` early `yes` p/ask `0.773654/0.72` won `True`; later approvals `2`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY070545-45` early `yes` p/ask `0.707647/0.6` won `False`; later approvals `1`, opposite `1`, first opposite `no` after `504.204941` sec
- `KXBTC15M-26MAY070645-45` early `yes` p/ask `0.895399/0.81` won `True`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY070745-45` early `yes` p/ask `0.903807/0.68` won `True`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY070815-15` early `yes` p/ask `0.501147/0.44` won `True`; later approvals `2`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY070830-30` early `yes` p/ask `0.514492/0.41` won `False`; later approvals `3`, opposite `3`, first opposite `no` after `242.386234` sec
- `KXBTC15M-26MAY070915-15` early `no` p/ask `0.788001/0.75` won `True`; later approvals `1`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY070930-30` early `no` p/ask `0.511849/0.48` won `False`; later approvals `2`, opposite `2`, first opposite `yes` after `190.693608` sec
- `KXBTC15M-26MAY070945-45` early `no` p/ask `0.532085/0.48` won `True`; later approvals `3`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY071000-00` early `yes` p/ask `0.54351/0.54` won `False`; later approvals `6`, opposite `6`, first opposite `no` after `27.841826` sec
- `KXBTC15M-26MAY071015-15` early `no` p/ask `0.609894/0.6` won `False`; later approvals `3`, opposite `1`, first opposite `yes` after `638.192633` sec
- `KXBTC15M-26MAY071030-30` early `no` p/ask `0.64638/0.62` won `True`; later approvals `3`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY071045-45` early `yes` p/ask `0.557862/0.55` won `False`; later approvals `3`, opposite `3`, first opposite `no` after `40.447724` sec
- `KXBTC15M-26MAY071100-00` early `no` p/ask `0.5788/0.56` won `True`; later approvals `1`, opposite `1`, first opposite `yes` after `319.276338` sec
- `KXBTC15M-26MAY071115-15` early `no` p/ask `0.635838/0.62` won `False`; later approvals `1`, opposite `1`, first opposite `yes` after `454.351598` sec
- `KXBTC15M-26MAY071130-30` early `no` p/ask `0.582087/0.58` won `True`; later approvals `2`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY071145-45` early `yes` p/ask `0.645637/0.61` won `True`; later approvals `3`, opposite `0`, first opposite `None` after `None` sec
- `KXBTC15M-26MAY071200-00` early `yes` p/ask `0.606055/0.6` won `False`; later approvals `1`, opposite `1`, first opposite `no` after `659.690295` sec
- `KXBTC15M-26MAY071215-15` early `yes` p/ask `0.509397/0.47` won `False`; later approvals `3`, opposite `3`, first opposite `no` after `397.197311` sec
- `KXBTC15M-26MAY071230-30` early `no` p/ask `0.729882/0.7` won `False`; later approvals `3`, opposite `3`, first opposite `yes` after `449.544461` sec
- `KXBTC15M-26MAY071315-15` early `yes` p/ask `0.533442/0.51` won `True`; later approvals `4`, opposite `0`, first opposite `None` after `None` sec

### Path-Confirmed Entry Candidates

- Live-realistic delay challengers for broad raw-p50 entries after the path-contradiction loss.
- Forward denominator/base entries: `152/150`
- `path_confirm_wait120`: entries `95`, settled `95`, W/L `53/42`, coverage `62.5`, net `-1731c`, brier/logloss delta `0.01694042521765265/0.049810992862453836`, blocked `55` {'opposite_approval_before_confirm': 8, 'same_side_not_confirmed': 47}
- `path_confirm_wait180`: entries `85`, settled `85`, W/L `49/36`, coverage `55.92105263157895`, net `-1616c`, brier/logloss delta `0.01698836583149414/0.04531572218925606`, blocked `65` {'opposite_approval_before_confirm': 11, 'same_side_not_confirmed': 54}
- `path_confirm_wait240`: entries `71`, settled `71`, W/L `41/30`, coverage `46.71052631578947`, net `-1477c`, brier/logloss delta `0.018511899939112696/0.05121716873706005`, blocked `79` {'opposite_approval_before_confirm': 19, 'same_side_not_confirmed': 60}
- `selective_fragile_wait180`: entries `126`, settled `126`, W/L `73/53`, coverage `82.89473684210526`, net `-1571c`, brier/logloss delta `0.013256310683158742/0.026201028196139533`, blocked `24` {'fragile_opposite_approval_before_confirm': 8, 'fragile_same_side_not_confirmed': 16}
- `selective_fragile_wait240`: entries `119`, settled `119`, W/L `70/49`, coverage `78.28947368421053`, net `-1495c`, brier/logloss delta `0.013078577698134464/0.024771742920880982`, blocked `31` {'fragile_opposite_approval_before_confirm': 11, 'fragile_same_side_not_confirmed': 20}
- `selective_nearstrike_wait180`: entries `130`, settled `130`, W/L `74/56`, coverage `85.52631578947368`, net `-1474c`, brier/logloss delta `0.013393962400007706/0.02738867593286138`, blocked `20` {'fragile_opposite_approval_before_confirm': 6, 'fragile_same_side_not_confirmed': 14}
- `selective_rmt_memory_gap_wait180`: entries `138`, settled `138`, W/L `79/59`, coverage `90.78947368421053`, net `-949c`, brier/logloss delta `0.009790593565224645/0.018841619700700193`, blocked `12` {'fragile_opposite_approval_before_confirm': 3, 'fragile_same_side_not_confirmed': 9}
- `selective_rmt_repetition_gap_wait180`: entries `139`, settled `139`, W/L `79/60`, coverage `91.44736842105263`, net `-1045c`, brier/logloss delta `0.009749927424467635/0.018277499992147235`, blocked `11` {'fragile_opposite_approval_before_confirm': 2, 'fragile_same_side_not_confirmed': 9}
- `selective_rmt_memory_gap_wait180_rmtedge02`: entries `126`, settled `126`, W/L `74/52`, coverage `82.89473684210526`, net `-420c`, brier/logloss delta `0.007844924209531751/0.014162511306276219`, blocked `24` {'fragile_opposite_approval_before_confirm': 3, 'fragile_same_side_not_confirmed': 21}
- `selective_rmt_repetition_gap_wait180_rmtedge02`: entries `132`, settled `132`, W/L `75/57`, coverage `86.8421052631579`, net `-909c`, brier/logloss delta `0.009364881442431828/0.01733868646286521`, blocked `18` {'fragile_opposite_approval_before_confirm': 2, 'fragile_same_side_not_confirmed': 16}
- `selective_rmt_memory_gap_wait180_rmtedge02_or_opp`: entries `129`, settled `129`, W/L `76/53`, coverage `84.86842105263158`, net `-470c`, brier/logloss delta `0.00817519031318605/0.016182663088319935`, blocked `21` {'fragile_same_side_not_confirmed': 21}
- `selective_rmt_repetition_gap_wait180_rmtedge02_or_opp`: entries `134`, settled `134`, W/L `76/58`, coverage `88.1578947368421`, net `-969c`, brier/logloss delta `0.009811386197022397/0.019767920906866614`, blocked `16` {'fragile_same_side_not_confirmed': 16}
- `selective_rmt_memory_gap_wait240_rmtedge02_or_opp`: entries `132`, settled `132`, W/L `79/53`, coverage `86.8421052631579`, net `-380c`, brier/logloss delta `0.007789017048492429/0.014567529717867579`, blocked `18` {'fragile_same_side_not_confirmed': 18}
- `selective_rmt_repetition_gap_wait240_rmtedge02_or_opp`: entries `136`, settled `136`, W/L `78/58`, coverage `89.47368421052632`, net `-910c`, brier/logloss delta `0.00956016801765442/0.018684006193126185`, blocked `14` {'fragile_same_side_not_confirmed': 14}
- `weakraw_rmt_memory_margin02_wait240_or_opp`: entries `88`, settled `88`, W/L `55/33`, coverage `57.89473684210527`, net `-750c`, brier/logloss delta `0.012605083527284101/0.03494276809223221`, blocked `62` {'fragile_same_side_not_confirmed': 62}
- `weakraw_rmt_repetition_margin02_wait240_or_opp`: entries `88`, settled `88`, W/L `55/33`, coverage `57.89473684210527`, net `-750c`, brier/logloss delta `0.012605083527284101/0.03494276809223221`, blocked `62` {'fragile_same_side_not_confirmed': 62}

### Path/RMT Fresh Forward Gate

- Fresh post-discovery freeze for the current best path/RMT challenger.
- Freeze timestamp UTC: `2026-05-06T00:38:39.999269+00:00`
- Forward denominator/base entries: `147/145`
- Any promotable: `False`
- Future clean markets needed for denominator 10: `0`
- Future clean markets needed for denominator 30: `0`
- `weakraw_rmt_memory_margin02_wait240_or_opp`: entries `85`, settled `85`, W/L `52/33`, coverage `57.82312925170068`, net `-942c`, brier `0.23723110228677646`, net_vs_base `-85c`, brier_vs_base `-0.001636615396533897`, settled_to_30 `0`, actual_needed_for_sim35 `107`, blockers `simulated_share_gt_0.35, coverage_too_low, net_not_positive, brier_delta_not_negative, logloss_delta_not_negative`
- `weakraw_rmt_repetition_margin02_wait240_or_opp`: entries `85`, settled `85`, W/L `52/33`, coverage `57.82312925170068`, net `-942c`, brier `0.23723110228677646`, net_vs_base `-85c`, brier_vs_base `-0.001636615396533897`, settled_to_30 `0`, actual_needed_for_sim35 `107`, blockers `simulated_share_gt_0.35, coverage_too_low, net_not_positive, brier_delta_not_negative, logloss_delta_not_negative`
- `v28_raw_p50_edge0_base`: entries `145`, settled `145`, W/L `81/64`, coverage `98.63945578231292`, net `-857c`, brier `0.23886771768331036`, net_vs_base `0c`, brier_vs_base `0.0`, settled_to_30 `0`, actual_needed_for_sim35 `250`, blockers `simulated_share_gt_0.35, coverage_too_high, net_not_positive, brier_delta_not_negative, logloss_delta_not_negative`
- `selective_rmt_memory_gap_wait240_rmtedge02_or_opp`: entries `128`, settled `128`, W/L `76/52`, coverage `87.07482993197279`, net `-456c`, brier `0.23076545528516407`, net_vs_base `401c`, brier_vs_base `-0.008102262398146293`, settled_to_30 `0`, actual_needed_for_sim35 `204`, blockers `simulated_share_gt_0.35, net_not_positive, brier_delta_not_negative, logloss_delta_not_negative`
- `selective_rmt_repetition_gap_wait240_rmtedge02_or_opp`: entries `132`, settled `132`, W/L `75/57`, coverage `89.79591836734694`, net `-986c`, brier `0.2378804539028409`, net_vs_base `-129c`, brier_vs_base `-0.000987263780469455`, settled_to_30 `0`, actual_needed_for_sim35 `217`, blockers `simulated_share_gt_0.35, net_not_positive, brier_delta_not_negative, logloss_delta_not_negative`

### FV Model Readiness

- Candidate: `v28_raw_entry_conditioned_plus05_fv`
- FV probability: `clamp(raw_v28_probability + 0.05)`
- Ready: `False`
- Blockers: `forward_coverage_too_high, forward_brier_not_better_than_raw, forward_logloss_not_better_than_raw, forward_bucket_failure, forward_path_contradiction_loss`
- Discovery +5pp Brier/logloss deltas: `0.006406016572098855/0.011122342497338011`
- Frozen forward denominator/rows: `152/150`

### FV Overlay Challenger Readiness

- Fixed raw-v28 p50 entry surface; compares FV overlays only.
- Forward denominator/entry rows: `152/150`
- Best forward overlay: `book_probability`
- Any ready: `False`
- `book_probability`: ready `False`, settled `150`, coverage `98.68421052631578`, fwd Brier/logloss d `-0.012290468851073322/-0.022480708936355454`, disc Brier/logloss d `-0.006548895154377898/-0.010476170391744977`, blockers `forward_coverage_too_high, forward_bucket_failure, forward_path_contradiction_loss`
- `noise_shrink_light_probability`: ready `False`, settled `150`, coverage `98.68421052631578`, fwd Brier/logloss d `-0.0026821987283214277/-0.005111910827987121`, disc Brier/logloss d `-0.0015024518536817244/-0.0025435962254067856`, blockers `forward_coverage_too_high, forward_bucket_failure, forward_path_contradiction_loss`
- `raw_probability`: ready `False`, settled `150`, coverage `98.68421052631578`, fwd Brier/logloss d `0.0/0.0`, disc Brier/logloss d `0.0/0.0`, blockers `forward_coverage_too_high, forward_path_contradiction_loss`
- `entry_conditioned_logit125_p60_only_probability`: ready `False`, settled `150`, coverage `98.68421052631578`, fwd Brier/logloss d `0.002981058258838626/0.004515305127756997`, disc Brier/logloss d `0.0023406348964918333/0.002944994531597911`, blockers `forward_coverage_too_high, forward_brier_not_better_than_raw, forward_logloss_not_better_than_raw, discovery_brier_not_better_than_raw, discovery_logloss_not_better_than_raw, forward_bucket_failure, forward_path_contradiction_loss`
- `entry_conditioned_logit125_probability`: ready `False`, settled `150`, coverage `98.68421052631578`, fwd Brier/logloss d `0.003343684183032325/0.005195227233231292`, disc Brier/logloss d `0.0022755488567699766/0.0027615184026530404`, blockers `forward_coverage_too_high, forward_brier_not_better_than_raw, forward_logloss_not_better_than_raw, discovery_brier_not_better_than_raw, discovery_logloss_not_better_than_raw, forward_bucket_failure, forward_path_contradiction_loss`
- `entry_conditioned_plus03_probability`: ready `False`, settled `150`, coverage `98.68421052631578`, fwd Brier/logloss d `0.005224376869339992/0.0094559212296077`, disc Brier/logloss d `0.0032454823860523507/0.005230896960615072`, blockers `forward_coverage_too_high, forward_brier_not_better_than_raw, forward_logloss_not_better_than_raw, discovery_brier_not_better_than_raw, discovery_logloss_not_better_than_raw, forward_bucket_failure, forward_path_contradiction_loss`

### Calibrated FV Sample Plan

- Forward-evidence runway for the raw-entry +5pp FV overlay.
- Current denominator/selected/settled/pending: `152/150/150/0`
- Remaining settled rows to 30: `0`
- Additional selected after pending to 30: `0`
- Misses needed for current high coverage <=90%: `15`
- Miss budget after 30 selected before coverage <70%: `62`

### Path/RMT Candidate Runway

- Current best target-coverage path policy: `selective_rmt_memory_gap_wait240_rmtedge02_or_opp`
- Entries/settled: `132/132`
- Actual/simulated entries: `13/119`; simulated share `0.9015151515151515`
- Coverage/net/Brier: `86.8421052631579` / `-380c` / `0.22835881042698486`
- Settled rows still needed for 30: `0`
- Additional actual entries needed for simulated share <=35%: `208`

### Raw-Entry Coverage Valve

- Shadow-only coverage valve for raw-v28 p50 entries using the current best FV overlay.
- Best current policy: `raw_p50_turbulence_valve_edge4_p60_recross90_near20`
- Forward denominator: `152`
- `raw_p50_turbulence_valve_edge4_p60_recross90_near20`: discovery coverage/net `80.23255813953489/337c`, forward entries/settled/W-L `125/125/73-52`, coverage/net/Brier `82.23684210526315/-333c/0.22610321967506236`, blockers `net_not_positive`
- `raw_p50_turbulence_valve_edge4_p60_recross90_near25`: discovery coverage/net `78.48837209302324/132c`, forward entries/settled/W-L `122/122/70-52`, coverage/net/Brier `80.26315789473685/-538c/0.2274553241415557`, blockers `net_not_positive`
- `raw_p50_coverage_valve_edge3_or_p60`: discovery coverage/net `75.5813953488372/-664c`, forward entries/settled/W-L `117/117/64-53`, coverage/net/Brier `76.97368421052632/-1136c/0.22974639934199823`, blockers `net_not_positive, net_worse_than_base`
- `raw_p50_turbulence_valve_edge3_p60_recross75_near25`: discovery coverage/net `77.90697674418605/-700c`, forward entries/settled/W-L `120/120/65-55`, coverage/net/Brier `78.94736842105263/-1272c/0.23015075023460663`, blockers `net_not_positive, net_worse_than_base`

### Target-Coverage FV Overlay Validator

- Scores FV overlays on the current best raw-entry coverage valve, not the broad raw-p50 surface.
- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Forward denominator: `152`
- `book_probability`: entries/settled `112/112`, coverage `73.68421052631578`, W/L `64-48`, net `-626c`, Brier/logloss d `-0.014912731593232115/-0.026989299326773852`, blockers `coverage_too_low`
- `boundary_recross_shrink_probability`: entries/settled `112/112`, coverage `73.68421052631578`, W/L `64-48`, net `-626c`, Brier/logloss d `-0.007140542347522316/-0.015608625993661529`, blockers `coverage_too_low`
- `noise_shrink_light_probability`: entries/settled `112/112`, coverage `73.68421052631578`, W/L `64-48`, net `-626c`, Brier/logloss d `-0.0029087216273770145/-0.005474528473659923`, blockers `coverage_too_low`
- `raw_probability`: entries/settled `112/112`, coverage `73.68421052631578`, W/L `64-48`, net `-626c`, Brier/logloss d `0.0/0.0`, blockers `coverage_too_low`
- `entry_conditioned_logit125_probability`: entries/settled `112/112`, coverage `73.68421052631578`, W/L `64-48`, net `-626c`, Brier/logloss d `0.003822646206758845/0.005634495775266202`, blockers `coverage_too_low, brier_not_better_than_raw, logloss_not_better_than_raw`

### Target-Coverage FV Sequential Evidence

- Paired evidence for the best target-coverage FV overlay versus raw FV.
- Policy/overlay: `raw_p50_turbulence_valve_edge4_p60_recross75_near25` / `book_probability`
- Entries/settled/coverage: `112/112/73.68421052631578`
- Brier mean/p95/prob-negative: `-0.014912731593232144/0.0006431900556874973/0.9422`
- Logloss mean/p95/prob-negative: `-0.026989299326773745/0.005780956177999605/0.914`
- Settled rows to 30: `0`; blockers `brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative, coverage_below_75`

### Target-Coverage FV Attribution

- Bucket attribution for where the target-coverage FV improvement comes from.
- Strong raw-p>=60 rows drive brier sum -0.7798092966370004 over 76 rows.
- Weak raw 50-60 rows contribute brier sum -0.8904166418049997 over 36 rows.
- Weak-but-edge-kept rows are mostly unadjusted by the selected overlay; brier sum -0.8807363632099998.
- Strong-raw thin-edge rows still benefited from sharpening; brier sum 0.09700876493399982.
- `all`: rows `112`, W/L `64-48`, net `-626c`, Brier sum `-1.6702259384420002`, logloss sum `-3.0228015245986595`
- `ask_lte_70`: rows `90`, W/L `44-46`, net `-976c`, Brier sum `-1.9956291835410003`, logloss sum `-4.146542136449396`
- `edge_lt_10pp`: rows `82`, W/L `53-29`, net `-231c`, Brier sum `0.14163320213400005`, logloss sum `0.7589778707653746`
- `raw_p_ge_60`: rows `76`, W/L `47-29`, net `-715c`, Brier sum `-0.7798092966370004`, logloss sum `-1.0592136805204548`
- `reason_keep_p_ge_60`: rows `76`, W/L `47-29`, net `-715c`, Brier sum `-0.7798092966370004`, logloss sum `-1.0592136805204548`
- `away_from_strike`: rows `71`, W/L `46-25`, net `-319c`, Brier sum `-0.5963409776730002`, logloss sum `-0.6867084800444696`
- `edge_ge_4pp`: rows `68`, W/L `36-32`, net `-255c`, Brier sum `-1.757554424781`, logloss sum `-3.31106775993561`
- `won`: rows `64`, W/L `64-0`, net `4381c`, Brier sum `3.09009049747`, logloss sum `6.989383519682317`

### Target-Coverage Promotion Audit

- Ready for promotion review: `False`
- Candidate: `raw_p50_turbulence_valve_edge4_p60_recross75_near25` / `book_probability`
- Entries/settled/coverage: `112/112/73.68421052631578`
- Net/Brier p95/Logloss p95: `-626.0/0.0006431900556874973/0.005780956177999605`
- Settled rows to 30: `0`
- blocker `target_coverage_band`: actual `73.68421052631578`, required `75.0-90.0`
- blocker `positive_forward_pnl`: actual `-626.0`, required `> 0.0`
- blocker `brier_interval_strictly_better_than_raw`: actual `0.0006431900556874973`, required `< 0`
- blocker `logloss_interval_strictly_better_than_raw`: actual `0.005780956177999605`, required `< 0`

### Target-Coverage Sample Runway

- Coverage/sample fragility for the current target-coverage FV candidate.
- Entries/settled/pending/denominator: `112/112/0/152`
- Coverage: `73.68421052631578`; settled rows to 30 `0`
- Miss runway before below 75%: `0`; entry runway before above 90%: `248`

### Target-Coverage FV Fragility Audit

- Stress-tests whether the active overlay edge is concentrated in one row or one fragile bucket.
- Rows/W/L: `112/64/48`
- Brier mean/sum: `-0.014912731593232144/-1.6702259384420002`
- Logloss mean/sum: `-0.026989299326773745/-3.0228015245986595`
- Negative/positive Brier rows: `48/64`
- Fragility flags: `none`
- geometry `strong_far_from_boundary`: rows/W-L `21/20-1`, brier sum `0.589710382582`
- geometry `strong_mid_geometry`: rows/W-L `55/27-28`, brier sum `-1.3695196792190003`
- geometry `weak_but_wide_edge`: rows/W-L `12/5-7`, brier sum `-0.5883449382650001`
- geometry `weak_other`: rows/W-L `11/6-5`, brier sum `0.030515354466000177`
- geometry `weak_turbulent_boundary`: rows/W-L `13/6-7`, brier sum `-0.33258705800599986`

### Target-Coverage FV Bucket Reliability

- Bucket calibration for raw FV versus the active target-coverage overlay.
- Rows: `112`
- Raw/overlay ECE: `0.1113570714285714/0.028928571428571415`
- ECE delta overlay-minus-raw: `-0.08242849999999999`
- Flags: `some_overlay_buckets_lt_10`
- overlay bucket `50_60`: count `27`, W/L `14-13`, avg p `0.5451851851851852`, win rate `0.5185185185185185`, reliable `True`
- overlay bucket `60_70`: count `29`, W/L `18-11`, avg p `0.6344827586206896`, win rate `0.6206896551724138`, reliable `True`
- overlay bucket `70_80`: count `14`, W/L `11-3`, avg p `0.7428571428571429`, win rate `0.7857142857142857`, reliable `True`
- overlay bucket `80_90`: count `9`, W/L `9-0`, avg p `0.8311111111111111`, win rate `1.0`, reliable `False`

### Target-Coverage FV Live Evidence Audit

- Separates approved-entry evidence from actionable rejected shadow rows.
- Total rows/W-L/net: `112/64-48/-626c`
- Approved-entry rows: `7`
- Simulated/rejected rows/share: `105/93.8%`
- Blockers: `actual_approved_rows_lt_10, simulated_share_gt_35pct`
- source `approved_entry`: rows/W-L `7/7-0`, brier d mean `0.029919474921714272`
- source `rejected_actionable`: rows/W-L `105/57-48`, brier d mean `-0.01790154536089524`

### Target-Coverage Danger Overlap

- Checks whether the target-coverage surface actually enters the raw/book danger-zone regime.
- Entries/settled/scored: `125/125/125`
- Danger rows >30pp/>20pp: `5/11`
- Max gap row: `KXBTC15M-26MAY062100-00` `no` gap `0.39558800000000005` won `False`
- Target-coverage surface has 125 entries and 125 settled rows.
- Rows with raw-book gap >30pp: 5; rows >20pp: 11; max gap: 0.39558800000000005.
- Current target-coverage evidence is not being driven by the approved-entry danger-zone regime.

### Target-Coverage Price Friction

- Separates directional FV failure from entry-price and boundary-friction damage.
- Entries/settled/coverage: `112/112/73.6842105263158`
- Net cents: `-626c`

| tag | settled | W/L | win rate | net c | avg ask | avg edge |
|---|---:|---:|---:|---:|---:|---:|
| mid_high_recross | 47 | 21/26 | 0.44680851063829785 | -950c | 0.5285106382978724 | 0.08769474468085107 |
| edge_lt_2pp | 22 | 10/12 | 0.45454545454545453 | -883c | 0.6359090909090909 | 0.009212590909090908 |
| early_no_boundary_decay | 30 | 12/18 | 0.4 | -875c | 0.5263333333333333 | 0.0853188 |
| early_ge_780 | 72 | 39/33 | 0.5416666666666666 | -794c | 0.5776388888888889 | 0.05957 |
| ask_55_65 | 31 | 17/14 | 0.5483870967741935 | -434c | 0.5983870967741935 | 0.03438603225806452 |
| ask_lt_50 | 33 | 12/21 | 0.36363636363636365 | -357c | 0.3987878787878788 | 0.1615571212121212 |
| side_no | 52 | 30/22 | 0.5769230769230769 | -323c | 0.5826923076923077 | 0.08501103846153847 |
| side_yes | 60 | 34/26 | 0.5666666666666667 | -303c | 0.5643333333333334 | 0.07734769999999999 |

### False-Conviction Physics Audit

- Tests whether medium-edge early boundary rows are over-sharp FV rather than real edge.
- Entries/settled/coverage: `112/112/73.68421052631578`
- Current W/L/net: `64/48/-626c`
- mid_edge_boundary_4_8pp is a repeated negative-expectancy pocket: 21 settled, W/L 10/11, net -290.0c.
- Best adjusted-FV valve for mid_edge_boundary_4_8pp is full_to_50: coverage 60.526315789473685%, net -228.0c, delta 398.0c.
- cheap_near_boundary_turbulence is a repeated negative-expectancy pocket: 24 settled, W/L 11/13, net -80.0c.
- Best adjusted-FV valve for cheap_near_boundary_turbulence is full_to_book: coverage 57.89473684210527%, net -546.0c, delta 80.0c.
- early_no_boundary_decay is a repeated negative-expectancy pocket: 30 settled, W/L 12/18, net -875.0c.
- Best adjusted-FV valve for early_no_boundary_decay is half_to_50: coverage 60.526315789473685%, net 200.0c, delta 826.0c.
- composite_false_conviction_zone is a repeated negative-expectancy pocket: 50 settled, W/L 21/29, net -1017.0c.
- Best adjusted-FV valve for composite_false_conviction_zone is half_to_50: coverage 56.57894736842105%, net 274.0c, delta 900.0c.
- `mid_edge_boundary_4_8pp`: inside settled/net `21/-290c`, best shrink `full_to_50` kept coverage/net/delta `60.526315789473685/-228c/398c`
- `composite_false_conviction_zone`: inside settled/net `50/-1017c`, best shrink `half_to_50` kept coverage/net/delta `56.57894736842105/274c/900c`

### Composite False-Conviction Repair Robustness

- Leave-one-market-out check for replacing composite false-conviction rows while preserving target coverage.
- Best scorer: `farthest_boundary`
- Full net/coverage: `133c/75.0`
- Worst leave-one-out net: `69c`
- Negative-net leaveouts: `0`
- Robust positive: `True`
- Best robustness-ranked scorer is farthest_boundary with full net 133.0c and coverage 75.0%.
- Leave-one-market-out worst net is 69.0c; negative-net exclusions 0.
- This remains diagnostic; live use requires the frozen forward validator to mature.

### Composite False-Conviction Repair Stress

- Source-mix and full-loss fragility check for the frozen composite repair candidate.
- Candidate settled/W-L/net/coverage: `83/55-28/-84c/75.45454545454545`
- Target settled/W-L/net/coverage: `80/47-33/100c/72.72727272727273`
- Delta vs target: `-184c`
- Source counts: `{'candidate': {'approved_entry': 28, 'rejected_actionable': 55}, 'danger': {'rejected_actionable': 33}, 'kept': {'approved_entry': 5, 'rejected_actionable': 42}, 'repair': {'approved_entry': 23, 'rejected_actionable': 13}, 'target': {'approved_entry': 5, 'rejected_actionable': 75}}`
- Warnings: `All avoided danger rows are reconstructed rejected-actionable rows so far; this is not enough live-approved proof.; 13 repair rows are reconstructed; approved-only repair behavior must stay acceptable.; Three ordinary full losses would erase current positive net.`
- Full candidate: 83 settled, 55/28, net -84.0c, coverage 75.45454545454545%.
- Delta versus target: -184.0c.
- Danger source mix: Counter({'rejected_actionable': 33}).
- Repair source mix: Counter({'approved_entry': 23, 'rejected_actionable': 13}).
- All avoided danger rows are reconstructed rejected-actionable rows so far; this is not enough live-approved proof.
- 13 repair rows are reconstructed; approved-only repair behavior must stay acceptable.
- Three ordinary full losses would erase current positive net.

### Weak-Boundary Reversal Bakeoff

- Tests whether weak near-boundary high-recross entries should wait for a same-market opposite-side signal.
- Best policy: `p55_recross75_near20_delay120_abstain`
- Candidate net/coverage/delta: `-259c/75.0/347c`
- Weak removed net / opposite replacement net / repair net: `-262c/119c/-34c`
- Leave-one-out worst net / negative exclusions: `-400c/114`
- Best variant p55_recross75_near20_delay120_abstain nets -259.0c at 75.0% coverage.
- Leave-one-market worst net is -400.0c with 114 negative exclusions.
- Even the best variant is not live-promotable because net P&L is not positive.
- Robustness is weak: one-market exclusions still leave negative net.
- This remains diagnostic until frozen forward validation earns enough future rows.

### Weak-Reversal Residual Attribution

- Shows what still loses after the best weak-boundary reversal repair.
- Best policy: `p55_recross75_near20_delay120_abstain`
- Best weak-reversal candidate remains negative: -259.0c on 114 settled rows.
- Worst residual tag is recross_65_80 with 23 settled rows and -1062.0c.
- This is attribution only; do not convert a tag into a rule without frozen forward evidence.
- `recross_65_80`: settled `23`, W/L `7/16`, net `-1062c`
- `edge_lt2pp`: settled `22`, W/L `10/12`, net `-883c`
- `stc_gte850`: settled `36`, W/L `19/17`, net `-703c`
- `absd_20_35`: settled `40`, W/L `20/20`, net `-476c`
- `delay_missing`: settled `111`, W/L `69/42`, net `-398c`

### Weak-Reversal Residual FV Shrink

- Discovery-only FV calibration test for the residual NO-side 5-8pp raw-edge zone.
- Best variant: `minus_08`
- All Brier/logloss delta: `-0.0015845515789473796/-0.0029887895193967395`
- Zone rows/avg p/win rate: `12/0.6374160833333334/0.5833333333333334`
- Zone Brier/logloss delta: `-0.015053239999999996/-0.028393500434269248`
- Residual zone raw rows: 12; raw avg p 0.7174160833333333 vs win rate 0.5833333333333334.
- Best FV variant is minus_08 with all Brier/logloss deltas -0.0015845515789473796/-0.0029887895193967395.
- In-zone adjusted avg p is 0.6374160833333334 with Brier/logloss deltas -0.015053239999999996/-0.028393500434269248.
- This is calibration evidence only; entry profitability still requires frozen forward validation.

### Frozen Weak-Reversal Residual FV Shrink

- Future-only calibration validator for the residual FV shrink.
- Freeze timestamp UTC: `2026-05-06T10:29:42.136727+00:00`
- Brier/logloss delta: `0.004216384841108062/0.01073650353744382`
- Ready: `False`; blockers `brier_not_better, logloss_not_better`
- Frozen forward denominator is 108; scored rows 81.
- Raw Brier/logloss 0.23701222812462963/0.6783386257825808; variant 0.2412286129657377/0.6890751293200246.
- Promotion blocked by: brier_not_better, logloss_not_better.
- This validates calibration only; entry PnL is tracked by the separate residual repair validator.

### NO Mid-Edge FV Generalization

- Checks whether NO-side 5-8pp overconfidence exists on the broader target surface.
- Best variant: `no_mid_to_book`
- All Brier/logloss delta: `-0.0008393972756696455/-0.0011176499406210239`
- NO-mid rows/W-L/net/avg p/win rate: `14/8-6/-97c/0.5864285714285714/0.5714285714285714`
- Raw NO mid-edge rows: 14; W/L 8/6; net -97.0c; avg p 0.6524786428571429 vs win rate 0.5714285714285714.
- Best broader FV variant is no_mid_to_book with all-row Brier/logloss deltas -0.0008393972756696455/-0.0011176499406210239.
- If this broader check disagrees with weak-reversal repair, treat the repair as candidate-specific until forward rows mature.

### Frozen NO Mid-Edge FV

- Future-only validator for the broader NO-side 5-8pp book-anchor FV shrink.
- Freeze timestamp UTC: `2026-05-06T10:33:21.044716+00:00`
- Brier/logloss delta: `0.002992138690551288/0.007193315774060016`
- Ready: `False`; blockers `brier_not_better, logloss_not_better`
- Frozen forward denominator is 107; scored rows 78.
- Raw Brier/logloss 0.21644742203030767/0.6144511667103113; variant 0.21943956072085896/0.6216444824843713.
- Promotion blocked by: brier_not_better, logloss_not_better.
- This is a frozen calibration overlay, not live order logic.

### NO Mid-Edge Entry Repair

- Discovery-only broader entry translation of the NO-side 5-8pp FV overconfidence clue.
- Policy: `skip_no_edge_5_8pp_repair_farthest_boundary`
- Target net / candidate net / delta: `-606c/-572c/34c`
- Candidate coverage: `75.0`; skipped/repair net `-97c/-63c`
- Leave-one-out worst net / negative exclusions: `-713c/114`
- Skipped NO mid-edge rows: 14; repair rows added: 16.
- Target net -606.0c; candidate net -572.0c at 75.0% coverage.
- Candidate is not live-promotable until net PnL is positive in frozen forward validation.
- Discovery-only; freeze separately if this remains useful.

### Weak-Reversal Residual Repair

- Discovery-only repair for the residual 5-8pp NO-side price-geometry loss cluster.
- Best policy: `weak_reversal_skip_recross_65_80_repair_farthest_boundary`
- Candidate net/coverage/delta: `-181c/73.02631578947368/839c`
- Leave-one-out worst net / negative exclusions: `-322c/111`
- Weak-reversal base net is -1020.0c at 75.0% coverage.
- Best residual repair is weak_reversal_skip_recross_65_80_repair_farthest_boundary with net -181.0c at 73.02631578947368% coverage.
- The repair improves damage if positive delta, but is still not live-promotable unless net becomes positive and forward-robust.
- Best leave-one-market worst net is -322.0c with 111 negative exclusions.
- This is discovery-only; any skip tag must be frozen before promotion.

### Frozen Weak-Reversal Residual Repair

- Future-only validator for the positive weak-reversal residual repair discovery.
- Freeze timestamp UTC: `2026-05-06T10:25:15.561162+00:00`
- Candidate entries/settled/net/coverage: `81/81/-1127c/75.0`
- Live ready: `False`; blockers `net_not_positive`
- Frozen forward denominator is 108; candidate has 81 settled rows and net -1127.0c.
- Promotion blocked by: net_not_positive.
- This is a forward validator, not live order logic.

### Early-Clock Wait Bakeoff

- Discovery-only test of whether very early boundary-churn rows should age before entry.
- Best policy: `all_early_wait480_p50_opposite_side_delay480`
- Candidate entries/settled/net/coverage: `114/114/615c/75.0`
- Target net/delta: `-606c/1221c`
- LOO worst/negative exclusions: `1046c/0`

### Frozen Early-Boundary Wait Repair

- Future-only validator for the early boundary-churn wait/repair discovery.
- Freeze timestamp UTC: `2026-05-06T10:48:07.385138+00:00`
- Candidate entries/settled/net/coverage: `80/80/82c/75.47169811320755`
- Live ready: `True`; blockers `none`
- Frozen forward denominator is 106; candidate has 80 settled rows and net 82.0c.
- Target net is 158.0c; candidate delta is -76.0c.
- Promotion blocked by: none.
- This is a forward validator, not live order logic.

### Frozen Early-Boundary Opposite Wait Repair

- Future-only validator for the same-market opposite-side wait/repair discovery.
- Freeze timestamp UTC: `2026-05-06T10:53:40.348250+00:00`
- Candidate entries/settled/net/coverage: `80/80/98c/75.47169811320755`
- Opposite replacements entries/net: `3/110c`
- Live ready: `True`; blockers `none`
- Frozen forward denominator is 106; candidate has 80 settled rows and net 98.0c.
- Same-market opposite replacements: 3; replacement net 110.0c.
- Target net is 158.0c; candidate delta is -60.0c.
- Promotion blocked by: none.
- This is a forward validator, not live order logic.

### Side-Asymmetry FV Entry Bridge

- Tests whether the side-asymmetry probability correction can become entry economics.
- Best adjusted-edge floor: `0.02`
- Candidate net/coverage/delta: `331c/75.0/937c`
- Skipped net / repair net: `-1293c/-356c`
- Best adjusted-edge floor is 0.02 with net 331.0c and delta 937.0c.
- Coverage is 75.0% after skipping 43 rows and adding 45 repairs.
- Skipped rows alone had net -1293.0c.
- This is diagnostic only; frozen future validation is required before promotion.

### Side-Asymmetry Bridge Repair Bakeoff

- Compares ex-ante repair scorers after the side-asymmetry bridge skip.
- Best repair scorer: `prob_edge_stability`
- Candidate net/coverage/delta: `475c/75.0/1081c`
- Repair net: `-212c`
- Best repair scorer is prob_edge_stability with net 475.0c and coverage 75.0%.
- Skipped rows net -1293.0c; repair rows net -212.0c.
- This is diagnostic only; frozen future validation is required before promotion.

### Side-Asymmetry Bridge Strict Repair

- Requires repair rows to clear the same adjusted-FV edge floor as kept rows.
- Best repair scorer: `prob_edge_stability`
- Coverage repaired: `True`
- Candidate net/coverage/delta: `427c/75.0/1033c`
- Strict repair net: `-260c`
- Best strict repair scorer is prob_edge_stability with net 427.0c and coverage 75.0%.
- Coverage repaired: True using 45/45 repair rows.
- Strict repair rows must clear the same adjusted-edge floor as kept target rows.

### Frozen Side-Asymmetry Entry Bridge

- Future-only validator for the fixed side-asymmetry adjusted-edge skip plus strict far-boundary repair.
- Candidate: `target_coverage_side_asymmetry_adjusted_edge2pp_strict_farthest_boundary_repair`
- Future denominator: `96`
- Candidate entries/settled/coverage: `72/72/75.0`
- Candidate net vs target: `233c/142c`
- Delta vs target: `91c`
- Skipped net / repair net: `-420c/-329c`
- Blockers: `none`
- Frozen side-asymmetry entry bridge has denominator 96, candidate entries/settled 72/72.
- Coverage 75.0%; candidate net 233.0c versus target 142.0c; delta 91.0c.
- Skipped rows were 12/11 for -420.0c; repairs were 13/9 for -329.0c.
- Strict repairs chosen/needed/available: 22/22/17.
- Promotion blockers: none.

### Target-Coverage Conservative FV Variants

- Diagnostic variants that reduce sharpening in churny mid-confidence rows.
- Entries/settled/denominator: `112/112/152`
- Best variant: `logit125_p60_calm_mid_or_p75`
- Best Brier/logloss mean: `-0.0022095221651635597/-0.008271439367388467`
- Best Brier/logloss p95: `0.00023302876583982003/-0.0010341869828960474`
- `logit125_p60_calm_mid_or_p75`: brier/logloss mean `-0.0022095221651635597/-0.008271439367388467`, p95 `0.00023302876583982003/-0.0010341869828960474`, blockers `brier_interval_not_strictly_negative`
- `logit125_p75`: brier/logloss mean `-0.0015769093300218757/-0.00675303480588537`, p95 `0.00010325429169352918/-0.000926151613492282`, blockers `brier_interval_not_strictly_negative`
- `logit125_p80`: brier/logloss mean `-0.0010898565154959564/-0.005465426752974486`, p95 `-0.0006003543229165092/-0.0032288640435887373`, blockers `none`
- `logit125_p70`: brier/logloss mean `-0.0003773633313270222/-0.003571990138160214`, p95 `0.0023817984473211875/0.004777279934570317`, blockers `brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative`

### Target-Coverage Source-Split FV

- Splits target-coverage FV calibration by approved-entry versus rejected-actionable rows.
- Entries/settled/denominator: `112/112/152`
- all best is logit125_p75 over 112 rows with Brier/logloss deltas -0.0015769093300218757/-0.00675303480588537.
- approved_entry best is logit125_p70 over 7 rows with Brier/logloss deltas -0.005753117335864851/-0.03925202238843982.
- rejected_actionable best is logit125_p75 over 105 rows with Brier/logloss deltas -0.0012984954629656775/-0.004586435633715074.
- `all` best `logit125_p75`: rows `112`, Brier/logloss `-0.0015769093300218757/-0.00675303480588537`, neg/pos Brier `20/1`
- `approved_entry` best `logit125_p70`: rows `7`, Brier/logloss `-0.005753117335864851/-0.03925202238843982`, neg/pos Brier `7/0`
- `rejected_actionable` best `logit125_p75`: rows `105`, Brier/logloss `-0.0012984954629656775/-0.004586435633715074`, neg/pos Brier `13/1`

### Target-Coverage P70 Jackknife

- Leave-one-market-out robustness for p70 FV versus raw.
- Pass/failures: `True/0`
- Full rows/adjusted: `112/31`
- Full Brier/logloss: `-0.0003773633313270222/-0.003571990138160214`
- Worst Brier leave-out: `KXBTC15M-26MAY061800-00` `-0.00016725015284209776`
- Worst logloss leave-out: `KXBTC15M-26MAY062300-00` `-0.0030458551730619884`

### Frozen Target-Coverage Conservative FV

- Forward-only validator for logit125_p60_calm_mid_or_p75.
- Freeze timestamp UTC: `2026-05-06T03:26:44.025585+00:00`
- Future entries/settled/denominator: `98/98/136`
- Coverage: `72.1%`
- Best variant: `logit125_p60_calm_mid_or_p75`
- Best Brier/logloss mean: `-0.0019986929824834733/-0.006824434041934604`
- Blockers: `brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative`

### Frozen Target-Coverage P70 FV

- Forward-only validator for high-confidence-only p70 sharpening.
- Freeze timestamp UTC: `2026-05-06T03:45:32.798460+00:00`
- Future entries/settled/denominator: `97/97/135`
- Coverage: `71.9%`
- Best variant: `logit125_p70`
- Best Brier/logloss mean: `0.0003572449270448449/-0.0008767815212288292`
- Blockers: `mean_brier_not_better, brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative`

### Frozen Target-Coverage P70 Runway

- Explains post-freeze p70 denominator markets without selected target-coverage entries.
- Future denominator/selected/base-seen: `135/97/133`
- Coverage: `71.9%`
- Frozen p70 has 97 selected markets, 36 markets with base rows that failed the target policy, and 2 markets with no target base row.
- Base rows by raw-probability bucket: <60=68, 60-70 boundary=40, >=70 p70-adjustable=25.
- Unselected p70-adjustable rows: 0; if this stays 0, the current blocker is not p70 scoring but lack of high-confidence post-freeze opportunities.
- If no-base dominates, the blocker is evidence availability/entry-surface opportunity, not p70 probability scoring.
- `KXBTC15M-26MAY060000-00` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060015-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060030-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060045-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060100-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060115-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060130-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060145-45` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060200-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060215-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060230-30` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060245-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060300-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060315-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060330-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060345-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060400-00` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060415-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060430-30` `no_target_base_row`: base `0`, selected `0`
- `KXBTC15M-26MAY060445-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060500-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060515-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060530-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060545-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060600-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060615-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060630-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060645-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060700-00` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060715-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060730-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060745-45` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060800-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060815-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060830-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060845-45` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060900-00` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060915-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060930-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060945-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061000-00` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061015-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061030-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061045-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061100-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061115-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061130-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061145-45` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061200-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061215-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061230-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061245-45` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061300-00` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061400-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061415-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061430-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061445-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061500-00` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061515-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061530-30` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061545-45` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061600-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061615-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061630-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061645-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061700-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061715-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061730-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061745-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061800-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061815-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061830-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061845-45` `no_target_base_row`: base `0`, selected `0`
- `KXBTC15M-26MAY061900-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061915-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061930-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061945-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062000-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062015-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062030-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062045-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062100-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062115-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY062130-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062145-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062200-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062215-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062230-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062245-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062300-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062315-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062330-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062345-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070000-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070015-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY070030-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070045-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070100-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070115-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070130-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070145-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070200-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070530-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070545-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070600-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070615-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070630-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070645-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070700-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070715-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070730-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070745-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070800-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070815-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070830-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070845-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070900-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070915-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070930-30` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY070945-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY071000-00` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY071015-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY071030-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY071045-45` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY071100-00` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY071115-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY071130-30` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY071145-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY071200-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY071215-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY071230-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY071245-45` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY071300-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY071315-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY071330-30` `base_seen_not_selected`: base `1`, selected `0`

### Frozen Target-Coverage P70 Empirical-Bayes Runway

- Explains post-freeze empirical-Bayes p70 denominator markets without selected target-coverage entries.
- Future denominator/selected/base-seen: `132/96/130`
- Coverage: `72.7%`
- Frozen empirical-Bayes p70 has 96 selected markets, 34 markets with base rows that failed the target policy, and 2 markets with no target base row.
- Base rows by raw-probability bucket: <60=66, 60-70 boundary=39, >=70 EB-adjustable=25.
- Unselected EB-adjustable rows: 0; if this stays 0, the blocker is opportunity, not EB probability scoring.
- `KXBTC15M-26MAY060045-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060100-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060115-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060130-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060145-45` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060200-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060215-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060230-30` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060245-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060300-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060315-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060330-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060345-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060400-00` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060415-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060430-30` `no_target_base_row`: base `0`, selected `0`
- `KXBTC15M-26MAY060445-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060500-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060515-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060530-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060545-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060600-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060615-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060630-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060645-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060700-00` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060715-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060730-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060745-45` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060800-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060815-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060830-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060845-45` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060900-00` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY060915-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060930-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY060945-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061000-00` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061015-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061030-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061045-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061100-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061115-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061130-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061145-45` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061200-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061215-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061230-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061245-45` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061300-00` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061400-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061415-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061430-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061445-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061500-00` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061515-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061530-30` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061545-45` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY061600-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061615-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061630-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061645-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061700-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061715-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061730-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061745-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061800-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061815-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061830-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061845-45` `no_target_base_row`: base `0`, selected `0`
- `KXBTC15M-26MAY061900-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061915-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061930-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY061945-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062000-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062015-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062030-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062045-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062100-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062115-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY062130-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062145-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062200-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062215-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062230-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062245-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062300-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062315-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062330-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY062345-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070000-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070015-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY070030-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070045-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070100-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070115-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070130-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070145-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070200-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070530-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070545-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070600-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070615-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070630-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070645-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070700-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070715-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070730-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070745-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070800-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070815-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070830-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070845-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070900-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070915-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY070930-30` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY070945-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY071000-00` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY071015-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY071030-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY071045-45` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY071100-00` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY071115-15` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY071130-30` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY071145-45` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY071200-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY071215-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY071230-30` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY071245-45` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY071300-00` `selected`: base `1`, selected `1`
- `KXBTC15M-26MAY071315-15` `base_seen_not_selected`: base `1`, selected `0`
- `KXBTC15M-26MAY071330-30` `base_seen_not_selected`: base `1`, selected `0`

### Frozen Target-Coverage P70 Pending Sensitivity

- Separates raw-only settled rows from pending p70-adjusted rows.
- hard_p70: entries 97/135, pending adjusted 0, settled adjusted 25.
- hard_p70: 39 settled losses were raw-only, so they are entry-surface evidence, not p70 FV evidence.
- empirical_bayes_p70: entries 96/132, pending adjusted 0, settled adjusted 25.
- empirical_bayes_p70: 38 settled losses were raw-only, so they are entry-surface evidence, not p70 FV evidence.
- `hard_p70`: entries `97`, pending-adjusted `0`, settled-adjusted `25`, raw-only losses `39`
- `empirical_bayes_p70`: entries `96`, pending-adjusted `0`, settled-adjusted `25`, raw-only losses `38`

### Frozen Target-Coverage Book-Edge Gate

- Future-only broad validator for the raw-over-book overconfidence signal on the target-coverage surface.
- Freeze timestamp UTC: `2026-05-06T13:14:17.059642+00:00`
- Denominator/entries/settled: `97/60/60`
- Coverage/net/delta: `61.855670103092784/-163c/-161c`
- Skipped W/L/net: `6/8/161c`
- Blockers: `coverage_too_low, delta_not_positive`

### Frozen Conservative FV Pending Sensitivity

- Shows unresolved frozen conservative FV rows before settlement.
- Pending rows: `0`
- No unresolved frozen conservative target-coverage rows are pending.

### Frozen Mid-Edge False-Conviction FV

- Forward-only probability shrink for early high-recross 4-8pp edge rows.
- Freeze timestamp UTC: `2026-05-06T09:29:25.082774+00:00`
- Future entries/settled/denominator: `82/82/112`
- Best variant: `mid_edge_false_conviction_shrink`
- Target variant rows/adjusted/false-conviction: `82/13/13`
- Brier/logloss mean: `0.0011798864136219548/0.002485718132951559`
- Blockers: `mean_brier_not_better, brier_interval_not_strictly_negative, mean_logloss_not_better, logloss_interval_not_strictly_negative`

### Frozen Composite False-Conviction FV

- Forward-only probability shrink for the broader early boundary/recross false-conviction zone.
- Freeze timestamp UTC: `2026-05-06T09:44:24.062007+00:00`
- Future entries/settled/denominator: `81/81/111`
- Best variant: `composite_false_conviction_full_to_50`
- Target variant rows/adjusted/false-zone: `81/33/33`
- Brier/logloss mean: `0.0014926214225802442/0.0025697363163897946`
- Blockers: `mean_brier_not_better, brier_interval_not_strictly_negative, mean_logloss_not_better, logloss_interval_not_strictly_negative`

### Side-Asymmetry FV Promotion Runway

- Tracks whether the small positive calibration lead can mature without overfit.
- Freeze timestamp UTC: `2026-05-06T07:52:22.405861+00:00`
- Entries/settled/denominator: `None/87/118`
- Adjusted clock/side/total: `37/6/43`
- Brier/logloss delta: `-0.011711620895563213/-0.024525492188571918`
- Ready for consideration: `False`
- blocker `coverage_band`: actual `73.72881355932203`, required `75.0-90.0%`
- blocker `live_readiness_gate`: actual `False`, required `true`

### Frozen Thin-Recross Mid-P Entry Gate

- Forward-only entry-policy candidate for thin-edge high-recross p60-75 rows.
- Freeze timestamp UTC: `2026-05-06T03:39:03.842700+00:00`
- Base entries/settled/net: `97/97/-769c`
- Candidate entries/settled/net: `88/88/-209c`
- Delta net: `560c`; blockers `coverage_too_low, net_not_positive`
- Frozen thin-recross entry gate has 88 entries versus 97 base entries.
- It has skipped 9 future rows so far; promotion requires settled forward rows, not this setup snapshot.
- This is entry-policy evidence, separate from the conservative FV overlay.
- skipped `KXBTC15M-26MAY060830-30` `no`: raw/ask/edge/recross `0.60073/0.59/0.010730000000000017/0.94370017939859`, won/net `False/-122c`
- skipped `KXBTC15M-26MAY060930-30` `yes`: raw/ask/edge/recross `0.604377/0.6/0.004377000000000075/1.150583070145743`, won/net `False/-124c`
- skipped `KXBTC15M-26MAY061030-30` `yes`: raw/ask/edge/recross `0.618153/0.61/0.008152999999999966/1.1682803908710917`, won/net `True/74c`
- skipped `KXBTC15M-26MAY061130-30` `yes`: raw/ask/edge/recross `0.653101/0.65/0.0031010000000000204/1.0562212924605836`, won/net `True/66c`
- skipped `KXBTC15M-26MAY061230-30` `yes`: raw/ask/edge/recross `0.681329/0.68/0.0013289999999999136/0.8624571365398368`, won/net `False/-140c`
- skipped `KXBTC15M-26MAY061430-30` `yes`: raw/ask/edge/recross `0.678512/0.67/0.008511999999999964/0.8935551730324466`, won/net `True/62c`
- skipped `KXBTC15M-26MAY071015-15` `no`: raw/ask/edge/recross `0.609894/0.6/0.00989400000000007/1.10286385624332`, won/net `False/-124c`
- skipped `KXBTC15M-26MAY071115-15` `no`: raw/ask/edge/recross `0.635838/0.62/0.01583800000000002/0.9827713747301794`, won/net `False/-128c`
- skipped `KXBTC15M-26MAY071200-00` `yes`: raw/ask/edge/recross `0.606055/0.6/0.006055000000000033/1.0963020284423506`, won/net `False/-124c`

### Frozen Raw-p52 Boundary-Turbulence Skip

- Future-only entry-policy candidate for weak raw near-strike high-recross rows.
- Freeze timestamp UTC: `2026-05-06T08:50:27.891448+00:00`
- Base entries/settled/net: `112/112/-258c`
- Candidate entries/settled/net: `88/88/266c`
- Delta net: `524c`; blockers `none`
- Frozen raw-p52 boundary-turbulence skip has 88 entries versus 112 base entries.
- Delta versus base is 524.0c on future settled rows.
- Skipped future rows so far: 24.
- skipped `KXBTC15M-26MAY060515-15` `yes`: raw/ask/edge/abs_d/recross `0.532512/0.41/0.12251200000000001/0.1415/0.9586252411430818`, won/net `False/-86c`
- skipped `KXBTC15M-26MAY060715-15` `yes`: raw/ask/edge/abs_d/recross `0.539914/0.53/0.009913999999999978/0.121733/0.9927087556978985`, won/net `True/90c`
- skipped `KXBTC15M-26MAY060745-45` `no`: raw/ask/edge/abs_d/recross `0.553279/0.54/0.01327899999999993/0.063119/1.2171111689146588`, won/net `True/88c`
- skipped `KXBTC15M-26MAY060800-00` `yes`: raw/ask/edge/abs_d/recross `0.523411/0.47/0.053410999999999986/0.027808/1.35887119729371`, won/net `True/102c`
- skipped `KXBTC15M-26MAY060815-15` `no`: raw/ask/edge/abs_d/recross `0.540349/0.54/0.0003489999999999327/0.089986/1.015007140576039`, won/net `True/88c`
- skipped `KXBTC15M-26MAY060845-45` `no`: raw/ask/edge/abs_d/recross `0.528543/0.52/0.008542999999999967/0.032503/1.2380786497088192`, won/net `True/92c`
- skipped `KXBTC15M-26MAY061115-15` `yes`: raw/ask/edge/abs_d/recross `0.533622/0.52/0.013622000000000023/0.014701/1.4528882832170376`, won/net `False/-108c`
- skipped `KXBTC15M-26MAY061145-45` `yes`: raw/ask/edge/abs_d/recross `0.544366/0.51/0.03436600000000001/0.150878/1.2299556173371293`, won/net `False/-106c`
- skipped `KXBTC15M-26MAY061215-15` `no`: raw/ask/edge/abs_d/recross `0.536898/0.53/0.00689799999999996/0.085521/1.278404126788222`, won/net `False/-110c`
- skipped `KXBTC15M-26MAY061245-45` `no`: raw/ask/edge/abs_d/recross `0.555732/0.52/0.035731999999999986/0.180237/1.2113630662378887`, won/net `False/-108c`
- skipped `KXBTC15M-26MAY061300-00` `no`: raw/ask/edge/abs_d/recross `0.544132/0.54/0.0041319999999999135/0.065489/1.32716783022847`, won/net `True/88c`
- skipped `KXBTC15M-26MAY061415-15` `no`: raw/ask/edge/abs_d/recross `0.521166/0.49/0.031166000000000027/0.052412/0.9729362862931707`, won/net `True/98c`
- skipped `KXBTC15M-26MAY061500-00` `yes`: raw/ask/edge/abs_d/recross `0.55091/0.55/0.0009099999999999664/0.111078/1.0028710028566805`, won/net `False/-114c`
- skipped `KXBTC15M-26MAY061530-30` `no`: raw/ask/edge/abs_d/recross `0.548704/0.53/0.018703999999999943/0.150647/0.995442388558846`, won/net `False/-110c`
- skipped `KXBTC15M-26MAY061930-30` `yes`: raw/ask/edge/abs_d/recross `0.551364/0.47/0.08136399999999999/0.100563/0.9053776147792911`, won/net `True/102c`
- skipped `KXBTC15M-26MAY070030-30` `no`: raw/ask/edge/abs_d/recross `0.523605/0.33/0.19360499999999997/0.059362/0.9016513046480161`, won/net `False/-70c`
- skipped `KXBTC15M-26MAY070730-30` `yes`: raw/ask/edge/abs_d/recross `0.530778/0.46/0.07077799999999995/0.091964/0.9361206885177036`, won/net `False/-96c`
- skipped `KXBTC15M-26MAY070945-45` `no`: raw/ask/edge/abs_d/recross `0.532085/0.48/0.05208500000000005/0.067417/1.0888633329884525`, won/net `True/100c`
- skipped `KXBTC15M-26MAY071000-00` `yes`: raw/ask/edge/abs_d/recross `0.54351/0.54/0.003510000000000013/0.037031/1.2196742426451674`, won/net `False/-112c`
- skipped `KXBTC15M-26MAY071045-45` `yes`: raw/ask/edge/abs_d/recross `0.557862/0.55/0.007861999999999925/0.082257/1.3063143472933103`, won/net `False/-114c`
- skipped `KXBTC15M-26MAY071215-15` `yes`: raw/ask/edge/abs_d/recross `0.543727/0.53/0.013726999999999934/0.056856/1.2728872894040717`, won/net `False/-110c`
- skipped `KXBTC15M-26MAY071245-45` `yes`: raw/ask/edge/abs_d/recross `0.559979/0.55/0.00997899999999996/0.168899/1.2558351836470223`, won/net `False/-114c`
- skipped `KXBTC15M-26MAY071315-15` `yes`: raw/ask/edge/abs_d/recross `0.533442/0.51/0.023441999999999963/0.04271/1.2152323464731665`, won/net `True/94c`
- skipped `KXBTC15M-26MAY071330-30` `yes`: raw/ask/edge/abs_d/recross `0.544206/0.52/0.02420599999999995/0.117101/1.086678742980054`, won/net `False/-108c`

### Frozen Target-Loss Tag Repair Entry

- Future-only repair candidate for weak-boundary and paid-thin-edge target-coverage loss tags.
- Freeze timestamp UTC: `2026-05-06T08:59:17.610337+00:00`
- Target entries/settled/net: `84/84/-143c`
- Candidate entries/settled/net: `86/86/-731c`
- Delta net: `-588c`; blockers `net_not_positive`
- Future candidate has 86 entries and 86 settled rows.
- Candidate net is -731.0c versus target -143.0c.
- Target-loss rows removed: 28; repair rows added: 30.
- Promotion blockers: net_not_positive.

### Frozen Early NO Boundary-Decay Repair Entry

- Future-only repair candidate for early NO-side boundary decay and cheap near-boundary turbulence.
- Freeze timestamp UTC: `2026-05-06T09:10:09.146392+00:00`
- Target entries/settled/net: `83/83/-57c`
- Danger entries/settled/net: `30/30/-314c`
- Candidate entries/settled/net: `85/85/27c`
- Delta net: `84c`; blockers `none`
- Future candidate has 85 entries and 85 settled rows.
- Candidate net is 27.0c versus target -57.0c.
- Early/path-decay danger rows removed: 30; repair rows added: 32.

### Early NO Boundary-Decay Repair Runway

- Promotion runway for the frozen early-NO boundary-decay repair lane.
- Candidate entries/settled/net/coverage: `85/85/27c/75.22123893805309`
- Rows needed for 30: `0`
- Full 100c losses before net flat: `0`
- Pending danger rows / stressed delta: `0/84c`
- Ready for consideration: `True`
- Need 0 more settled candidate rows before the sample-size gate is met.
- Candidate net is 27.0c versus target -57.0c.
- The rule has a clean physics story, but current evidence can be broken by a small number of adverse future rows.

### Early NO Boundary-Decay Repair Stress

- Anti-overfit/source-quality stress for the frozen early-NO boundary-decay repair lane.
- Candidate settled/net/coverage: `85/27c/75.22123893805309`
- Source counts: candidate `{'approved_entry': 26, 'rejected_actionable': 59}`, danger `{'rejected_actionable': 30}`, repair `{'approved_entry': 21, 'rejected_actionable': 11}`
- warning: All avoided danger rows are reconstructed rejected-actionable rows so far; this is useful physics evidence, but not enough live-approved proof.
- warning: 11 repair rows are reconstructed; check approved-only repair performance before promotion.

### Frozen Mid-Edge Boundary-Deception Repair Entry

- Future-only repair candidate for early high-recross 4-8pp edge rows that may be false conviction.
- Freeze timestamp UTC: `2026-05-06T09:23:03.299714+00:00`
- Target entries/settled/net: `82/82/55c`
- Danger entries/settled/net: `13/13/404c`
- Candidate entries/settled/net: `84/84/-431c`
- Delta net: `-486c`; blockers `net_not_positive`
- Future candidate has 84 entries and 84 settled rows.
- Candidate net is -431.0c versus target 55.0c.
- Mid-edge boundary-deception rows removed: 13; repair rows added: 15.
- Promotion blockers: net_not_positive.

### Frozen Composite False-Conviction Repair Entry

- Future-only repair candidate for the broader false-conviction zone using highest raw-p clean replacements.
- Freeze timestamp UTC: `2026-05-06T09:49:36.645793+00:00`
- Target entries/settled/net: `80/80/100c`
- Danger entries/settled/net: `33/33/-159c`
- Repair entries/settled/net: `36/36/-343c`
- Candidate entries/settled/net: `83/83/-84c`
- Candidate coverage: `75.5%`
- Delta net: `-184c`; blockers `net_not_positive`
- Future candidate has 83 entries and 83 settled rows.
- Candidate net is -84.0c versus target 100.0c.
- Composite false-conviction rows removed: 33; repair rows added: 36.
- Promotion blockers: net_not_positive.

### Frozen Goldilocks Edge Repair Entry

- Forward-only candidate for false-conviction edge phases; diagnostic read uses existing target-surface evidence only.
- Freeze timestamp UTC: `2026-05-06T13:41:43.611538+00:00`
- Diagnostic target entries/settled/net: `90/90/-432c`
- Diagnostic candidate entries/settled/coverage/net: `92/92/75.40983606557377/63c`
- Diagnostic delta net: `495c`
- Frozen future entries/settled/net: `49/49/-159c`
- Frozen blockers: `net_not_positive`
- Diagnostic candidate has 92 entries, 92 settled, coverage 75.40983606557377, net 63.0c versus target -432.0c.
- Diagnostic delta versus target is 495.0c; danger rows removed 38, repair rows added 40.
- Frozen future candidate has 49 entries and 49 settled rows since its own freeze.
- Frozen future blockers: net_not_positive.

### False-Conviction Family Scorecard

- Consolidates the current lead direction: early boundary/high-recross rows where FV edge may be false conviction.
- Integrity-pass candidates: `0`
- Lead with early boundary/high-recross false-conviction filtering, not broad FV sharpening.
- Best forward target-coverage evidence is false_conviction_fv_entry_bridge with settled 70, net 762.0c, coverage 75.26881720430107.
- Goldilocks edge is promising only as a diagnostic: 63.0c net at 75.40983606557377% coverage, but frozen future rows are 48.
- FV-entry bridge approved-only diagnostic support is 321.0c net on 70 settled rows; this is weaker than the all-source/reconstructed read and remains non-promotable.
- No false-conviction family candidate currently clears integrity gates.
- `false_conviction_fv_entry_bridge`: mode `fv_bridge_diagnostic_plus_frozen`, settled `70`, W/L `48/22`, coverage `75.26881720430107`, net `762c`, recon share `0.9142857142857143`, loss cushion `None`, pass `False`, blockers `reconstructed_share_gt_35pct, full_loss_cushion_unknown`
- `early_no_boundary_decay_repair`: mode `frozen_forward_stress`, settled `85`, W/L `56/29`, coverage `75.22123893805309`, net `27c`, recon share `0.6941176470588235`, loss cushion `0`, pass `False`, blockers `reconstructed_share_gt_35pct, full_loss_cushion_lt_3`
- `composite_false_conviction_repair`: mode `frozen_forward_stress`, settled `83`, W/L `55/28`, coverage `75.45454545454545`, net `-84c`, recon share `0.6626506024096386`, loss cushion `0`, pass `False`, blockers `net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3`
- `goldilocks_edge_repair`: mode `diagnostic_plus_frozen`, settled `48`, W/L `30/18`, coverage `75.38461538461539`, net `-90c`, recon share `0.9387755102040817`, loss cushion `0`, pass `False`, blockers `net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3`
- `false_conviction_approved_repair`: mode `frozen_forward_source_quality`, settled `70`, W/L `45/25`, coverage `75.26881720430107`, net `-226c`, recon share `None`, loss cushion `None`, pass `False`, blockers `net_not_positive, source_mix_unknown, full_loss_cushion_unknown`
- `mid_edge_boundary_deception_repair`: mode `frozen_forward`, settled `84`, W/L `50/34`, coverage `75.0`, net `-431c`, recon share `None`, loss cushion `None`, pass `False`, blockers `net_not_positive, source_mix_unknown, full_loss_cushion_unknown`

### False-Conviction Source-Quality Repair

- Tests whether the lead false-conviction lane can preserve 75%+ coverage while keeping reconstructed evidence under 35%.
- Coverage floor needs 85 entries from denominator 113; kept after danger skip is 53, so repairs needed are 32.
- To keep reconstructed share <=35%, at least 56 of 85 entries must be approved-entry rows.
- Approved kept rows: 5; approved clean repair rows currently available: 30.
- Source-quality plus 75% coverage is not feasible with the current forward pool.
- `approved_first_missed_then_any`: entries `85`, settled `85`, coverage `75.22123893805309`, net `-144c`, approved/recon `27/58`, recon share `0.6823529411764706`, blockers `reconstructed_share_gt_35pct, net_not_positive`
- `min_reconstructed_high_p`: entries `85`, settled `85`, coverage `75.22123893805309`, net `-133c`, approved/recon `27/58`, recon share `0.6823529411764706`, blockers `reconstructed_share_gt_35pct, net_not_positive`
- `approved_only`: entries `83`, settled `83`, coverage `73.45132743362832`, net `151c`, approved/recon `35/48`, recon share `0.5783132530120482`, blockers `coverage_too_low, reconstructed_share_gt_35pct`

### Frozen Candidate Leaderboard

- Consolidated forward-only view across frozen candidate families.
- `p50_book_edge_entry` `p50_book_plus_05_edge_nonnegative`: entries `104`, settled `104`, coverage `88.13559322033898`, net `660c`, brier `None`, live_ready `False`
- `composite_false_conviction_fv` `raw_p50_turbulence_valve_edge4_p60_recross75_near25 + composite_false_conviction_full_to_50`: entries `81`, settled `81`, coverage `72.97297297297297`, net `127c`, brier `-0.005133304503345682`, live_ready `False`
- `mid_edge_false_conviction_fv` `raw_p50_turbulence_valve_edge4_p60_recross75_near25 + mid_edge_false_conviction_shrink`: entries `82`, settled `82`, coverage `73.21428571428571`, net `35c`, brier `0.0011798864136219548`, live_ready `False`
- `early_no_boundary_decay_repair_entry` `skip_early_no_boundary_decay_repair_calm_geometry`: entries `85`, settled `85`, coverage `75.22123893805309`, net `27c`, brier `None`, live_ready `False`
- `noise_shrinkage` `noise_shrink_light_p50_edge1`: entries `146`, settled `146`, coverage `96.05263157894737`, net `10c`, brier `0.21553304553452313`, live_ready `False`
- `composite_false_conviction_repair_entry` `skip_composite_false_conviction_repair_highest_raw_p`: entries `83`, settled `83`, coverage `75.45454545454545`, net `-84c`, brier `None`, live_ready `False`

### Candidate Integrity Scorecard

- Separates positive PnL lanes from lanes with enough sample, source quality, and loss cushion.
- Positive target-coverage lanes: `582`
- Integrity-pass lanes: `0`
- Any live-ready candidate: `False`
- Positive target-coverage lanes scored: 582.
- Entry/FV integrity-pass lanes: 0.
- Top entry/FV lane is top_component_parent_fill_repair_child / diagnostic_observable_mid_confidence_parent_fill_quarter with net 2233.0c, settled 76, blockers ['diagnostic_prefreeze', 'source_gate_zero_row_margin'].
- No positive lane currently clears sample, coverage, source-quality, and fragility gates.
- Positive pure exit-policy lanes scored: 50.
- Exit integrity-pass lanes: 0.
- Top exit lane is exit_shallow_drawdown / diagnostic_shallow_drawdown_any_exit_lte5 with net 1576.0c, delta 1287.0c, suppressed 57, blockers ['loss_control_cost_negative', 'live_ready_false'].
- `top_component_parent_fill_repair_child` `diagnostic_observable_mid_confidence_parent_fill_quarter`: settled `76`, coverage `75.24752475247524`, net `2233c`, recon share `0.34210526315789475`, loss cushion `22`, pass `False`, blockers `diagnostic_prefreeze, source_gate_zero_row_margin`
- `top_component_parent_fill_repair_child` `diagnostic_mid_confidence_parent_fill_quarter`: settled `76`, coverage `75.24752475247524`, net `2233c`, recon share `0.34210526315789475`, loss cushion `22`, pass `False`, blockers `diagnostic_prefreeze, source_label_diagnostic, source_gate_zero_row_margin`
- `top_component_parent_fill_repair_child` `diagnostic_observable_mid_confidence_parent_fill_half`: settled `76`, coverage `75.24752475247524`, net `2190c`, recon share `0.34210526315789475`, loss cushion `21`, pass `False`, blockers `diagnostic_prefreeze, source_gate_zero_row_margin`
- `top_component_parent_fill_repair_child` `diagnostic_mid_confidence_parent_fill_half`: settled `76`, coverage `75.24752475247524`, net `2190c`, recon share `0.34210526315789475`, loss cushion `21`, pass `False`, blockers `diagnostic_prefreeze, source_label_diagnostic, source_gate_zero_row_margin`
- `top_component_parent_fill_repair_child` `diagnostic_parent_fill_wide_mid_absd_ask_notch`: settled `76`, coverage `75.24752475247524`, net `2145c`, recon share `0.34210526315789475`, loss cushion `21`, pass `False`, blockers `diagnostic_prefreeze, source_gate_zero_row_margin`
- `top_component_parent_fill_repair_child` `diagnostic_parent_fill_mid_absd_ask_notch`: settled `76`, coverage `75.24752475247524`, net `2142c`, recon share `0.34210526315789475`, loss cushion `21`, pass `False`, blockers `diagnostic_prefreeze, source_gate_zero_row_margin`

### Candidate vs Control Overlap

- Same-market comparison against `baseline_v28_approved`, plus candidate-only simulated exposure.
- Baseline entries/settled/W-L/gross: `107/107/91-16/494c`
- Top gross candidate is book_plus_03_cheap_convex with 916.0c on its selected settled markets.
- Best same-market overlap delta is book_plus_03_cheap_convex at 740.0c across 48 overlapping markets.
- Best 75-90% coverage candidate by gross is p50_book_plus_05_edge_nonnegative with coverage 83.42541436464089 and gross 890.0c.
- Common blockers remain: candidate_simulated_share_gt_35pct, coverage_above_90pct, coverage_below_75pct.
- `p50_book_plus_05_edge_nonnegative`: coverage `83.42541436464089`, gross `890c`, overlap delta `598c`, sim share `74.8%`, blockers `candidate_simulated_share_gt_35pct`
- `p55_edge_nonnegative`: coverage `83.42541436464089`, gross `305c`, overlap delta `117c`, sim share `83.4%`, blockers `candidate_simulated_share_gt_35pct`
- `p65_large_disagreement_anchor_plus_02`: coverage `80.11049723756905`, gross `-1198c`, overlap delta `-932c`, sim share `81.4%`, blockers `candidate_simulated_share_gt_35pct`
- `p65_v28_premium_anchor_plus_02`: coverage `79.55801104972376`, gross `-1376c`, overlap delta `-1030c`, sim share `80.6%`, blockers `candidate_simulated_share_gt_35pct`

### Candidate Live-Validation Runway

- Estimates future non-simulated evidence needed before shadow candidates are operationally credible.
- Best target-coverage gross row is p50_book_plus_05_edge_nonnegative at 890.0c, but it needs 172 future actual-only entries to bring simulated share to <=35%.
- Closest row to validation by count is book_plus_03_cheap_convex needing 171 future validation rows, coverage 50.82872928176796.
- This runway is not a live-trading instruction; it defines how much forward evidence is still missing.
- `p50_book_plus_05_edge_nonnegative`: coverage `83.42541436464089`, gross `890c`, sim share `74.8%`, future actual needed `172`, settled needed `0`
- `p65_book_plus_03`: coverage `80.11049723756905`, gross `-1486c`, sim share `77.2%`, future actual needed `175`, settled needed `0`
- `p65_v28_premium_anchor_plus_02`: coverage `79.55801104972376`, gross `-1376c`, sim share `80.6%`, future actual needed `188`, settled needed `0`
- `p65_large_disagreement_anchor_plus_02`: coverage `80.11049723756905`, gross `-1198c`, sim share `81.4%`, future actual needed `193`, settled needed `0`
- `p65_book_plus_02`: coverage `83.97790055248619`, gross `-1542c`, sim share `82.2%`, future actual needed `206`, settled needed `0`
- `p55_edge_nonnegative`: coverage `83.42541436464089`, gross `305c`, sim share `83.4%`, future actual needed `209`, settled needed `0`

### Broad Book-Edge Source Audit

- Diagnostic-only source/physics check for the current broad book-edge lane.
- Policy: `book_plus_05_no_cheap_yes_boundary`
- Diagnostic supported: `False`
- Entries/settled/W-L/gross: `164/164/92-72/646c`
- Simulated share: `81.1%`
- Blockers: `simulated_share_gt_35pct`
- `approved_entry`: settled `31`, W-L `26-5`, gross `132c`
- `rejected_actionable`: settled `133`, W-L `66-67`, gross `514c`

### Frozen Book-Edge Pending Sensitivity

- Pre-settlement raw-vs-book sensitivity for frozen book-edge rows.
- Pending rows: `0`
- Unique pending markets: `0`

### Live Trade Readiness

- Any live-ready candidate: `False`
- Control risk stop active: `True`
- `primary_p60` `first_side_raw_later_book_p60_edge0`: live_ready `False`, entries `153`, settled `153`, net `-3318c`, blockers `fv:coverage_too_high, fv:net_not_positive, execution:simulated_share_gt_0.35, execution:coverage_too_high, execution:net_not_positive, control_risk_stop_active`
- `primary_p60` `rmt_repetition_forget_p60_edge0`: live_ready `False`, entries `153`, settled `153`, net `-3048c`, blockers `fv:coverage_too_high, fv:net_not_positive, execution:simulated_share_gt_0.35, execution:coverage_too_high, execution:net_not_positive, control_risk_stop_active`
- `primary_p60` `book_ask_prior_p60_edge0`: live_ready `False`, entries `155`, settled `155`, net `-2777c`, blockers `fv:coverage_too_high, fv:net_not_positive, execution:simulated_share_gt_0.35, execution:coverage_too_high, execution:net_not_positive, control_risk_stop_active`
- `primary_p60` `v28_raw_p50_edge0`: live_ready `False`, entries `154`, settled `154`, net `-627c`, blockers `fv:coverage_too_high, fv:net_not_positive, execution:simulated_share_gt_0.35, execution:coverage_too_high, execution:net_not_positive, control_risk_stop_active`
- `threshold_p58` `first_side_raw_later_book_p58_edge0`: live_ready `False`, entries `152`, settled `152`, net `-2557c`, blockers `fv:coverage_too_high, fv:net_not_positive, execution:simulated_share_gt_0.35, execution:coverage_too_high, execution:net_not_positive, control_risk_stop_active`
- `threshold_p58` `rmt_repetition_forget_p58_edge0`: live_ready `False`, entries `152`, settled `152`, net `-3210c`, blockers `fv:coverage_too_high, fv:net_not_positive, execution:simulated_share_gt_0.35, execution:coverage_too_high, execution:net_not_positive, control_risk_stop_active`
- `side_agreement` `raw_when_same_else_first_side_raw_later_book_p60_edge0`: live_ready `False`, entries `150`, settled `150`, net `-2071c`, blockers `fv:coverage_too_high, fv:net_not_positive, execution:simulated_share_gt_0.35, execution:coverage_too_high, execution:net_not_positive, control_risk_stop_active`
- `side_agreement` `raw_when_same_else_rmt_repetition_forget_p60_edge0`: live_ready `False`, entries `150`, settled `150`, net `-1694c`, blockers `fv:coverage_too_high, fv:net_not_positive, execution:simulated_share_gt_0.35, execution:coverage_too_high, execution:net_not_positive, control_risk_stop_active`
- `convex_escape` `raw_edge20_else_first_side_raw_later_book_p60_edge0`: live_ready `False`, entries `152`, settled `152`, net `-4099c`, blockers `fv:coverage_too_high, fv:net_not_positive, execution:simulated_share_gt_0.35, execution:coverage_too_high, execution:net_not_positive, control_risk_stop_active`
- `convex_escape` `raw_edge20_else_rmt_repetition_forget_p60_edge0`: live_ready `False`, entries `152`, settled `152`, net `-3556c`, blockers `fv:coverage_too_high, fv:net_not_positive, execution:simulated_share_gt_0.35, execution:coverage_too_high, execution:net_not_positive, control_risk_stop_active`
- `raw_physics` `v28_raw_p52_edge0`: live_ready `False`, entries `150`, settled `150`, net `-879c`, blockers `fv:coverage_too_high, fv:net_not_positive, execution:simulated_share_gt_0.35, execution:coverage_too_high, execution:net_not_positive, control_risk_stop_active`
- `raw_physics` `raw_fee_friction_p50_edge0`: live_ready `False`, entries `149`, settled `149`, net `-555c`, blockers `fv:coverage_too_high, fv:net_not_positive, execution:simulated_share_gt_0.35, execution:coverage_too_high, execution:net_not_positive, control_risk_stop_active`
- `raw_physics` `raw_touch_friction_p50_edge0`: live_ready `False`, entries `149`, settled `149`, net `-515c`, blockers `fv:coverage_too_high, fv:net_not_positive, execution:simulated_share_gt_0.35, execution:coverage_too_high, execution:net_not_positive, control_risk_stop_active`
- `raw_p52_sideflip` `raw_p50_else_p52_sideflip_confirm`: live_ready `False`, entries `150`, settled `150`, net `-819c`, blockers `fv:coverage_too_high, fv:net_not_positive, execution:simulated_share_gt_0.35, execution:coverage_too_high, execution:net_not_positive, control_risk_stop_active`
- `raw_p52_recross_escape` `v28_raw_p52_edge0_base`: live_ready `False`, entries `143`, settled `143`, net `-947c`, blockers `fv:coverage_too_high, fv:net_not_positive, execution:simulated_share_gt_0.35, execution:coverage_too_high, execution:net_not_positive, control_risk_stop_active`
- `raw_p52_recross_escape` `p52_recross_escape_opp240_oppedge5_keep`: live_ready `False`, entries `143`, settled `143`, net `-753c`, blockers `fv:coverage_too_high, fv:net_not_positive, execution:simulated_share_gt_0.35, execution:coverage_too_high, execution:net_not_positive, control_risk_stop_active`
- `noise_shrinkage` `noise_shrink_light_p50_edge1`: live_ready `False`, entries `146`, settled `146`, net `10c`, blockers `fv:coverage_too_high, execution:simulated_share_gt_0.35, execution:coverage_too_high, control_risk_stop_active`
- `noise_shrinkage` `noise_shrink_light_p50_edge0`: live_ready `False`, entries `149`, settled `149`, net `-381c`, blockers `fv:coverage_too_high, fv:net_not_positive, execution:simulated_share_gt_0.35, execution:coverage_too_high, execution:net_not_positive, control_risk_stop_active`
- `path_confirmed` `path_confirm_wait120`: live_ready `False`, entries `95`, settled `95`, net `-1731c`, blockers `fv:coverage_too_low, execution:coverage_too_low, fv:net_not_positive, execution:net_not_positive, fv:brier_delta_not_negative, fv:logloss_delta_not_negative, execution:simulated_share_gt_0.35, control_risk_stop_active`
- `path_confirmed` `path_confirm_wait180`: live_ready `False`, entries `85`, settled `85`, net `-1616c`, blockers `fv:coverage_too_low, execution:coverage_too_low, fv:net_not_positive, execution:net_not_positive, fv:brier_delta_not_negative, fv:logloss_delta_not_negative, execution:simulated_share_gt_0.35, control_risk_stop_active`
- `path_confirmed` `path_confirm_wait240`: live_ready `False`, entries `71`, settled `71`, net `-1477c`, blockers `fv:coverage_too_low, execution:coverage_too_low, fv:net_not_positive, execution:net_not_positive, fv:brier_delta_not_negative, fv:logloss_delta_not_negative, execution:simulated_share_gt_0.35, control_risk_stop_active`
- `path_confirmed` `selective_fragile_wait180`: live_ready `False`, entries `126`, settled `126`, net `-1571c`, blockers `fv:net_not_positive, execution:net_not_positive, fv:brier_delta_not_negative, fv:logloss_delta_not_negative, execution:simulated_share_gt_0.35, control_risk_stop_active`
- `path_confirmed` `selective_fragile_wait240`: live_ready `False`, entries `119`, settled `119`, net `-1495c`, blockers `fv:net_not_positive, execution:net_not_positive, fv:brier_delta_not_negative, fv:logloss_delta_not_negative, execution:simulated_share_gt_0.35, control_risk_stop_active`
- `path_confirmed` `selective_nearstrike_wait180`: live_ready `False`, entries `130`, settled `130`, net `-1474c`, blockers `fv:net_not_positive, execution:net_not_positive, fv:brier_delta_not_negative, fv:logloss_delta_not_negative, execution:simulated_share_gt_0.35, control_risk_stop_active`
- `path_confirmed` `selective_rmt_memory_gap_wait180`: live_ready `False`, entries `138`, settled `138`, net `-949c`, blockers `fv:coverage_too_high, execution:coverage_too_high, fv:net_not_positive, execution:net_not_positive, fv:brier_delta_not_negative, fv:logloss_delta_not_negative, execution:simulated_share_gt_0.35, control_risk_stop_active`
- `path_confirmed` `selective_rmt_repetition_gap_wait180`: live_ready `False`, entries `139`, settled `139`, net `-1045c`, blockers `fv:coverage_too_high, execution:coverage_too_high, fv:net_not_positive, execution:net_not_positive, fv:brier_delta_not_negative, fv:logloss_delta_not_negative, execution:simulated_share_gt_0.35, control_risk_stop_active`
- `path_confirmed` `selective_rmt_memory_gap_wait180_rmtedge02`: live_ready `False`, entries `126`, settled `126`, net `-420c`, blockers `fv:net_not_positive, execution:net_not_positive, fv:brier_delta_not_negative, fv:logloss_delta_not_negative, execution:simulated_share_gt_0.35, control_risk_stop_active`
- `path_confirmed` `selective_rmt_repetition_gap_wait180_rmtedge02`: live_ready `False`, entries `132`, settled `132`, net `-909c`, blockers `fv:net_not_positive, execution:net_not_positive, fv:brier_delta_not_negative, fv:logloss_delta_not_negative, execution:simulated_share_gt_0.35, control_risk_stop_active`
- `path_confirmed` `selective_rmt_memory_gap_wait180_rmtedge02_or_opp`: live_ready `False`, entries `129`, settled `129`, net `-470c`, blockers `fv:net_not_positive, execution:net_not_positive, fv:brier_delta_not_negative, fv:logloss_delta_not_negative, execution:simulated_share_gt_0.35, control_risk_stop_active`
- `path_confirmed` `selective_rmt_repetition_gap_wait180_rmtedge02_or_opp`: live_ready `False`, entries `134`, settled `134`, net `-969c`, blockers `fv:net_not_positive, execution:net_not_positive, fv:brier_delta_not_negative, fv:logloss_delta_not_negative, execution:simulated_share_gt_0.35, control_risk_stop_active`
- `path_confirmed` `selective_rmt_memory_gap_wait240_rmtedge02_or_opp`: live_ready `False`, entries `132`, settled `132`, net `-380c`, blockers `fv:net_not_positive, execution:net_not_positive, fv:brier_delta_not_negative, fv:logloss_delta_not_negative, execution:simulated_share_gt_0.35, control_risk_stop_active`
- `path_confirmed` `selective_rmt_repetition_gap_wait240_rmtedge02_or_opp`: live_ready `False`, entries `136`, settled `136`, net `-910c`, blockers `fv:net_not_positive, execution:net_not_positive, fv:brier_delta_not_negative, fv:logloss_delta_not_negative, execution:simulated_share_gt_0.35, control_risk_stop_active`
- `path_confirmed` `weakraw_rmt_memory_margin02_wait240_or_opp`: live_ready `False`, entries `88`, settled `88`, net `-750c`, blockers `fv:coverage_too_low, execution:coverage_too_low, fv:net_not_positive, execution:net_not_positive, fv:brier_delta_not_negative, fv:logloss_delta_not_negative, execution:simulated_share_gt_0.35, control_risk_stop_active`
- `path_confirmed` `weakraw_rmt_repetition_margin02_wait240_or_opp`: live_ready `False`, entries `88`, settled `88`, net `-750c`, blockers `fv:coverage_too_low, execution:coverage_too_low, fv:net_not_positive, execution:net_not_positive, fv:brier_delta_not_negative, fv:logloss_delta_not_negative, execution:simulated_share_gt_0.35, control_risk_stop_active`
- `raw_entry_coverage_valve` `raw_p50_turbulence_valve_edge4_p60_recross90_near20`: live_ready `False`, entries `125`, settled `125`, net `-333c`, blockers `fv:net_not_positive, control_risk_stop_active`
- `raw_entry_coverage_valve` `raw_p50_turbulence_valve_edge4_p60_recross90_near25`: live_ready `False`, entries `122`, settled `122`, net `-538c`, blockers `fv:net_not_positive, control_risk_stop_active`
- `raw_entry_coverage_valve` `raw_p50_coverage_valve_edge3_or_p60`: live_ready `False`, entries `117`, settled `117`, net `-1136c`, blockers `fv:net_not_positive, fv:net_worse_than_base, control_risk_stop_active`
- `raw_entry_coverage_valve` `raw_p50_turbulence_valve_edge3_p60_recross75_near25`: live_ready `False`, entries `120`, settled `120`, net `-1272c`, blockers `fv:net_not_positive, fv:net_worse_than_base, control_risk_stop_active`
- `raw_entry_coverage_valve` `raw_p50_coverage_valve_edge4_or_p60`: live_ready `False`, entries `108`, settled `108`, net `-574c`, blockers `fv:coverage_too_low, fv:net_not_positive, control_risk_stop_active`
- `raw_entry_coverage_valve` `raw_p50_turbulence_valve_edge4_p60_recross75_near25`: live_ready `False`, entries `112`, settled `112`, net `-626c`, blockers `fv:coverage_too_low, fv:net_not_positive, control_risk_stop_active`
- `raw_entry_coverage_valve` `raw_p50_coverage_valve_edge5_or_p60`: live_ready `False`, entries `105`, settled `105`, net `-638c`, blockers `fv:coverage_too_low, fv:net_not_positive, control_risk_stop_active`
- `approved_entry_book_fv` `actual_approved_entries + book_probability`: live_ready `False`, entries `133`, settled `133`, net `701c`, blockers `fv:brier_not_better_than_raw, control_risk_stop_active`
- `target_coverage_fv` `raw_p50_turbulence_valve_edge4_p60_recross75_near25 + book_probability`: live_ready `False`, entries `112`, settled `112`, net `-626c`, blockers `fv:brier_interval_not_strictly_negative, fv:logloss_interval_not_strictly_negative, fv:coverage_below_75, live_evidence:actual_approved_rows_lt_10, live_evidence:simulated_share_gt_35pct, control_risk_stop_active`
- `target_coverage_conservative_fv` `raw_p50_turbulence_valve_edge4_p60_recross75_near25 + logit125_p60_calm_mid_or_p75`: live_ready `False`, entries `98`, settled `98`, net `-699c`, blockers `fv:brier_interval_not_strictly_negative, fv:logloss_interval_not_strictly_negative, fv:coverage_too_low, control_risk_stop_active`
- `target_coverage_p70_fv` `raw_p50_turbulence_valve_edge4_p60_recross75_near25 + logit125_p70`: live_ready `False`, entries `97`, settled `97`, net `-769c`, blockers `fv:mean_brier_not_better, fv:brier_interval_not_strictly_negative, fv:logloss_interval_not_strictly_negative, fv:coverage_too_low, control_risk_stop_active`
- `target_coverage_p70_empirical_bayes` `raw_p50_turbulence_valve_edge4_p60_recross75_near25 + p70_empirical_bayes_prior6`: live_ready `False`, entries `96`, settled `96`, net `-663c`, blockers `fv:mean_brier_not_better, fv:brier_interval_not_strictly_negative, fv:logloss_interval_not_strictly_negative, fv:coverage_too_low, control_risk_stop_active`
- `path_state_p70_fv` `raw_p50_turbulence_valve_edge4_p60_recross75_near25 + path_state_guarded_p70_logit125`: live_ready `False`, entries `94`, settled `94`, net `-541c`, blockers `fv:brier_interval_not_strictly_negative, fv:logloss_interval_not_strictly_negative, fv:coverage_too_low, control_risk_stop_active`
- `boundary_recross_shrink_fv` `raw_p50_turbulence_valve_edge4_p60_recross75_near25 + boundary_recross_shrink_probability`: live_ready `False`, entries `93`, settled `93`, net `-619c`, blockers `fv:brier_interval_not_strictly_negative, fv:logloss_interval_not_strictly_negative, fv:coverage_too_low, control_risk_stop_active`
- `boundary_temperature_fv` `raw_p50_turbulence_valve_edge4_p60_recross75_near25 + boundary_temp_strong`: live_ready `False`, entries `78`, settled `78`, net `None`, blockers `control_risk_stop_active`
- `boundary_energy_fv_entry` `boundary_energy_fv_entry`: live_ready `False`, entries `73`, settled `73`, net `156c`, blockers `fv_entry:coverage_too_low, control_risk_stop_active`
- `early_no_boundary_fv_entry` `early_no_boundary_fv_entry`: live_ready `False`, entries `73`, settled `73`, net `94c`, blockers `fv_entry:coverage_too_low, control_risk_stop_active`
- `mid_edge_false_conviction_fv` `raw_p50_turbulence_valve_edge4_p60_recross75_near25 + mid_edge_false_conviction_shrink`: live_ready `False`, entries `82`, settled `82`, net `35c`, blockers `fv:mean_brier_not_better, fv:brier_interval_not_strictly_negative, fv:mean_logloss_not_better, fv:logloss_interval_not_strictly_negative, fv:coverage_too_low, control_risk_stop_active`
- `composite_false_conviction_fv` `raw_p50_turbulence_valve_edge4_p60_recross75_near25 + composite_false_conviction_full_to_book`: live_ready `False`, entries `81`, settled `81`, net `127c`, blockers `fv:mean_brier_not_better, fv:brier_interval_not_strictly_negative, fv:mean_logloss_not_better, fv:logloss_interval_not_strictly_negative, fv:coverage_too_low, control_risk_stop_active`
- `boundary_clock_fv_overlay` `raw_p50_turbulence_valve_edge4_p60_recross75_near25 + clock_shrink_0p00`: live_ready `False`, entries `88`, settled `88`, net `-401c`, blockers `control_risk_stop_active`
- `side_asymmetry_fv_overlay` `raw_p50_turbulence_valve_edge4_p60_recross75_near25 + clock_then_side_no_midboundary_0p00`: live_ready `False`, entries `87`, settled `87`, net `-321c`, blockers `control_risk_stop_active`
- `edge_phase_shrink_fv` `raw_p50_turbulence_valve_edge4_p60_recross75_near25 + edge_phase_shrink`: live_ready `False`, entries `93`, settled `93`, net `-619c`, blockers `fv:brier_interval_not_strictly_negative, fv:logloss_interval_not_strictly_negative, fv:coverage_too_low, control_risk_stop_active`
- `edge_phase_edge_gate` `edge_phase_shrink adjusted_edge_floor=-0.12`: live_ready `False`, entries `92`, settled `92`, net `-695c`, blockers `entry:coverage_too_low, entry:net_not_positive, control_risk_stop_active`
- `edge_gate_opposite_side` `edge_phase_skip_then_same_or_later_opposite`: live_ready `False`, entries `91`, settled `91`, net `-585c`, blockers `entry:coverage_too_low, entry:net_not_positive, control_risk_stop_active`
- `thin_recross_midp_entry_gate` `skip_midp60_75_edge_lt2pp_recross_ge85`: live_ready `False`, entries `88`, settled `88`, net `-209c`, blockers `entry:coverage_too_low, entry:net_not_positive, control_risk_stop_active`
- `raw_p52_boundary_turbulence_skip` `raw_p52_skip_weakraw_nearstrike_recross90`: live_ready `False`, entries `88`, settled `88`, net `266c`, blockers `control_risk_stop_active`
- `raw_p52_favorite_valley_skip` `raw_p52_skip_ask65_75_favorite_valley`: live_ready `False`, entries `84`, settled `84`, net `-731c`, blockers `entry:net_not_positive, entry:simulated_share_gt_35pct, control_risk_stop_active`
- `raw_p52_mid_edge_skip` `raw_p52_skip_mid_edge_5_10pp`: live_ready `False`, entries `77`, settled `77`, net `-963c`, blockers `entry:net_not_positive, entry:simulated_share_gt_35pct, control_risk_stop_active`
- `raw_p52_shadow_mid_edge_skip` `raw_p52_skip_rejected_mid_edge_5_10pp`: live_ready `False`, entries `83`, settled `83`, net `-898c`, blockers `entry:net_not_positive, entry:simulated_share_gt_35pct, control_risk_stop_active`
- `raw_p52_book_disagreement_skip` `raw_p52_skip_v28_minus_book_gt15pp`: live_ready `False`, entries `88`, settled `88`, net `-619c`, blockers `entry:net_not_positive, entry:simulated_share_gt_35pct, control_risk_stop_active`
- `raw_p52_book_shrink_entry` `gap15_book50_p52_edge0`: live_ready `False`, entries `99`, settled `99`, net `-645c`, blockers `entry:coverage_too_high, entry:net_not_positive, entry:simulated_share_gt_35pct, control_risk_stop_active`
- `raw_p52_early_no_boundary_skip` `raw_p52_skip_early_no_boundary_decay`: live_ready `False`, entries `73`, settled `73`, net `-444c`, blockers `entry:coverage_too_low, entry:net_not_positive, entry:simulated_share_gt_35pct, control_risk_stop_active`
- `raw_p52_early_no_boundary_band_skip` `raw_p52_skip_midconf_early_no_boundary`: live_ready `False`, entries `93`, settled `93`, net `-604c`, blockers `entry:coverage_too_high, entry:net_not_positive, entry:simulated_share_gt_35pct, control_risk_stop_active`
- `target_loss_tag_repair_entry` `skip_target_loss_tags_repair_lowest_recross`: live_ready `False`, entries `86`, settled `86`, net `-731c`, blockers `entry:net_not_positive, control_risk_stop_active`
- `early_no_boundary_decay_repair_entry` `skip_early_no_boundary_decay_repair_calm_geometry`: live_ready `False`, entries `85`, settled `85`, net `27c`, blockers `control_risk_stop_active`
- `mid_edge_boundary_deception_repair_entry` `skip_mid_edge_boundary_deception_repair_stable_geometry`: live_ready `False`, entries `84`, settled `84`, net `-431c`, blockers `entry:net_not_positive, control_risk_stop_active`
- `composite_false_conviction_repair_entry` `skip_composite_false_conviction_repair_highest_raw_p`: live_ready `False`, entries `83`, settled `83`, net `-84c`, blockers `entry:net_not_positive, control_risk_stop_active`
- `goldilocks_edge_repair_entry` `skip_false_edge_phase_repair_goldilocks`: live_ready `False`, entries `49`, settled `49`, net `-159c`, blockers `entry:net_not_positive, control_risk_stop_active`
- `false_conviction_approved_repair` `skip_false_conviction_repair_approved_heavy`: live_ready `False`, entries `70`, settled `70`, net `-226c`, blockers `entry:net_not_positive, entry:reconstructed_share_gt_35pct, control_risk_stop_active`
- `low_recross_repair_entry` `skip_paid_or_weak_boundary_repair_lowest_recross`: live_ready `False`, entries `92`, settled `92`, net `-217c`, blockers `entry:net_not_positive, control_risk_stop_active`
- `high_raw_p_repair_entry` `skip_paid_or_weak_boundary_repair_highest_raw_p`: live_ready `False`, entries `89`, settled `89`, net `-274c`, blockers `entry:net_not_positive, control_risk_stop_active`
- `p50_book_edge_entry` `p50_book_plus_05_edge_nonnegative`: live_ready `False`, entries `104`, settled `104`, net `660c`, blockers `entry:simulated_share_gt_35pct, control_risk_stop_active`
- `book_plus05_entry` `book_plus_05`: live_ready `False`, entries `113`, settled `113`, net `-514c`, blockers `entry:coverage_too_high, entry:net_not_positive, entry:simulated_share_gt_35pct, control_risk_stop_active`
- `book_plus05_no_cheap_yes_entry` `book_plus_05_no_cheap_yes_boundary`: live_ready `False`, entries `111`, settled `111`, net `-172c`, blockers `entry:coverage_too_high, entry:net_not_positive, entry:simulated_share_gt_35pct, control_risk_stop_active`
- `boundary_clock_repair_entry` `skip_boundary_clock_composite_repair_lowest_recross`: live_ready `False`, entries `91`, settled `91`, net `-151c`, blockers `entry:net_not_positive, control_risk_stop_active`
- `boundary_clock_fv_entry_bridge` `boundary_clock_adjusted_edge_floor_0p02_repair_lowest_recross`: live_ready `False`, entries `90`, settled `90`, net `229c`, blockers `control_risk_stop_active`
- `weak_reversal_residual_repair` `weak_reversal_skip_edge_5_8pp_no_repair_farthest_boundary`: live_ready `False`, entries `81`, settled `81`, net `-1127c`, blockers `entry:net_not_positive, control_risk_stop_active`
- `weak_reversal_residual_fv_shrink` `half_to_50`: live_ready `False`, entries `81`, settled `81`, net `-721c`, blockers `fv:brier_not_better, fv:logloss_not_better, control_risk_stop_active`
- `no_mid_edge_fv` `no_mid_to_book`: live_ready `False`, entries `78`, settled `78`, net `158c`, blockers `fv:brier_not_better, fv:logloss_not_better, control_risk_stop_active`
- `early_boundary_wait_repair` `early_boundary_wait480_p50_any_side`: live_ready `False`, entries `80`, settled `80`, net `82c`, blockers `control_risk_stop_active`
- `early_boundary_opposite_wait_repair` `early_boundary_wait480_p50_opposite_side_delay480`: live_ready `False`, entries `80`, settled `80`, net `98c`, blockers `control_risk_stop_active`
- `exit_reduce_suppression` `suppress_reduce_p_hold_ge_075`: live_ready `False`, entries `132`, settled `132`, net `337c`, blockers `exit:suppressed_loss_control_cost_negative, control_risk_stop_active`
- `exit_reduce_yes_suppression` `suppress_yes_reduce_p_hold_ge_075`: live_ready `False`, entries `103`, settled `103`, net `112c`, blockers `exit:suppressed_losers_present, exit:suppressed_loss_control_cost_negative, control_risk_stop_active`
- `exit_book_gap_suppression` `suppress_soft_gap15_or_p_hold75`: live_ready `False`, entries `120`, settled `120`, net `235c`, blockers `exit:suppressed_loss_control_cost_negative, control_risk_stop_active`

## State Watch

- Candidate: `no_same_side_reentry`
- Status: `shadow_only`
- Reason: Allows side flips but blocks repeated entries on the same side in the same 15m market.
- `current_v28`: trades `173`, gross `823c`, delta `0c`
- `no_same_side_reentry`: trades `116`, gross `532c`, delta `-291c`
- `first_entry_per_market`: trades `107`, gross `494c`, delta `-329c`
## FV Watch

- Candidate: `information_decay_state_penalty`
- Status: `diagnostic_only`
- Reason: Tests whether stale same-market evidence should be forgotten faster after live probability/book updates.
- Half-life `15s` retained-current Brier: `0.012014023541394664` (comparable `6448`)
- Half-life `45s` retained-current Brier: `0.017286359721707` (comparable `6448`)
- Half-life `120s` retained-current Brier: `0.027137828737833103` (comparable `6448`)
- Half-life `300s` retained-current Brier: `0.04213314090420517` (comparable `6448`)
- State FV variants by Brier:
  - `book_prior`: avg_brier `0.16348959988231831`, vs_current `-0.005395446097961165`
  - `book_anchor_on_large_surprise`: avg_brier `0.16798063398204083`, vs_current `-0.0009044119982386523`
  - `shock_forget_else_light_15s_blend`: avg_brier `0.16886016877499022`, vs_current `-2.4877205289264293e-05`
  - `current_v28`: avg_brier `0.16888504598027948`, vs_current `0.0`
- FV variant robustness:
  - `book_ask_prior`: avg_brier `0.1559896855345912`, vs_raw `-0.007316655838284281`
  - `large_disagreement_book_anchor`: avg_brier `0.1565593626802031`, vs_raw `-0.0067469786926723785`
  - `fixed_shrink_50_v28_50_book`: avg_brier `0.15686328414825032`, vs_raw `-0.006443057224625154`
  - `book_when_v28_coinflip`: avg_brier `0.15713528313480252`, vs_raw `-0.006171058238072957`
- FV view `source_entry` best: `large_disagreement_book_anchor` avg_brier `0.12589318248201217`, vs_raw `-0.007740852228265288`
- FV view `first_per_market_side_source` best: `book_ask_prior` avg_brier `0.2023805615550756`, vs_raw `-0.007667043510025895`
- FV view `last_per_market_side_source` best: `book_ask_prior` avg_brier `0.14672008639308853`, vs_raw `-0.010174763213777555`
- RMT spectral regime diagnostic:
  - `insufficient_history`: obs `24`, settled `24`, best `book_ask_prior`, avg_brier `0.16191666666666665`, vs_raw `-0.008186914299166681`
  - `spectral_dominant_factor`: obs `6740`, settled `6740`, best `book_ask_prior`, avg_brier `0.16324740356083084`, vs_raw `-0.0055754934032494485`
  - `spectral_factor`: obs `33`, settled `33`, best `v28_raw`, avg_brier `0.17367439627866665`, vs_raw `0.0`
  - `spectral_noise`: obs `1`, settled `1`, best `v28_premium_book_anchor`, avg_brier `0.406462351936`, vs_raw `0.0`
  - view `approved_entries`: obs `173`, settled `173`, best `large_disagreement_book_anchor`, avg_brier `0.12589318248201217`, vs_raw `-0.007740852228265288`
  - view `first_per_market_side_source`: obs `464`, settled `464`, best `book_ask_prior`, avg_brier `0.20270668103448278`, vs_raw `-0.007774069794836164`
  - view `last_per_market_side_source`: obs `464`, settled `464`, best `book_ask_prior`, avg_brier `0.06001875`, vs_raw `-0.010809290484219823`
- State-aware FV candidates:
  - `rmt_aggressive_forget`: count `6798`, avg_brier `0.16336582157652194`, vs_raw `-0.00552010500632788`
  - `book_ask_prior`: count `6798`, avg_brier `0.16348959988231831`, vs_raw `-0.005396326700531501`
  - `rmt_repetition_forget`: count `6798`, avg_brier `0.1635382431353129`, vs_raw `-0.005347683447536916`
  - `first_market_raw_later_book`: count `6798`, avg_brier `0.16368691360941662`, vs_raw `-0.005199012973433198`
  - view `approved_entries` best `repeated_side_book_anchor`, avg_brier `0.12556714923250034`, vs_raw `-0.00806688547777712`
  - view `first_per_market_side_source` best `rmt_aggressive_forget`, avg_brier `0.2026928255478901`, vs_raw `-0.0077879252814288535`
  - view `last_per_market_side_source` best `first_market_raw_later_book`, avg_brier `0.05971571228742026`, vs_raw `-0.011112328196799567`

### Boundary-Memory FV Candidates

- Frozen forward validator for catastrophic-forgetting-style FV overlays.
- Freeze timestamp UTC: `2026-05-06T01:40:40.929142+00:00`
- Forward denominator: `143`
- `raw_probability`: entries/settled `141/141`, Brier/logloss d `0.0/0.0`, avg p `0.624167134751773`, blockers `none`
- `boundary_memory_logit125`: entries/settled `141/141`, Brier/logloss d `0.0027215530221556816/0.004142140693235041`, avg p `0.6386511768586765`, blockers `brier_not_better_than_raw, logloss_not_better_than_raw`
- `conditional_logit125_p60_only`: entries/settled `141/141`, Brier/logloss d `0.0036598338287285037/0.0062715581814349886`, avg p `0.642840907108002`, blockers `brier_not_better_than_raw, logloss_not_better_than_raw`
- `boundary_memory_plus05`: entries/settled `141/141`, Brier/logloss d `0.00538014983043264/0.009565630854355023`, avg p `0.6453181914893616`, blockers `brier_not_better_than_raw, logloss_not_better_than_raw`

### Reward-Memory FV Candidates

- Frozen forward validator for constrained reward-calibrated FV memory controllers.
- Freeze timestamp UTC: `2026-05-06T01:46:48.111889+00:00`
- Forward denominator: `142`
- `raw_probability`: entries/settled `140/140`, Brier/logloss d `0.0/0.0`, avg p `0.62468445`, blockers `none`
- `reward_memory_logit125`: entries/settled `140/140`, Brier/logloss d `0.0025980314275309557/0.0042888493859538634`, avg p `0.6422796216500396`, blockers `brier_not_better_than_raw, logloss_not_better_than_raw`
- `logit125_probability`: entries/settled `140/140`, Brier/logloss d `0.003771575783797748/0.0064220518422468675`, avg p `0.6487525235639718`, blockers `brier_not_better_than_raw, logloss_not_better_than_raw`
- `reward_memory_plus05`: entries/settled `140/140`, Brier/logloss d `0.0076999480846025314/0.014560871068898584`, avg p `0.6637638456974456`, blockers `brier_not_better_than_raw, logloss_not_better_than_raw`
- `plus05_probability`: entries/settled `140/140`, Brier/logloss d `0.009964453217149977/0.019161283759796865`, avg p `0.6745155857142858`, blockers `brier_not_better_than_raw, logloss_not_better_than_raw`
- controller `reward_memory_logit125`: training rows `31`, objective `0.6208877044603069`, weights `{'bias': 1.0, 'edge_strength': 0.0, 'high_recross': 0.0, 'near_strike': 0.0, 'raw_strength': 0.0, 'spectral_dominant_weak': 0.0, 'spectral_noise': 0.0, 'thin_edge': 0.0, 'turbulent_boundary': 0.0, 'weak_raw': 0.0}`
- controller `reward_memory_plus05`: training rows `31`, objective `0.6073209493033028`, weights `{'bias': 1.0, 'edge_strength': 0.75, 'high_recross': 0.0, 'near_strike': 0.0, 'raw_strength': 0.0, 'spectral_dominant_weak': 0.0, 'spectral_noise': 0.0, 'thin_edge': 0.0, 'turbulent_boundary': 0.0, 'weak_raw': 0.0}`

### Reward-Memory Jackknife

- Leave-one-market-out anti-overfit check for reward-memory FV overlays.
- Selected/settled/markets: `172/172/172`
- `reward_memory_logit125`: pass `False`, failures `172`, full Brier/logloss d `0.0015033263803742036/0.0016248974825573415`, worst Brier d `0.0016155238845123043`
- `logit125_probability`: pass `False`, failures `172`, full Brier/logloss d `0.0022755488567699766/0.0027615184026530404`, worst Brier d `0.0024276246473613206`
- `reward_memory_plus05`: pass `False`, failures `172`, full Brier/logloss d `0.004831451270001064/0.008144199655697126`, worst Brier d `0.0050973091185027575`
- `plus05_probability`: pass `False`, failures `172`, full Brier/logloss d `0.006406016572098855/0.011122342497338011`, worst Brier d `0.006720585674859697`

### FV Candidate Decision Matrix

- Evidence-ranked comparison across simple posterior, selective memory, boundary memory, and reward memory.
- Discovery best by Brier is conditional_book_no_late_discount (-0.025583191549724993); this is not promotion evidence.
- 34 candidate rows have at least one post-freeze forward entry; 34 have at least 30 settled rows.
- Reward-memory +5pp is robust but discovery Brier delta (0.004831451270001064) is weaker than simple +5pp (0.006406016572098855).
- Best coverage valve is raw_p50_turbulence_valve_edge4_p60_recross90_near20 with forward coverage 82.23684210526315 and net -333.0c.
- Cleanest actual-approved FV evidence is book_probability: 133 settled rows, Brier/logloss deltas 0.006168655138428583/-0.025019035845109228.
- Approved-entry book-edge actionability best is skip_discount15_book_edge_lt_5pp: retained coverage 84.21052631578948, net 927.0c, delta 226.0c versus keeping all actual v28-approved entries.
- Frozen approved-entry book-edge gate now has future entries/settled 88/71; delta 152.0c and blockers [].
- Frozen target-coverage book-edge gate has denominator/entries/settled 97/60/60; coverage 61.855670103092784, delta -161.0c, blockers ['coverage_too_low', 'delta_not_positive'].
- Conditional approved-entry book FV is now frozen for future validation: future settled 93, pre-freeze Brier/logloss deltas -0.025583191549724993/-0.1425133634906126.
- On the target-coverage surface, best FV overlay is book_probability with coverage 73.68421052631578, Brier delta -0.014912731593232115, and logloss delta -0.026989299326773852.
- Raw-p52 crowd-prior skip discovery keeps coverage 85.6353591160221 versus base 93.37016574585635, net 43.0c versus 71.0c; skipped rows are 6/8 for 28.0c.
- Frozen raw-p52 crowd-prior skip has denominator 101, settled 88, and blockers ['net_not_positive', 'simulated_share_gt_35pct']; it is watch-only.
- Book-disagreement shrink is not currently stronger than raw: raw p52 net 71.0c, 50% shrink -263.0c, 75% shrink -136.0c.
- Shrink underperformance is partly entry-order interaction: 50% shrink replacement delta is -334.0c across 7 replacements, so hard abstention is cleaner than side-search replacement.
- Raw-p52 middle-confidence early-NO boundary skip is the strongest discovery row right now: coverage 86.1878453038674 versus base 93.37016574585635, net 633.0c versus 71.0c; skipped bucket 5/8 for -562.0c.
- Early-NO band robustness pass is True; canonical coverage/net 86.1878453038674/633.0c and worst leave-one-skipped delta 426.0c.
- Frozen early-NO boundary band skip has denominator 100, settled 93, and blockers ['coverage_too_high', 'net_not_positive', 'simulated_share_gt_35pct']; it needs fresh forward rows before use.
- Early-NO boundary band runway ready=False with checks [{'name': 'settled_rows_ge_30', 'needed': 0, 'passed': True, 'value': 93}, {'name': 'coverage_75_to_90', 'needed': '75.0-90.0', 'passed': False, 'value': 93.0}, {'name': 'candidate_net_positive', 'needed': '>0', 'passed': False, 'value': -604.0}, {'name': 'delta_vs_raw_positive', 'needed': '>0', 'passed': False, 'value': -186.0}, {'name': 'simulated_share_lte_35pct', 'needed': '<=0.35', 'passed': False, 'value': 0.9247311827956989}]; pending skipped rows 0 and stressed delta -186.0c.
- Early-NO boundary decay repair runway has entries/settled/net 85/85/27.0c at coverage 75.22123893805309; rows needed 0 and full-loss cushion 0.
- Target-coverage paired evidence has 112 settled rows; Brier mean/p95 -0.014912731593232144/0.0006431900556874973, logloss mean/p95 -0.026989299326773745/0.005780956177999605.
- Strong raw-p>=60 rows drive brier sum -0.7798092966370004 over 76 rows.
- Weak raw 50-60 rows contribute brier sum -0.8904166418049997 over 36 rows.
- Weak-but-edge-kept rows are mostly unadjusted by the selected overlay; brier sum -0.8807363632099998.
- Strong-raw thin-edge rows still benefited from sharpening; brier sum 0.09700876493399982.
- Target-coverage PnL attribution: direction-wrong rows are 48 rows for -5007.0c; side-won negative-PnL rows are 2 rows for -52.0c.
- Boundary-entropy FV diagnostic best is entropy_book_s100 with Brier/logloss -0.011616674934007004/-0.02398221407513712; best target-coverage bridge None net Nonec, so entropy shrink is diagnostic rather than stronger than book-anchor right now.
- Danger-zone entry valve has 322.0c discovery P&L lift but entry robustness pass is True; treat it as watched, not promotable.
- Danger-zone FV shrink has Brier/logloss deltas -0.011340997078595372/-0.0661185329043299 and FV robustness pass True.
- Target-coverage conservative FV best diagnostic variant is logit125_p60_calm_mid_or_p75 with Brier/logloss mean deltas -0.0022095221651635597/-0.008271439367388467; frozen forward evidence starts separately.
- P70 diagnostic jackknife pass is True with 0 failures; full Brier/logloss -0.0003773633313270222/-0.003571990138160214, worst Brier leave-out -0.00016725015284209776.
- P70 paired interval has 112 settled rows and 31 adjusted rows; Brier/logloss p95 0.0024900748554538173/0.004755180402661384.
- Confidence-temperature bakeoff best is hard_logit125_p72 with Brier/logloss -0.0013255736275738735/-0.006030666765288752; hard p70 is -0.0003773633313270222/-0.003571990138160214.
- P70 fragility stress: one adverse p75 row breaks interval evidence at count 1; one adverse p80 row breaks mean at count 1.
- P70 scale bakeoff best robustness-ranked scale is 1.05 with first adverse p80 break count 1; scale tuning has not solved fragility.
- P70 empirical-Bayes throttle best is p70_empirical_bayes_prior48 scale 1.0981012658227849 with Brier/logloss p95 0.0008474887950797044/0.0013279133000561657 and first adverse p80 break 1.
- P70 source split all best logit125_p75 over 112 rows with Brier/logloss -0.0015769093300218757/-0.00675303480588537.
- P70 source split approved_entry best logit125_p70 over 7 rows with Brier/logloss -0.005753117335864851/-0.03925202238843982.
- P70 source split rejected_actionable best logit125_p75 over 105 rows with Brier/logloss -0.0012984954629656775/-0.004586435633715074.
- Frozen p70 runway has denominator/selected/base-seen 135/97/133; current zero rows are explained by target-policy abstention if selected remains 0.
- Frozen p70 empirical-Bayes runway has denominator/selected/base-seen 132/96/130.
- Frozen p70 quality registry has denominator/target-entries/p70-rows 131/95/24.
- hard_p70 pending sensitivity: pending-adjusted 0, settled-adjusted 25, raw-only losses 39.
- empirical_bayes_p70 pending sensitivity: pending-adjusted 0, settled-adjusted 25, raw-only losses 38.
- Approved-entry book FV robustness has 173 actual rows; full Brier/logloss deltas -0.004816693669815029/-0.048654430823182764, bootstrap p95 0.010699206867728323/0.02821750921046068, blockers ['leave_one_market_failure', 'bootstrap_brier_p95_not_negative', 'bootstrap_logloss_p95_not_negative'].
- Approved-entry book/raw blend best alpha is 0.35; Brier/logloss deltas -0.007791697570985245/-0.057993896385894306, bootstrap p95 0.0035903825386584265/0.009404569721470635.
- Frozen approved-entry book FV has entries/settled 133/133; Brier/logloss deltas 0.006168655138428583/-0.025019035845109228.
- Frozen path-state p70 has denominator/entries/settled 129/94/94; path_state_guarded_p70_logit125 Brier/logloss -0.00021098173948253023/-0.002381742406517639.
- Frozen boundary-recross shrink has denominator/entries/settled 128/93/93; boundary_recross_shrink_probability Brier/logloss -0.006721901187172044/-0.014189908647494757.
- Boundary reversal diagnostic found 24/42 boundary rows with opposite replacements; replacement-only net -106.0c and non-boundary-plus-replacement coverage 61.8421052631579.
- Danger-tag replacement diagnostic found 33/37 replacements; target net -606.0c versus replacement net -271.0c.
- Coverage-repair diagnostic removes toxic rows and repairs from missed markets: target net -606.0c versus candidate net -513.0c at coverage 75.0.
- Danger-repair bakeoff best diagnostic variant is paid_price_fragile_only with net -140.0c and coverage 75.0; realized-order repair rows make this diagnostic only.
- Ex-ante repair scoring best is highest_raw_edge with net -170.0c, coverage 75.29411764705883, and delta 674.0c; it is frozen separately as low-recross repair.
- Boundary-clock hazard repair best diagnostic rule is early_boundary_recross with net 541.0c, coverage 75.177304964539, and removed-row net -1014.0c; it is frozen separately for future-only validation.
- Boundary-clock robustness pass is True; worst leave-one delta 685.0c and pending-adverse delta 819.0c.
- Boundary-clock FV diagnostic best overlay is clock_shrink_0p00 with Brier/logloss deltas -0.010892657298312514/-0.02374336772308172 over 112 settled rows.
- Boundary-clock FV robustness pass is True; worst leave-one Brier/logloss means -0.007478313623666667/-0.01570564313807691.
- Boundary-clock residual attribution: clock hazard explains 26 direction-wrong rows for -2896.0c; residual non-clock errors are 22 rows for -2111.0c.
- Frozen boundary-clock residual registry has denominator/entries/settled/net 120/9/9/-167.0c; registry only, not a candidate.
- Side-asymmetry diagnostic top bucket is side:no|p60_70 with settled 27, net -888.0c, avg p 0.632525037037037, and win rate 0.4074074074074074; registry-only until future rows validate it.
- Frozen side-asymmetry registry has denominator/bucket/non-clock settled 118/6/6; net -187.0c, registry only.
- Side-asymmetry FV overlay diagnostic best is clock_then_side_no_midboundary_0p00 with Brier/logloss deltas -0.016270297254624977/-0.03486722952707222 and adjusted rows 57.
- Frozen side-asymmetry FV overlay has denominator/entries/settled/adjusted 118/87/87/43; Brier/logloss -0.011711620895563213/-0.024525492188571918, blockers [].
- Boundary-clock promotion runway ready=False with 3 frozen promotion blockers; FV/entry robustness True/True.
- Boundary-clock FV entry bridge diagnostic best floor 0.02 has net 425.0c, coverage 75.0, and delta 766.0c.
- Frozen edge-phase shrink has denominator/entries/settled 127/93/93; edge_phase_shrink Brier/logloss -0.005422811682086021/-0.01160240490360638.
- Adjusted-FV edge gate diagnostic best positive row is confidence_leak_shrink floor 0.02 with coverage 42.10526315789474, net 689.0c, blockers ['coverage_too_low'].
- Edge-gate opposite-side diagnostic found 1/1 skips with a same-or-later opposite replacement; kept-plus-replacement coverage 73.6842105263158 and net -424.0c, blockers ['coverage_too_low', 'net_not_positive'].
- Frozen edge-phase edge gate has denominator/base/candidate 126/92/92; coverage 73.01587301587301, net -695.0c.
- Frozen edge-gate opposite replacement has denominator/entries/replacements 125/91/0; coverage 72.8, net -585.0c.
- Frozen low-recross repair entry has denominator/entries/settled 122/92/92; coverage 75.40983606557377, net -217.0c, blockers ['net_not_positive'].
- Frozen high-raw-p repair entry has denominator/entries/settled 118/89/89; coverage 75.42372881355932, net -274.0c, blockers ['net_not_positive'].
- Frozen boundary-clock repair entry has denominator/entries/settled 121/91/91; coverage 75.20661157024793, net -151.0c, blockers ['net_not_positive'].
- Frozen boundary-clock FV overlay has denominator/entries/settled/adjusted 120/88/88/38; Brier/logloss -0.007305008905659105/-0.015397418335031166, blockers [].
- Frozen boundary-clock FV entry bridge has denominator/entries/settled/net 119/90/90/229.0c, blockers [].
- `book_anchor` `book_probability`: fwd `150/150`, coverage `98.68421052631578`, fwd Brier/logloss d `-0.012290468851073322/-0.022480708936355454`, disc Brier d `-0.006548895154377898`, blockers `forward_coverage_too_high, forward_bucket_failure, forward_path_contradiction_loss`
- `side_asymmetry_fv_overlay` `clock_then_side_no_midboundary_0p00`: fwd `87/87`, coverage `73.72881355932203`, fwd Brier/logloss d `-0.011711620895563213/-0.024525492188571918`, disc Brier d `None`, blockers `settled_lt_30`
- `approved_entry_book_raw_blend` `book_plus_alpha_raw_memory_alpha_0.35`: fwd `173/173`, coverage `None`, fwd Brier/logloss d `-0.007791697570985245/-0.057993896385894306`, disc Brier d `-0.007791697570985245`, blockers `bootstrap_brier_p95_not_negative, bootstrap_logloss_p95_not_negative`
- `boundary_clock_fv_overlay` `clock_shrink_0p00`: fwd `88/88`, coverage `73.33333333333333`, fwd Brier/logloss d `-0.007305008905659105/-0.015397418335031166`, disc Brier d `None`, blockers `settled_lt_30`
- `boundary_recross_shrink_fv` `boundary_recross_shrink_probability`: fwd `93/93`, coverage `72.65625`, fwd Brier/logloss d `-0.006721901187172044/-0.014189908647494757`, disc Brier d `-0.007140542347522316`, blockers `brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative`
- `edge_phase_shrink_fv` `edge_phase_shrink`: fwd `93/93`, coverage `73.22834645669292`, fwd Brier/logloss d `-0.005422811682086021/-0.01160240490360638`, disc Brier d `-0.006876302832962052`, blockers `brier_interval_not_strictly_negative, logloss_interval_not_strictly_negative`

### Pending FV Sensitivity

- Pre-settlement scoring impact for unresolved forward FV rows.
- Pending rows: `0`

### Anti-Overfit Freeze Audit

- Checks that forward evidence is tied to frozen candidate/state definitions, not moving best-row selection.
- All clear: `True`; fail/watch counts `0/35`
- `v28_target_coverage_fv_overlay_validator`: status `pass`, freeze `2026-05-06T02:08:01.321286+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_raw_entry_calibrated_probability`: status `pass`, freeze `2026-05-05T23:30:17.615882+00:00`, dynamic-best risk `False`, failures `none`
- `v28_boundary_memory_fv_candidates`: status `pass`, freeze `2026-05-06T01:40:40.929142+00:00`, dynamic-best risk `False`, failures `none`
- `v28_reward_memory_fv_candidates`: status `pass`, freeze `2026-05-06T01:46:48.111889+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_book_exact_entry_gate`: status `watch`, freeze `2026-05-06T11:33:52.584603+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_approved_entry_state_valve`: status `watch`, freeze `2026-05-06T02:42:53.253731+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_approved_entry_book_fv`: status `pass`, freeze `2026-05-06T06:20:06.824407+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_danger_zone_entry_valve`: status `watch`, freeze `2026-05-06T03:09:58.042066+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_danger_zone_fv_calibration`: status `pass`, freeze `2026-05-06T03:14:35.467881+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_danger_zone_robustness`: status `pass`, freeze `2026-05-06T03:14:35.467881+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_target_coverage_conservative_fv`: status `pass`, freeze `2026-05-06T03:26:44.025585+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_target_coverage_p70_fv`: status `pass`, freeze `2026-05-06T03:45:32.798460+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_target_coverage_p70_empirical_bayes`: status `pass`, freeze `2026-05-06T04:22:07.414318+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_boundary_temperature_fv`: status `watch`, freeze `2026-05-06T11:12:06.081553+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_boundary_energy_fv_entry`: status `watch`, freeze `2026-05-06T11:19:55.494948+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_early_no_boundary_fv_entry`: status `watch`, freeze `2026-05-06T11:24:55.409912+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_path_state_p70_fv`: status `pass`, freeze `2026-05-06T05:07:19.935392+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_boundary_recross_shrink_fv`: status `pass`, freeze `2026-05-06T05:29:47.434585+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_mid_edge_false_conviction_fv`: status `pass`, freeze `2026-05-06T09:29:25.082774+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_boundary_clock_fv_overlay`: status `watch`, freeze `2026-05-06T07:18:17.705020+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_boundary_clock_residual_registry`: status `pass`, freeze `2026-05-06T07:28:09.623811+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_side_asymmetry_registry`: status `pass`, freeze `2026-05-06T07:47:04.735626+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_side_asymmetry_fv_overlay`: status `watch`, freeze `2026-05-06T07:52:22.405861+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_edge_phase_shrink_fv`: status `pass`, freeze `2026-05-06T05:40:31.466696+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_edge_phase_edge_gate`: status `watch`, freeze `2026-05-06T05:46:47.707629+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_edge_gate_opposite_side`: status `watch`, freeze `2026-05-06T06:05:34.391059+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_exit_reduce_suppression`: status `pass`, freeze `2026-05-06T06:33:56.987999+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_exit_reduce_yes_suppression`: status `pass`, freeze `2026-05-06T11:04:54.847536+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_exit_book_gap_suppression`: status `pass`, freeze `2026-05-06T08:46:39.207330+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_target_coverage_p70_quality_registry`: status `pass`, freeze `2026-05-06T04:32:03.738730+00:00`, dynamic-best risk `False`, failures `none`
- `v28_live_p70_quality_registry`: status `pass`, freeze `2026-05-06T04:49:26.047798+00:00`, dynamic-best risk `False`, failures `none`
- `v28_live_collapse_reentry_registry`: status `pass`, freeze `2026-05-06T04:56:06.196433+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_thin_recross_midp_entry_gate`: status `watch`, freeze `2026-05-06T03:39:03.842700+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_raw_p52_boundary_turbulence_skip`: status `watch`, freeze `2026-05-06T08:50:27.891448+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_target_loss_tag_repair_entry`: status `watch`, freeze `2026-05-06T08:59:17.610337+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_low_recross_repair_entry`: status `watch`, freeze `2026-05-06T06:55:26.848310+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_early_no_boundary_decay_repair_entry`: status `watch`, freeze `2026-05-06T09:10:09.146392+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_mid_edge_boundary_deception_repair_entry`: status `watch`, freeze `2026-05-06T09:23:03.299714+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_high_raw_p_repair_entry`: status `watch`, freeze `2026-05-06T07:59:24.730118+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_p50_book_edge_entry`: status `pass`, freeze `2026-05-06T08:09:01.165913+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_book_plus05_entry`: status `pass`, freeze `2026-05-06T08:12:48.716932+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_book_plus05_no_cheap_yes_entry`: status `pass`, freeze `2026-05-06T08:24:46.840351+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_book_edge_fv_calibration`: status `watch`, freeze `2026-05-06T08:12:48.716932+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_recross_book_shrink_fv`: status `pass`, freeze `2026-05-06T08:42:25.757266+00:00`, dynamic-best risk `False`, failures `none`
- `v28_frozen_boundary_clock_repair_entry`: status `watch`, freeze `2026-05-06T07:07:27.790042+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_boundary_clock_fv_entry_bridge`: status `watch`, freeze `2026-05-06T07:35:02.597585+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_book_trajectory_fv`: status `watch`, freeze `2026-05-06T02:47:06.099693+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_weak_reversal_residual_repair`: status `watch`, freeze `2026-05-06T10:25:15.561162+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_weak_reversal_residual_fv_shrink`: status `watch`, freeze `2026-05-06T10:29:42.136727+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_no_mid_edge_fv`: status `watch`, freeze `2026-05-06T10:33:21.044716+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_early_boundary_wait_repair`: status `watch`, freeze `2026-05-06T10:48:07.385138+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_early_boundary_opposite_wait_repair`: status `watch`, freeze `2026-05-06T10:53:40.348250+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_gamma_repair_entry`: status `watch`, freeze `2026-05-06T11:43:09.046274+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_raw_entry_coverage_valve`: status `watch`, freeze `2026-05-05T23:30:17.615882+00:00`, dynamic-best risk `True`, failures `none`
- `v28_frozen_raw_p52_favorite_valley_skip`: status `watch`, freeze `2026-05-06T11:52:57.665782+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_raw_p52_mid_edge_skip`: status `watch`, freeze `2026-05-06T11:57:26.075880+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_raw_p52_shadow_mid_edge_skip`: status `watch`, freeze `2026-05-06T11:58:59.805901+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_raw_p52_book_disagreement_skip`: status `watch`, freeze `2026-05-06T12:06:41.849306+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_raw_p52_book_shrink_entry`: status `watch`, freeze `2026-05-06T12:12:25.258308+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_raw_p52_early_no_boundary_skip`: status `watch`, freeze `2026-05-06T12:18:20.259368+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_frozen_raw_p52_early_no_boundary_band_skip`: status `watch`, freeze `2026-05-06T12:20:19.153557+00:00`, dynamic-best risk `False`, failures `report_has_scored_rows`
- `v28_live_trade_readiness`: status `pass`, freeze `2026-05-05T22:07:37.064896+00:00`, dynamic-best risk `False`, failures `none`

### Goal Completion Audit

- Strict checklist against the active long-term objective.
- Achieved: `False`
- Missing checks: `8`
- `broad_market_coverage`: actual `73.68421052631578`, required `75-90% forward coverage`
- `positive_forward_pnl`: actual `-626.0`, required `>0 net cents on forward selected rows`
- `brier_interval_better_than_raw`: actual `0.0006431900556874973`, required `bootstrap Brier p95 < 0`
- `logloss_interval_better_than_raw`: actual `0.005780956177999605`, required `bootstrap logloss p95 < 0`
- `p70_interval_better_than_raw`: actual `{'brier_p95': 0.0024900748554538173, 'logloss_p95': 0.004755180402661384, 'settled': 112}`, required `p70 bootstrap Brier p95 < 0 and logloss p95 < 0`
- `live_evidence_quality`: actual `{'approved_entry_rows': 7, 'blockers': ['actual_approved_rows_lt_10', 'simulated_share_gt_35pct'], 'simulated_share': 0.9375}`, required `>=30 settled rows, >=10 approved-entry rows, and simulated/rejected share <=35%`
- next: Prefer conservative sharpening over broad p>=60 sharpening unless future Brier interval recovers.
- next: Keep refreshing the p70 sequential-evidence artifact and reject p70 if its interval turns positive before frozen validation matures.
- next: Keep validating positive broad-coverage lanes until at least one clears sample size, source-quality, and full-loss fragility gates.
- next: Do not place live trades from candidates while live_readiness remains false.
- Interpretation: positive retained-current Brier means current/live evidence beat stale retained evidence.

## Avoid Watch

- Status: `do_not_promote`
- Reason: Cheap low-probability/near-boundary expansion keeps producing losses in forward rows.
