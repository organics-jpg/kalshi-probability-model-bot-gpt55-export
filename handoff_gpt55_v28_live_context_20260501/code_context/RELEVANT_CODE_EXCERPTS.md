# Relevant Code Excerpts

These excerpts are included so a model can reason about the live-entry/exit paths without reading the 400k+ byte bot file first.

## RuntimeState around line 732

```python
00732: class RuntimeState:
00733:     pending_order: PendingOrder | None = None
00734:     position: PositionState | None = None
00735:     exit_confirmation: ExitConfirmationState | None = None
00736:     traded_markets: list[str] = field(default_factory=list)
00737: 
00738: 
00739: @dataclass
00740: class MarketSnapshot:
00741:     market_ticker: str | None = None
00742:     market_status: str | None = None
00743:     yes_bid_cents: int | None = None
00744:     yes_ask_cents: int | None = None
00745:     no_bid_cents: int | None = None
00746:     no_ask_cents: int | None = None
00747:     yes_bid_size: Decimal | None = None
00748:     yes_ask_size: Decimal | None = None
00749:     no_bid_size: Decimal | None = None
00750:     no_ask_size: Decimal | None = None
00751:     close_time: str | None = None
00752:     strike: float | None = None
00753:     updated_time: str | None = None
00754:     local_received_monotonic: float | None = None
00755: 
00756: 
00757: class StateStore:
00758:     def __init__(self, path: Path) -> None:
00759:         self.path = path
00760:         self.path.parent.mkdir(parents=True, exist_ok=True)
00761: 
00762:     def load(self) -> RuntimeState:
00763:         if not self.path.exists():
00764:             return RuntimeState()
00765:         raw = json.loads(self.path.read_text(encoding="utf-8"))
00766:         pending = raw.get("pending_order")
00767:         position = raw.get("position")
00768:         exit_confirmation = raw.get("exit_confirmation")
00769:         return RuntimeState(
00770:             pending_order=PendingOrder(**pending) if pending else None,
00771:             position=PositionState(**position) if position else None,
00772:             exit_confirmation=ExitConfirmationState(**exit_confirmation) if exit_confirmation else None,
00773:             traded_markets=list(raw.get("traded_markets", [])),
00774:         )
00775: 
00776:     def save(self, state: RuntimeState) -> None:
```

## entry_block_reason around line 1526

```python
01526:     def entry_block_reason(self, ticker: str, side: str | None = None, count: int | None = None) -> str | None:
01527:         ticker_key = normalize_ticker(ticker)
01528:         position = self.state.position
01529:         add_count = max(1, int(count or self.config.position_size))
01530:         if position is None:
01531:             if self.already_traded(ticker) and not self.config.multi_entry_same_market_enabled:
01532:                 return "already_traded"
01533:             return None
01534:         if normalize_ticker(position.market_ticker) != ticker_key:
01535:             return "different_open_position"
01536:         if side is not None and position.side != side:
01537:             return "opposite_side_position"
01538:         if not self.config.multi_entry_same_market_enabled:
01539:             return "position_open"
01540:         max_contracts = max(1, int(self.config.multi_entry_max_position_contracts))
01541:         if int(position.count) + add_count > max_contracts:
01542:             return "max_position_contracts"
01543:         cooldown = float(self.config.multi_entry_min_seconds_between_entries)
01544:         if cooldown > 0:
01545:             filled_at = parse_iso(position.filled_at)
01546:             if filled_at is not None:
01547:                 seconds_since_fill = (utc_now() - filled_at).total_seconds()
01548:                 if seconds_since_fill < cooldown:
01549:                     return "multi_entry_cooldown"
01550:             if side is not None:
01551:                 last_attempt = self.entry_last_attempt_monotonic.get(f"{ticker_key}:{side}")
01552:                 if last_attempt is not None and (time.monotonic() - last_attempt) < cooldown:
01553:                     return "multi_entry_cooldown"
01554:         return None
01555: 
01556:     def note_entry_attempt_for_cooldown(self, ticker: str, side: str) -> None:
01557:         position = self.state.position
01558:         if position is None:
01559:             return
01560:         if normalize_ticker(position.market_ticker) != normalize_ticker(ticker) or position.side != side:
01561:             return
01562:         self.entry_last_attempt_monotonic[f"{normalize_ticker(ticker)}:{side}"] = time.monotonic()
01563: 
01564:     def weighted_average_cents(self, old_price: int | None, old_count: int, new_price: int | None, new_count: int) -> int | None:
01565:         if old_price is None and new_price is None:
01566:             return None
01567:         if old_count <= 0:
01568:             return int(new_price) if new_price is not None else None
01569:         if new_count <= 0:
01570:             return int(old_price) if old_price is not None else None
01571:         old_value = Decimal(str(old_price if old_price is not None else new_price))
01572:         new_value = Decimal(str(new_price if new_price is not None else old_price))
01573:         total_count = Decimal(str(old_count + new_count))
01574:         weighted = ((old_value * Decimal(str(old_count))) + (new_value * Decimal(str(new_count)))) / total_count
01575:         return int(weighted.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
01576: 
01577:     def apply_entry_fill_to_position(
01578:         self,
01579:         *,
01580:         market_ticker: str,
01581:         side: str,
01582:         fill_count: int,
01583:         entry_order_id: str,
01584:         entry_limit_price_cents: int,
01585:         entry_fill_price_cents: int,
01586:         entry_fee_cents: int,
01587:         entry_trigger_price_cents: int | None,
01588:     ) -> PositionState:
01589:         if fill_count <= 0:
01590:             raise ValueError("Cannot apply an entry fill with non-positive count.")
01591:         now_iso = utc_now().isoformat()
01592:         existing = self.state.position
01593:         if existing is not None:
01594:             if normalize_ticker(existing.market_ticker) != normalize_ticker(market_ticker):
01595:                 raise ValueError("Cannot add entry fill to a different open market.")
01596:             if existing.side != side:
01597:                 raise ValueError("Cannot add entry fill on the opposite side of an open position.")
01598:             old_count = int(existing.count)
01599:             old_limit_price = int(existing.entry_limit_price_cents)
01600:             old_fill_price = (
01601:                 int(existing.entry_fill_price_cents)
01602:                 if existing.entry_fill_price_cents is not None
01603:                 else old_limit_price
01604:             )
01605:             existing.count = old_count + int(fill_count)
```

