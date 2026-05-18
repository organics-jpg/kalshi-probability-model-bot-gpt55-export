# Truffle LLM Finance Research Notes

## Purpose

Capture paper-backed guidance for where Truffle is most and least likely to create real edge for this Kalshi BTC 15 minute bot.

The key question is not whether LLMs can be useful in finance in general.
The key question is whether an LLM layer can create incremental edge on top of this bot's existing deterministic logic and numeric trade history.

## Current repo-level constraint

The current bot repo has rich numeric and execution data:

- BTC candles
- Kalshi order book data
- fills and exits
- latencies and freshness
- trade labels and market outcomes

But it does **not** currently have a real semantic input stream such as:

- macro calendar events
- headlines
- narrative tags
- crypto-specific sentiment feed
- linked market descriptions

That matters because many finance LLM papers show value mainly when the model is asked to interpret text, event context, or semantic relationships that a numeric baseline does not already capture.

## Papers that matter most

### 1. LLM as a Risk Manager: LLM Semantic Filtering for Lead-Lag Trading in Prediction Markets

Source:
- https://arxiv.org/abs/2602.07048

Why it matters:
- This is the closest paper in spirit to what we are trying to do.
- The LLM is not the primary trader.
- A statistical stage proposes candidates first.
- The LLM acts as a semantic risk filter on top.

Reported result:
- On Kalshi Economics markets, win rate improves from 51.4% to 54.5%.
- Average losing trade magnitude drops from 649 USD to 347 USD.

Takeaway for this bot:
- Best fit is a **risk manager** or **candidate filter**, not a raw execution brain.
- The LLM seems most useful when it filters statistically fragile candidates that would otherwise create outsized losses.

Direct implication:
- Truffle should only be asked to arbitrate already-filtered borderline cases.
- It should not be the first-pass market decision maker.

### 2. Are Language Models Actually Useful for Time Series Forecasting?

Source:
- https://arxiv.org/abs/2406.16964

Why it matters:
- It directly challenges the common assumption that an LLM helps on raw time-series prediction.

Reported result:
- Removing the LLM component often does not hurt performance and can even improve it.
- Pretrained LLMs do not clearly beat simpler attention-based alternatives for time series.

Takeaway for this bot:
- Passing mostly numeric rolling summaries into Truffle and hoping for forecasting magic is unlikely to create durable edge.

Direct implication:
- Avoid using Truffle as a direct numerical forecaster over recent market stats alone.
- If Truffle stays in the loop, it should process information that is meaningfully more semantic than the deterministic baseline already uses.

### 3. EventCast: Hybrid Demand Forecasting with LLM-Based Event Knowledge

Source:
- https://arxiv.org/abs/2602.07695

Why it matters:
- The architecture is highly relevant even though the domain is e-commerce.
- The LLM is used for event reasoning, while the numeric forecaster still handles historical structure.

Reported result:
- Strong gains during event-driven periods versus baselines that ignore event knowledge.

Takeaway for this bot:
- The strongest future Truffle edge likely comes from event interpretation:
  - CPI
  - FOMC
  - ETF headlines
  - exchange/regulatory/security shocks
  - weekend/liquidity narrative shifts

Direct implication:
- If we want Truffle to earn its keep, we should build a compact semantic context channel rather than repeatedly prompt over numeric trade summaries.

### 4. Sentiment trading with large language models

Source:
- https://arxiv.org/abs/2412.19245

Why it matters:
- Shows that LLM-extracted sentiment can have predictive relevance for returns.

Reported result:
- LLM scores have significant association with subsequent daily stock returns.
- LLM sentiment outperforms traditional dictionary approaches.

Takeaway for this bot:
- If we can provide high-quality BTC-relevant text, Truffle may be useful as a sentiment or narrative classifier.
- Without text, this paper is less directly actionable.

Direct implication:
- Build a small text ingestion path before expecting semantic Truffle edge.

### 5. Enhancing Zero-Shot Crypto Sentiment with Fine-tuned Language Model and Prompt Engineering

Source:
- https://arxiv.org/abs/2310.13226

Why it matters:
- Crypto-specific.
- Prompt-design finding is directly usable.

Reported result:
- Fine-tuning materially improves crypto sentiment performance.
- Short and simple instructions outperform long and complex instructions by more than 12 percentage points in their setup.

