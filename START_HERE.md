# ExperimentIQ — Complete top-to-bottom setup

## 0. Important choice

This is a **different GitHub repository from SchemaGuard**. Use the included complete project folder and do not merge it into the older Ollama-only ExperimentIQ prototype.

## 1. Folder layout

```text
Project 2/ExperimentIQ_Cloud_Pro/
  app.py
  engine.py
  graph_agent.py
  requirements.txt
  README.md
  .streamlit/config.toml
  .streamlit/secrets.example.toml
  assets/console.css
  tests/
  .github/workflows/tests.yml
```

## 2. Install on your Mac

Open `ExperimentIQ_Cloud_Pro` itself in VS Code (not Project 2). Terminal:

```bash
pwd
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

If terminal already shows `(.venv)`, first run `which python` and confirm it is in this project folder. If port 8501 is occupied, Streamlit proposes 8502.

## 3. Validate the statistical dashboard

- Overview: metric cards and effect confidence interval display.
- Validity Monitor: switch on synthetic SRM; it should show an allocation warning and a HOLD decision.
- AI Decision Agent: confirm credential entry is required; do not enter a key until ready for a paid tool-call test.
- Evaluation Lab: run the 20-scenario benchmark and export CSV.
- Data & Reports: export result JSON and sample dataset.

## 4. Validate the paid cloud model locally

Visit https://platform.openai.com/api-keys to create a key and enable API billing. The ChatGPT Plus subscription does not pay for API usage.

In the agent tab, choose AI Decision Agent → My own OpenAI API key. Paste key, run the example "Validity and decision".

Verify the tool trace contains `get_experiment_results`; download JSON. Never commit screenshots containing a key.

If you see model not found, check your project's model entitlement and the current documented model name. This package uses `gpt-6-luna` as of October 2026; update MODEL in graph_agent.py only if required.

## 5. Add a secure recruiter demo access code (optional)

Only after you've configured provider-side spending limits:

1. Generate a long unpredictable secret code locally.
2. Create `.streamlit/secrets.toml` locally (gitignored) or set the following as Streamlit Cloud Secrets:

```toml
OPENAI_API_KEY = "YOUR_KEY"
DEMO_ACCESS_CODE = "LONG_UNGUESSABLE_CODE"
```

3. Never paste the secret into README, screenshots, git commits, or the public UI.
4. Give the code privately to an interviewer who you trust.

A Streamlit `st.session_state` limit is not a global billing cap; it can be bypassed by opening a new browser session. If you cannot establish a provider-side spend limit that suits your $20 budget, **do not set `OPENAI_API_KEY` on the public app**. BYOK remains available without your own key.

## 6. Publish to separate GitHub repository

Create a public repository `ExperimentIQ-Agent` without initializing an online README. From project root:

```bash
git init
git branch -M main
git add .
git status
git commit -m "Build cloud-first LangGraph experimentation analyst"
git remote add origin https://github.com/YOUR_USERNAME/ExperimentIQ-Agent.git
git push -u origin main
```

If your remote contains newer work, use `git pull --rebase origin main` before pushing. Never force-push casually.

## 7. Deploy to Streamlit Cloud

- https://share.streamlit.io → Create app
- Repo: `YOUR_USERNAME/ExperimentIQ-Agent`
- Branch: `main`
- Entrypoint: `app.py`
- Python: `3.12`
- Advanced → Secrets: empty is fine for BYOK and the free statistical dashboard
- Choose a short app URL such as `experimentiq-agent` if available

Test in a private/incognito window to ensure public accessibility. The app needs no separate backend server or GPU. Hosted model requests go from your Streamlit Python process directly to the OpenAI API.

## 8. Screenshot checklist

After real deployment, capture Overview, Validity Monitor showing SRM, AI Decision Agent with verified tool trace, Evaluation Lab. Store under `docs/screenshots/` and add links in README.

## 9. What to say in interview

"I built an experimentation agent where SciPy and Statsmodels own numerical inference, LangGraph handles conditional orchestration, and a hosted LLM accesses bounded analytics and methodology tools. I separately evaluate statistical decision rules and actual LLM tool selection. The free public dashboard always runs, while paid AI access is opt-in and credential-gated."

## 10. Deployment and budget limitations

- Model API availability and account billing requirements are external to this package.
- No rate-limit/security scheme based solely on session state is globally reliable.
- Public app credentials must be stored in Cloud secrets, never in GitHub.
- An optional recruiter demo passcode is access gating, not full authentication or abuse prevention.