## detect_entry_signal around line 4563

```python
04563:     def detect_entry_signal(self) -> EntrySignal | None:
04564:         if self.config.mushroom_v28_decision_engine_enabled:
04565:             return self.detect_mushroom_v28_entry_signal()
04566:         if self.config.mushroom_v21_decision_engine_enabled:
04567:             return self.detect_mushroom_v21_entry_signal()
04568:         if self.config.liquidity_dwell_entry_enabled:
04569:             return self.detect_liquidity_dwell_entry_signal()
04570:         ticker = self.current_watch_ticker
04571:         if not ticker or not self.orderbook.snapshot_ready:
04572:             return None
04573:         yes_ask = self.market.yes_ask_cents
04574:         no_ask = self.market.no_ask_cents
04575:         if yes_ask is None:
04576:             no_bid_book, _ = self.orderbook.best_bid("no")
04577:             if no_bid_book is not None:
04578:                 yes_ask = 100 - no_bid_book
04579:             elif self.market.no_bid_cents is not None:
04580:                 yes_ask = 100 - self.market.no_bid_cents
04581:         if no_ask is None:
04582:             yes_bid_book, _ = self.orderbook.best_bid("yes")
04583:             if yes_bid_book is not None:
04584:                 no_ask = 100 - yes_bid_book
04585:             elif self.market.yes_bid_cents is not None:
04586:                 no_ask = 100 - self.market.yes_bid_cents
04587:         if yes_ask is None and no_ask is None:
04588:             return None
04589:         triggered: list[tuple[str, int]] = []
04590:         if yes_ask is not None and yes_ask >= self.config.target_entry_odds_cents:
04591:             triggered.append(("yes", yes_ask))
04592:         if no_ask is not None and no_ask >= self.config.target_entry_odds_cents:
04593:             triggered.append(("no", no_ask))
04594:         triggered = [
04595:             (side, ask)
04596:             for side, ask in triggered
04597:             if self.entry_block_reason(ticker, side, self.config.position_size) is None
04598:         ]
04599:         if len(triggered) != 1:
04600:             return None
04601:         side, trigger_price = triggered[0]
04602:         rejection_state = self.entry_rejection_state.get(f"{normalize_ticker(ticker)}:{side}")
04603:         if rejection_state and time.monotonic() < rejection_state.block_until_monotonic:
04604:             return None
04605:         top_of_book_limit = self.orderbook.top_of_book_buy_limit_cents(side)
04606:         executable_limit = self.orderbook.executable_buy_limit_cents(side, self.config.position_size)
04607:         eligible_limit = executable_limit if executable_limit is not None else top_of_book_limit
04608:         eligible_depth = Decimal("0")
04609:         if eligible_limit is not None:
04610:             eligible_depth = self.orderbook.executable_buy_depth(side, eligible_limit)
04611:         book_age_ms = self.current_book_age_ms()
04612:         signal_signature = "|".join([
04613:             f"trigger={trigger_price}",
04614:             f"yes={yes_ask}",
04615:             f"no={no_ask}",
04616:             f"top={top_of_book_limit}",
04617:             f"exec={executable_limit}",
04618:             f"depth={format_decimal_compact(eligible_depth)}",
04619:             f"trust={self.orderbook.trust.trust_state}",
04620:         ])
04621:         signal = EntrySignal(
04622:             market_ticker=ticker,
04623:             side=side,
04624:             trigger_price_cents=trigger_price,
04625:             cap_price_cents=self.config.target_entry_odds_cents,
04626:             top_of_book_limit_cents=top_of_book_limit,
04627:             executable_limit_cents=executable_limit,
04628:             eligible_depth=eligible_depth,
04629:             book_age_ms=book_age_ms,
04630:             seconds_to_close=self.seconds_to_close(),
04631:             book_summary=self.describe_live_buy_book(side),
04632:             yes_ask_cents=yes_ask,
04633:             no_ask_cents=no_ask,
04634:             signal_signature=signal_signature,
04635:         )
04636:         self.update_executable_window(signal)
04637:         window = self.executable_windows.get(self.market_side_key(ticker, side))
04638:         if window and window.active and window.since_monotonic is not None:
04639:             signal.first_executable_at_monotonic = window.since_monotonic
04640:             signal.executable_window_ms = (time.monotonic() - window.since_monotonic) * 1000.0
04641:         return signal
04642: 
```

## detect_mushroom_v28_entry_signal around line 4164

