# Known Issues And Hypotheses

## P0/P1: Same-Market Exposure Stacking

Observed overnight: `KXBTC15M-26MAY010430-30` reached 4 same-side YES contracts. This was profitable, but it violated the intended mental model of a size-2 live posture.

Important config evidence:

- `POSITION_SIZE=2`
- `MULTI_ENTRY_SAME_MARKET_ENABLED=true`
- `MULTI_ENTRY_MAX_POSITION_CONTRACTS=10`

Hypothesis: this is not a pure code bug. The runner explicitly allowed multi-entry up to 10 contracts, so the bot was permitted to add after the first fill. If current strategy is supposed to be strict size 2, fix the runner config first and consider adding a v28-specific hard cap.

Recommended conservative fix:

- Set `MULTI_ENTRY_SAME_MARKET_ENABLED=false`, or set `MULTI_ENTRY_MAX_POSITION_CONTRACTS=2` for this launcher.
- Add a v28 live safety guard so `target_count + current_position_count` can never exceed the intended v28 cap, regardless of generic multi-entry settings.
- Add a telemetry field showing `current_position_count`, `allowed_entry_count`, and the exact multi-entry block reason.

## P1: Missing Rejection Telemetry

Current v28 logs mostly emit approvals. Quiet periods are hard to audit because failed gates are usually invisible.

Recommended fix:

- Emit periodic `mushroom_v28_decision_snapshot` events.
- Emit `mushroom_v28_rejected` when a candidate comes close or when a top-side p/edge condition fails.
- Include p_yes, p_no, YES/NO ask, fair values, net edges, all gate booleans, BTC age, book age, and block reason.

## P1: IOC Chasing / Zero-Fill Noise

Overnight had repeated entry/exit zero-fills. The bot generally handled them, but this can cause rapid re-evaluation and multiple attempts within seconds as the book moves.

Recommended fix:

- Add or tune per-market/per-side approval suppression after zero-fill.
- Consider requiring a material book improvement or fresh model tick before retrying after zero-fill.
- Keep the current `LIVE_ENTRY_STALE_SUPPRESSION_MS` and material-book-change logic visible in telemetry.

## P2: Settlement State Clearing

Several closed markets briefly reported nonzero live positions after close. The bot cleared local state and advanced. This appears intentional for settlement-only positions, but it should be reviewed because local state clearing can hide unresolved live-account discrepancies if the settlement-only detector is wrong.

Recommended fix:

- Preserve a `settlement_pending` record separate from active trade state.
- Log inferred/confirmed settlement outcome and expected payout.
- Keep current market advancement, but make accounting explicit.

## P2: Gross PnL Only

The generated ledger uses gross cents before fees and inferred settlement. Do not treat it as final account PnL.

Recommended fix:

- Join actual fees from Kalshi order responses/account history where available.
- Store canonical settlement result per market if the API exposes it.
