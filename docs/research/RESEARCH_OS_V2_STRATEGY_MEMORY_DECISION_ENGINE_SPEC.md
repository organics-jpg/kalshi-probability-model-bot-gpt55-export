# Research OS V2: Strategy Memory And Decision Engine Spec

## Purpose

This spec defines an ambitious but realistic overnight work package for the separate Research OS Dashboard on `127.0.0.1:8503`.

The goal is not merely to make the Obsidian-style atlas prettier. The goal is to make the dashboard function as a **strategy memory system** and **research decision engine**:

- prevent repeating past strategy variants without a changed assumption,
- surface profitable-looking traps that are still blocked,
- identify which motifs recur across successful candidates,
- identify which blocker motifs recur across failed candidates,
- show which families are overworked, underdeveloped, or missing evidence,
- make candidate lineage and nearest prior attempts obvious,
- produce a morning-facing research plan that says what to test, what to validate, what to archive, and what not to repeat.

This should be sized as a genuine 7-9 hour implementation sprint, not as a nominal automation wrapper. It requires code changes, registry-derived analysis, UI changes, tests, and browser verification.

## Pointer Goal

Use this exact short goal when starting the overnight run:

```text
Use subagents for an 8-hour research-only sprint implementing docs/research/RESEARCH_OS_V2_STRATEGY_MEMORY_DECISION_ENGINE_SPEC.md. Build Research OS V2 as a Strategy Memory and Candidate Decision Engine: repeat-risk signatures, nearest-prior lineage, positive-but-blocked traps, failure motif mining, family gap analysis, candidate inspector upgrades, research-move recommendations, atlas readability improvements, tests, and browser QA. Do not touch live bot logic, order logic, scorer behavior, thresholds, secrets, or live trading state. Keep the existing live dashboard on 8501 unchanged and work only on the separate Research OS dashboard on 8503 plus project_os modules.
```

## Absolute Guardrails

These are hard constraints.

1. Do not change live bot logic.
2. Do not change order placement logic.
3. Do not change scorer behavior or thresholds used outside the Research OS dashboard.
4. Do not place trades.
5. Do not stop, restart, or mutate the live bot unless the user separately asks for that.
6. Do not edit secrets.
7. Do not move, delete, or archive research artifacts.
8. Keep the existing live dashboard on `127.0.0.1:8501` unchanged.
9. The Research OS dashboard remains separate on `127.0.0.1:8503`.
10. Treat all strategy conclusions as research-only dashboard guidance, not deployment approval.
11. Backtest or replay evidence alone must never imply readiness.
12. Positive P&L alone must never override blockers.
13. A new strategy family should be justified only after existing candidate/family evidence has been classified, blocked, or shown incomplete.
14. Manual dashboard refresh should not launch bots, run live collectors, place orders, archive files, or mutate strategy outputs.
15. If anything is ambiguous, prefer read-only summaries and explicit "needs classification" warnings.

## Current State To Build From

Known current Research OS components:

- `project_os_dashboard.py`
- `project_os/models.py`
- `project_os/registry.py`
- `project_os/family.py`
- `project_os/graph.py`
- `project_os/patterns.py`
- `project_os/views/dashboard_views.py`
- `project_os/adapters/*`
- `logs/project_os/registry_latest.json`

Known current dashboard concepts:

- Obsidian-style atlas on `8503`.
- Atlas node art already has layered visual grammar:
  - core fill = status/verdict,
  - outer ring = evidence strength,
  - soft aura = family,
  - shape and glyph = node kind,
  - dimming/focus rings = selected neighborhood.
- Pattern Cartography exists as an initial section.
- Current registry shape is approximately:
  - `1,406` nodes,
  - `1,424` edges,
  - `16` candidates,
  - `63` particle reports,
  - `92` datasets,
  - `988` scripts,
  - `17` health issues.
- Default graph has been reduced from noisy all-node view to a smarter collapsed view around roughly `292` nodes and `310` edges.
- Initial pattern logic exists for:
  - motif summaries,
  - repetition clusters,
  - family pattern rows,
  - frontier cards,
  - positive-but-blocked rows,
  - lineage gap rows.

These counts are baseline hints, not fixed acceptance targets. The overnight run must regenerate or reload the current registry and report the actual node, edge, candidate, report, dataset, script, and health counts it sees at runtime.

The overnight sprint should harden, deepen, test, and productize this into a truly useful research control system.

## Desired Morning Outcome

By morning, opening `http://127.0.0.1:8503/` should make the following questions answerable in under five minutes:

1. What are the strongest existing candidates or motifs?
2. Which positive-looking results are actually blocked and should not be repeated unchanged?
3. Which strategy variants are near-duplicates of prior attempts?
4. Which candidate/family has the clearest next proof step?
5. Which family is over-tested and should stop receiving sibling variants?
6. Which family is underdeveloped enough to justify a new candidate or forward proof run?
7. Which blockers recur most often, by family and motif?
8. Which results have insufficient lineage edges and need classification?
9. Which research move should happen next: exploit, validate, repair, archive, or branch?
10. Why is a proposed next test different from the failed or blocked sibling attempts?

## Eight-Hour Work Budget

This spec is intentionally more ambitious than a simple dashboard-polish pass, but it is still bounded.

### Estimated Schedule