```python
04164:     def detect_mushroom_v28_entry_signal(self) -> EntrySignal | None:
04165:         ticker = self.current_watch_ticker
04166:         if not ticker or not self.orderbook.snapshot_ready:
04167:             return None
04168:         if self.mushroom_v28_worker is None:
04169:             return None
04170:         seconds_to_close = self.seconds_to_close()
04171:         book_age_ms = self.current_book_age_ms()
04172:         candidates: list[tuple[float, float, EntrySignal]] = []
04173:         for side in ("yes", "no"):
04174:             max_count, block_reason = self.mushroom_v28_entry_max_count(ticker, side)
04175:             if max_count < 1 or block_reason:
04176:                 continue
04177:             rejection_state = self.entry_rejection_state.get(f"{normalize_ticker(ticker)}:{side}")
04178:             if rejection_state and time.monotonic() < rejection_state.block_until_monotonic:
04179:                 continue
04180:             top_limit = self.orderbook.top_of_book_buy_limit_cents(side)
04181:             ask_cents = top_limit if top_limit is not None else self.current_entry_ask_cents(side)
04182:             eligible_depth = Decimal("0")
04183:             if ask_cents is not None:
04184:                 eligible_depth = self.orderbook.executable_buy_depth(side, int(ask_cents))
04185:             fields = self.build_mushroom_v28_decision_fields(
04186:                 side=side,
04187:                 ask_cents=int(ask_cents) if ask_cents is not None else None,
04188:                 top_limit=top_limit,
04189:                 executable_limit=int(ask_cents) if ask_cents is not None else None,
04190:                 eligible_depth=eligible_depth,
04191:                 seconds_to_close=seconds_to_close,
04192:                 book_age_ms=book_age_ms,
04193:             )
04194:             if not fields.get("mushroom_v28_approved"):
04195:                 continue
04196:             target_count = int(fields.get("mushroom_v28_target_count") or 0)
04197:             if target_count < 1:
04198:                 continue
04199:             edge_cents = float(fields.get("mushroom_v28_edge_cents") or 0.0)
04200:             p_side = float(fields.get("mushroom_v28_p_side") or 0.0)
04201:             trigger_price = int(ask_cents)
04202:             model_max_buy_price = int(fields.get("mushroom_v28_model_max_buy_price_cents") or trigger_price)
04203:             signal_signature = "|".join(
04204:                 [
04205:                     "mushroom_v28",
04206:                     f"p={p_side:.6f}",
04207:                     f"edge={edge_cents:.6f}",
04208:                     f"ask={trigger_price}",
04209:                     f"max_buy={model_max_buy_price}",
04210:                     f"qty={target_count}",
04211:                     f"btc_age={fields.get('mushroom_v28_btc_age_ms')}",
04212:                     f"ttc={self._round_or_none(seconds_to_close, 3)}",
04213:                     f"trust={self.orderbook.trust.trust_state}",
04214:                 ]
04215:             )
04216:             signal = EntrySignal(
04217:                 market_ticker=ticker,
04218:                 side=side,
04219:                 trigger_price_cents=trigger_price,
04220:                 cap_price_cents=trigger_price,
04221:                 top_of_book_limit_cents=top_limit,
04222:                 executable_limit_cents=trigger_price,
04223:                 eligible_depth=eligible_depth,
04224:                 book_age_ms=book_age_ms,
04225:                 seconds_to_close=seconds_to_close,
04226:                 book_summary=self.describe_live_buy_book(side),
04227:                 yes_ask_cents=self.current_entry_ask_cents("yes"),
04228:                 no_ask_cents=self.current_entry_ask_cents("no"),
04229:                 signal_signature=signal_signature,
04230:                 target_count=target_count,
04231:                 model_max_buy_price_cents=model_max_buy_price,
04232:                 mushroom_shadow=fields,
04233:             )
04234:             self.update_executable_window(signal)
04235:             window = self.executable_windows.get(self.market_side_key(ticker, side))
04236:             if window and window.active and window.since_monotonic is not None:
04237:                 signal.first_executable_at_monotonic = window.since_monotonic
04238:                 signal.executable_window_ms = (time.monotonic() - window.since_monotonic) * 1000.0
04239:             candidates.append((edge_cents, p_side, signal))
04240:         if not candidates:
04241:             return None
04242:         _, _, selected = max(candidates, key=lambda item: (item[0], item[1]))
04243:         self.logger.info(
04244:             "Mushroom v28 entry approved | market=%s side=%s ask=%sc max_buy=%sc qty=%s p_side=%.4f edge=%.3fc depth=%s btc_age_ms=%s secs_to_close=%s",
04245:             selected.market_ticker,
04246:             selected.side,
04247:             selected.trigger_price_cents,
04248:             selected.model_max_buy_price_cents,
04249:             selected.target_count,
04250:             float(selected.mushroom_shadow.get("mushroom_v28_p_side") or 0.0),
04251:             float(selected.mushroom_shadow.get("mushroom_v28_edge_cents") or 0.0),
04252:             format_decimal_compact(selected.eligible_depth),
04253:             selected.mushroom_shadow.get("mushroom_v28_btc_age_ms"),
04254:             f"{selected.seconds_to_close:.2f}" if selected.seconds_to_close is not None else "NA",
04255:         )
04256:         self.telemetry.emit(
04257:             "mushroom_v28_approved",
04258:             self.telemetry_context_from_signal(selected),
04259:             **self.mushroom_telemetry_fields(selected),
04260:             **self.orderbook.telemetry_fields(),
04261:         )
04262:         return selected
04263: 
04264:     def liquidity_dwell_mushroom_fields(self, candidate: LiquidityDwellCandidate) -> dict[str, Any]:
04265:         top_of_book_limit = self.orderbook.top_of_book_buy_limit_cents(candidate.side)
04266:         executable_limit = self.orderbook.executable_buy_limit_cents(candidate.side, self.config.position_size)
04267:         entry_limit = executable_limit if executable_limit is not None else top_of_book_limit
04268:         if entry_limit is None:
04269:             entry_limit = candidate.initial_trigger_price_cents
04270:         eligible_depth = self.orderbook.executable_buy_depth(candidate.side, int(entry_limit))
04271:         elapsed_ms = max(0.0, (time.monotonic() - candidate.first_seen_monotonic) * 1000.0)
04272:         signal = EntrySignal(
04273:             market_ticker=candidate.market_ticker,
04274:             side=candidate.side,
04275:             trigger_price_cents=int(entry_limit),
04276:             cap_price_cents=int(top_of_book_limit if top_of_book_limit is not None else entry_limit),
04277:             top_of_book_limit_cents=top_of_book_limit,
04278:             executable_limit_cents=int(entry_limit),
04279:             eligible_depth=eligible_depth,
04280:             book_age_ms=self.current_book_age_ms(),
04281:             seconds_to_close=self.seconds_to_close(),
04282:             book_summary=self.describe_live_buy_book(candidate.side),
04283:             yes_ask_cents=self.current_entry_ask_cents("yes"),
04284:             no_ask_cents=self.current_entry_ask_cents("no"),
04285:             signal_signature=f"liquidity_dwell_candidate|initial={candidate.initial_trigger_price_cents}|entry_limit={entry_limit}",
04286:             first_executable_at_monotonic=candidate.first_seen_monotonic,
04287:             executable_window_ms=elapsed_ms,
04288:         )
04289:         self.attach_mushroom_shadow(signal)
04290:         return self.mushroom_telemetry_fields(signal)
04291: 
04292:     def liquidity_dwell_candidate_key(self, ticker: str, side: str) -> str:
04293:         return f"{normalize_ticker(ticker)}:{side}"
```

