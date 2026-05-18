# Research OS V2: Candidate Foundry And Discovery Engine Spec

## Purpose

This spec defines an ambitious 8-hour implementation sprint for a new Research OS feature set focused on finding **new, testable strategy candidates** without drifting into random idea generation or accidental live-system changes.

The existing Research OS V2 Strategy Memory spec is about seeing what already exists, avoiding repeated mistakes, and turning the dashboard into a project atlas. This spec adds the next layer: a **Candidate Foundry** that uses the registry, evidence graph, failure motifs, family gaps, lineage, and existing candidate history to propose well-formed next candidates.

The goal is not "invent lots of ideas." The goal is:

- discover candidate opportunities hidden in existing logs, reports, scripts, docs, stats, and research data,
- convert those opportunities into complete candidate drafts,
- prove that each draft differs meaningfully from prior failed or blocked siblings,
- rank drafts by evidence quality, novelty, feasibility, and research value,
- create a validation queue that can be tested later without ambiguity,
- prevent broad family sprawl by grounding every candidate in source artifacts and explicit assumptions.

The output of this sprint should be a dashboard and report where the user can answer:

```text
What should we test next, why is it actually new, what evidence inspired it, what killed nearby siblings, and what exact proof would make it worth continuing?
```

## Pointer Goal

Use this exact short goal when starting the 8-hour candidate-discovery run:

```text
/goal Use subagents for an 8-hour research-only sprint implementing docs/research/RESEARCH_OS_V2_CANDIDATE_FOUNDRY_SPEC.md. Build a Candidate Foundry inside the separate Research OS dashboard on 8503 that discovers new testable strategy candidates from the existing registry, reports, stats, scripts, docs, datasets, blockers, and strategy-memory patterns. Implement opportunity mining, candidate genomes, assumption-delta checks, nearest-failed-sibling checks, candidate draft cards, validation recipes, discovery scoring, anti-sprawl gates, a candidate queue, dashboard views, report output, tests, browser QA, and the final completion gate. Do not touch live bot logic, order logic, scorer behavior, thresholds, secrets, live trading state, or the existing 8501 dashboard. Work only on project_os modules, project_os_dashboard.py, tests, docs, and logs/project_os outputs. Do not mark complete until every required item in this spec has been implemented where applicable, tested, checked for calculation/UI bugs, and either passed or documented as a residual gap.
```

## Relationship To The Strategy Memory Spec

This spec complements:

```text
docs/research/RESEARCH_OS_V2_STRATEGY_MEMORY_DECISION_ENGINE_SPEC.md
```

The Strategy Memory spec answers:

- What exists?
- What worked?
- What failed?
- What should not be repeated?
- How do all artifacts connect?

This Candidate Foundry spec answers:

- What new candidate should be formulated next?
- What exact prior evidence inspired it?
- What exact prior failure does it avoid?
- What changed assumption makes it non-duplicative?
- What validation recipe would be fair?
- What kill rule would stop it fast?
- What would count as moderate proof?

If both specs exist, Strategy Memory should be treated as the base layer and Candidate Foundry as the proposal layer. Candidate Foundry must consume registry and strategy-memory outputs when available, but it should degrade gracefully if some pattern functions are missing.

## Absolute Guardrails

These are hard constraints.

1. Research-only work.
2. Do not place trades.
3. Do not modify live bot logic.
4. Do not modify order placement logic.
5. Do not modify scorer behavior used outside Research OS.
6. Do not modify thresholds used by live or shadow bots.
7. Do not stop, restart, or mutate the live bot.
8. Do not edit secrets.
9. Do not move, delete, archive, or rewrite research artifacts.
10. Do not write candidate conclusions into `stats/*` or `logs/particle_research/*` source evidence folders.
11. Keep the existing dashboard on `127.0.0.1:8501` unchanged.
12. Keep Candidate Foundry inside the separate Research OS dashboard on `127.0.0.1:8503`.
13. Manual refresh must not launch bots, scorers, collectors, order code, backtests, or archival jobs.
14. Candidate drafts are not deployment approvals.
15. Backtest/replay evidence alone cannot produce a "test live" recommendation.
16. Positive P&L alone cannot produce a candidate recommendation if blockers remain unresolved.
17. A new broad strategy family is allowed only when existing families have been classified and the gap is explicit.
18. Every proposed candidate must cite source nodes or say it lacks enough provenance.
19. Every proposed candidate must include a changed-assumption explanation or be marked duplicate-risk.
20. If the system cannot prove why a candidate is different from failed siblings, it should recommend classification or repair, not testing.

## Strategic Philosophy

The Candidate Foundry should behave like a disciplined research lead.

It should be imaginative, but not sloppy.

It should prefer:

- nearby variants with changed assumptions over random new families,
- evidence-backed gaps over novelty for novelty's sake,
- forward/shadow validation plans over replay-only excitement,
- complete candidate systems over isolated entry rules,
- rejection and triage over endless expansion,
- small crisp validation recipes over giant vague sweeps.

It should reject:

- "same idea again with a new name,"
- positive-but-blocked traps,
- high P&L with hidden concentration,
- backfill winners with no forward plan,
- candidate cards missing exit, risk, sizing, kill, or accounting,
- recommendations that cannot cite source artifacts.

## Candidate Definitions

### Raw Signal

A raw signal is any registry-derived clue that might inspire a candidate.

Examples:

- positive-but-blocked report,
- family with many scripts but no frozen candidate,
- repeated blocker motif with one missing control,
- stats node with favorable shape but stale evidence,
- dataset with good coverage but no linked plan,
- docs mentioning an untested condition,
- script cluster around a motif with no report,
- archive containing old idea with no modern evidence.

### Opportunity

An opportunity is a raw signal promoted into a research gap or possible move.

An opportunity must have:

- family,
- motif,
- source nodes,
- evidence level,
- blocker context,
- why it may matter,
- why it may be dangerous,
- recommended research move.

### Candidate Draft

A candidate draft is a structured proposal for a possible strategy candidate.