1. Orientation and baseline verification: 30-45 minutes
2. Data/model hardening in `project_os/patterns.py`: 90-120 minutes
3. Repeat-risk signatures and nearest-prior lineage: 90-120 minutes
4. Failure motif mining and positive-but-blocked traps: 60-90 minutes
5. Candidate inspector and family research map upgrades: 75-90 minutes
6. Atlas lens/art/readability upgrades: 60-75 minutes
7. Tests and logic audits: 60-90 minutes
8. Browser verification and morning report: 45-60 minutes

Expected total: 7-9 hours.

If time runs short, prioritize repeat-risk signatures, positive-but-blocked traps, candidate inspector, tests, and browser verification over additional visual polish.

## Subagent Plan

Use subagents deliberately. Do not spawn duplicate agents doing the same task.

### Subagent A: Visual Atlas And Interaction

Purpose:

- audit `project_os/graph.py` and atlas-related UI,
- propose and/or implement improvements that make the atlas easier to read as a research map.

Focus:

- label placement,
- family-region readability,
- repeat-risk lens,
- selected-neighborhood edge readability,
- dense graph legibility,
- keeping the real node trace clickable,
- keeping Plotly trace count reasonable,
- preserving hidden modebar.

Expected output:

- concrete patch or recommendations,
- list of touched files,
- risks to verify in browser.

### Subagent B: Pattern Mining And Data Semantics

Purpose:

- inspect registry data, reports, locked plans, metrics, blockers, and edges,
- define repeat signatures and motif extraction rules.

Focus:

- candidate signatures,
- nearest prior attempts,
- sibling clusters,
- positive-but-blocked rows,
- blocker motif extraction,
- family gap flags,
- lineage completeness.

Expected output:

- concrete metrics,
- examples from current registry,
- implementation notes for `project_os/patterns.py`.

### Subagent C: Logic And Calculation Audit

Purpose:

- check all status/evidence/P&L logic for false conclusions.

Focus:

- cents versus dollars,
- replay/backtest evidence constraints,
- positive P&L versus blocked status,
- evidence ranking,
- repeat-risk scoring,
- sorting and tie-breaking,
- no hidden live readiness claims.

Expected output:

- findings with file/line references,
- test cases to add.

### Subagent D: Browser QA And UX Readability

Purpose:

- verify dashboard behavior in the rendered browser.

Focus:

- no Streamlit errors,
- graph nonblank,
- Pattern Cartography visible,
- filters/lenses work,
- inspector updates,
- tables readable,
- no CSS leakage,
- modebar hidden,
- existing `8501` dashboard still separate.

Expected output:

- browser verification facts,
- screenshots if stable,
- DOM-based fallback if screenshot capture is flaky.

### Subagent Integration Protocol

Subagent output is not completion by itself. The primary worker must integrate the useful findings, reject or defer unsafe findings, and record the result.

Rules:

1. Each subagent should have a distinct scope.
2. No two subagents should modify the same file without explicit coordination.
3. Subagent recommendations must be checked against the live-system guardrails before implementation.
4. If a subagent reports a bug, the primary worker must either patch it, add it to residual risks with a reason, or explain why it is not a bug.
5. If subagents produce conflicting recommendations, prefer the one that preserves registry-first, read-only, no-false-promotion behavior.
6. The final report must summarize subagent contributions and list any subagent finding that was deferred.
7. The final completion gate still belongs to the primary worker. Do not close the goal merely because all subagents returned.

## Architecture Principles

### Registry-First

All analysis should consume `ProjectRegistry`. Do not make dashboard views independently crawl the filesystem.

Correct flow:

```text
workspace artifacts
  -> adapters
  -> registry
  -> pattern analysis
  -> graph/UI views
  -> optional overnight report
```

Incorrect flow:

```text
dashboard table
  -> direct filesystem scan
  -> one-off path parsing
```

### Read-Only Analysis

Pattern analysis may compute derived rows in memory. It may write a Research OS report under `logs/project_os/` if explicitly part of the overnight deliverable, but it must not mutate research outputs.

Allowed:

- `logs/project_os/research_os_v2_overnight_report.md`
- `logs/project_os/research_os_v2_patterns_latest.json`
- tests under normal test files
- dashboard code under `project_os`

Not allowed:

- modifying `stats/*`,
- modifying `logs/particle_research/*` evidence outputs,
- editing live bot state,
- moving/deleting artifacts,
- changing live strategy code.

### V1 Non-Regression Invariants

V2 must not lose the foundational Research OS behavior while adding strategy memory features.

Preserve:

- manual refresh only,
- registry-first views,
- unknown artifacts visible by default,
- archived artifacts visible by default,
- health issues visible in the atlas and health surfaces,
- sensitive nodes visible by default but clearly marked,
- local-only sensitive warning,
- separate `8503` Research OS dashboard,
- existing `8501` live dashboard left unchanged,
- registry snapshots and latest registry behavior unchanged unless the spec explicitly says otherwise.

If any V1 invariant cannot be preserved, the overnight worker must stop treating the work as complete and document the exact regression.

### Sensitive And Local-Only Handling

The dashboard is local, but sensitive local files may be visible by design. V2 work must keep that explicit and controlled.

Requirements:

- sensitive nodes stay marked with `sensitive=true`,
- the local-only warning remains visible,
- a hide-sensitive filter remains available,
- screenshots or morning reports must not print raw secret values,
- browser QA may verify sensitive-node styling, but should avoid capturing raw secret contents,
- no external network transmission of registry contents, secret contents, screenshots, or reports,
- no web links or generated links should expose local file contents.