## build_mushroom_v28_decision_fields around line 3981

```python
03981:     def build_mushroom_v28_decision_fields(
03982:         self,
03983:         *,
03984:         side: str,
03985:         ask_cents: int | None,
03986:         top_limit: int | None,
03987:         executable_limit: int | None,
03988:         eligible_depth: Decimal,
03989:         seconds_to_close: float | None,
03990:         book_age_ms: float | None,
03991:         target_count_hint: int | None = None,
03992:     ) -> dict[str, Any]:
03993:         ticker = self.current_watch_ticker or ""
03994:         fields: dict[str, Any] = {
03995:             "mushroom_v28_version": MUSHROOM_V28_VERSION,
03996:             "mushroom_v28_status": "disabled",
03997:             "mushroom_v28_side": side,
03998:             "mushroom_v28_shadow_enabled": bool(self.config.mushroom_v28_shadow_enabled),
03999:             "mushroom_v28_decision_engine_enabled": bool(self.config.mushroom_v28_decision_engine_enabled),
04000:             "mushroom_v28_live_exit_enabled": bool(self.config.mushroom_v28_live_exit_enabled),
04001:             "mushroom_v28_ask_cents": ask_cents,
04002:             "mushroom_v28_top_of_book_limit_cents": top_limit,
04003:             "mushroom_v28_executable_limit_cents": executable_limit,
04004:             "mushroom_v28_eligible_depth": format_decimal_compact(eligible_depth),
04005:             "mushroom_v28_seconds_to_close": self._round_or_none(seconds_to_close, 3),
04006:             "mushroom_v28_book_age_ms": self._round_or_none(book_age_ms, 3),
04007:             "mushroom_v28_btc_age_ms": self._round_or_none(self.mushroom_v28_btc_age_ms(), 3),
04008:             "mushroom_v28_btc_source": self.mushroom_v28_last_tick_source,
04009:             "mushroom_v28_btc_price": self._round_or_none(self.mushroom_v28_last_tick_price, 2),
04010:         }
04011:         if self.mushroom_v28_worker is None:
04012:             return fields
04013: 
04014:         strike = self.market.strike
04015:         history_bars = self.mushroom_v28_history_count()
04016:         min_history = int(getattr(self.mushroom_v28_worker.engine.config, "min_bars", MushroomV28Config().min_bars))
04017:         max_book_age_ms = self.allowed_live_book_age_ms(seconds_to_close)
04018:         btc_age_ms = self.mushroom_v28_btc_age_ms()
04019:         max_allowed_count, block_reason = self.mushroom_v28_entry_max_count(ticker, side) if ticker else (0, "missing_ticker")
04020:         if target_count_hint is not None:
04021:             max_allowed_count = min(max_allowed_count, max(0, int(target_count_hint)))
04022:         book_ok = book_age_ms is not None and float(book_age_ms) <= float(max_book_age_ms)
04023:         btc_ok = btc_age_ms is not None and float(btc_age_ms) <= float(self.config.mushroom_v28_btc_max_age_ms)
04024:         time_ok = (
04025:             seconds_to_close is not None
04026:             and float(seconds_to_close) >= float(self.config.mushroom_v28_min_seconds_to_close)
04027:             and float(seconds_to_close) <= float(self.config.mushroom_v28_max_seconds_to_close)
04028:         )
04029:         ask_ok = ask_cents is not None and int(ask_cents) <= int(self.config.mushroom_v28_max_ask_cents)
04030:         depth_count = max(0, decimal_to_int(eligible_depth) or 0)
04031:         fields.update(
04032:             {
04033:                 "mushroom_v28_status": "warming",
04034:                 "mushroom_v28_history_bars": history_bars,
04035:                 "mushroom_v28_min_history_bars": min_history,
04036:                 "mushroom_v28_strike": self._round_or_none(strike, 2),
04037:                 "mushroom_v28_book_ok": bool(book_ok),
04038:                 "mushroom_v28_max_book_age_ms": self._round_or_none(max_book_age_ms, 3),
04039:                 "mushroom_v28_btc_ok": bool(btc_ok),
04040:                 "mushroom_v28_btc_max_age_ms": self._round_or_none(self.config.mushroom_v28_btc_max_age_ms, 3),
04041:                 "mushroom_v28_time_ok": bool(time_ok),
04042:                 "mushroom_v28_ask_ok": bool(ask_ok),
04043:                 "mushroom_v28_depth_count": depth_count,
04044:                 "mushroom_v28_max_allowed_count": max_allowed_count,
04045:                 "mushroom_v28_block_reason": block_reason,
04046:                 "mushroom_v28_min_p_side": float(self.config.mushroom_v28_min_p_side),
04047:                 "mushroom_v28_min_edge_cents": float(self.config.mushroom_v28_min_edge_cents_15m),
04048:                 "mushroom_v28_model_buffer_cents": float(self.config.mushroom_v28_model_buffer_cents),
04049:                 "mushroom_v28_slippage_cents": float(self.config.mushroom_v28_slippage_cents),
04050:                 "mushroom_v28_max_ask_cents": int(self.config.mushroom_v28_max_ask_cents),
04051:                 "mushroom_v28_max_market_risk_cents": int(self.config.mushroom_v28_max_market_risk_cents),
04052:             }
04053:         )
04054:         if strike is None:
04055:             fields["mushroom_v28_status"] = "missing_strike"
04056:             return fields
04057:         if seconds_to_close is None or float(seconds_to_close) <= 0:
04058:             fields["mushroom_v28_status"] = "missing_horizon"
04059:             return fields
04060:         if ask_cents is None:
04061:             fields["mushroom_v28_status"] = "missing_ask"
04062:             return fields
04063:         if history_bars < min_history or not self.mushroom_v28_ready():
04064:             return fields
04065: 
04066:         fee_count = max(1, max_allowed_count or int(self.config.position_size))
04067:         fee_cents = self.estimated_order_fee_cents(int(ask_cents), fee_count) / float(fee_count)
04068:         try:
04069:             with self.mushroom_lock:
04070:                 pred = self.mushroom_v28_worker.engine.predict_many(
04071:                     strikes=[float(strike)],
04072:                     horizon_seconds=float(seconds_to_close),
04073:                 )
04074:         except Exception as exc:  # noqa: BLE001
04075:             fields["mushroom_v28_status"] = "prediction_error"
04076:             fields["mushroom_v28_error"] = str(exc)
04077:             return fields
04078: 
04079:         p_yes = float(pred.p_yes[0])
04080:         p_side = p_yes if side == "yes" else (1.0 - p_yes)
04081:         fair_yes = float(pred.fair_yes_cents[0])
04082:         fair_no = float(pred.fair_no_cents[0])
04083:         fair_side = fair_yes if side == "yes" else fair_no
04084:         raw_edge_cents = fair_side - float(ask_cents) - fee_cents
04085:         edge_cents = raw_edge_cents - float(self.config.mushroom_v28_slippage_cents) - float(self.config.mushroom_v28_model_buffer_cents)
04086:         model_max_buy_price = int(math.floor(
04087:             fair_side
04088:             - fee_cents
04089:             - float(self.config.mushroom_v28_slippage_cents)
04090:             - float(self.config.mushroom_v28_model_buffer_cents)
04091:             - float(self.config.mushroom_v28_min_edge_cents_15m)
04092:         ))
04093:         model_max_buy_price = max(1, min(99, model_max_buy_price))
04094:         risk_per_contract_cents = max(1.0, float(ask_cents) + fee_cents)
04095:         risk_count = int(float(self.config.mushroom_v28_max_market_risk_cents) // risk_per_contract_cents)
04096:         balance_count = max_allowed_count
04097:         balance_ok = True
04098:         account_age_ms = self.account_snapshot_age_ms()
04099:         if not self.config.dry_run:
04100:             if self.live_account_snapshot.available_balance_cents is None or account_age_ms is None or account_age_ms > self.config.live_account_state_max_age_ms:
04101:                 balance_ok = False
04102:                 balance_count = 0
04103:             else:
04104:                 spendable_cents = (
04105:                     int(self.live_account_snapshot.available_balance_cents or 0)
04106:                     - int(self.config.live_balance_fee_buffer_cents)
04107:                     - int(self.config.live_balance_min_buffer_cents)
04108:                 )
04109:                 balance_count = max(0, int(spendable_cents // risk_per_contract_cents))
04110:                 balance_ok = balance_count > 0
```