A candidate draft is not a strategy implementation.

It must include:

- candidate id,
- plain-English name,
- family,
- source evidence,
- entry hypothesis,
- exit hypothesis,
- sizing rule,
- risk control,
- kill rule,
- validation recipe,
- accounting rule,
- P&L rule,
- expected failure mode,
- changed assumption versus nearest prior,
- duplicate-risk score,
- evidence requirements before continuing.

### Frozen Candidate

A frozen candidate is a candidate draft that is specific enough to test without moving the target later.

Frozen does not mean good.

Frozen means:

- entry condition is defined,
- exit condition is defined,
- sizing is defined,
- fees/accounting are defined,
- de-duplication is defined,
- baseline comparison is defined,
- forward/shadow evaluation window is defined,
- kill rule is defined,
- no retrospective threshold changes are allowed inside the validation window.

### Validation Recipe

A validation recipe is the smallest fair next test for a candidate.

It must answer:

- what data to use,
- what baseline to compare,
- what sample size or market count is minimally useful,
- what metrics matter,
- what blockers would fail it,
- what would move it from draft to watch,
- what would reject it,
- what not to change during the test.

### Candidate Queue

The candidate queue is a ranked list of proposed drafts and validation recipes.

It is a planning artifact only.

It must not:

- launch tests,
- change bot behavior,
- modify live state,
- claim readiness.

## Desired Morning Outcome

By morning, opening `http://127.0.0.1:8503/` should reveal a Candidate Foundry section where the user can answer the following in under five minutes:

1. What are the top 5 new candidate drafts worth considering?
2. Which candidate drafts are descendants of existing families?
3. Which candidate drafts are true frontier ideas and why are they justified?
4. Which candidates are near-duplicates of blocked siblings?
5. Which candidates were rejected by the Foundry before reaching the queue?
6. Which source artifacts inspired each candidate?
7. Which blockers from prior attempts does each candidate explicitly avoid?
8. Which validation recipe is the smallest fair proof for each candidate?
9. Which candidate has the best combination of evidence, novelty, feasibility, and coverage?
10. Which idea should not be tested because it is just a renamed old failure?
11. Which families are underdeveloped enough to deserve new candidates?
12. Which families are overworked and should receive no new variants until evidence improves?
13. What exact changed assumption makes the top candidate different?
14. What kill rule stops the top candidate if it is wrong?
15. What does the next research session do first?

## Eight-Hour Work Budget

This should be sized as a genuine 7-9 hour sprint.

### Estimated Schedule

1. Baseline orientation and registry load: 30-45 minutes
2. Opportunity mining model: 75-90 minutes
3. Candidate genome and assumption-delta model: 90-120 minutes
4. Candidate draft generation and scoring: 90-120 minutes
5. Candidate Foundry dashboard views: 90-120 minutes
6. Candidate queue and report outputs: 45-75 minutes
7. Tests and logic audit: 60-90 minutes
8. Browser QA and final completion audit: 45-60 minutes

Expected total: 7-9 hours.

If time runs short, prioritize:

1. opportunity mining,
2. candidate draft schema,
3. assumption-delta and nearest-failed-sibling checks,
4. dashboard candidate cards,
5. tests,
6. browser QA,
7. completion gate.

Visual polish is valuable, but it is secondary to producing logically safe candidate drafts.

## Subagent Plan

Use subagents with distinct scopes. Do not duplicate work between agents.

### Subagent A: Evidence And Opportunity Miner

Purpose:

- inspect registry nodes, reports, stats, docs, datasets, scripts, and health issues,
- identify opportunity types and source evidence.

Focus:

- positive-but-blocked patterns,
- families with evidence gaps,
- script clusters with no candidate,
- datasets with no linked plan,
- docs with untested hypotheses,
- archived ideas that may deserve reclassification,
- high-signal stats/report motifs.

Expected output:

- opportunity categories,
- example current opportunities,
- source node ids/paths,
- implementation notes for `project_os/discovery.py`.

### Subagent B: Candidate Genome And Assumption Delta

Purpose:

- define how candidate drafts should encode the full strategy system.

Focus:

- entry rule,
- exit rule,
- sizing rule,
- risk control,
- kill rule,
- validation rule,
- accounting rule,
- P&L rule,
- iteration rule,
- changed assumption versus nearest prior.

Expected output:

- candidate schema recommendations,
- assumption-delta scoring ideas,
- examples of duplicate-risk versus genuinely changed candidates.

### Subagent C: Anti-Sprawl And Logic Audit

Purpose:

- prevent the Foundry from becoming a random idea generator.

Focus:

- false novelty,
- overfit replay/backtest winners,
- ambiguous P&L units,
- positive-but-blocked traps,
- new broad family justification,
- ranking logic,
- readiness language,
- source provenance.

Expected output:

- findings with file/line references if code exists,
- test cases,
- wording corrections.

### Subagent D: Dashboard UX And Browser QA

Purpose:

- make the Candidate Foundry easy to use inside the Research OS dashboard.

Focus:

- candidate cards,
- opportunity radar,
- validation queue,
- "why different?" panel,
- filters,
- no Streamlit errors,
- no text overflow,
- graph/dashboard integration,
- modebar and CSS behavior,
- sensitive content not leaked in screenshots/reports.

Expected output:

- UI recommendations or patch,
- browser verification facts,
- residual UX risks.

### Subagent Integration Rules

The primary worker must:

1. assign distinct scopes,
2. integrate useful findings,
3. reject unsafe findings,
4. avoid overlapping file edits where possible,
5. test integrated work,
6. list deferred findings in the report,
7. retain responsibility for the final completion gate.

Subagent completion is not project completion.

## Architecture

Use registry-first architecture.

Correct flow:

```text
workspace artifacts
  -> adapters
  -> ProjectRegistry
  -> Strategy Memory patterns if available
  -> opportunity mining
  -> candidate genome extraction
  -> assumption-delta checks
  -> candidate draft generation
  -> discovery scoring and queueing
  -> dashboard views and report outputs
```

