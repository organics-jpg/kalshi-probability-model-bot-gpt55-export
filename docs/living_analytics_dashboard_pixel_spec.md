# Living Analytics Dashboard Pixel Spec

## Purpose

Rebuild the dashboard into a functional "Living Analytics" P&L cockpit based on the selected generated reference image:

- Reference image: `docs/dashboard_living_analytics_reference_generated_image_3.png`
- Reference dimensions: `1536 x 1024`
- Primary implementation target: `dashboard.py`
- Data sources must remain the existing scored artifacts and live logs. Do not add new data-recording requirements unless explicitly approved.

The goal is to make the real dashboard match the reference as closely as physically possible while keeping the interface usable, accurate, and stable. This is not a loose inspiration pass. It is a pixel-match implementation brief.

## Pixel-Match North Star

The implementation should aim for the closest practical pixel-for-pixel translation of the reference image at the primary desktop viewport. "As close as physically possible" means:

1. Match the reference layout proportions, visual hierarchy, color relationships, panel placement, and overall atmosphere first.
2. Preserve exact dashboard function and data correctness second.
3. Only diverge when a generated-image detail is impossible, nonfunctional, inaccessible, or unstable in a browser/Streamlit runtime.
4. When divergence is required, replace the impossible detail with the nearest implementable equivalent, not a generic dashboard substitute.

The target is not a normal Streamlit dashboard wearing a dark theme. The target is a living, alien, high-end analytics instrument that happens to run in the existing dashboard.

## Current Logical Clarifications

### Pixel Copy Versus Functional UI

The generated image contains painterly and impossible UI details: organic membranes, invented microtext, hand-painted luminosity, branching contour fields, and irregular panel shapes. These cannot all be copied literally with standard Streamlit widgets. The implementation must still attempt a near-pixel match by using:

- CSS gradients and layered backgrounds.
- Plotly charts with custom line/fill styling.
- SVG overlays for organic root, contour, and glow effects.
- HTML/CSS components for custom pods, rails, badges, and trade capsules.
- Optional later custom component/canvas if Plotly and CSS cannot get close enough.

### Primary Desktop Target Versus Responsive Behavior

Pixel matching applies first to a `1536 x 1024` reference-sized desktop viewport, then to practical desktop at `1280 x 720`. Responsive/mobile behavior should preserve the same design language but does not need to be pixel-for-pixel with the desktop reference.

### Dark UI Versus "Not Too Dark"

Earlier direction avoided a flat dark dashboard. This spec allows a dark aubergine/ink atmosphere because the selected reference depends on luminous dark depth. The rule is:

- Accept dark instrument wells and dark global atmosphere.
- Avoid flat black slabs, generic dark SaaS cards, and low-contrast text.
- Use porcelain controls, luminous chart color, and strong data contrast so the UI feels premium and alive, not gloomy.

### Feature Palette Versus Checklist

Not every existing dashboard feature must be visible in the first viewport. The first viewport must prioritize:

- P&L/equity.
- Drawdown/risk.
- Recent trade outcomes.
- Kalshi API accounting truth.
- Live lock/current dataset.
- Manual refresh and refresh mode.
- Current market/feed status.

Diagnostics, file paths, research controls, raw tables, and verbose explanations must remain collapsed or moved into secondary views.

## Visual Identity

### Core Metaphor

The dashboard is a living financial organism:

- Equity is a luminous vine or root path.
- Drawdown is coral/violet root stress beneath the vine.
- Trades are seed capsules or spores attached to the path/tape.
- API accounting is a lab-grade verification tag.
- Live lock is a biological/technical life-support indicator.
- Market pulse is a compact vital-sign instrument.

The metaphor is visual only. The UI must not show literal creatures or fantasy imagery.

### Mood

Use the mood of:

- Alien horticultural observatory.
- Luminous mycelium market map.
- Dark botanical lab instrument.
- Living financial console.
- Premium high-contrast analytics cockpit.

