# ExperimentIQ | Experiment Decision Memo

**Deterministic gate:** SHIP  
**Outcome:** conversion · **Method:** two-proportion z-test / Newcombe CI

### Observed evidence
- Conversion was **20.2%** in control and **30.33%** in treatment.
- The observed treatment effect was **+10.13 percentage points** (about **+50.2% relative** to control).
- The reported 95% confidence interval for the absolute effect is **+7.03 to +13.21 percentage points**; the two-proportion test reported **p = 1.70 × 10⁻¹⁰**.

### Validity checks
- Sample sizes were equal (**1,500 per group**). The SRM test showed no sample-ratio mismatch (**p = 1.0**), and the results report no warnings.
- An absent SRM is reassuring about allocation counts, but **does not by itself establish randomization validity** or rule out other design or measurement problems.

### Decision and caveats
- **Deterministic gate: SHIP.** The reported recommendation is SHIP.
- **Conditional recommendation:** The result is strongly positive; shipping is reasonable if the experiment’s assignment, exposure, and conversion measurement were implemented correctly. The observed difference should not be treated as causal if those design checks fail.

---

**Methodological limitations:** Single outcome, naive independent-unit inference, prespecified ratio assumed 50/50. Not a production causal-inference system; no multiple-comparisons adjustment, guardrail integration, cluster-robust estimators, or sequential p-value correction. Synthetic benchmarks evaluate programmed decision gates, not LLM accuracy.