Incorrect flow:

```text
dashboard widget
  -> direct filesystem scan
  -> one-off idea text
  -> uncited candidate recommendation
```

### Files To Add Or Modify

Preferred new files:

```text
project_os/discovery.py
project_os/candidate_schema.py
project_os/views/candidate_foundry.py
test_project_os_discovery.py
logs/project_os/candidate_foundry_latest.json
logs/project_os/candidate_foundry_YYYYMMDDTHHMMSSZ.json
logs/project_os/candidate_foundry_report_latest.md
docs/research/RESEARCH_OS_V2_CANDIDATE_FOUNDRY_SPEC.md
```

Allowed existing files:

```text
project_os_dashboard.py
project_os/views/dashboard_views.py
project_os/patterns.py
project_os/graph.py
project_os/reporting.py
project_os/models.py
```

Only modify existing files when needed to wire the Foundry into Research OS. Keep edits scoped.

Not allowed:

```text
kalshi_btc15m_bot_ws.py
live bot launch scripts
order code
scorer behavior used outside dashboard
state/*
stats/*
logs/particle_research/*
secrets
.env
```

## Core Data Models

These can be dataclasses, dictionaries, or light models consistent with the existing code style.

### `Opportunity`

Fields:

```text
id
family
motifs
kind
title
source_node_ids
source_paths
evidence_level
status_context
metrics_snapshot
blockers
why_interesting
why_dangerous
recommended_move
confidence
created_at_utc
```

Opportunity kinds:

```text
positive_blocked_trap
underdeveloped_family
script_cluster_no_candidate
dataset_no_candidate
report_no_validation
stale_promising_stats
lineage_gap
blocker_motif_gap
archived_possible_revisit
frontier_gap
existing_candidate_extension
```

### `CandidateGenome`

Fields:

```text
family
motifs
entry_tokens
exit_tokens
sizing_tokens
risk_tokens
kill_tokens
accounting_tokens
validation_tokens
baseline_tokens
evidence_tokens
blocker_tokens
data_source_tokens
time_horizon_tokens
market_scope_tokens
```

Purpose:

- describe a candidate in comparable pieces,
- support nearest-sibling and duplicate-risk checks,
- make missing candidate components obvious.

### `AssumptionDelta`

Fields:

```text
nearest_prior_id
nearest_prior_label
similarity
same_family
shared_motifs
changed_entry
changed_exit
changed_sizing
changed_risk
changed_data_source
changed_validation
changed_accounting
changed_baseline
changed_assumption_summary
duplicate_risk
warning
```

Duplicate-risk levels:

```text
low
medium
high
unknown
```

Rules:

- same family plus same motifs plus no changed entry/exit/risk/accounting means high duplicate risk,
- changed label alone is not a changed assumption,
- changed timestamp alone is not a changed assumption,
- changed sample window alone is weak unless the validation recipe says why,
- adding forward proof to a replay-only idea is a meaningful validation change,
- adding risk control to a concentration-blocked idea is a meaningful design change,
- changing only thresholds after seeing results is duplicate/overfit risk unless pre-registered.

### `CandidateDraft`

Fields:

```text
id
title
family
origin_type
source_opportunity_ids
source_node_ids
motifs
entry_rule
exit_rule
sizing_rule
risk_control
kill_rule
validation_recipe
accounting_rule
pnl_rule
baseline_rule
data_requirements
minimum_sample
expected_failure_mode
nearest_prior
assumption_delta
duplicate_risk
evidence_level
blockers_to_clear
discovery_score
confidence
status
warnings
next_action
```

Statuses:

```text
draft
needs_classification
duplicate_risk
needs_more_source_evidence
ready_to_freeze
validation_ready
blocked
rejected
frontier_gap
```

Important:

- `validation_ready` means ready for a research validation recipe, not ready for live trading.
- `ready_to_freeze` means the card is specific enough to become a frozen test plan after human review.
- `frontier_gap` means a new or thin family may deserve exploration, not that a candidate exists.

### `ValidationRecipe`

Fields:

```text
id
candidate_id
data_scope
market_scope
time_window
sample_target
baseline
fee_model
fillability_check
dedup_rule
metrics
pass_conditions
fail_conditions
kill_conditions
do_not_change
outputs_expected
manual_review_required
```

### `CandidateQueue`

Fields:

```text
generated_at_utc
registry_source
registry_generated_at_utc
opportunity_count
draft_count
queue_items
rejected_drafts
warnings
tests_run
browser_qa
```

Queue item fields:

```text
rank
candidate_id
title
lane
family
discovery_score
confidence
duplicate_risk
evidence_level
why_now
next_action
source_node_ids
```

Queue lanes:

```text
Freeze Next
Validate Next
Repair Before Candidate
Do Not Repeat
Frontier Explore
Archive/Ignore
```

## Discovery Scoring

Candidate Foundry should rank candidates using a transparent score.

Suggested fields:

```text
evidence_score
novelty_score
feasibility_score
coverage_score
blocker_clearance_score
lineage_score
source_confidence_score
anti_sprawl_penalty
duplicate_risk_penalty
metric_ambiguity_penalty
```

Suggested formula:

```text
discovery_score =
  0.20 * evidence_score
  + 0.15 * novelty_score
  + 0.15 * feasibility_score
  + 0.15 * coverage_score
  + 0.15 * blocker_clearance_score
  + 0.10 * lineage_score
  + 0.10 * source_confidence_score
  - 0.15 * duplicate_risk_penalty
  - 0.10 * anti_sprawl_penalty
  - 0.10 * metric_ambiguity_penalty
```

Clamp final score to `0.0` through `1.0`.

Logical constraints:

- blocked positive P&L cannot produce a top queue item unless the candidate explicitly changes the blocker-causing assumption,
- replay/backtest-only evidence cannot produce `Validate Next` unless the validation recipe is forward/shadow and the card says proof is missing,
- metadata-only evidence can produce `Repair Before Candidate`, not `Freeze Next`,
- high novelty with low provenance should be `Frontier Explore` or `needs_more_source_evidence`,
- high duplicate risk should be `Do Not Repeat` unless changed assumption is explicit,
- evidence score should outrank novelty when sorting validation-ready cards,
- coverage score should penalize one-market or one-root concentration,
- source confidence should penalize ambiguous metrics, stale registry, malformed source, or missing lineage.

## Required Implementation Areas

### 1. Add `project_os/discovery.py`

Implement pure registry-consuming functions.

Required functions:

```python
def build_opportunities(registry, patterns=None) -> list[dict]: ...
def candidate_genome(node_or_row) -> dict: ...
def compare_candidate_genomes(a: dict, b: dict) -> dict: ...
def assumption_delta_for_opportunity(opportunity, registry, patterns=None) -> dict: ...
def generate_candidate_drafts(registry, patterns=None) -> list[dict]: ...
def score_candidate_draft(draft: dict) -> dict: ...
def build_candidate_queue(registry, patterns=None) -> dict: ...
def serialize_candidate_foundry(queue: dict, path: Path) -> None: ...
```

Rules:

- no direct filesystem crawl,
- no live API,
- no external network,
- deterministic output for a fixed registry,
- stable ids,
- source-node citations on every opportunity/draft when available,
- graceful fallback if `patterns.py` does not expose all Strategy Memory helpers.

### 2. Opportunity Mining

The Foundry should mine these opportunity classes.

#### Positive-Blocked Design Fix

Input:

- positive P&L report,
- status blocked/rejected/diagnostic,
- blocker text or failure motif.

Candidate direction:

- not "rerun this",
- instead "create a variant that directly addresses blocker X."

Examples:

- concentration blocker -> candidate must include market/root concentration cap,
- matched-v28 failure -> candidate must define baseline-beating rule,
- low positive market fraction -> candidate must define broader coverage or stronger entry filter,
- source-quality blocker -> candidate must define stricter fillability/source-quality gate,
- stale stats -> candidate must define refresh/forward proof step.

#### Underdeveloped Family Gap

Input:

- family has artifacts but no candidate,
- family has docs/scripts but no forward evidence,
- family has datasets but no report,
- family has reports but no validation recipe.

Candidate direction:

- create a draft that names the missing test shape,
- or classify as `Repair Before Candidate`.

#### Script Cluster With No Candidate

Input:

- root scripts such as `probe_*`, `build_*`, `score_*`, `audit_*`, `backtest_*`, `validate_*`, `train_*`,
- shared motif/family naming,
- no linked candidate/report.

Candidate direction:

- infer candidate family and purpose,
- propose a candidate only if a coherent entry/exit/risk hypothesis can be inferred,
- otherwise create lineage repair item.

#### Dataset Without Candidate

Input:

- research dataset or manifest,
- recorder status,
- schema/coverage,
- no linked candidate or report.

Candidate direction:

- propose data-readiness/validation candidate,
- or classify as data repair.

#### Archived Possible Revisit

Input:

- archived family or handoff folder,
- older idea with missing modern validation,
- current family gap matches old idea.

Candidate direction:

- only revive if changed environment or missing proof is explicit,
- otherwise keep archived.

#### Cross-Family Motif Transfer

Input:

- motif succeeds or remains promising in one family,
- another family fails from a blocker that motif may address.

Candidate direction:

- propose a transfer candidate, such as applying a risk-control motif to a different entry family.

Strict rule:

- motif transfer is not allowed to claim proof from the source family. It only suggests a research hypothesis.

#### Negative-Space Candidate

Input:

- obvious absence in family matrix,
- no candidate where artifacts imply one should exist,
- recurrent blocker with no tested mitigation.

Candidate direction:

- propose the smallest candidate that fills the gap.

Strict rule:

- negative-space candidates have low evidence score and must be framed as frontier/repair unless source evidence is strong.

### 3. Candidate Genome Extraction

Candidate genome extraction should work for:

- candidate nodes,
- report nodes,
- stats nodes,
- locked plan nodes,
- docs,
- scripts,
- opportunity rows.

Use:

- label,
- id,
- family,
- kind,
- status,
- evidence level,
- tags,
- blockers,
- summary,
- raw preview when present,
- metric keys,
- source adapter,
- path.

Extract:

- motifs,
- candidate type,
- entry hints,
- exit hints,
- risk hints,
- sizing hints,
- accounting hints,
- data source hints,
- validation hints,
- baseline hints,
- blocker hints.

Do not overclaim precision. If the genome is incomplete, mark missing pieces.

### 4. Assumption Delta Engine

For every candidate draft:

1. find nearest prior candidates/reports/stats/plans,
2. compute similarity,
3. identify changed assumptions,
4. identify unchanged assumptions,
5. decide duplicate-risk level,
6. require an explicit "why different" note.

Output should include:

```text
Nearest prior: ...
Similarity: ...
Shared motifs: ...
Changed assumption: ...
Still same: ...
Duplicate risk: ...
Decision: freeze, validate, repair, do not repeat, frontier.
```

Logical checks:

- a threshold tweak is weak delta unless pre-registered,
- a new sample window is weak delta unless justified,
- a new risk control is strong delta if prior blocker was risk/concentration,
- a new baseline rule is strong delta if prior blocker was failure to beat baseline,
- new forward/shadow recipe is strong delta if prior evidence was replay/backtest only,
- changed name alone is no delta,
- missing nearest prior should produce lower confidence, not automatic novelty.

### 5. Candidate Draft Generation

Draft generation should be deterministic and templated, not free-form chaos.

Generate candidates from:

- top opportunities,
- existing candidate extensions,
- family gaps,
- blocker motifs,
- cross-family motif transfers,
- lineage gaps only when enough source evidence exists.

Candidate draft template:

```text
Title:
Family:
Origin:
Source evidence:
Motifs:
Hypothesis:
Entry rule:
Exit rule:
Sizing rule:
Risk control:
Kill rule:
Accounting rule:
P&L rule:
Baseline:
Validation recipe:
Minimum sample:
Expected blocker:
Nearest prior:
Changed assumption:
Duplicate risk:
Why now:
Why not repeat blindly:
Next action:
Status:
```

Rules:

- if entry rule is missing, status `needs_classification`,
- if exit rule is missing, status `needs_classification`,
- if risk/kill rule is missing, status `needs_classification`,
- if accounting rule is missing, status `needs_classification`,
- if source nodes are missing, status `needs_more_source_evidence`,
- if duplicate risk is high and changed assumption missing, lane `Do Not Repeat`,
- if candidate is complete but needs human review, lane `Freeze Next`,
- if candidate is complete and validation recipe is forward/shadow, lane `Validate Next`,
- if candidate is broad but justified by gap, lane `Frontier Explore`.

### 6. Validation Recipe Builder

Every queued candidate should have a validation recipe.

Validation recipe requirements:

- data source,
- market scope,
- time horizon,
- sample target,
- baseline,
- fees/accounting,
- fillability/source-quality checks,
- de-duplication,
- metrics,
- pass conditions,
- fail conditions,
- kill conditions,
- outputs expected,
- do-not-change list.

Pass condition examples:

- positive net after fees,
- beats current matched baseline by defined margin,
- not dominated by one market/root,
- enough entries,
- enough positive markets,
- source-quality gate passes,
- no accounting mismatch,
- forward/shadow evidence collected after freeze.

Fail condition examples:

- nonpositive net after fees,
- one-market concentration too high,
- does not beat baseline,
- insufficient entries after collection window,
- fillability fails,
- accounting mismatch,
- repeated blocker motif from nearest prior.

### 7. Candidate Queue

Add a candidate queue artifact:

```text
logs/project_os/candidate_foundry_latest.json
logs/project_os/candidate_foundry_YYYYMMDDTHHMMSSZ.json
```

Contents:

- generation time,
- registry source,
- current counts,
- opportunity rows,
- candidate drafts,
- queue items,
- rejected drafts,
- warnings,
- tests/browser checks if generated after verification.

Do not delete old snapshots.

Manual refresh:

- may rebuild registry and Foundry queue,
- must not run scorers,
- must not launch bots,
- must not run backtests,
- must not mutate evidence folders.

### 8. Dashboard Views

Add a Candidate Foundry section to Research OS.

It should be visible on the same dashboard, below or beside Strategy Memory depending on current layout.

Required panels:

#### Foundry Header

Shows:

- candidate drafts,
- validation-ready count,
- duplicate-risk count,
- frontier count,
- repair-before-candidate count,
- top family gap,
- registry age,
- generated time.

#### Opportunity Radar

A compact map/table of opportunity types.

Columns:

```text
Opportunity
Family
Motifs
Kind
Evidence
Signal
Danger
Source Nodes
Recommended Move
```

UI behavior:

- filter by family,
- filter by opportunity kind,
- filter by evidence level,
- filter by duplicate risk,
- click row to populate candidate draft inspector.

#### Candidate Draft Cards

Cards grouped by lane:

- Freeze Next,
- Validate Next,
- Repair Before Candidate,
- Do Not Repeat,
- Frontier Explore,
- Archive/Ignore.

Each card shows:

- title,
- family,
- discovery score,
- confidence,
- evidence level,
- duplicate risk,
- changed assumption,
- nearest prior,
- next action,
- source count.

Card warnings:

- blocked-positive source,
- ambiguous metric,
- replay/backtest-only,
- high duplicate risk,
- missing exit,
- missing risk,
- missing accounting,
- missing source nodes.

#### Why Different Panel

For selected candidate:

```text
Nearest prior:
What is the same:
What changed:
What blocker this addresses:
What blocker remains:
Duplicate risk:
Decision:
```

This panel is mandatory. A candidate without "why different" is not validation-ready.

#### Candidate Completeness Checklist

For selected candidate:

- entry rule,
- exit rule,
- sizing,
- risk control,
- kill rule,
- validation rule,
- accounting rule,
- P&L rule,
- baseline,
- do-not-change list.

Show pass/missing/ambiguous.

#### Validation Recipe Panel

Shows:

- data scope,
- sample target,
- baseline,
- accounting,
- fillability,
- pass/fail/kill conditions,
- expected outputs.

#### Candidate Source Map

Shows source nodes and edges:

- reports,
- stats,
- scripts,
- docs,
- datasets,
- blockers,
- health issues.

If graph integration is feasible, selected candidate source nodes should highlight in the atlas. If not feasible in 8 hours, show source-node table.

#### Rejected Drafts

Show candidates the Foundry refused to queue.

Reasons:

- duplicate with no changed assumption,
- missing source,
- positive-but-blocked with no blocker fix,
- ambiguous P&L only,
- broad family invented without gap,
- incomplete candidate system.

This is important. The user should see what the system refused, not just what it proposed.

### 9. Atlas Integration

If time allows, add a Foundry lens to the Obsidian-style atlas.

Lens:

```text
Candidate Foundry
```

Visual priorities:

- source opportunity nodes,
- proposed candidate draft summary nodes,
- nearest-prior links,
- blocker nodes,
- family gaps,
- validation-ready queue nodes.

Possible visual grammar:

- candidate draft = bright outlined hex/card-like node,
- validation-ready = green/cyan outer ring,
- duplicate-risk = amber/red warning ring,
- frontier = dotted aura,
- repair-before-candidate = wrench-style glyph if icon system exists,
- rejected draft = dim red crossed marker,
- source evidence edges = solid,
- assumption-delta edges = dashed,
- blocker-addressing edges = warning color.

Constraints:

- keep graph vectorized,
- do not create trace per node,
- preserve clickability,
- keep labels readable,
- do not make the default dashboard unreadable,
- Foundry lens may be optional if dashboard panels cover the core need.

### 10. Report Generator

Create or extend reporting:

```text
logs/project_os/candidate_foundry_report_latest.md
```

The report should include:

1. generation time,
2. registry source and registry time,
3. top candidate drafts,
4. top validation-ready candidates,
5. top repair-before-candidate items,
6. top do-not-repeat items,
7. frontier gaps,
8. rejected drafts and reasons,
9. nearest-prior and changed-assumption summaries,
10. validation recipes,
11. files changed,
12. tests run,
13. browser QA,
14. residual risks.

Report rules:

- no live-readiness claims,
- no raw secrets,
- cite source node ids/paths,
- distinguish generated candidates from existing candidates,
- distinguish forward validation from replay/backtest evidence,
- list deferred subagent findings.

## Logical Flow Check

Implementation must follow this reasoning chain:

```text
Registry tells us what exists.
Strategy Memory tells us what succeeded, failed, repeated, and blocked.
Opportunity mining identifies candidate-worthy gaps and signals.
Candidate genomes make attempts comparable.
Assumption deltas prove whether a draft is meaningfully different.
Candidate completeness prevents isolated entry ideas from pretending to be systems.
Validation recipes define fair proof before testing starts.
Discovery scoring ranks candidates without letting novelty or P&L overwhelm blockers.
Dashboard views make the candidate queue inspectable.
Tests and browser QA verify that the Foundry is not lying or broken.
Completion gate prevents closing until every required check is done.
```

Common logical mistakes to avoid:

1. Mistake: generating many ideas and calling that discovery.
   - Correction: generate fewer, complete, source-cited candidate drafts.

2. Mistake: treating near-duplicate siblings as new candidates.
   - Correction: require changed assumption and nearest-prior comparison.

3. Mistake: turning positive blocked P&L into a top candidate.
   - Correction: only queue it if the new candidate directly addresses the blocker.

4. Mistake: inventing broad new families before existing families are classified.
   - Correction: use frontier-gap lane and justify why existing families are insufficient.

5. Mistake: missing exit/risk/accounting and still recommending validation.
   - Correction: incomplete candidates go to repair/classification.

6. Mistake: ranking ambiguous P&L over cleaner evidence.
   - Correction: use metric provenance and confidence penalties.

7. Mistake: letting dashboard refresh run research jobs.
   - Correction: refresh registry/Foundry only.

8. Mistake: treating replay/backtest as proof.
   - Correction: replay/backtest can inspire, but validation recipe must seek forward/shadow proof.

9. Mistake: hiding rejected ideas.
   - Correction: show rejected drafts and reasons.

10. Mistake: making the UI look pretty but not actionable.
    - Correction: every top candidate card must show next action, changed assumption, and validation recipe.

## Implementation Phases

### Phase 0: Baseline Verification

Time: 30-45 minutes.

Steps:

1. Confirm cwd:

```text
C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT
```

2. Confirm Research OS dashboard is separate on `8503`.
3. Confirm existing dashboard on `8501` is not modified.
4. Load `logs/project_os/registry_latest.json` or build registry through existing Research OS flow.
5. Print current registry counts.
6. Inspect available Strategy Memory helpers in `project_os/patterns.py`.
7. Inspect current dashboard wiring.
8. Run existing tests.

Acceptance:

- no import errors,
- current registry loads,
- actual counts recorded,
- existing tests pass or failures are documented before changes,
- no live process touched.

### Phase 1: Discovery Data Model

Time: 60-90 minutes.

Files:

- `project_os/discovery.py`
- `project_os/candidate_schema.py` if needed
- `test_project_os_discovery.py`

Implement:

- opportunity rows,
- candidate genome rows,
- assumption delta rows,
- draft rows,
- queue rows.

Acceptance:

- deterministic output,
- source-node citation support,
- no filesystem crawling,
- no live API,
- unit fixtures pass.

### Phase 2: Opportunity Mining

Time: 75-90 minutes.

Implement:

- positive-blocked opportunities,
- family-gap opportunities,
- script-cluster opportunities,
- dataset-without-candidate opportunities if registry exposes enough data,
- lineage-gap opportunities,
- cross-family motif-transfer opportunities if pattern data exists,
- rejected/unsafe opportunity reasons.

Acceptance:

- at least several opportunity rows generated on current registry or clear explanation why not,
- every opportunity has source evidence or is downgraded,
- opportunity kinds are visible and countable,
- blocker context appears where available.

### Phase 3: Candidate Draft And Assumption Delta

Time: 90-120 minutes.

Implement:

- candidate draft generation,
- nearest-prior matching,
- assumption-delta explanation,
- duplicate-risk scoring,
- completeness checklist,
- validation recipe builder.

Acceptance:

- every draft has candidate id and source opportunity,
- every draft has nearest-prior result or explicit missing-prior warning,
- every validation-ready draft has entry/exit/sizing/risk/kill/accounting/baseline,
- high duplicate-risk drafts are not in `Validate Next`,
- source-less drafts are downgraded.

### Phase 4: Discovery Scoring And Queue

Time: 60-90 minutes.

Implement:

- discovery scoring,
- queue lanes,
- rejected draft rows,
- JSON snapshot output.

Acceptance:

- queue writes `candidate_foundry_latest.json`,
- timestamped snapshot writes,
- queue includes generated time and registry source,
- ranking is stable for fixed input,
- score components are inspectable,
- rejected drafts are included.

### Phase 5: Dashboard Candidate Foundry

Time: 90-120 minutes.

Files:

- `project_os/views/candidate_foundry.py`
- `project_os/views/dashboard_views.py`
- `project_os_dashboard.py` if needed

Add:

- Foundry Header,
- Opportunity Radar,
- Candidate Draft Cards,
- Why Different Panel,
- Candidate Completeness Checklist,
- Validation Recipe Panel,
- Source Map/Table,
- Rejected Drafts.

Acceptance:

- visible in Research OS on one page,
- candidate cards are readable,
- user can sort/filter by family, lane, duplicate risk, evidence, score,
- warnings are visually distinct,
- no raw secret contents shown,
- no live-readiness claims.

### Phase 6: Atlas Foundry Lens

