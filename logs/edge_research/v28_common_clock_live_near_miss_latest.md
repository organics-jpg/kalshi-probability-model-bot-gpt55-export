# v28 Common-Clock Live Near-Miss

- Log source: `live_mushroom_v28_common_clock_exit_guard_sourcefix_broad_btcrest_size1`
- Latest market: `KXBTC15M-26MAY080015-15`
- Events/rejected/approved/order-like: `509` / `473` / `8` / `8`
- Latest-market decision: `reconcile_order_like_events`
- Latest-market source stale: `16/26` (61.5%)
- Otherwise-approved book-stale rows: `0`
- Near rows: `9`
- Max p_side / net edge: `0.792657` / `18.622997`

## Latest-Market Reasons

- `btc_stale`: `10`
- `p_below_floor`: `10`
- `book_stale`: `6`

## Near Rows

- `2026-05-08T04:00:31.357198+00:00` `btc_stale` `no` ask=`43` p=`0.492191` edge=`2.21907` book_ms=`0.0` p_ok=`False` edge_ok=`True` model_price_ok=`True`
- `2026-05-08T04:00:33.305899+00:00` `book_stale` `no` ask=`43` p=`0.492195` edge=`2.219465` book_ms=`1125.0` p_ok=`False` edge_ok=`True` model_price_ok=`True`
- `2026-05-08T04:00:51.371707+00:00` `btc_stale` `yes` ask=`56` p=`0.78623` edge=`18.622997` book_ms=`204.0` p_ok=`False` edge_ok=`True` model_price_ok=`True`
- `2026-05-08T04:01:12.886877+00:00` `p_below_floor` `yes` ask=`59` p=`0.78781` edge=`15.781017` book_ms=`719.0` p_ok=`False` edge_ok=`True` model_price_ok=`True`
- `2026-05-08T04:01:31.485733+00:00` `btc_stale` `no` ask=`33` p=`0.481531` edge=`11.153119` book_ms=`313.0` p_ok=`False` edge_ok=`True` model_price_ok=`True`
- `2026-05-08T04:01:32.940328+00:00` `p_below_floor` `no` ask=`32` p=`0.481524` edge=`12.15245` book_ms=`766.0` p_ok=`False` edge_ok=`True` model_price_ok=`True`
- `2026-05-08T04:01:33.221259+00:00` `book_stale` `no` ask=`32` p=`0.481523` edge=`12.15232` book_ms=`1047.0` p_ok=`False` edge_ok=`True` model_price_ok=`True`
- `2026-05-08T04:01:52.686267+00:00` `btc_stale` `yes` ask=`67` p=`0.79248` edge=`8.248026` book_ms=`516.0` p_ok=`False` edge_ok=`True` model_price_ok=`True`
- `2026-05-08T04:01:54.936863+00:00` `p_below_floor` `yes` ask=`67` p=`0.792657` edge=`8.265674` book_ms=`766.0` p_ok=`False` edge_ok=`True` model_price_ok=`True`