Takeaway for this bot:
- If Truffle is given a semantic text classification task, prompts should be short, rigid, and specific.
- Long narrative prompts are likely counterproductive.

Direct implication:
- Prefer compact structured prompts and short output contracts.
- If we ever fine-tune or adapt a local model for crypto text, small domain-adapted models are plausible.

### 6. Large Language Model Adaptation for Financial Sentiment Analysis

Source:
- https://arxiv.org/abs/2401.14777

Why it matters:
- Reinforces the idea that domain adaptation matters more than sheer model size.

Reported result:
- Small models under 1.5B parameters can be adapted to finance successfully.
- Small adapted models can be comparable to larger models while being more efficient.

Takeaway for this bot:
- If we build a semantic classifier inside Truffle, a small finance- or crypto-adapted model may be a better production path than a raw general-purpose reasoning model.

Direct implication:
- Strong candidate architecture:
  - deterministic router
  - small adapted classifier for semantic route
  - Truffle orchestration / supervision around it

### 7. Fine-Tuning is All You Need: Compact Models Can Outperform GPT's Classification Abilities

Source:
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5199077

Why it matters:
- Again reinforces that classification tasks often favor adapted compact models over generic giant models.

Takeaway for this bot:
- If the target task is a narrow lease-classification problem, the best end state may be:
  - Truffle as the app/runtime layer
  - compact adapted classifier as the decision engine
  - not a giant prompt-only model

### 8. Large Language Models and Financial Market Sentiment

Source:
- https://ssrn.com/abstract=4584928

Why it matters:
- Shows LLMs can extract useful market-level sentiment from aggregated text.

Takeaway for this bot:
- A market-level or session-level sentiment regime score could be a better Truffle input than raw microstructure features.

Direct implication:
- If we add a text feed, convert it to:
  - short horizon sentiment
  - crowd excitement / panic score
  - policy shock score
  - narrative disagreement score

### 9. Does sentiment help in asset pricing? A novel approach using large language models and market-based labels

Source:
- https://ssrn.com/abstract=4905533

Why it matters:
- The most actionable idea here is the label design.

Reported result:
- Market-based labeling beat traditional human-labeled sentiment approaches in their setup.

Takeaway for this bot:
- If we collect text, our labels should come from realized market outcomes, not generic human sentiment classes.

Direct implication:
- For future training:
  - label text windows by subsequent bot-safe outcome classes
  - not by positive / negative / neutral human sentiment

### 10. Assessing Consistency and Reproducibility in LLM Outputs in Finance and Accounting Tasks

Source:
- https://ssrn.com/abstract=5189069

Why it matters:
- We have already seen local instability in Truffle outputs.

Reported result:
- Aggregating 3 to 5 runs dramatically improves consistency in finance tasks.

Takeaway for this bot:
- Single-call Truffle decisions should be distrusted.
- Committee or aggregation logic is not optional if Truffle is in the live path.

Direct implication:
- If Truffle remains live:
  - 3-call or 5-call aggregation
  - fail closed on disagreement
  - log disagreement rate as a first-class metric

### 11. KalshiBench: Evaluating Epistemic Calibration via Prediction Markets

Source:
- https://arxiv.org/abs/2512.16030

Why it matters:
- This is a strong warning against trusting raw model confidence.

Reported result:
- Systematic overconfidence across models.
- Most models perform worse than base rates on Brier Skill Score.

Takeaway for this bot:
- Truffle confidence should not be treated as decision quality without shadow calibration.

Direct implication:
- Do not use raw `confidence` to scale size or widen permission.
- At most, use it to decide whether to request extra committee votes, and only after shadow validation.

### 12. Efficient Test-Time Scaling via Self-Calibration

Source:
- https://arxiv.org/abs/2503.00031

Why it matters:
- Gives a framework for adaptive committee size.

Takeaway for this bot:
- We may not need fixed 3 or fixed 5 calls for every lease.
- A future design can request more votes only when the first responses look uncertain or conflict.

Direct implication:
- Candidate future live policy:
  - call once
  - if low-confidence or malformed or ambiguous rationale, expand to 3 votes
  - if split persists, block

### 13. A Financial Brain Scan of the LLM

Source:
- https://ssrn.com/abstract=5412277

Why it matters:
- Suggests a path for steering the model's stance instead of only prompt tuning.