### No False Promotion

The dashboard can recommend research moves. It cannot claim readiness unless existing readiness artifacts already support it.

Correct language:

- "worth validating",
- "needs forward proof",
- "do not repeat unchanged",
- "blocked until baseline comparison clears",
- "frontier candidate gap",
- "candidate requires lineage classification."

Incorrect language:

- "deploy",
- "ready",
- "promote",
- "trade live",
- "profitable strategy found" unless strict evidence exists and the dashboard can cite it.

## Core Data Concepts

### Candidate

A candidate is a named strategy hypothesis or locked plan/report/stats object that could become part of a complete strategy.

Candidate nodes are not enough. The system should also interpret report and stats nodes as candidate evidence.

### Motif

A motif is a recurring strategy idea or research mechanism, such as:

- realized-vol / RV,
- sidecar slice,
- forward/OOS validation,
- common-clock v28,
- phi reward memory,
- exit/risk control,
- fillability/source quality,
- OU/mispricing,
- threshold/touch,
- replay/backtest diagnostic.

Motifs are not final strategy families. Motifs cut across families and explain repeated assumptions.

### Repeat-Risk Signature

A repeat-risk signature is a stable fingerprint of a strategy attempt.

It should combine:

- family,
- motif tags,
- locked-plan schema,
- candidate/plan id pattern,
- time-to-close band if available,
- entry rule language,
- exit/risk language,
- accounting mode,
- evidence scope,
- baseline comparison target,
- blocker/gate language.

Initial signature can be heuristic. It does not need full JSON schema support in V2, but it must be deterministic and visible.

### Nearest Prior

Nearest prior is the most similar older candidate/report/plan according to signature overlap, motif overlap, family, and evidence history.

The dashboard should show:

- nearest prior label,
- similarity score,
- prior status,
- prior blocker,
- what changed, if detectable,
- warning if nothing meaningful changed.

### Positive-But-Blocked

Positive-but-blocked means:

- P&L metric is positive,
- status is `blocked`, `rejected`, or `diagnostic_only`,
- or blockers/gates indicate it cannot be counted as proof.

This is a critical class because it prevents loops like "this had positive P&L, try it again" when the actual reason was concentration, insufficient entries, poor baseline comparison, or post-hoc slicing.

### Family Gap

Family gap flags should include:

- no candidate,
- no forward evidence,
- no live/stat evidence,
- many artifacts but no candidate,
- many scripts but unclassified,
- many reports but no current next action,
- no blocker lineage,
- positive diagnostics but no frozen candidate,
- repeated locked siblings without a changed assumption.

### Lineage Completeness

Lineage completeness measures whether a node has meaningful graph edges beyond shallow containment.

Important edge types:

- `blocks`,
- `rejects`,
- `supersedes`,
- `validates`,
- `depends_on`,
- `documents`,
- `uses`,
- `scores`.

The current registry has many `contains` edges, but a decision engine needs more semantic links. V2 should surface missing links even if it cannot fix every one.

### Metric Normalization And Provenance

Pattern logic must treat numeric metrics conservatively because reports may use different units, names, and shapes.

Every P&L-like value shown in V2 should carry:

- source node id,
- source metric key,
- raw value,
- inferred unit when known,
- display value,
- confidence.

Rules:

- do not compare cents and dollars unless the unit is known or normalized,
- if unit is unknown, show the value as raw and lower confidence,
- if multiple P&L fields exist, prefer explicit net-after-fee fields over gross fields,
- if only gross or ambiguous fields exist, label the metric as ambiguous,
- sorting by P&L must not outrank evidence level, blocker state, or unit confidence,
- positive-but-blocked detection may use a positive ambiguous metric as a warning signal, but not as proof.

## Required Implementation Areas

### 1. Harden `project_os/patterns.py`

Add or refine the following functions.

#### `normalized_metric_snapshot(node: ProjectNode) -> dict`

Purpose:

- extract conservative display metrics from a node without pretending all reports use the same units.

Expected fields:

```text
pnl_value
pnl_display
pnl_unit
pnl_key
pnl_confidence
entries
markets
roots
win_rate
metric_warnings
```

Logic constraints:

- no filesystem IO,
- no external calls,
- handle missing metrics,
- handle string numeric values,
- handle nested metric dictionaries if already present on the node,
- preserve raw values in warnings when the unit is ambiguous,
- never convert ambiguous P&L into readiness evidence.

#### `node_pattern_tags(node: ProjectNode) -> list[str]`

Purpose:

- infer motif tags from node id, label, family, path, source adapter, summary, next action, tags, blockers, and metric keys.

Requirements:

- deterministic,
- no filesystem IO,
- no external calls,
- returns stable lowercase motif ids,
- caps output to a readable number.

Logic constraints:

- `forward_shadow` evidence can add forward/OOS motif,
- `live_stats` can add live/stat motif,
- blockers can add failure/risk motifs,
- path can help infer source quality or family, but should not override explicit family.

#### `candidate_signature(node: ProjectNode) -> str`

Purpose:

- produce a deterministic repeat-risk signature for candidates/reports/stats.

Suggested fields:

```text
family
kind
motif tags
evidence level bucket
normalized label tokens
normalized summary tokens
key blocker tokens
metric-shape tokens
```