## apply_entry_fill_to_position around line 1577

```python
01577:     def apply_entry_fill_to_position(
01578:         self,
01579:         *,
01580:         market_ticker: str,
01581:         side: str,
01582:         fill_count: int,
01583:         entry_order_id: str,
01584:         entry_limit_price_cents: int,
01585:         entry_fill_price_cents: int,
01586:         entry_fee_cents: int,
01587:         entry_trigger_price_cents: int | None,
01588:     ) -> PositionState:
01589:         if fill_count <= 0:
01590:             raise ValueError("Cannot apply an entry fill with non-positive count.")
01591:         now_iso = utc_now().isoformat()
01592:         existing = self.state.position
01593:         if existing is not None:
01594:             if normalize_ticker(existing.market_ticker) != normalize_ticker(market_ticker):
01595:                 raise ValueError("Cannot add entry fill to a different open market.")
01596:             if existing.side != side:
01597:                 raise ValueError("Cannot add entry fill on the opposite side of an open position.")
01598:             old_count = int(existing.count)
01599:             old_limit_price = int(existing.entry_limit_price_cents)
01600:             old_fill_price = (
01601:                 int(existing.entry_fill_price_cents)
01602:                 if existing.entry_fill_price_cents is not None
01603:                 else old_limit_price
01604:             )
01605:             existing.count = old_count + int(fill_count)
01606:             existing.filled_at = now_iso
01607:             existing.entry_order_id = entry_order_id or existing.entry_order_id
01608:             existing.entry_limit_price_cents = self.weighted_average_cents(
01609:                 old_limit_price,
01610:                 old_count,
01611:                 int(entry_limit_price_cents),
01612:                 int(fill_count),
01613:             ) or int(entry_limit_price_cents)
01614:             existing.entry_fill_price_cents = self.weighted_average_cents(
01615:                 old_fill_price,
01616:                 old_count,
01617:                 int(entry_fill_price_cents),
01618:                 int(fill_count),
01619:             )
01620:             existing.entry_fee_cents = int(existing.entry_fee_cents or 0) + int(entry_fee_cents or 0)
01621:             existing.entry_trigger_price_cents = (
01622:                 int(entry_trigger_price_cents)
01623:                 if entry_trigger_price_cents is not None
01624:                 else existing.entry_trigger_price_cents
01625:             )
01626:             self.state.exit_confirmation = None
01627:             return existing
01628:         self.state.position = PositionState(
01629:             market_ticker=market_ticker,
01630:             side=side,
01631:             count=int(fill_count),
01632:             filled_at=now_iso,
01633:             entry_order_id=entry_order_id,
01634:             entry_limit_price_cents=int(entry_limit_price_cents),
01635:             entry_fill_price_cents=int(entry_fill_price_cents),
01636:             entry_fee_cents=int(entry_fee_cents or 0),
01637:             entry_trigger_price_cents=entry_trigger_price_cents,
01638:         )
01639:         self.state.exit_confirmation = None
01640:         return self.state.position
01641: 
01642:     def ensure_market_outcome_record(self, market_ticker: str, close_time: str | None = None) -> None:
01643:         close_dt = parse_iso(close_time) if close_time else None
01644:         local_close_dt = close_dt.astimezone() if close_dt is not None else None
01645:         self.market_outcomes.ensure_market(
01646:             market_ticker,
01647:             session=infer_session_label(local_close_dt),
01648:             watched_at=utc_now().isoformat(),
01649:             market_close_time=close_time or "",
01650:         )
01651:         self.market_outcomes.save()
01652: 
01653:     def backfill_persisted_position_outcome(self) -> None:
01654:         position = self.state.position
01655:         if position is None:
01656:             return
```

## detect_mushroom_v28_exit_signal around line 6158

