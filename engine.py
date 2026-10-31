"""A/B inference, diagnostics and synthetic experiment benchmark."""
import numpy as np
import pandas as pd
from scipy.stats import chi2, chi2_contingency, mannwhitneyu, ttest_ind, skew
from statsmodels.stats.power import TTestIndPower
from statsmodels.stats.proportion import proportions_ztest, confint_proportions_2indep

def simulate(seed=33,n=2200,metric="conversion",effect=.045,srm=False,skewed=False,peeking=False):
    rng=np.random.default_rng(seed)
    nt=int(n*(.70 if srm else .50))
    assigned=np.array(["control"]*nt+["treatment"]*(n-nt))
    rng.shuffle(assigned)
    pre=rng.normal(20,7,n)
    treat=assigned=="treatment"
    if metric=="conversion":
        # effect is absolute conversion probability points
        y=rng.binomial(1,np.clip(.22 +effect*treat,0,1),n).astype(float)
    else:
        noise=rng.lognormal(2.7,1.25,n) if skewed else rng.normal(15,8,n)
        y=100+1.8*pre + noise +(effect*100)*treat
    return pd.DataFrame({"unit_id":np.arange(n),"variant":assigned,"outcome":y,
                         "pre_period":pre,"metric_type":metric,"peeked":peeking})

def srm_check(df,expected_control=.5):
    c=int((df.variant=="control").sum());t=int((df.variant=="treatment").sum());n=c+t
    if n==0: raise ValueError("No control/treatment assignments")
    expected=np.array([n*expected_control,n*(1-expected_control)])
    stat=float(np.sum((np.array([c,t])-expected)**2/expected))
    p=float(chi2.sf(stat,df=1))
    return {"control":c,"treatment":t,"p_value":p,"srm_flag":p<.001}

def analyze(df,metric="conversion",use_cuped=False):
    required={"variant","outcome"}
    if not required.issubset(df.columns): raise ValueError("Missing required columns: variant, outcome")
    if not df.variant.isin(["control","treatment"]).all():
        raise ValueError("All variant values must be control or treatment; no rows are silently dropped")
    df=df.copy()
    df["outcome"]=pd.to_numeric(df.outcome,errors="coerce")
    if df.outcome.isna().any(): raise ValueError("Outcome contains missing or nonnumeric values")
    c=df[df.variant=="control"].outcome.to_numpy();t=df[df.variant=="treatment"].outcome.to_numpy()
    if min(len(c),len(t))<5: raise ValueError("At least five observations per arm required")
    srm=srm_check(df)
    if metric=="conversion":
        if not set(np.unique(df.outcome)).issubset({0.,1.}): raise ValueError("Conversion outcomes must be 0 or 1")
        counts=np.array([t.sum(),c.sum()]);nobs=np.array([len(t),len(c)])
        stat,p=proportions_ztest(counts,nobs)
        lo,hi=confint_proportions_2indep(count1=int(t.sum()),nobs1=len(t),count2=int(c.sum()),nobs2=len(c),method="newcomb")
        test="two-proportion z-test / Newcombe CI"
    else:
        if use_cuped:
            if "pre_period" not in df: raise ValueError("CUPED requires pre_period")
            cov=pd.to_numeric(df.pre_period,errors="coerce")
            if cov.isna().any(): raise ValueError("Missing pre-period values")
            variance=cov.var(ddof=1)
            theta=float(np.cov(df.outcome,cov,ddof=1)[0,1]/variance) if variance>0 else 0.
            df["outcome"]=df.outcome-theta*(cov-cov.mean())
            c=df[df.variant=="control"].outcome.to_numpy();t=df[df.variant=="treatment"].outcome.to_numpy()
        stat,p=ttest_ind(t,c,equal_var=False)
        from scipy.stats import t as student_t
        se=np.sqrt(np.var(t,ddof=1)/len(t)+np.var(c,ddof=1)/len(c))
        v1=np.var(t,ddof=1)/len(t);v2=np.var(c,ddof=1)/len(c)
        dof=(v1+v2)**2/(v1**2/(len(t)-1)+v2**2/(len(c)-1))
        critical=student_t.ppf(.975,dof)
        diff=float(t.mean()-c.mean());lo=diff-critical*se;hi=diff+critical*se
        test="Welch t-test"+(" with CUPED" if use_cuped else "")
    lift=float(t.mean()-c.mean())
    if "peeked" in df:
        vals=df["peeked"].astype(str).str.strip().str.lower()
        if not vals.isin(["true","false","1","0","yes","no"]).all():
            raise ValueError("peeked must contain true/false or 1/0")
        peeked=bool(vals.isin(["true","1","yes"]).any())
    else:
        peeked=False
    skew_warning=metric!="conversion" and (abs(skew(t))>2 or abs(skew(c))>2)
    warnings=[]
    if srm["srm_flag"]: warnings.append("Sample ratio mismatch: investigate assignment or missingness")
    if peeked: warnings.append("Repeated peeking is declared: nominal p-value may be invalid")
    if skew_warning: warnings.append("Strongly skewed outcome: examine robust or bootstrap inference")
    if min(len(c),len(t))<30: warnings.append("Small sample per arm")
    valid=not(srm["srm_flag"] or peeked)
    # No arbitrary LLM judgment for recommendation.
    recommendation="SHIP" if valid and float(p)<.05 and lift>0 else "DO NOT SHIP" if valid else "INVESTIGATE / HOLD"
    return {"test":test,"control_n":len(c),"treatment_n":len(t),"control_mean":float(c.mean()),
            "treatment_mean":float(t.mean()),"absolute_effect":lift,"p_value":float(p),
            "ci_low":float(lo),"ci_high":float(hi),"srm_p_value":srm["p_value"],
            "recommendation":recommendation,"warnings":warnings,
            "metric":metric,"use_cuped":use_cuped}

def power_approx(effect_size=.2,alpha=.05,power=.8):
    if effect_size<=0: raise ValueError("Effect size must be > 0")
    n=TTestIndPower().solve_power(effect_size=effect_size,alpha=alpha,power=power,ratio=1)
    return int(np.ceil(n))

def benchmark():
    records=[]
    # 20 scenarios: 5 SRM, 5 peeking, 5 clear positive treatment effects, 5 null outcomes.
    for i in range(20):
        family=i//5
        kwargs={"seed":100+i,"n":3000,"metric":"conversion","effect":0.0,
                "srm":family==0,"peeking":family==1}
        if family==2: kwargs["effect"]=.12
        df=simulate(**kwargs)
        result=analyze(df)
        expected="INVESTIGATE / HOLD" if family in (0,1) else "SHIP" if family==2 else "DO NOT SHIP"
        detected=(result["recommendation"]==expected)
        records.append({"case":i+1,"scenario":["SRM","Peeking","Strong uplift","Null effect"][family],
                        "expected":expected,"actual":result["recommendation"],"correct":detected,
                        "p_value":result["p_value"],"warnings":"; ".join(result["warnings"])})
    data=pd.DataFrame(records)
    return {"correct":int(data.correct.sum()),"total":len(data),"accuracy":float(data.correct.mean()),"cases":data}