Do not include timestamps except when useful to distinguish evidence roots. A repeat-risk signature should group siblings, not split every run by timestamp.

#### `signature_similarity(a, b) -> float`

Purpose:

- compare two signature payloads.

Initial heuristic:

- +0.25 same family,
- +0.25 motif overlap,
- +0.15 same evidence bucket,
- +0.15 normalized token overlap,
- +0.10 blocker token overlap,
- +0.10 similar metric shape.

Return `0.0` to `1.0`.

#### `nearest_prior_rows(registry) -> list[dict]`

Purpose:

- for each candidate/report/stats node, find nearest earlier or sibling attempt.

If timestamps are missing, still compute nearest sibling by similarity but label the ordering as "sibling" rather than "prior".

Columns:

```text
Label
Family
Kind
Signature
Nearest Prior
Similarity
Prior Status
Prior Evidence
Prior Blocker
Changed Assumption
Repeat Warning
```

#### `positive_blocked_rows(registry) -> list[dict]`

Already exists in initial form. Improve it.

Columns:

```text
Label
Family
Kind
Status
Evidence
P&L
Markets
Entries
Primary Blocker
Why It Is Tempting
Why It Is Blocked
Do Next
```

Logic:

- positive P&L plus blocked status means trap, not promotion.
- positive diagnostic-only means "hypothesis clue", not proof.
- positive metadata-only means "needs freezing or forward evidence".

#### `failure_motif_rows(registry) -> list[dict]`

Purpose:

- mine blocker text across nodes.

Normalize common blocker tokens:

```text
positive_roots_below_60pct
positive_markets_below_60pct
single_market_share_above_25pct
avg_entry_below_10c
last_window_nonpositive
nonpositive_pnl
fewer_than_25_entries
does_not_beat_matched_v28_by_20pct
beats_baseline_brier
beats_baseline_logloss
low_positive_market_fraction
underpowered_markets
trajectory_blocked_shadow_only
shadow_only
source_quality
fillability
accounting
```

Columns:

```text
Family
Failure Motif
Count
Affected Nodes
Example
Likely Meaning
Required Change
```

#### `family_gap_rows(registry) -> list[dict]`

Purpose:

- turn family state into action flags.

Columns:

```text
Family
Nodes
Candidates
Reports
Stats
Forward Evidence
Live Evidence
Blocked/Rejected
Watch/Active
Dominant Motifs
Gap Flags
Next Move
```

Gap flags:

- `NO_CANDIDATE`,
- `NO_FORWARD_EVIDENCE`,
- `NO_STATS`,
- `DATA_WITHOUT_CANDIDATE`,
- `SCRIPT_HEAVY_UNCLASSIFIED`,
- `POSITIVE_DIAGNOSTIC_NO_FREEZE`,
- `REPEAT_RISK_HIGH`,
- `LINEAGE_UNDER_SPECIFIED`.

#### `research_move_cards(registry) -> list[dict]`

Purpose:

- create a morning-facing decision panel.

Lanes:

- `Test Next`,
- `Validate`,
- `Do Not Repeat`,
- `Repair Lineage`,
- `Frontier`,
- `Archive/Ignore`.

Each card:

```text
Lane
Title
Family
Signal
Evidence
Why
Next Action
Risk
Source Nodes
```

Rules:

- `Test Next` should prefer existing candidates with strong/worth/active status and live/forward evidence.
- `Validate` should prefer worth-watching or positive diagnostic candidates with missing forward proof.
- `Do Not Repeat` should prefer high repeat-risk clusters and positive-but-blocked traps.
- `Repair Lineage` should surface high-impact lineage gaps.
- `Frontier` should be family gaps, not random new ideas.
- `Archive/Ignore` should be rejected/archived clusters with repeated blockers and no changed assumption.

### 2. Upgrade Candidate Inspector

The inspector is where the atlas becomes actionable.

When a candidate/report/stats node is selected, show:

1. identity:
   - label,
   - kind,
   - family,
   - status,
   - evidence,
   - source adapter,
   - path.

2. proof summary:
   - P&L,
   - entries,
   - markets,
   - roots,
   - win rate,
   - evidence level,
   - whether proof is live/forward/backtest/diagnostic only.

3. motif summary:
   - motif tags,
   - signature,
   - sibling cluster,
   - nearest prior,
   - similarity score,
   - what changed.

4. blocker summary:
   - primary blocker,
   - failure motifs,
   - whether blocker is structural or evidence-volume related.

5. decision summary:
   - `Test next`,
   - `Collect more forward evidence`,
   - `Do not repeat unchanged`,
   - `Repair lineage`,
   - `Archive unless new assumption appears`,
   - `Name candidate before judging`.

6. linked artifacts:
   - incoming/outgoing graph edges,
   - reports,
   - datasets,
   - scripts,
   - docs.

7. raw preview remains collapsible.

Logical rule:

The inspector must not hide blockers behind positive metrics. If a node is positive-but-blocked, the blocked warning must appear above the P&L table.

### 3. Add Pattern Cartography V2 Section

The existing Pattern Cartography section should become the research control center.

Required panels:

#### Research Moves

Horizontal cards:

- Test Next,
- Validate,
- Do Not Repeat,
- Repair,
- Frontier,
- Archive.

Each card has:

- one-line signal,
- why,
- next action,
- source nodes.

#### Motif Heatmap

Family x motif count.

Requirements:

- distinguish high-volume noise from high-value signal,
- tooltips mention count and strongest status/evidence,
- keep it compact.

#### Winning Motifs

Table sorted by:

1. live/forward evidence,
2. worth/strong/active status,
3. positive P&L,
4. low blocker pressure.

Columns:

```text
Motif
Families
Nodes
Candidates
Watch/Active
Blocked/Rejected
Best Evidence
Best P&L
Repeat Pressure
Guidance
```

#### Do Not Repeat Blindly

Table of repeated sibling clusters and failed motifs.

Columns:

```text
Family
Pattern
Attempts
Watch/Active
Blocked/Rejected
Best Evidence
Best P&L
Risk
Examples
Guidance
```

#### Tempting But Blocked

Table of positive P&L, blocked/rejected/diagnostic-only nodes.

This panel should be visually warning-colored.

Columns:

```text
Label
Family
Status
Evidence
P&L
Markets
Entries
Primary Blocker
Do Next
```

#### Family Gap Matrix

Show:

- family,
- candidate count,
- report count,
- stats count,
- forward evidence,
- live evidence,
- blocker load,
- gap flags,
- next move.

#### Lineage Gaps

Show nodes with important statuses but no semantic edges.

Columns:

```text
Label
Family
Kind
Status
Evidence
Motifs
Missing Link
Priority
```

### 4. Add Atlas Lenses

Current lenses should remain.

Add/refine:

#### Repeat Risk

Purpose:

- show families, candidates, reports, stats, health, positive-blocked traps, and summary artifact clusters.

Visual:

- repeated clusters get stronger warning rings,
- blocked/rejected high-P&L nodes are visible,
- low-signal artifacts collapsed.

#### Frontier Gaps

Purpose:

- show underdeveloped families and missing evidence surfaces.

Visual:

- families with no candidates or no forward evidence should show distinct frontier styling.

#### Failure Motifs

Purpose:

- show blocker-heavy clusters.

Visual:

- health/blocker nodes and rejected reports prominent,
- edge neighborhood around blockers emphasized.

#### Evidence Quality

Purpose:

- make proof maturity obvious:
  - live forward,
  - live stats,
  - forward shadow,
  - replay,
  - backtest,
  - diagnostic,
  - metadata-only.

### 5. Improve Atlas Art And Readability

Work in `project_os/graph.py`.

Requirements:

- Keep graph vectorized. Do not create a trace per node.
- Keep true node marker trace topmost or keep selectable traces with matching `customdata`.
- Do not use per-node layout images.
- Family region shapes can be per-family, not per-node.
- Preserve `customdata` for node and label selection where possible.
- Keep modebar hidden through config and CSS.
- Avoid too many labels in default view.

Enhancements:

1. family regions:
   - region labels,
   - subtle double rings,
   - shape intensity based on node count or blocker pressure.

2. labels:
   - explicit `balanced` label mode,
   - per-point label placement,
   - ellipsis not hard truncation,
   - clickable label metadata.

3. edge readability:
   - global edges faint,
   - selected-neighborhood edges more visible,
   - selected edges colored by evidence or relation if feasible.

4. LOD collapse:
   - default view should stay readable,
   - preserve detail through filters,
   - summarize low-signal logs/datasets/docs/artifacts when graph exceeds threshold.

5. hover:
   - include motifs,
   - include signature or cluster size when available,
   - include primary blocker if present,
   - include next action.

### 6. Add A Morning Report

Create an optional report generator, either as a helper function or a small script:

```text
project_os/reporting.py
```

or:

```text
scripts/build_research_os_v2_report.py
```

Preferred output:

```text
logs/project_os/research_os_v2_overnight_report.md
logs/project_os/research_os_v2_patterns_latest.json
```

The report should include:

1. registry generation time,
2. dashboard generation time,
3. top research moves,
4. top repeat-risk clusters,
5. top positive-but-blocked traps,
6. top failure motifs by family,
7. family gaps,
8. lineage gaps,
9. exact files changed,
10. tests run,
11. browser verification result,
12. residual risks.

Report logic:

- This report is a summary artifact only.
- It must not claim a strategy is live-ready.
- It should cite source node ids/paths where possible.

## Logical Flow Check

The implementation must follow this reasoning chain:

```text
Registry tells us what exists.
Motifs tell us what ideas recur.
Signatures tell us what attempts are near-duplicates.
Blockers tell us why an apparent win is not proof.
Evidence level tells us how mature a result is.
Family gaps tell us where evidence is missing.
Lineage completeness tells us whether the graph explains decisions.
Research moves combine all of the above into next actions.
Atlas and inspector make those moves visually explorable.
Tests and browser QA check that the decision engine is not lying or broken.
```

Common logical mistakes to avoid:

1. Treating high P&L as enough.
   - Correction: high P&L plus blocker becomes "Tempting But Blocked."

2. Treating backtests as strong candidates.
   - Correction: backtest/replay-only is diagnostic or worth watching at most.

3. Inventing new families before classifying existing ones.
   - Correction: show family gaps and formal rejection before novelty.

4. Hiding unclassified scripts.
   - Correction: summarize them, but keep unclassified load visible.

5. Collapsing away health issues.
   - Correction: health/secret/blocker nodes must remain visible.

6. Letting labels or overlays break node selection.
   - Correction: marker trace remains topmost or selectable overlays carry matching `customdata`.