```python
06158:     def detect_mushroom_v28_exit_signal(self, position: PositionState, filled_at: datetime) -> ExitSignal | None:
06159:         if not self.config.mushroom_v28_live_exit_enabled or self.mushroom_v28_worker is None:
06160:             return None
06161:         if normalize_ticker(self.current_watch_ticker or "") != normalize_ticker(position.market_ticker):
06162:             return None
06163:         seconds_to_close = self.seconds_to_close()
06164:         if seconds_to_close is None or float(seconds_to_close) <= float(self.config.mushroom_v28_min_seconds_to_close):
06165:             return None
06166:         if self.market.strike is None:
06167:             return None
06168:         if not self.mushroom_v28_ready():
06169:             return None
06170:         btc_age_ms = self.mushroom_v28_btc_age_ms()
06171:         if btc_age_ms is None or btc_age_ms > float(self.config.mushroom_v28_btc_max_age_ms):
06172:             return None
06173:         book_age_ms = self.current_book_age_ms()
06174:         if book_age_ms is None or book_age_ms > float(self.config.exit_max_book_age_ms):
06175:             return None
06176:         quote_time = parse_ws_time(self.market.updated_time)
06177:         if quote_time is None or quote_time < (filled_at + timedelta(seconds=self.config.post_fill_exit_delay_seconds)):
06178:             return None
06179: 
06180:         top_bid, _ = self.orderbook.best_bid(position.side)
06181:         if top_bid is None:
06182:             top_bid = self.market.yes_bid_cents if position.side == "yes" else self.market.no_bid_cents
06183:         if top_bid is None:
06184:             return None
06185:         held_ask = self.current_entry_ask_cents(position.side)
06186: 
06187:         try:
06188:             with self.mushroom_lock:
06189:                 pred = self.mushroom_v28_worker.engine.predict_many(
06190:                     strikes=[float(self.market.strike)],
06191:                     horizon_seconds=float(seconds_to_close),
06192:                 )
06193:         except Exception as exc:  # noqa: BLE001
06194:             self.mushroom_v28_last_error = str(exc)
06195:             return None
06196: 
06197:         p_yes = float(pred.p_yes[0])
06198:         p_hold = p_yes if position.side == "yes" else (1.0 - p_yes)
06199:         fair_yes = float(pred.fair_yes_cents[0])
06200:         fair_no = float(pred.fair_no_cents[0])
06201:         fair_hold = fair_yes if position.side == "yes" else fair_no
06202:         qty = max(1, int(position.count))
06203:         fee_cents = self.estimated_order_fee_cents(int(top_bid), qty) / float(qty)
06204:         exit_net = float(top_bid) - fee_cents - float(self.config.mushroom_v28_slippage_cents)
06205:         hold_net = fair_hold - float(self.config.mushroom_v28_exit_hold_buffer_cents)
06206:         entry_basis = int(position.entry_fill_price_cents or position.entry_limit_price_cents or 0)
06207:         fair_drawdown = float(entry_basis) - fair_hold if entry_basis > 0 else 0.0
06208: 
06209:         reason = ""
06210:         target_count = 0
06211:         if exit_net >= hold_net + float(self.config.mushroom_v28_exit_hysteresis_cents):
06212:             reason = "mushroom_v28_exit_value_over_hold"
06213:             target_count = qty
06214:         elif p_hold <= float(self.config.mushroom_v28_exit_full_p_hold_floor):
06215:             reason = "mushroom_v28_probability_collapse_full"
06216:             target_count = qty
06217:         elif entry_basis > 0 and fair_drawdown >= float(self.config.mushroom_v28_exit_full_drawdown_cents):
06218:             reason = "mushroom_v28_fair_drawdown_full"
06219:             target_count = qty
06220:         elif p_hold <= float(self.config.mushroom_v28_exit_reduce_p_hold_floor):
06221:             reason = "mushroom_v28_probability_reduce"
06222:             target_count = max(1, int(math.ceil(qty * float(self.config.mushroom_v28_exit_reduce_fraction))))
06223:         elif entry_basis > 0 and fair_drawdown >= float(self.config.mushroom_v28_exit_fair_drawdown_cents):
06224:             reason = "mushroom_v28_fair_drawdown_reduce"
06225:             target_count = max(1, int(math.ceil(qty * float(self.config.mushroom_v28_exit_reduce_fraction))))
06226:         if not reason or target_count <= 0:
06227:             return None
06228:         target_count = min(qty, target_count)
06229:         executable_limit = self.orderbook.executable_sell_limit_cents(position.side, target_count)
06230:         if executable_limit is None and target_count < qty:
06231:             top_depth = max(0, decimal_to_int(self.orderbook.executable_sell_depth(position.side, int(top_bid))) or 0)
06232:             target_count = min(target_count, top_depth)
06233:             executable_limit = int(top_bid) if target_count > 0 else None
06234:         eligible_depth = Decimal("0")
06235:         if executable_limit is not None:
06236:             eligible_depth = self.orderbook.executable_sell_depth(position.side, executable_limit)
06237:         if target_count <= 0:
```

## maybe_check_entry around line 3473

