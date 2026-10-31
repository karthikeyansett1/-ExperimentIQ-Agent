"""ExperimentIQ — cloud-first A/B experimentation command center."""
from __future__ import annotations
import hashlib
import hmac
import json
import os
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from engine import simulate, analyze, benchmark, power_approx
from graph_agent import investigate, MODEL

BASE=Path(__file__).parent
st.set_page_config(page_title="ExperimentIQ | Decision Intelligence",page_icon="🧬",layout="wide",initial_sidebar_state="expanded")
css=BASE/"assets"/"console.css"
if css.exists(): st.markdown(f"<style>{css.read_text()}</style>",unsafe_allow_html=True)

# The app deliberately does NOT persist uploaded datasets, API keys, or transcripts.
def secret(name):
    try:
        return str(st.secrets.get(name,""))
    except Exception:
        return os.getenv(name,"")

def plot_style(fig,height=350):
    fig.update_layout(template="plotly_dark",height=height,margin=dict(l=20,r=20,t=35,b=35),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#B9C9D7",family="Inter, sans-serif"),
        xaxis=dict(gridcolor="rgba(127,164,182,.10)"),
        yaxis=dict(gridcolor="rgba(127,164,182,.10)"))
    return fig

def header(eyebrow,title,description):
    st.markdown(f'<div class="eyebrow">{eyebrow}</div><div class="section-title">{title}</div><div class="section-copy">{description}</div>',unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-icon">✦</span><span>EXPERIMENT<span class="brand-accent">IQ</span></span></div>',unsafe_allow_html=True)
    st.caption("DECISION INTELLIGENCE / V2.0")
    st.markdown('<div class="sidebar-section">DATA SOURCE</div>',unsafe_allow_html=True)
    upload=st.file_uploader("Experiment CSV",type="csv",help="Requires variant and outcome; optional pre_period, peeked. Max 10 MB.")
    metric=st.selectbox("Outcome model",["conversion","continuous"])
    if upload is None:
        st.markdown('<div class="pill">● SYNTHETIC EXPERIMENT</div>',unsafe_allow_html=True)
        n=st.slider("Participants",400,10000,3000,200)
        effect=st.slider("Injected effect",-0.10,0.20,0.08,0.01)
        srm=st.toggle("Inject sample-ratio mismatch",False)
        peeking=st.toggle("Flag repeated peeking",False)
        heavy=st.toggle("Heavy-tailed outcomes",False,disabled=metric!="continuous")
    else:
        st.markdown('<div class="pill">● USER CSV / SESSION ONLY</div>',unsafe_allow_html=True)
    cuped=st.toggle("Use CUPED",False,disabled=metric!="continuous")
    st.markdown('<div class="sidebar-section">AGENT ACCESS</div>',unsafe_allow_html=True)
    st.caption("Statistical dashboard is free. AI investigation uses hosted OpenAI inference and requires API credentials.")
    st.markdown('<div class="sidebar-foot">AGGREGATE EVIDENCE ONLY TO MODEL<br>OPENAI API · LANGGRAPH · SCIENTIFIC PYTHON</div>',unsafe_allow_html=True)

try:
    if upload is None:
        df=simulate(n=n,effect=effect,metric=metric,srm=srm,peeking=peeking,skewed=heavy)
        source="SYNTHETIC SANDBOX"
        data_hash=hashlib.sha256(f"{n}/{effect}/{srm}/{peeking}/{heavy}/{metric}".encode()).hexdigest()
    else:
        raw=upload.getvalue()
        if len(raw)>10*1024*1024: raise ValueError("CSV must be no larger than 10MB")
        df=pd.read_csv(__import__('io').BytesIO(raw))
        source="UPLOADED DATA"
        data_hash=hashlib.sha256(raw).hexdigest()
    if len(df)>50000 or len(df.columns)>20: raise ValueError("At most 50,000 rows and 20 columns")
    result=analyze(df,metric=metric,use_cuped=cuped)
except Exception as exc:
    st.error(f"Dataset validation failed: {exc}")
    st.stop()

st.markdown('<div class="main-header"><div><div class="eyebrow">EXPERIMENT OPERATIONS / CAUSAL EVIDENCE</div><h1>Decision Intelligence<span class="accent">.</span></h1><p>From randomization checks to defensible rollout decisions.</p></div><div class="header-chip">◉ &nbsp; LIVE ANALYSIS</div></div>',unsafe_allow_html=True)
st.markdown(f'<div class="data-strip">DATASET  <strong>{source}</strong> &nbsp; / &nbsp; UNITS <strong>{len(df):,}</strong> &nbsp; / &nbsp; INFERENCE <strong>{result["test"]}</strong></div>',unsafe_allow_html=True)

cards=st.columns(4)
for col,lab,val,sub in zip(cards,["DECISION GATE","TREATMENT EFFECT","NOMINAL P-VALUE","SRM P-VALUE"],
    [result['recommendation'],f"{result['absolute_effect']:+.4f}",f"{result['p_value']:.4g}",f"{result['srm_p_value']:.4g}"],
    ["Programmed decision policy","Treatment minus control","Not sequentially adjusted","50/50 allocation check"]):
    with col:
        st.markdown(f'<div class="metric-card"><div class="metric-label">{lab}</div><div class="metric-value">{val}</div><div class="metric-sub">{sub}</div></div>',unsafe_allow_html=True)

page=st.radio("Navigation",["Overview","Validity Monitor","AI Decision Agent","Evaluation Lab","Data & Reports"],
    horizontal=True,label_visibility="collapsed",key="page")
st.divider()

if page=="Overview":
    header("01 / EXECUTIVE READOUT","Experiment performance","Interpretable effects, intervals, and statistical decision evidence.")
    a,b=st.columns([1.1,1])
    with a:
        st.markdown("#### Group outcomes")
        means=pd.DataFrame({"Variant":["Control","Treatment"],"Mean":[result["control_mean"],result["treatment_mean"]]})
        fig=px.bar(means,x="Variant",y="Mean",color="Variant",text_auto=".4f",color_discrete_sequence=["#38CFD1","#A898FF"])
        fig.update_traces(marker_line_width=0,textposition="outside")
        fig.update_layout(showlegend=False)
        st.plotly_chart(plot_style(fig),use_container_width=True)
    with b:
        st.markdown("#### Effect & 95% confidence interval")
        fig=go.Figure()
        lo,hi=result['ci_low'],result['ci_high'];eff=result['absolute_effect']
        fig.add_trace(go.Scatter(x=[lo,hi],y=[0,0],mode="lines+markers",line=dict(color="#65F0DF",width=7),marker=dict(size=10),name="95% CI"))
        fig.add_trace(go.Scatter(x=[eff],y=[0],mode="markers",marker=dict(size=18,color="#BCA7FF",symbol="diamond"),name="Estimate"))
        fig.add_vline(x=0,line_dash="dash",line_color="#FFB971")
        fig.update_layout(yaxis=dict(visible=False,range=[-.4,.4]),xaxis_title="Absolute treatment − control",showlegend=False)
        st.plotly_chart(plot_style(fig),use_container_width=True)
    st.info("Interpretation: Conversion effects are absolute probability points; continuous effects use original outcome units. A low p-value alone is not a rollout mandate.")
    st.markdown("#### At-a-glance diagnostics")
    if result['warnings']:
        for warning in result['warnings']: st.warning(warning)
    else: st.success("No configured warnings triggered. This does not establish that the design is fully valid.")

elif page=="Validity Monitor":
    header("02 / EXPERIMENT INTEGRITY","Validity monitor","Verify allocation and assumptions before interpreting uplift.")
    c1,c2,c3=st.columns(3)
    c1.metric("Control units",f"{result['control_n']:,}")
    c2.metric("Treatment units",f"{result['treatment_n']:,}")
    c3.metric("SRM p-value",f"{result['srm_p_value']:.5g}")
    fig=go.Figure(data=[go.Bar(x=["Control","Treatment"],y=[result['control_n'],result['treatment_n']],marker_color=["#38CFD1","#A898FF"] )])
    fig.add_hline(y=(result['control_n']+result['treatment_n'])/2,line_dash="dot",line_color="#FFB971",annotation_text="Expected under 50/50")
    st.plotly_chart(plot_style(fig,340),use_container_width=True)
    for issue in result['warnings']:st.warning(issue)
    if not result['warnings']:st.success("No configured validity warnings triggered.")
    st.caption("An SRM result below 0.001 is a diagnostic alert. Peeking is taken from the dataset's peeked field; the app cannot infer undeclared repeated analyses.")
    st.markdown("#### Power planning — continuous metrics only")
    d=st.slider("Standardized effect size (Cohen d)",0.1,1.0,0.2,0.05)
    st.metric("Approx. units per arm",f"{power_approx(d):,}")
    st.caption("This is a two-sample continuous-metric power approximation, NOT a conversion-rate sample-size calculation.")

elif page=="AI Decision Agent":
    header("03 / AGENT ORCHESTRATION","AI experiment investigator","Evidence → methodology retrieval → hosted function calls → audited decision memo.")
    st.markdown('<div class="agent-status">◇ &nbsp; LIVE CLOUD AGENT: GPT-6 LUNA &nbsp; · &nbsp; LANGGRAPH + VERIFIED PYTHON TOOLS</div>',unsafe_allow_html=True)
    st.caption("This is a real hosted LLM tool-calling agent, not a deterministic text generator. Statistical calculations remain deterministic and reproducible.")
    paid=True
    mode="Hosted GPT-6 Luna"
    api_key=""
    if paid:
        access=st.radio("Credentials",["My own OpenAI API key","Private recruiter demo access code"],horizontal=True)
        if access.startswith("My own"):
            api_key=st.text_input("OpenAI API key (used for this run only)",type="password",placeholder="sk-...")
            st.caption("Your key stays in your browser session and is sent to the Python server for the request. Do not use this mode with data you cannot share with the application operator.")
        else:
            code=st.text_input("Recruiter access code",type="password")
            owner_key=secret("OPENAI_API_KEY");owner_code=secret("DEMO_ACCESS_CODE")
            if code and owner_key and owner_code and hmac.compare_digest(code,owner_code):
                api_key=owner_key;st.success("Private demo access enabled for this session.")
            elif code:st.error("Invalid access code or server-side paid mode is not configured.")
        st.caption("Hosted model may bill the API account. Public users do not automatically receive access to your key.")
    demo={"Validity and decision":"Call get_experiment_results; assess sample ratio mismatch, intervals and launch decision.",
          "Methodology retrieval":"Call get_experiment_results and get_methodology for srm and decision; explain why statistical significance alone isn't enough.",
          "Continuous power planning":"Call get_experiment_results and get_power_estimate with effect_size 0.2; explain limitations."}
    preset=st.selectbox("Suggested investigation",list(demo))
    question=st.text_area("Decision question",value=demo[preset],height=100,max_chars=800)
    fingerprint=hashlib.sha256(f"{data_hash}|{metric}|{cuped}|{mode}|{question}|{preset}|{access}".encode()).hexdigest()
    # Session quota is a convenience, not a provider-level billing cap.
    if 'paid_runs' not in st.session_state:st.session_state.paid_runs=0
    runs=st.session_state.paid_runs
    if paid:st.caption(f"Safety throttle: {runs}/3 hosted investigations in this session. Not a global billing cap or a substitute for provider billing controls.")
    disabled=paid and (not api_key or runs>=3)
    if st.button("▶ Run investigation",type="primary",disabled=disabled):
        if paid:st.session_state.paid_runs+=1
        with st.spinner("Running statistical graph and analyst tools..."):
            try:
                output=investigate(df,metric=metric,cuped=cuped,question=question,paid=paid,api_key=api_key)
                st.session_state['last_run']={"signature":fingerprint,"output":output}
            except Exception as exc:st.error(f"Investigation failed: {type(exc).__name__}: {str(exc)[:250]}")
    saved=st.session_state.get('last_run')
    if saved:
        if saved['signature']!=fingerprint:
            st.warning("Dataset or settings changed since the saved investigation. Run again to refresh it.")
        else:
            state=saved['output'];status=state.get('model_status','unknown')
            if status=='failed':st.error("Hosted inference failed; results below are not a completed AI report.")
            elif status=='completed':st.success("Hosted model executed and used the experiment-results tool.")
            else:st.info(f"Execution status: {status}")
            st.markdown(state['report'])
            st.markdown("#### LangGraph execution trace")
            st.dataframe(pd.DataFrame(state.get('stages',[])),hide_index=True,use_container_width=True)
            with st.expander("Actual model tool calls",expanded=True):st.json(state.get('trace',[]))
            u=state.get('tokens') or {}
            if u:st.caption(f"Observed token usage: input {u.get('input_tokens',0)} · output {u.get('output_tokens',0)}. Check provider billing for actual charges.")
            aa,bb=st.columns(2)
            aa.download_button("Download decision memo",state['report'],file_name="experimentiq_memo.md",mime="text/markdown")
            safe={k:v for k,v in state.items() if k not in ('data','api_key')}
            bb.download_button("Download agent trace",json.dumps(safe,indent=2,default=str),file_name="experimentiq_trace.json",mime="application/json")

elif page=="Evaluation Lab":
    header("04 / REPRODUCIBILITY","Synthetic evaluation lab","Twenty designed experiments. Decision agreement is not real-world accuracy.")
    @st.cache_data(show_spinner=False)
    def evaluation():return benchmark()
    ev=evaluation()
    x,y,z=st.columns(3)
    x.metric("Cases",ev['total']);y.metric("Gate labels matched",ev['correct']);z.metric("Agreement",f"{ev['accuracy']:.0%}")
    rows=ev['cases'].groupby(['scenario','correct']).size().reset_index(name='count')
    fig=px.bar(rows,x='scenario',y='count',color='correct',barmode='group',color_discrete_map={True:'#38CFD1',False:'#FA6A8C'})
    st.plotly_chart(plot_style(fig,340),use_container_width=True)
    st.dataframe(ev['cases'],hide_index=True,use_container_width=True)
    st.download_button("Export benchmark cases",ev['cases'].to_csv(index=False),file_name="experimentiq_evaluation.csv",mime="text/csv")
    st.warning("Designed scenario agreement is not blind validation, causal effect recovery accuracy, or hosted model tool-selection accuracy.")

else:
    header("05 / AUDIT PACK","Data & reports","Export deterministic evidence without sending participant rows to the LLM.")
    st.json(result)
    c1,c2=st.columns(2)
    c1.download_button("Export verified statistics",json.dumps(result,indent=2,default=str),file_name="experimentiq_analysis.json",mime="application/json")
    c2.download_button("Export experiment CSV",df.to_csv(index=False),file_name="experimentiq_dataset.csv",mime="text/csv")
    with st.expander("Dataset preview — first 20 rows"):
        st.dataframe(df.head(20),hide_index=True,use_container_width=True)
    st.info("Privacy: Uploaded rows are processed by the Streamlit server. Hosted model calls receive only aggregate tool results; avoid sensitive datasets on public infrastructure.")

st.markdown('<div class="footer">EXPERIMENTIQ • REPRODUCIBLE PRODUCT SCIENCE • LANGGRAPH / STATS / HOSTED AI</div>',unsafe_allow_html=True)