Avoid:

- Normal SaaS card grid.
- Generic crypto trading terminal.
- Casino neon.
- Full cyberpunk darkness.
- Literal plants, animals, or mascots.
- Decorative art that does not map to data or controls.

## Color System

### Background

Primary background should be a deep radial/linear gradient:

- Near-black ink: `#07060c`
- Deep aubergine: `#180d24`
- Dark plum: `#251336`
- Deep teal shadow, used sparingly: `#092c35`

Recommended CSS direction:

```css
background:
  radial-gradient(circle at 48% 36%, rgba(99,242,177,0.10), transparent 28%),
  radial-gradient(circle at 76% 24%, rgba(217,76,255,0.10), transparent 32%),
  linear-gradient(135deg, #07060c 0%, #180d24 48%, #092c35 100%);
```

### Primary Data Colors

Profit/equity:

- Mint: `#63f2b1`
- Bioluminescent green: `#9cff9f`
- Gold: `#f7c85f`

Risk/drawdown/loss:

- Coral: `#ff5f73`
- Hot magenta: `#d94cff`
- Deep violet: `#5b3a80`

Trust/status:

- API verified cyan: `#79e7ff`
- Live green: `#7dffb2`
- Warning amber: `#ffbf4d`
- Failure coral: `#ff4f66`

Neutral surfaces:

- Porcelain: `#f7f1e8`
- Soft lavender gray: `#a99bb9`
- Muted plum text: `#d9cde7`
- Graphite ink: `#17121d`

### Color Rules

- Profit values use mint-to-gold gradients.
- Drawdown uses coral-to-magenta-to-violet gradients.
- API/accounting uses cyan when verified, amber when partial, coral when fallback or failed.
- Live/feed uses green/cyan when fresh, amber when stale, coral when broken.
- Avoid reusing red for both harmless status and loss.
- Do not let purple dominate every element. Purple/aubergine is the atmosphere; mint, gold, coral, and cyan carry meaning.

## Typography

Use compact, modern sans-serif for most UI. The actual font can be the existing browser/system font stack unless a local project dependency already provides a better option.

Recommended stack:

```css
font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
```

Rules:

- KPI values must be large, legible, and high contrast.
- Labels should be compact uppercase or title case.
- Microtext is allowed as decorative technical texture but must not replace essential text.
- One expressive title treatment is allowed: `LIVING ANALYTICS`, `LIVING P&L`, or `EQUITY VINE`.
- Do not use visible explanatory prose describing how to use the dashboard.
- Do not use negative letter spacing.
- Avoid text over high-noise gradients unless it has a dark or light backing surface.

## Primary Desktop Layout

Target reference size: `1536 x 1024`.

### Viewport Regions

Approximate region map:

- Top command strip: `0-92px` height.
- Left vital pod rail: `24-310px` width, below command strip.
- Center living chart field: `300-1110px` width, dominant region.
- Right inspector column: `1110-1510px` width.
- Bottom trade seed tape: lower `170-230px`, spanning center and right.

These values are directional. Preserve the proportions and hierarchy from the reference, not exact numbers at all costs.

### Top Command Strip

Purpose:

The top strip is the stable operational control surface. It must be visually calmer than the center chart so the user can always control the dashboard.

Required contents:

- Dataset selector.
- Manual Refresh button.
- Auto refresh mode indicator, default `Manual`.
- Live Lock status.
- Kalshi API accounting badge.
- Current market short label if available.

Visual style:

- Frosted porcelain/glass command capsule over dark background.
- Soft internal glow.
- Segmented-pill controls.
- Subtle organic bevels, but obvious click targets.
- No large decorative title here.

Behavior:

- Manual refresh remains default.
- `Refresh now` must trigger cache refresh and scoring only on demand.
- Auto scoring must run periodically only when user selects a polling interval.
- Dataset selection must be preserved during the Streamlit session unless selected dataset disappears.

### Left Vital Pod Rail