```python
03473:     async def maybe_check_entry(self) -> None:
03474:         if self.state.pending_order or self.order_inflight:
03475:             return
03476:         if self.state.position is not None:
03477:             ticker = self.current_watch_ticker or self.state.position.market_ticker
03478:             entry_block_count = 1 if self.config.mushroom_v28_decision_engine_enabled else self.config.position_size
03479:             reason = self.entry_block_reason(ticker, count=entry_block_count)
03480:             if reason in {"different_open_position", "position_open", "max_position_contracts", "multi_entry_cooldown"}:
03481:                 return
03482:             if reason == "opposite_side_position":
03483:                 return
03484:         if self.current_watch_ticker is None:
03485:             return
03486:         if time.monotonic() < self.entry_retry_block_until_monotonic:
03487:             return
03488:         signal = self.detect_entry_signal()
03489:         if signal is None:
03490:             return
03491:         self.attach_mushroom_shadow(signal)
03492:         existing_market_record = self.market_outcomes.get(signal.market_ticker)
03493:         if existing_market_record is None or existing_market_record.signal_count <= 0:
03494:             self.market_outcomes.mark_signal_seen(signal.market_ticker)
03495:         if self.should_suppress_stale_book(signal):
03496:             return
03497:         if self.should_suppress_dead_market(signal):
03498:             return
03499:         mushroom_fields = self.mushroom_telemetry_fields(signal)
03500:         self.telemetry.emit("signal_seen", self.telemetry_context_from_signal(signal), **mushroom_fields, **self.orderbook.telemetry_fields())
03501:         filter_decision = self.evaluate_pre_entry_filters(signal)
03502:         if not filter_decision.allowed:
03503:             self.telemetry.emit("filter_blocked", self.telemetry_context_from_signal(signal, filter_decision=filter_decision), **mushroom_fields, **self.orderbook.telemetry_fields())
03504:             return
03505:         regime_decision = self.evaluate_btc_vol_regime_gate(signal)
03506:         if not regime_decision.allowed:
03507:             self.telemetry.emit("filter_blocked", self.telemetry_context_from_signal(signal, filter_decision=regime_decision), btc_range_dollars=self.btc_vol_regime_snapshot.range_dollars, btc_range_threshold_dollars=float(self.config.btc_vol_regime_max_range_dollars), btc_regime_age_ms=self.btc_vol_regime_age_ms(), btc_regime_source=self.btc_vol_regime_snapshot.source, **mushroom_fields, **self.orderbook.telemetry_fields())
03508:             return
03509:         lease_decision = self.evaluate_truffle_regime_lease(signal)
03510:         if not lease_decision.allowed:
03511:             self.telemetry.emit(
03512:                 "filter_blocked",
03513:                 self.telemetry_context_from_signal(signal, filter_decision=lease_decision),
03514:                 lease_mode=self.config.truffle_regime_lease_mode,
03515:                 lease_decision=self.current_regime_lease.decision if self.current_regime_lease is not None else "",
03516:                 lease_issued_at=self.current_regime_lease.issued_at if self.current_regime_lease is not None else "",
03517:                 **mushroom_fields,
03518:                 **self.orderbook.telemetry_fields(),
03519:             )
03520:             return
03521:         plan = self.build_execution_plan(signal, filter_decision)
03522:         if plan is None:
03523:             return
03524:         self.telemetry.emit("plan_built", self.telemetry_context_from_plan(plan, filter_decision), account_age_ms=plan.account_age_ms, **self.mushroom_telemetry_fields(plan), **self.orderbook.telemetry_fields())
03525:         await self.submit_execution_plan(plan, filter_decision)
03526: 
03527:     def current_entry_ask_cents(self, side: str) -> int | None:
03528:         if side == "yes":
03529:             held_ask = self.market.yes_ask_cents
03530:             if held_ask is None:
03531:                 no_bid_book, _ = self.orderbook.best_bid("no")
03532:                 if no_bid_book is not None:
03533:                     held_ask = 100 - no_bid_book
03534:                 elif self.market.no_bid_cents is not None:
03535:                     held_ask = 100 - self.market.no_bid_cents
03536:             return held_ask
03537:         if side == "no":
03538:             held_ask = self.market.no_ask_cents
03539:             if held_ask is None:
03540:                 yes_bid_book, _ = self.orderbook.best_bid("yes")
03541:                 if yes_bid_book is not None:
03542:                     held_ask = 100 - yes_bid_book
03543:                 elif self.market.yes_bid_cents is not None:
03544:                     held_ask = 100 - self.market.yes_bid_cents
03545:             return held_ask
03546:         raise ValueError(f"Invalid side: {side}")
03547: 
03548:     def current_market_p_yes(self) -> float | None:
03549:         yes_bid, yes_ask, _, _ = self.derived_quote_values()
03550:         if yes_bid is None or yes_ask is None:
03551:             return None
03552:         mid = (float(yes_bid) + float(yes_ask)) / 200.0
```

## maybe_check_exit around line 7051

```python
07051:     async def maybe_check_exit(self) -> None:
07052:         position = self.state.position
07053:         if not position:
07054:             self.clear_exit_confirmation(persist=self.state.exit_confirmation is not None)
07055:             return
07056:         if self.state.pending_order or self.order_inflight:
07057:             return
07058:         if time.monotonic() < self.exit_retry_block_until_monotonic:
07059:             return
07060:         if self.current_watch_ticker != position.market_ticker:
07061:             self.clear_exit_confirmation(persist=self.state.exit_confirmation is not None)
07062:             return
07063:         filled_at = parse_iso(position.filled_at)
07064:         if not filled_at:
07065:             self.clear_exit_confirmation(persist=self.state.exit_confirmation is not None)
07066:             return
07067:         seconds_since_fill = (utc_now() - filled_at).total_seconds()
07068:         if seconds_since_fill < self.config.post_fill_exit_delay_seconds:
07069:             return
07070:         if self.config.mushroom_v28_live_exit_enabled:
07071:             signal = self.detect_mushroom_v28_exit_signal(position, filled_at)
07072:             if signal is not None:
07073:                 await self.execute_exit_signal(signal, exit_source="mushroom_v28_ev")
07074:                 return
07075:         if self.config.truffle_post_entry_shadow_live_exit_enabled:
07076:             truffle_decision = self.current_truffle_live_exit_decision(position.market_ticker)
07077:             if truffle_decision is not None:
07078:                 signal = self.detect_truffle_exit_signal(position, filled_at)
07079:                 if signal is not None:
07080:                     await self.execute_exit_signal(
07081:                         signal,
07082:                         exit_source="truffle_post_entry_shadow",
07083:                         truffle_decision=truffle_decision,
07084:                     )
07085:                     return
07086:         if not self.config.exit_stop_loss_enabled:
07087:             self.clear_exit_confirmation(persist=self.state.exit_confirmation is not None)
07088:             return
07089:         if str(current_plan.reason).startswith("mushroom_v28_"):
07090:             signal = self.detect_mushroom_v28_exit_signal(position, filled_at)
07091:         else:
07092:             signal = self.detect_exit_signal(position, filled_at)
07093:         if signal is None:
07094:             self.clear_exit_confirmation(persist=self.state.exit_confirmation is not None)
07095:             return
07096:         exit_allowed, gate_reason = self.evaluate_exit_confirmation(signal)
07097:         if not exit_allowed:
07098:             self.telemetry.emit(
07099:                 "exit_execution_deferred",
07100:                 self.telemetry_context_from_exit_signal(signal),
07101:                 result=gate_reason,
07102:                 stop_tier=signal.stop_tier,
07103:                 confirmation_count=signal.confirmation_count,
07104:                 confirmation_elapsed_seconds=round(signal.confirmation_elapsed_seconds, 3),
07105:                 required_confirm_checks=int(self.config.exit_confirm_checks),
07106:                 required_confirm_seconds=float(self.config.exit_confirm_seconds),
07107:                 account_age_ms=self.account_snapshot_age_ms(),
07108:                 **self.orderbook.telemetry_fields(),
07109:             )
07110:             return
07111:         await self.execute_exit_signal(signal, exit_source="hard_stop")
07112: 
07113:     async def submit_order(
07114:         self,
07115:         *,
07116:         purpose: str,
07117:         market_ticker: str,
07118:         side: str,
07119:         action: str,
07120:         count: int,
07121:         limit_price_cents: int,
07122:         trigger_price_cents: int,
07123:         reduce_only: bool,
07124:         time_in_force: str = "fill_or_kill",
07125:     ) -> None:
07126:         if self.order_inflight:
07127:             return
07128:         self.order_inflight = True
07129:         try:
07130:             self.logger.info(
```