Time: 45-75 minutes.

Optional but strongly preferred if core panels are working.

Files:

- `project_os/graph.py`
- `project_os/views/dashboard_views.py`

Add:

- Candidate Foundry lens,
- source-node highlighting if feasible,
- candidate draft summary nodes if feasible,
- nearest-prior or blocker-addressing edges if feasible.

Acceptance:

- graph remains nonblank,
- default graph remains readable,
- clickability remains intact,
- modebar remains hidden,
- trace count remains reasonable.

### Phase 7: Report Output

Time: 45-60 minutes.

Files:

- `project_os/reporting.py` or new helper
- `logs/project_os/candidate_foundry_report_latest.md`

Acceptance:

- report writes without running scorers/bots/backtests,
- report cites source nodes/paths,
- report contains queue, rejected drafts, validation recipes, changed-file summary, tests, browser QA,
- report says research-only,
- no raw secrets.

### Phase 8: Tests, Browser QA, Completion Audit

Time: 60-90 minutes.

Tests:

- discovery model determinism,
- opportunity mining,
- positive-blocked candidate handling,
- assumption delta,
- duplicate risk,
- validation recipe completeness,
- scoring constraints,
- queue lanes,
- rejected drafts,
- no direct filesystem crawl,
- no live API,
- dashboard import side effects.

Browser QA:

- `8503` loads,
- Foundry section visible,
- cards visible,
- Why Different visible,
- Validation Recipe visible,
- Rejected Drafts visible,
- filters work,
- no Streamlit errors,
- no CSS leak,
- local-only warning remains,
- sensitive filter remains,
- `8501` separate.

Acceptance:

- tests pass,
- browser QA passes,
- changed-file safety audit passes,
- residual risks documented.

## Test Fixtures

Add lightweight synthetic fixtures.

### Fixture 1: Positive Blocked With Fixable Blocker

Input:

- report node,
- family `v28_successor`,
- status `blocked`,
- evidence `forward_shadow`,
- positive net metric,
- blocker `single_market_share_above_25pct`.

Expected:

- opportunity kind `positive_blocked_trap`,
- draft can be generated only if risk/concentration control is added,
- duplicate risk medium or high until changed assumption is explicit,
- lane `Repair Before Candidate` or `Freeze Next`, not `Validate Next` unless complete.

### Fixture 2: Backtest-Only Frontier

Input:

- report node,
- family `ou_mispricing`,
- status `diagnostic_only`,
- evidence `backtest`,
- positive metric.

Expected:

- candidate may be `Frontier Explore` or `Repair Before Candidate`,
- validation recipe requires forward/shadow proof,
- not strong,
- not live-ready,
- evidence score capped.

### Fixture 3: Duplicate Sibling

Input:

- three similar candidate/report nodes,
- same family,
- same motifs,
- same blockers,
- only timestamp/label changes.

Expected:

- high duplicate risk,
- nearest prior populated,
- lane `Do Not Repeat`,
- no validation-ready recommendation.

### Fixture 4: Changed Risk Assumption

Input:

- blocked prior due to concentration,
- new draft includes explicit concentration cap and kill rule.

Expected:

- assumption delta identifies changed risk control,
- duplicate risk reduced,
- candidate can become `Freeze Next` if complete.

### Fixture 5: Missing Accounting

Input:

- promising opportunity with entry/exit but no fee/accounting rule.

Expected:

- completeness checklist marks accounting missing,
- lane `Repair Before Candidate`,
- not `Validate Next`.

### Fixture 6: Script Cluster No Candidate

Input:

- several script nodes with shared family/motif,
- no candidate/report links.

Expected:

- opportunity created,
- candidate draft only if enough hypothesis tokens exist,
- otherwise lineage repair item.

### Fixture 7: Ambiguous P&L

Input:

- metrics include positive raw P&L with unknown unit.

Expected:

- metric ambiguity penalty,
- lower confidence,
- not top-ranked over clearer evidence,
- raw metric provenance visible.

### Fixture 8: New Broad Family Attempt

Input:

- source node with a new motif/family not seen elsewhere,
- no supporting evidence,
- no existing-family rejection.

Expected:

- high anti-sprawl penalty,
- lane `Frontier Explore` or `needs_more_source_evidence`,
- no validation-ready recommendation.

## Acceptance Criteria

### Functional Acceptance

1. Research OS dashboard still launches on `8503`.
2. Existing dashboard on `8501` remains unchanged.
3. No live bot/order/scorer/state files changed.
4. Candidate Foundry code consumes registry, not direct filesystem crawls.
5. Opportunity mining produces rows or documented empty-state reasons.
6. Candidate drafts are generated from opportunities.
7. Candidate drafts include source node citations.
8. Candidate drafts include complete-system fields.
9. Assumption-delta checks exist.
10. Duplicate-risk checks exist.
11. Validation recipes exist for queued candidates.
12. Candidate queue JSON writes latest plus timestamped snapshot.
13. Candidate Foundry dashboard section renders.
14. Rejected drafts are visible.
15. Report output exists.
16. Browser QA shows no Streamlit errors.

### Logical Acceptance

1. Existing candidates and families are considered before broad novelty.
2. New broad family recommendations require explicit frontier-gap justification.
3. Positive blocked P&L cannot become validation-ready without a blocker-addressing change.
4. Replay/backtest-only evidence cannot become live-ready or strong proof.
5. Candidate drafts missing exit/risk/accounting cannot be validation-ready.
6. Duplicate candidates are caught unless changed assumption is explicit.
7. Changed label/timestamp alone does not count as changed assumption.
8. Ambiguous metrics lower confidence.
9. Source-less candidates are downgraded.
10. Every top recommendation cites sources and explains "why different."
11. Every validation-ready item has a kill rule.
12. Every queued item has a smallest fair next test.

### UX Acceptance