Purpose:

Fast read of the dashboard's vital signs.

Required pods:

- Net P&L.
- Max drawdown.
- Win rate.
- Entries/open positions.
- Latest trade.

Visual style:

- Organic translucent pods, not rectangular cards.
- Each pod has a small label, large value, and one micro-note.
- Pods can have irregular rounded edges, glow rims, or membrane-like backgrounds.
- Use mint/gold for positive, coral/magenta for negative, gray/violet for neutral/open.

Data:

- Net P&L should use actual/net API-backed values when available.
- Drawdown should come from the equity curve drawdown calculation.
- Win rate should use completed trade outcomes.
- Open positions should use current open scored rows or summary fallback.
- Latest trade should use the most recent sorted trade row by exit/settlement/entry timestamp.

### Center Living Chart Field

Purpose:

This is the visual and analytical heart of the dashboard. It must dominate the first viewport.

Required layers:

1. Organic contour/background field.
2. Equity vine path.
3. Drawdown/root stress layer.
4. Trade event markers.
5. Minimal chart legend/stat line.

#### Background Field

Implement with one or more:

- CSS radial gradients.
- SVG contour patterns.
- Semi-transparent background image generated from CSS/SVG.
- Plotly paper/plot background transparency.

The field should feel like luminous root/mycelium analytics, but it must not obscure the data.

#### Equity Vine

Data:

- Prefer `actual_net_pnl_dollars` if present.
- Else `net_pnl_dollars`.
- Else `scaled_net_pnl_dollars`.
- Else fallback to `gross_pnl_dollars`.

Rendering:

- Left-to-right cumulative equity path.
- Mint-to-gold line or ribbon.
- Soft glow shadow.
- Rounded markers at trade events.
- Slight visual smoothing is acceptable only if raw trade markers remain accurate.

Implementation options:

- Phase 1: Plotly line chart with glow simulated by duplicate traces.
- Phase 2: SVG overlay with organic path stroke and filter glow.
- Phase 3: Canvas/custom component if needed.

#### Drawdown Roots

Data:

- Compute drawdown from cumulative equity curve.
- Drawdown is `equity - rolling_max(equity)`.
- Values should be zero or negative.

Rendering:

- Drawdown appears directly below or behind equity, not as a disconnected chart.
- Coral/magenta/violet filled stress shadow.
- Root-like branches can be decorative if they map to drawdown depth or trade density.
- The max drawdown should be visually findable.

#### Trade Markers

Data:

- Use recent trades and P&L sign.
- Win/loss/flat/open categories.

Rendering:

- Seed/spore nodes attached to the equity vine.
- Win: mint/gold.
- Loss: coral/magenta.
- Flat/open: violet/gray glass.
- Hover detail should show side, market, P&L, entry/exit, fees/accounting source.

### Right Inspector Column

Purpose:

The truth panel. It explains whether the dashboard can be trusted right now.

Required modules:

- Kalshi API accounting.
- Live Lock.
- Market pulse.
- Orderbook pulse/freshness.
- Feed/heartbeat freshness.
- Score freshness.

Visual style:

- Stacked frosted instrument housings.
- More structured and readable than the central organic field.
- Small status lights and meters.
- Compact, not verbose.

#### Kalshi API Accounting Module

Use scorer fields from `summary.json`:

- `kalshi_api_accounting_enabled`
- `kalshi_api_accounting_authenticated`
- `kalshi_api_accounting_fill_count`
- `accounting_entry_rows_matched_api`
- `accounting_exit_rows_matched_api`
- `accounting_unmatched_entries`
- `accounting_unmatched_realized_exits`
- `accounting_source`
- `accounting.reconciliation_json`

Status copy:

- Full verified:
  - Label: `Kalshi API`
  - Value: `Verified`
  - Note: `<entry+exit matches> matched / 0 unmatched`
- Partial:
  - Label: `Kalshi API`
  - Value: `Partial`
  - Note: `<unmatched> unmatched fills`
