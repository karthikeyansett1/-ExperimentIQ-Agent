# Final deployment checklist — ExperimentIQ Cloud

## 1. Before GitHub

- Confirm repository is **separate** from SchemaGuard.
- Do not commit `.streamlit/secrets.toml` or API keys. Check `git status` and `git diff --cached`.
- Run `python -m pytest -q` locally (7 tests expected in this release).
- Verify `app.py` imports, and that the sample data renders in the Overview, Validity Monitor and Evaluation Lab.

## 2. First live cloud test (bring your own key)

- On Streamlit Community Cloud select the repo, `main`, and `app.py`; use Python 3.12.
- Leave cloud Secrets empty at first.
- Open the deployment in a private browser window; confirm free statistics display.
- In AI Decision Agent choose **My own OpenAI API key**; supply a project key you control.
- Run one prompt asking it to call `get_experiment_results`; verify a trace event and report.
- Check your actual API usage, not merely the on-screen estimate.

## 3. Optional recruiter access

- Only add `OPENAI_API_KEY` and `DEMO_ACCESS_CODE` to cloud Secrets when you intentionally want shared-key usage.
- Share code privately; it is not a login system or global security boundary.
- The 3-run-per-session control can be reset and must **not** be relied on to enforce spend limits.
- Set billing alerts and leave auto-reload off. Even alerts/spend limits may not be hard enforced.
- Prefer BYOK for unknown visitors. Remove the server-side API key from Streamlit Secrets when demos end.

## 4. GitHub documentation

- Add an actual deployed app URL to README.
- Screenshot Overview, Validity Monitor, agent's actual tool trace, and Evaluation Lab.
- Do not claim the 20-case synthetic benchmark measures LLM accuracy.
- No uploaded participant rows are sent to the model, but the Streamlit server itself processes those rows; don't upload sensitive data.