7. Making dashboard refresh mutate research outputs.
   - Correction: refresh rebuilds registry/pattern cache only. No scorers/bots/orders.

8. Mixing live dashboard code with Research OS.
   - Correction: all changes stay in `project_os` or `project_os_dashboard.py`, except tests/docs/report helper.

9. Letting a report summary become stale silently.
   - Correction: show generation time and registry source time.

10. Claiming a family is exhausted.
   - Correction: say "blocked under current assumptions" unless evidence truly proves exhaustion.

11. Trusting stale baseline counts.
   - Correction: regenerate or reload the current registry, then report actual current counts.

12. Treating a subagent's final message as verification.
   - Correction: integrate, review, test, and include the finding in the final changed-file and residual-risk audit.

13. Leaking sensitive local contents through screenshots or reports.
   - Correction: verify sensitive styling and filters without printing raw secret values.

14. Ranking ambiguous P&L above cleaner evidence.
   - Correction: use metric provenance and confidence; evidence maturity and blockers outrank ambiguous numeric values.

## Implementation Phases

### Phase 0: Baseline Verification

Time: 30-45 minutes.

Steps:

1. Confirm current cwd is:

```text
C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT
```

2. Confirm current Research OS dashboard launches on `8503`.
3. Confirm existing dashboard on `8501` is separate.
4. Load current registry.
5. Print node/edge counts.
6. Build default atlas figure in Python without Streamlit.
7. Run existing tests.

Acceptance:

- no import errors,
- registry loads,
- existing tests pass,
- `8501` and `8503` are separate if both running,
- no live bot process touched,
- actual current registry counts are recorded instead of assuming the approximate counts in this spec.

### Phase 1: Pattern Model Hardening

Time: 90-120 minutes.

Files:

- `project_os/patterns.py`
- tests file, preferably `test_project_os_patterns.py`

Add:

- metric normalization and provenance snapshots,
- deterministic motif tagging,
- signature extraction,
- repeat-risk scoring,
- nearest prior detection,
- positive-but-blocked detection,
- failure motif extraction,
- family gap flags,
- lineage completeness,
- research move card generation.

Acceptance:

- all functions are pure registry consumers,
- no direct filesystem crawling,
- repeat-risk rows exist on current registry,
- positive-but-blocked rows exist on current registry,
- family gap rows exist for OU/truffle/ninety/unclassified/live_v28 cases,
- lineage gaps are surfaced but do not crash if edges are sparse.

### Phase 2: UI Decision Engine

Time: 90-120 minutes.

Files:

- `project_os/views/dashboard_views.py`

Add/upgrade:

- Research Moves cards,
- Motif Heatmap,
- Winning Motifs,
- Do Not Repeat Blindly,
- Tempting But Blocked,
- Family Gap Matrix,
- Lineage Gaps,
- Candidate Inspector pattern panel.

Acceptance:

- sections render in one page,
- tables are not too tall by default,
- wording is plain English,
- warnings do not imply live readiness,
- source node labels are visible,
- current top traps are visible.

### Phase 3: Atlas Art And Lenses

Time: 60-90 minutes.

Files:

- `project_os/graph.py`
- `project_os/views/dashboard_views.py`

Add/upgrade:

- Repeat Risk lens,
- Frontier Gaps lens,
- Failure Motifs lens if time allows,
- family region readability,
- selected-neighborhood readability,
- label placement,
- label clickability if feasible,
- hover text with motifs/signature/primary blocker.

Acceptance:

- graph remains nonblank,
- modebar hidden,
- trace count remains reasonable,
- label overlays do not break selection,
- default graph is readable,
- filters still work.

### Phase 4: Report Generation

Time: 45-75 minutes.

Files:

- `project_os/reporting.py` or `scripts/build_research_os_v2_report.py`
- `logs/project_os/research_os_v2_overnight_report.md`
- `logs/project_os/research_os_v2_patterns_latest.json`

Acceptance:

- report writes without running scorers/bots,
- report cites generated time and registry time,
- report includes top moves, traps, repeat clusters, family gaps, lineage gaps,
- report says research-only,
- report includes tests/browser checks run.

### Phase 5: Tests

Time: 60-90 minutes.

Add tests for:

1. metric normalization and ambiguous P&L handling,
2. motif tagging,
3. repeat-risk signature determinism,
4. positive-but-blocked detection,
5. blocked positive P&L not counted as strong,
6. backtest/replay-only not strong,
7. family gap flags,
8. lineage gap detection,
9. research move lane assignment,
10. graph collapse keeps health/candidates/families,
11. sensitive/health/archive/unknown nodes remain visible or filterable as intended,
12. dashboard import has no side effects.

Acceptance:

- existing tests pass,
- new tests pass,
- tests do not require live API,
- tests do not require running Streamlit,
- tests cover at least one ambiguous or missing metric case.

### Phase 6: Browser QA

Time: 45-60 minutes.

Use the in-app browser or equivalent browser automation.

Verify:

- `http://127.0.0.1:8503/` loads,
- no Streamlit exceptions,
- no CSS text leak,
- local-only sensitive warning visible,
- sensitive nodes are marked and hideable,
- graph nonblank,
- Pattern Cartography visible,
- Research Moves visible,
- Repeat Risk lens selectable,
- Tempting But Blocked visible,
- Lineage Gaps visible,
- Candidate Inspector visible,
- modebar hidden,
- existing dashboard on `8501` remains separate.
- manual refresh does not run scorers, bots, live collectors, order code, or archival actions.