- Fallback:
  - Label: `Accounting`
  - Value: `Fallback`
  - Note: `API unavailable`

Do not claim "100% accurate" in the UI unless every scored entry and realized exit was matched to API fills and API auth succeeded.

#### Live Lock Module

Use:

- `state/live_trading.lock`
- Active dataset resolver logic.
- Active dataset `tag` and `log_source_tag`.

States:

- `Live Lock`: selected dataset follows lock strategy.
- `Manual Dataset`: user selected a non-lock dataset.
- `No Lock`: lock missing/unusable.

#### Market Pulse Module

Use parsed latest heartbeat/watch/log state:

- Current market ticker.
- YES/NO quotes.
- Spread if available.
- Book ready.
- Pending order.
- Heartbeat age.
- Feed age/local reaction if available.

Show as meters or short rows, not paragraphs.

### Bottom Trade Seed Tape

Purpose:

Make recent outcomes scannable and tactile.

Data:

- Most recent 8-16 trades depending on viewport.
- Use sorted recent trades.
- Display P&L sign, side, entry/exit cents, and short timestamp.

Visual style:

- Horizontal rail across bottom.
- Capsules/seeds are irregular but aligned.
- Each capsule has color-coded glow.
- Hover reveals details.
- Click/expand can open a full trade detail drawer in a later phase.

Capsule contents:

- Side: `YES` or `NO`.
- P&L: signed money.
- Entry-to-exit: `42c -> 56c` when exit exists.
- Outcome icon or color dot.

Fallback:

- If no trades, show a quiet empty state: `Waiting for scored trades`.

## Secondary Views

The full app can keep existing views, but the design language should not collapse back into normal cards.

Recommended view mapping:

- `Overview`: Living Analytics command center.
- `Visualizer`: More detailed chart interactions, optional larger chart.
- `Research Lab`: Dense inspector layout with current experimental tables.
- `Loss diagnostics`: Drawdown/root stress focused view.
- `Strategy optimizer`: Keep functional, but restyle as instrument grid later.

Do not try to convert every secondary view in the first pass. The first viewport matters most.

## Data Contracts

### Existing Files

Use existing dashboard data only:

- `stats/<tag>/summary.json`
- `stats/<tag>/trades.csv`
- `stats/<tag>/market_results.csv`
- `logs/<log_source_tag>/bot.log`
- `logs/<log_source_tag>/execution_events.ndjson`
- `state/live_trading.lock`

Do not require a new data recorder.

### Dataset Resolution

Preserve current behavior:

- Read `state/live_trading.lock` first.
- Use `strategy_tag` as canonical stats tag.
- If `logs/<strategy_tag>` is missing but `logs/live_<strategy_tag>` exists, use `live_` log source while keeping stats tag unchanged.
- Fall back to newest `logs/live_*` only if lock is missing or unusable.
- Resolved live dataset appears first on fresh load.
- User manual selection persists in the session unless the selected dataset disappears.

### Accounting

The dashboard must expose whether P&L is API-backed.

Rules:

- Use API-backed net P&L when present in scored trades.
- Never silently mix assumed and API values without showing accounting status.
- If API matching is partial, show partial status.
- If fallback is used, show fallback status.
- Keep detailed reconciliation paths collapsed.

## Interaction Behavior

### Manual Refresh

Default:

- Auto refresh: `Manual`.

Manual action:

- `Refresh now` clears dashboard caches.
- Triggers score refresh on demand.
- Reruns once.

Auto action:

- Only active when user chooses interval.
- Auto scoring should be periodic, not continuous/glitchy.

### Hover Detail

Required hover interactions:

- Equity markers show timestamp, cumulative P&L, trade P&L.
- Drawdown layer shows drawdown amount.
- Trade seed capsules show full trade summary.
- API badge shows match counts.
- Market pulse shows heartbeat age and quote data.

### Collapsed Diagnostics

Diagnostics drawer should include:

- File paths.
- Raw summary JSON path.
- Reconciliation JSON path.
- Log source.
- Score mode.
- Last score timestamp if available.

It should be collapsed by default.

## Implementation Strategy

### Phase 0: Reference Pinning

Completed for this spec:

- Copied selected generated reference to `docs/dashboard_living_analytics_reference_generated_image_3.png`.

Future implementation should open this reference while coding and compare first viewport against it.

### Phase 1: Layout Skeleton

Create the overview top fold with:

- `.living-dashboard-shell`
- `.living-command-strip`
- `.living-vitals-rail`
- `.living-chart-field`
- `.living-inspector`
- `.living-trade-tape`

Use CSS/HTML inside Streamlit markdown where Streamlit native widgets cannot achieve the shape. Keep actual dataset selector/refresh controls functional in the sidebar or top command area depending on Streamlit limitations.

Phase 1 acceptance:

- Layout proportions match reference direction.
- First viewport no longer reads as card grid.
- Manual refresh and dataset controls still work.

### Phase 2: Visual Skin

Add:

- Deep aubergine/ink background.
- Organic contour SVG background for chart field.
- Frosted pod surfaces.
- Mint/gold/coral/violet gradients.
- Glow and depth effects.

Phase 2 acceptance:

- Looks recognizably related to the reference image at a glance.
- Text remains readable.
- No major overlap at `1536 x 1024` and `1280 x 720`.

### Phase 3: Living Chart

Implement Plotly chart:

- Equity line/ribbon.
- Drawdown filled layer.
- Trade markers.
- Transparent background.
- Custom hover.

Glow strategy:

- Trace 1: wide blurred-looking transparent line.
- Trace 2: medium semi-transparent line.
- Trace 3: sharp bright line.
- Markers layered similarly.

If Plotly cannot achieve enough resemblance, add SVG overlay behind/above chart.

Phase 3 acceptance:

- Equity and drawdown are both readable.
- Main chart feels like a living vine/root system.
- Values match current trades.

### Phase 4: Trade Seed Tape

Replace or supplement recent trade table with capsules.

Phase 4 acceptance:

- User can identify latest trade result without reading a table.
- Capsules have hover detail.
- Empty state is graceful.

### Phase 5: Inspector Truth Panel

Build right rail modules:

- Accounting.
- Live lock.
- Market pulse.
- Feed freshness.
- Score freshness.

Phase 5 acceptance:

- User can tell whether accounting is Kalshi API backed within 5 seconds.
- User can tell if live data is fresh within 5 seconds.

### Phase 6: Pixel-Match Polish

Use side-by-side reference comparison.

Tune:

- Region proportions.
- Glow strength.
- Color balance.
- Pod shapes.
- Chart field density.
- Label positions.
- Bottom tape rhythm.
- Inspector compactness.

Phase 6 acceptance:

- At `1536 x 1024`, first viewport captures at least 80-90% of the reference's composition and atmosphere.
- At `1280 x 720`, first viewport still shows command strip, vitals, main chart, inspector, and at least part of trade tape.

## Technical Notes For Streamlit

### Known Constraints

Streamlit is not ideal for arbitrary custom geometry. To approach pixel matching:

- Use `st.markdown(..., unsafe_allow_html=True)` for custom layout shells.
- Use Plotly for data charts, not static images.
- Use CSS pseudo-elements where supported by injected markup.
- Keep native Streamlit widgets where function matters most.
- Avoid relying on CSS selectors that may break across Streamlit versions unless already used in this dashboard.

### Possible Escape Hatches

If Streamlit blocks the desired fidelity:

1. Build custom HTML/CSS components inside markdown for noninteractive visual pieces.
2. Use SVG generated from Python/HTML for contour and root overlays.
3. Use a small custom Streamlit component or embedded iframe for the central living chart.
4. Use canvas/WebGL only if Plotly/SVG cannot approximate the reference.

The first implementation should avoid WebGL unless necessary.