## reconcile_live_position_after_close around line 5884

```python
05884:     async def reconcile_live_position_after_close(self, market_ticker: str) -> bool:
05885:         try:
05886:             live_positions = await asyncio.to_thread(self.client.get_positions, market_ticker)
05887:         except Exception as exc:  # noqa: BLE001
05888:             self.logger.warning(
05889:                 "Closed-market live position reconciliation failed for %s. Keeping position state until the next check. Error: %s",
05890:                 market_ticker,
05891:                 exc,
05892:             )
05893:             return False
05894: 
05895:         persisted_ticker = normalize_ticker(market_ticker)
05896:         matching_live: list[dict[str, Any]] = []
05897:         for pos in live_positions:
05898:             live_ticker = normalize_ticker(str(pos.get("ticker") or pos.get("market_ticker") or ""))
05899:             qty = to_decimal(pos.get("position_fp", pos.get("position", 0)))
05900:             if live_ticker == persisted_ticker and qty != 0:
05901:                 matching_live.append(pos)
05902: 
05903:         if matching_live:
05904:             if self.live_position_is_settlement_only(market_ticker):
05905:                 self.logger.warning(
05906:                     "Closed market %s still reports a nonzero live account position, but the market is already past the settlement grace window. Clearing position state and advancing anyway.",
05907:                     market_ticker,
05908:                 )
05909:                 self.state.position = None
05910:                 self.state.pending_order = None
05911:                 self.save_state()
05912:                 return True
05913:             self.logger.info(
05914:                 "Closed market %s still has a live account position. Keeping position state until settlement fully clears.",
05915:                 market_ticker,
05916:             )
05917:             return False
05918: 
05919:         self.logger.warning(
05920:             "Market %s is closed and no matching live account position remains. Clearing position state and advancing to the next market.",
05921:             market_ticker,
05922:         )
05923:         self.state.position = None
05924:         self.state.pending_order = None
05925:         self.save_state()
05926:         return True
05927: 
05928:     def live_position_is_settlement_only(self, market_ticker: str) -> bool:
05929:         with contextlib.suppress(Exception):
05930:             market = self.client.get_market(market_ticker)
05931:             if market_is_closed_for_recovery(market):
05932:                 return True
05933:         record = self.market_outcomes.get(market_ticker)
05934:         close_dt = parse_iso(record.market_close_time) if record is not None else None
05935:         if close_dt is None and normalize_ticker(self.current_watch_ticker or "") == normalize_ticker(market_ticker):
05936:             close_dt = parse_iso(self.watch_close_time or "")
05937:         return bool(close_dt and utc_now() >= close_dt + timedelta(seconds=SETTLEMENT_ONLY_GRACE_SECONDS))
05938: 
05939:     def persisted_market_close_time(self, market_ticker: str) -> str | None:
05940:         with contextlib.suppress(Exception):
05941:             market = self.client.get_market(market_ticker)
05942:             close_time = str(market.get("close_time") or market.get("expiration_time") or "").strip()
05943:             if close_time:
05944:                 return close_time
05945:         record = self.market_outcomes.get(market_ticker)
05946:         if record is not None and str(record.market_close_time or "").strip():
05947:             return str(record.market_close_time).strip()
05948:         return None
05949: 
05950:     def describe_live_buy_book(self, side: str, max_levels: int | None = None) -> str:
05951:         levels = int(max_levels or self.config.live_entry_book_diagnostics_levels)
05952:         if side == "yes":
05953:             raw_levels = sorted(self.orderbook.no_bids.items(), key=lambda item: item[0], reverse=True)
05954:             rendered = [f"{100 - price}:{format_decimal_compact(qty)}" for price, qty in raw_levels[:levels] if qty > 0]
05955:         else:
05956:             raw_levels = sorted(self.orderbook.yes_bids.items(), key=lambda item: item[0], reverse=True)
05957:             rendered = [f"{100 - price}:{format_decimal_compact(qty)}" for price, qty in raw_levels[:levels] if qty > 0]
05958:         return "[" + ", ".join(rendered) + "]" if rendered else "[]"
05959: 
05960:     def describe_live_sell_book(self, side: str, max_levels: int | None = None) -> str:
05961:         levels = int(max_levels or self.config.exit_book_diagnostics_levels)
05962:         raw_levels = sorted((self.orderbook.yes_bids if side == "yes" else self.orderbook.no_bids).items(), key=lambda item: item[0], reverse=True)
05963:         rendered = [f"{price}:{format_decimal_compact(qty)}" for price, qty in raw_levels[:levels] if qty > 0]
```