If screenshot capture is flaky, use DOM/SVG checks:

- `.js-plotly-plot` count,
- `.point` count,
- body text contains sections,
- error count is zero,
- modebar is hidden.

Manual-refresh verification should use code review plus browser behavior. It is acceptable to verify by checking callbacks and changed files rather than clicking refresh repeatedly if a live bot is running nearby.

## Test Fixtures

Add lightweight unit fixtures rather than copying real large reports.

Fixture cases:

### Positive Blocked

Node:

- kind `report`,
- family `v28_successor`,
- status `blocked`,
- evidence `forward_shadow`,
- metrics `{"net_pnl": 1739.7, "markets": 24}`,
- blocker `"does_not_beat_v28_brier"`.

Expected:

- appears in positive-but-blocked,
- not in test-next as ready,
- recommendation says do not rerun unchanged.

### Backtest Only

Node:

- kind `report`,
- family `ou_mispricing`,
- status `diagnostic_only`,
- evidence `backtest`,
- metrics positive.

Expected:

- diagnostic/frontier/validate, not strong,
- next action requires forward evidence.

### Duplicate Locked Plans

Nodes:

- three candidate nodes with similar labels and motifs,
- same family,
- same forward/OOS evidence,
- statuses blocked/needs_more_proof.

Expected:

- repeat-risk cluster size 3,
- nearest prior populated,
- repeat warning if no changed assumption detected.

### Family Gap

Family:

- reports exist,
- no candidates,
- no forward evidence.

Expected:

- flags `NO_CANDIDATE`, `NO_FORWARD_EVIDENCE`,
- next move says name candidate or collect forward evidence.

### Lineage Gap

Node:

- blocked report,
- no `blocks` or `rejects` edge.

Expected:

- appears in lineage gaps.

### Ambiguous Metric Unit

Node:

- kind `report`,
- family `rv600`,
- status `worth_watching`,
- evidence `replay`,
- metrics contain both `gross_pnl` and a string `net_pnl` with no clear unit.

Expected:

- display includes raw metric provenance,
- P&L confidence is not high,
- sorting does not place it above clearer live/forward evidence,
- no readiness or strong-candidate claim appears.

### V1 Visibility Preservation

Nodes:

- one `health_issue`,
- one `unknown`,
- one `archive`,
- one `secret` or sensitive node.

Expected:

- all are represented in registry-derived UI surfaces,
- health and unknown remain visible by default,
- archive remains visible by default,
- sensitive node is visibly marked,
- sensitive node can be hidden by filter,
- no raw secret value appears in generated report text.

## Acceptance Criteria

### Functional Acceptance

1. Research OS dashboard launches on `8503`.
2. Existing live dashboard remains available on `8501` if it was already running.
3. No live bot/order/scorer logic changed.
4. Registry loads successfully.
5. Pattern analysis runs from registry only.
6. Dashboard shows Pattern Cartography V2.
7. Dashboard shows Research Moves.
8. Dashboard shows repeat-risk clusters.
9. Dashboard shows positive-but-blocked traps.
10. Dashboard shows failure motifs or at least blocker motif summaries.
11. Dashboard shows family gap matrix.
12. Dashboard shows lineage gaps.
13. Candidate Inspector shows nearest prior/sibling or says none found.
14. Repeat Risk lens exists.
15. Health issues remain visible in atlas/health surfaces.
16. Unknown and archived artifacts remain visible by default.
17. Sensitive nodes remain marked, warning-bannered, and hideable.
18. Manual refresh remains registry-only and does not launch bots/scorers/orders.
19. Browser QA shows no Streamlit errors.

### Logical Acceptance

1. Positive P&L plus blocked status remains blocked.
2. Replay/backtest-only never becomes strong.
3. Diagnostic-only remains diagnostic unless forward/live evidence exists.
4. New family recommendations are framed as frontier gaps, not inventions.
5. Existing candidates and motifs are ranked before novelty.
6. Repeat-risk warnings require a changed assumption before retesting.
7. Lineage gaps do not pretend to be blocker conclusions.
8. Family gap flags are descriptive, not claims of failure.
9. P&L unit handling is explicit for cents versus dollars.
10. All morning recommendations cite source nodes or motif rows.
11. Ambiguous metrics reduce confidence rather than silently becoming proof.
12. Positive ambiguous P&L can create a warning, but cannot create a strong recommendation.

### UX Acceptance

1. One-page dashboard remains scannable.
2. Atlas remains the first major visual component.
3. Pattern Cartography is easy to find below the atlas.
4. Tables have readable heights and do not overwhelm the page.
5. Warnings are visually distinct.
6. "Do Not Repeat" and "Tempting But Blocked" are hard to miss.
7. Labels do not visibly overlap into unreadable noise in default view.
8. The inspector is actionable, not just raw metadata.

### Verification Acceptance

Run:

```powershell
python -m compileall project_os project_os_dashboard.py test_project_os_registry.py
python -m unittest test_project_os_registry.py -v
```

If new tests are added:

```powershell
python -m unittest test_project_os_registry.py test_project_os_patterns.py -v
```

Verify browser:

```text
URL: http://127.0.0.1:8503/
error count: 0
graph present: yes
Pattern Cartography present: yes
Research Moves present: yes
Tempting But Blocked present: yes
Lineage Gaps present: yes
Repeat Risk lens present: yes
local-only sensitive warning: yes
sensitive hide filter: yes
manual refresh registry-only: yes
modebar hidden: yes
CSS leak: no
```