Reported result:
- The authors map LLM economic forecasts to interpretable concepts such as sentiment, technical analysis, and timing.
- They also show steering the model to be more risk-averse or optimistic.

Takeaway for this bot:
- Truffle can potentially be framed as a deliberately **risk-averse lease issuer** instead of a neutral forecaster.

Direct implication:
- For live use, steer the system explicitly toward:
  - false-negative tolerance
  - loss avoidance
  - skepticism toward hot or mixed states

## What the literature says **not** to do

### Do not use Truffle as a raw next-market forecaster over numeric-only summaries

Paper support:
- Are Language Models Actually Useful for Time Series Forecasting?
- FinTradeBench

Reason:
- LLMs remain weak and unreliable on numerical/time-series reasoning compared with what people often assume.

### Do not trust one-shot confidence

Paper support:
- KalshiBench
- Consistency and Reproducibility in Finance Tasks

Reason:
- Overconfidence and instability are real.

### Do not assume a larger reasoning model automatically fixes finance-specific classification

Paper support:
- Large Language Model Adaptation for Financial Sentiment Analysis
- Fine-Tuning is All You Need

Reason:
- Domain adaptation and narrow-task supervision matter more than scale in many financial classification settings.

## Best paper-backed Truffle applications for this bot

### Tier 1: Most defensible

1. Semantic risk filter over deterministic candidates
   - Truffle only sees ambiguous cases after hard blocks and hard allows.
   - This is the closest match to the prediction-market risk-manager paper.

2. Offline labeler for semantic regime classes tied to realized outcomes
   - Use realized next-session or next-day PnL labels.
   - Build text-window labels around those outcomes.

3. Runtime wrapper around a compact adapted finance or crypto classifier
   - Truffle handles orchestration, schemas, logging, and committee logic.
   - The classifier handles the narrow decision.

### Tier 2: Plausible but requires new data

4. Macro and headline-aware lease issuer
   - Add scheduled event tags and short news bundles.
   - Then ask Truffle whether the current market should inherit a red or green semantic lease.

5. Narrative shock detector for loss clusters
   - Detect whether a cluster is associated with regime exhaustion, news shock, policy risk, or pure strategy weakness.

### Tier 3: Weakly supported

6. Raw numerical lease forecasting from rolling summaries only
   - Current evidence does not support this strongly.

7. Direct live exit brain
   - Literature and our tests both suggest this is unlikely to be the first winning application.

## Concrete next experiments implied by the papers

### Experiment A: Add a real semantic context channel

Inputs:
- next macro event type within 0 to 6 hours
- macro event proximity bucket
- short BTC headline bundle
- short crypto narrative bundle
- optional binary tags like `policy_shock`, `exchange_incident`, `ETF_flow_story`, `risk_off_macro`

Goal:
- test whether Truffle adds value once it has information the numeric baseline does not already own

### Experiment B: Replace prompt-only Truffle classification with a compact adapted classifier

Architecture:
- deterministic router
- small adapted finance / crypto classifier
- Truffle app as wrapper for calls, aggregation, logging, and version control

Goal:
- see whether narrow supervised classification beats prompt-only reasoning on ambiguous routed cases

### Experiment C: Adaptive committee

Policy:
- call once
- if malformed, low-confidence, or inconsistent rationale, expand to 3 calls
- if split remains, block

Goal:
- reduce inference cost while preserving consistency

### Experiment D: Market-based semantic labeling

Label classes:
- `GOOD_REBOUND`
- `HOT_EXHAUSTION`
- `PANIC_CONTINUATION`
- `NO_EDGE_CHOP`
- `EXECUTION_DEGRADED`

Goal:
- train or evaluate semantic classifiers on labels tied to actual subsequent outcomes instead of generic sentiment

## Working conclusion

The literature does **not** support the idea that Truffle will discover stable edge from the bot's current numeric rolling summaries alone.

The literature **does** support these narrower possibilities:

- Truffle as a semantic risk manager on top of deterministic candidate generation
- Truffle as an orchestrator around a compact domain-adapted classifier
- Truffle as a system that becomes useful once we feed it genuine semantic inputs

So the most evidence-backed path forward is:

1. keep deterministic routing
2. add real semantic context
3. use Truffle only on the unresolved middle
4. aggregate multiple runs
5. distrust raw confidence unless calibrated on shadow data