1. Candidate Foundry is easy to find.
2. Top candidate cards are readable.
3. The user can see "why this is different" without opening raw files.
4. The user can see what was rejected and why.
5. Warnings are visually distinct.
6. The dashboard does not bury blockers under positive metrics.
7. Filters make the queue usable.
8. No text overflow in the main panels.
9. Atlas remains usable if Foundry lens is added.

### Verification Acceptance

Run:

```powershell
python -m compileall project_os project_os_dashboard.py test_project_os_registry.py test_project_os_discovery.py
python -m unittest test_project_os_registry.py test_project_os_discovery.py -v
```

If `test_project_os_discovery.py` is not added for a documented reason, the final report must explain what equivalent tests were run.

Browser verification:

```text
URL: http://127.0.0.1:8503/
error count: 0
Candidate Foundry visible: yes
Opportunity Radar visible: yes
Candidate Draft Cards visible: yes
Why Different visible: yes
Validation Recipe visible: yes
Rejected Drafts visible: yes
local-only sensitive warning: yes
sensitive hide filter: yes
manual refresh registry-only: yes
modebar hidden if graph used: yes
CSS leak: no
```

Process separation:

```powershell
Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8501,8503 -State Listen
```

Changed-file safety:

```powershell
git diff --name-only
```

If not a Git checkout, use timestamp audit and the report's changed-file list. The changed-file list should stay inside:

```text
project_os/*
project_os_dashboard.py
test_project_os_*.py
docs/research/*
logs/project_os/*
```

unless the user explicitly approved broader edits.

## Candidate Foundry Report Shape

The final report should be detailed. The final chat answer can be concise.

Preferred report:

```text
# Candidate Foundry Report

## Summary
## Registry Source
## Top Queue
## Freeze Next
## Validate Next
## Repair Before Candidate
## Do Not Repeat
## Frontier Explore
## Rejected Drafts
## Opportunity Radar
## Candidate Drafts
## Assumption Delta Review
## Validation Recipes
## Files Changed
## Tests Run
## Browser QA
## Residual Risks
```

Every top candidate should have:

```text
Title:
Family:
Lane:
Score:
Confidence:
Source nodes:
Nearest prior:
Changed assumption:
Main blocker addressed:
Remaining blocker:
Validation recipe:
Kill rule:
Next action:
```

## Risk Register

### Risk: Candidate Sprawl

Mitigation:

- anti-sprawl penalty,
- source citation requirement,
- existing-family-first rule,
- rejected drafts panel.

### Risk: False Novelty

Mitigation:

- nearest-prior matching,
- assumption-delta checks,
- duplicate-risk lane.

### Risk: Positive P&L Trap

Mitigation:

- positive-blocked opportunity class,
- blocker-addressing requirement,
- no validation-ready lane unless blocker fix is explicit.

### Risk: Incomplete Candidate Systems

Mitigation:

- candidate completeness checklist,
- missing entry/exit/risk/accounting forces repair lane.

### Risk: Overfitting To Backtests

Mitigation:

- replay/backtest evidence cap,
- forward/shadow validation recipe requirement,
- do-not-change list.

### Risk: Ambiguous Metrics

Mitigation:

- metric provenance,
- confidence penalty,
- unit warnings.

### Risk: Sensitive Data Exposure

Mitigation:

- no raw secrets in report,
- local-only warning preserved,
- sensitive filter preserved.

### Risk: Live-System Mutation

Mitigation:

- allowed file list,
- no live/scorer/order scripts,
- changed-file safety audit,
- process separation check.

## Stretch Goals If Time Remains

Only attempt after core acceptance criteria pass.

1. Add a "Candidate Diff" visual:
   - selected draft versus nearest prior,
   - same assumptions,
   - changed assumptions,
   - unresolved blockers.

2. Add a "Mutation Lab" table:
   - blocker,
   - possible changed assumption,
   - candidate draft target,
   - validation recipe.

3. Add a "No More Variants Until" rule per family:
   - family is paused until missing evidence or blocker classification is repaired.

4. Add a "Candidate Graveyard":
   - rejected drafts with exact reason and nearest sibling.

5. Add candidate export:
   - one markdown card per validation-ready draft under `logs/project_os/candidate_cards/`.

6. Add a "coverage frontier" mini-map:
   - families by artifacts, candidates, reports, forward evidence, and blockers.

7. Add a "human review checklist" button or export:
   - not mutating files outside `logs/project_os`.

8. Add an assumption-delta heatmap:
   - entry changed,
   - exit changed,
   - risk changed,
   - accounting changed,
   - validation changed.

## Final Logic Review

Before final response, the overnight worker must check:

1. Did I keep all work research-only?
2. Did I avoid live bot/order/scorer/state changes?
3. Did I preserve the existing `8501` dashboard?
4. Did I keep Research OS on `8503`?
5. Did I consume registry data rather than crawling from dashboard views?
6. Did I generate opportunities from source evidence?
7. Did every top candidate cite source nodes?
8. Did every top candidate show nearest prior or missing-prior warning?
9. Did every top candidate explain what changed?
10. Did I catch duplicate-risk candidates?
11. Did I prevent positive-blocked traps from becoming validation-ready without a blocker fix?
12. Did I prevent replay/backtest-only evidence from becoming proof?
13. Did I require complete candidate systems before validation?
14. Did I include validation recipes and kill rules?
15. Did I show rejected drafts and reasons?
16. Did I preserve sensitive/local-only warnings and filters?
17. Did I run tests?
18. Did I verify browser rendering?
19. Did I verify process separation?
20. Did I audit changed files?
21. Did I document residual risks honestly?
22. Completion gate: do not mark the goal complete until every required item in this spec, including all implementation phases, logical constraints, test fixtures, acceptance criteria, browser QA checks, candidate queue outputs, changed-file safety audit, subagent integration, and bug-fix follow-ups discovered during the work, has been implemented where applicable, tested, checked for calculation/UI bugs, and either passed or explicitly documented as an unresolved residual gap.

If any answer is no, finish that item before claiming completion. The goal may only be closed when item 22 is true; otherwise the final response must say exactly what remains unfinished, what was tested, what failed, and what still needs another pass.