## Accessibility And Usability

Even while chasing pixel matching:

- Text contrast must be readable.
- Manual refresh must remain obvious.
- Dataset state must be visible.
- API/fallback status must not rely on color alone.
- Loss/drawdown must not rely on red alone; include labels and numeric values.
- Hover details should not be the only place important status appears.
- Avoid animations that cause visual instability or refresh glitches.

## Empty And Failure States

The design must handle:

- Empty `trades.csv`.
- Missing `summary.json`.
- Missing live lock.
- Missing or stale bot log.
- Kalshi API accounting unavailable.
- Partial API fill match.
- Open positions with no realized P&L.

Visual behavior:

- Empty trades: quiet seed rail empty state.
- Missing accounting: amber/coral fallback badge.
- Missing live lock: `No Lock` status.
- Stale feed: amber pulse state.
- Broken feed: coral pulse state.

## QA Plan

Run:

```powershell
python -m py_compile .\dashboard.py
```

If scorer changes are made:

```powershell
python -m py_compile .\score_bot_log.py
python -m unittest .\test_score_bot_log_accounting.py
```

Browser checks:

- Open `http://127.0.0.1:8501`.
- Confirm fresh load uses `Auto refresh: Manual`.
- Confirm no continuous refresh glitch.
- Confirm first viewport at `1536 x 1024` resembles reference composition.
- Confirm first viewport at `1280 x 720` keeps functional hierarchy.
- Confirm console has no errors or warnings.
- Confirm text does not overlap.
- Confirm API accounting badge reflects `summary.json`.
- Confirm diagnostic paths are collapsed.

Visual comparison checklist:

- Dark aubergine atmosphere present.
- Central living equity field dominates.
- Coral/violet drawdown stress layer visible.
- Left vital pods visible.
- Right inspector truth panel visible.
- Bottom seed trade tape visible or partially visible.
- Top command strip visible and functional.
- No normal equal-card overview remains in first viewport.

## Definition Of Done

The overhaul is done when:

1. The dashboard first viewport visually reads as a close functional translation of `dashboard_living_analytics_reference_generated_image_3.png`.
2. The main P&L/drawdown experience is the dominant visual.
3. Kalshi API accounting status is visible without opening diagnostics.
4. Live lock/dataset/refresh controls remain functional and stable.
5. Recent trades are shown as seed capsules/tape, not only as a table.
6. Empty/failure states are handled gracefully.
7. `python -m py_compile .\dashboard.py` passes.
8. Browser DOM/console checks pass.
9. No text overlaps at desktop and mobile breakpoints.
10. The implementation does not change live trading logic or data recording requirements.

## Explicit Non-Goals

- Do not change live bot trading logic.
- Do not add new API calls from the dashboard unless already supported by scoring or explicitly approved.
- Do not require new live data recording.
- Do not expose secrets or credential paths in visible UI.
- Do not turn the dashboard into a static image.
- Do not hide critical accounting/live status behind decoration.
- Do not make a marketing landing page.

## Open Implementation Questions

These should be resolved during implementation, not before writing any code:

1. Can the top command strip host Streamlit's actual dataset and refresh widgets cleanly, or should the functional controls remain in the sidebar while the top strip mirrors their state?
2. Is Plotly sufficient for the living vine and drawdown root effect, or is an SVG overlay needed?
3. Should trade seed capsules be HTML-only first, then upgraded with click/hover detail later?
4. Which first viewport should be treated as the hard visual target during QA: `1536 x 1024` reference size or the user's most common browser size?
5. Do we want to preserve the current segmented view navigation as-is, or restyle it into the command strip later?

## Implementation Bias

When there is a tradeoff, choose in this order:

1. Data correctness.
2. Manual refresh stability.
3. Pixel resemblance to the reference.
4. Readability.
5. Implementation simplicity.

Pixel resemblance is intentionally high priority, but it cannot override accurate P&L/accounting or a stable refresh model.
