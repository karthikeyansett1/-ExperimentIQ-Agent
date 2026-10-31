# ExperimentIQ | Experiment Decision Memo

**Deterministic gate:** INVESTIGATE / HOLD  
**Outcome:** conversion · **Method:** two-proportion z-test / Newcombe CI

### Observed evidence
- Conversion was **20.76%** in control (2,100 users) and **29.67%** in treatment (900 users): an observed increase of **8.90 percentage points** (about **42.9% relative** to control).
- The reported 95% confidence interval for the absolute difference is **5.50 to 12.40 percentage points**; the reported p-value is **1.32 × 10⁻⁷**.

### Validity checks
- **Severe sample ratio mismatch:** SRM p-value **2.14 × 10⁻¹⁰⁶**, with group sizes 2,100 vs. 900.
- The results flag this as requiring investigation of assignment or missingness. The small p-value for the conversion difference does not resolve that validity concern.

### Decision and caveats
**Investigate first; hold launch.** This is the reported decision gate, and the treatment’s positive observed effect should not be treated as reliable until the SRM is explained. Check allocation, exposure logging, eligibility, and missingness, then reassess using valid data.

---

**Methodological limitations:** Single outcome, naive independent-unit inference, prespecified ratio assumed 50/50. Not a production causal-inference system; no multiple-comparisons adjustment, guardrail integration, cluster-robust estimators, or sequential p-value correction. Synthetic benchmarks evaluate programmed decision gates, not LLM accuracy.