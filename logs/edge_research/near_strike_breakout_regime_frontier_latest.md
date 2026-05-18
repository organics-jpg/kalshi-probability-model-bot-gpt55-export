# Near-Strike Breakout Regime Frontier

Generated UTC: `20260504_110858Z`

## Scope

- Research-only scan; no orders are submitted and no bot files or live processes are touched.
- Keeps `book_margin` as the high-coverage base and tests only weak near-strike overlays.
- Strict pass requires current+v21 coverage, positive validation/holdout, positive all splits, and block stability.

## Diagnostics

- Current markets: 307
- V21 markets: 221
- Candidate specs: 1921
- Strict pass rows: 0

## Top Rows

| policy | strict | combined all net | combined OOS net | min split cov | current/v21 net | current/v21 acc | fades current/v21 | min block+ | worst block |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.65; impulse_over_margin>=10; sec>=300; fade_ask<=45` | False | 2146.0c | 1987.0c | 97.78% | 2409.0c/-263.0c | 69.51%/63.93% | 76/38 | 0.545 | -366.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.65; impulse_over_margin>=10; sec>=300; fade_ask<=50` | False | 2146.0c | 1987.0c | 97.78% | 2409.0c/-263.0c | 69.51%/63.93% | 76/38 | 0.545 | -366.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.65; impulse_over_margin>=10; sec>=300; fade_ask<=55` | False | 2146.0c | 1987.0c | 97.78% | 2409.0c/-263.0c | 69.51%/63.93% | 76/38 | 0.545 | -366.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.5; book_score<=0.65; impulse_over_margin>=10; sec>=300; fade_ask<=45` | False | 2072.0c | 1893.0c | 97.78% | 2233.0c/-161.0c | 68.52%/63.93% | 81/42 | 0.636 | -316.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.5; book_score<=0.65; impulse_over_margin>=10; sec>=300; fade_ask<=50` | False | 2072.0c | 1893.0c | 97.78% | 2233.0c/-161.0c | 68.52%/63.93% | 81/42 | 0.636 | -316.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.5; book_score<=0.65; impulse_over_margin>=10; sec>=300; fade_ask<=55` | False | 2072.0c | 1893.0c | 97.78% | 2233.0c/-161.0c | 68.52%/63.93% | 81/42 | 0.636 | -316.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.7; impulse_over_margin>=10; sec>=300; fade_ask<=45` | False | 1770.0c | 1864.0c | 97.78% | 2233.0c/-463.0c | 66.89%/62.10% | 94/44 | 0.545 | -344.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.7; impulse_over_margin>=10; sec>=300; fade_ask<=50` | False | 1770.0c | 1864.0c | 97.78% | 2233.0c/-463.0c | 66.89%/62.10% | 94/44 | 0.545 | -344.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.7; impulse_over_margin>=10; sec>=300; fade_ask<=55` | False | 1770.0c | 1864.0c | 97.78% | 2233.0c/-463.0c | 66.89%/62.10% | 94/44 | 0.545 | -344.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.65; impulse_over_margin>=10; sec>=600; fade_ask<=45` | False | 2044.0c | 1862.0c | 97.78% | 2359.0c/-315.0c | 69.51%/63.93% | 74/36 | 0.545 | -366.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.65; impulse_over_margin>=10; sec>=600; fade_ask<=50` | False | 2044.0c | 1862.0c | 97.78% | 2359.0c/-315.0c | 69.51%/63.93% | 74/36 | 0.545 | -366.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.65; impulse_over_margin>=10; sec>=600; fade_ask<=55` | False | 2044.0c | 1862.0c | 97.78% | 2359.0c/-315.0c | 69.51%/63.93% | 74/36 | 0.545 | -366.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.5; book_score<=0.65; impulse_over_margin>=10; sec>=600; fade_ask<=45` | False | 1970.0c | 1768.0c | 97.78% | 2183.0c/-213.0c | 68.52%/63.93% | 79/40 | 0.636 | -316.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.5; book_score<=0.65; impulse_over_margin>=10; sec>=600; fade_ask<=50` | False | 1970.0c | 1768.0c | 97.78% | 2183.0c/-213.0c | 68.52%/63.93% | 79/40 | 0.636 | -316.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.5; book_score<=0.65; impulse_over_margin>=10; sec>=600; fade_ask<=55` | False | 1970.0c | 1768.0c | 97.78% | 2183.0c/-213.0c | 68.52%/63.93% | 79/40 | 0.636 | -316.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.7; impulse_over_margin>=10; sec>=600; fade_ask<=45` | False | 1668.0c | 1739.0c | 97.78% | 2183.0c/-515.0c | 66.89%/62.10% | 92/42 | 0.545 | -271.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.7; impulse_over_margin>=10; sec>=600; fade_ask<=50` | False | 1668.0c | 1739.0c | 97.78% | 2183.0c/-515.0c | 66.89%/62.10% | 92/42 | 0.545 | -271.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.7; impulse_over_margin>=10; sec>=600; fade_ask<=55` | False | 1668.0c | 1739.0c | 97.78% | 2183.0c/-515.0c | 66.89%/62.10% | 92/42 | 0.545 | -271.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.75; impulse_over_margin>=10; sec>=300; fade_ask<=45` | False | 1581.0c | 1642.0c | 97.78% | 2152.0c/-571.0c | 65.90%/61.19% | 99/46 | 0.545 | -344.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.75; impulse_over_margin>=10; sec>=300; fade_ask<=50` | False | 1581.0c | 1642.0c | 97.78% | 2152.0c/-571.0c | 65.90%/61.19% | 99/46 | 0.545 | -344.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.75; impulse_over_margin>=10; sec>=300; fade_ask<=55` | False | 1581.0c | 1642.0c | 97.78% | 2152.0c/-571.0c | 65.90%/61.19% | 99/46 | 0.545 | -344.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.65; impulse_over_margin>=20; sec>=300; fade_ask<=45` | False | 1344.0c | 1622.0c | 97.78% | 1445.0c/-101.0c | 68.52%/65.75% | 49/28 | 0.455 | -389.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.65; impulse_over_margin>=20; sec>=300; fade_ask<=50` | False | 1344.0c | 1622.0c | 97.78% | 1445.0c/-101.0c | 68.52%/65.75% | 49/28 | 0.455 | -389.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.65; impulse_over_margin>=20; sec>=300; fade_ask<=55` | False | 1344.0c | 1622.0c | 97.78% | 1445.0c/-101.0c | 68.52%/65.75% | 49/28 | 0.455 | -389.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=25; margin_sigma<=0.35; book_score<=0.7; impulse_over_margin>=10; sec>=300; fade_ask<=45` | False | 1914.0c | 1573.0c | 97.78% | 2212.0c/-298.0c | 67.87%/64.38% | 81/31 | 0.545 | -237.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=25; margin_sigma<=0.35; book_score<=0.7; impulse_over_margin>=10; sec>=300; fade_ask<=50` | False | 1914.0c | 1573.0c | 97.78% | 2212.0c/-298.0c | 67.87%/64.38% | 81/31 | 0.545 | -237.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=25; margin_sigma<=0.35; book_score<=0.7; impulse_over_margin>=10; sec>=300; fade_ask<=55` | False | 1914.0c | 1573.0c | 97.78% | 2212.0c/-298.0c | 67.87%/64.38% | 81/31 | 0.545 | -237.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.75; impulse_over_margin>=10; sec>=600; fade_ask<=45` | False | 1530.0c | 1568.0c | 97.78% | 2153.0c/-623.0c | 66.23%/61.19% | 96/44 | 0.545 | -315.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.75; impulse_over_margin>=10; sec>=600; fade_ask<=50` | False | 1530.0c | 1568.0c | 97.78% | 2153.0c/-623.0c | 66.23%/61.19% | 96/44 | 0.545 | -315.0c |
| `base=choose=book_p_side; book_p_side>=0.6; ask<=95; sec_to_close>=120; margin_rv15>=0; action=fade; abs_margin<=40; margin_sigma<=0.35; book_score<=0.75; impulse_over_margin>=10; sec>=600; fade_ask<=55` | False | 1530.0c | 1568.0c | 97.78% | 2153.0c/-623.0c | 66.23%/61.19% | 96/44 | 0.545 | -315.0c |

## Read

- No near-strike breakout/reversion overlay clears the strict gate.