Verify process separation:

```powershell
Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8501,8503 -State Listen
```

Verify changed-file safety:

```powershell
git diff --name-only
```

If the workspace is not a Git checkout, perform an equivalent changed-file audit from timestamps and the final report. The changed-file list should be limited to `project_os`, `project_os_dashboard.py`, tests, docs, and `logs/project_os` report/cache outputs unless the user explicitly approved something broader.

## Suggested Morning Report Shape

The final overnight response should be concise, but the report artifact should be detailed.

Final chat answer should include:

```text
Implemented Research OS V2 strategy-memory sprint.

Changed:
- ...

Current registry-derived signals:
- repeat-risk clusters: N
- positive-but-blocked traps: N
- family gaps: N
- lineage gaps: N
- top research move: ...

Verified:
- tests
- browser
- process separation

Report:
- logs/project_os/research_os_v2_overnight_report.md
```

The report file should include more detail:

```text
# Research OS V2 Overnight Report

## Summary
## Top Research Moves
## Do Not Repeat
## Tempting But Blocked
## Winning Motifs
## Family Gaps
## Lineage Gaps
## Files Changed
## Tests Run
## Browser QA
## Residual Risks
```

## Risk Register

### Risk: False Confidence From Positive P&L

Mitigation:

- Positive-but-blocked table.
- Inspector warning.
- Logic tests.

### Risk: Over-Collapsing Graph Detail

Mitigation:

- Keep candidates/families/health/stats visible.
- Filters can expose detail.
- Inspector shows collapsed summary.

### Risk: Pattern Heuristics Become Too Clever

Mitigation:

- Label all motif/signature inference as heuristic.
- Show source nodes.
- Avoid readiness claims.

### Risk: Stale Registry

Mitigation:

- Show registry generation time.
- Report cites registry time.
- Manual refresh available.

### Risk: Browser Screenshot Flakes

Mitigation:

- DOM/SVG verification accepted.
- Do not block on screenshots if DOM verifies rendering.

### Risk: Too Much Dashboard Density

Mitigation:

- Keep raw tables in drawers.
- Use cards for research moves.
- Use compact heights.
- Keep atlas dominant.

### Risk: Accidentally Touching Live System

Mitigation:

- Scope files to `project_os`, tests, docs, `logs/project_os`.
- No live bot commands.
- No scorer behavior changes.
- Verify `8501` remains separate.

## Stretch Goals If Time Remains

Only attempt after core acceptance criteria pass.

1. Add a `Strategy Memory` search mode:
   - search by motif, blocker, family, nearest prior.

2. Add a `Why Not Repeat?` mini-inspector:
   - for selected node, show the exact sibling attempts and blockers.

3. Add edge enrichment:
   - create inferred `blocks`, `rejects`, `supersedes`, or `similar_to` edges in memory only.

4. Add cluster badges to atlas nodes:
   - repeat count,
   - positive blocked flag,
   - lineage gap flag.

5. Add pattern JSON cache:
   - `logs/project_os/research_os_v2_patterns_latest.json`.

6. Add an "assumption delta" detector:
   - show whether the proposed next candidate actually differs from prior siblings.

7. Add family-specific playbooks:
   - RV600,
   - v28 successor,
   - live_v28,
   - OU mispricing,
   - truffle,
   - ninety_touch.

8. Add a "candidate completeness" checklist:
   - entry,
   - exit,
   - sizing,
   - risk,
   - kill rule,
   - live-test rule,
   - accounting,
   - P&L rule,
   - iteration rule.

## Final Logic Review

The overnight worker should pause before final response and check:

1. Did I use existing candidates first?
2. Did I avoid making up new broad families without evidence?
3. Did I keep live bot logic untouched?
4. Did I keep scorer/order behavior untouched?
5. Did I distinguish P&L from proof?
6. Did I distinguish diagnostic/backtest from forward/live evidence?
7. Did I make repeat-risk visible?
8. Did I make positive-but-blocked traps visible?
9. Did I make family gaps visible?
10. Did I make lineage gaps visible?
11. Did I run tests?
12. Did I verify browser rendering?
13. Did I verify `8501` and `8503` are separate?
14. Did I write or update a morning report?
15. Did I summarize residual risks honestly?
16. Did I preserve V1 invariants: manual refresh only, unknown/archive visibility, health visibility, sensitive marking/filtering, local-only warning, and registry-first views?
17. Did I audit changed files and confirm no live/scorer/order/secret/state file was unintentionally touched?
18. Did I integrate or explicitly defer every subagent finding?
19. Did I check metric units/provenance and prevent ambiguous P&L from becoming proof?
20. Completion gate: do not mark the goal complete until every required item in this spec, including all implementation phases, logical constraints, acceptance criteria, test fixtures, browser QA checks, V1 non-regression invariants, changed-file safety audit, subagent integration checks, metric/provenance checks, and bug-fix follow-ups discovered during the work, has been implemented where applicable, tested, checked for calculation errors, checked for UI/interaction bugs, and either passed or been explicitly documented as an unresolved residual gap.

If any answer is no, finish that item before claiming completion. The goal may only be closed when item 20 is true; otherwise the final response must say exactly what remains unfinished, what was tested, what failed, and what still needs another pass.
