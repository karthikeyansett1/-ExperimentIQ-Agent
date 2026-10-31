from pathlib import Path
import pytest
from graph_agent import investigate
from engine import simulate


def test_hosted_mode_rejects_missing_key():
    with pytest.raises(ValueError, match='API key'):
        investigate(simulate(n=400), api_key='')


def test_no_fake_free_agent_ui():
    text = (Path(__file__).resolve().parents[1] / 'app.py').read_text()
    assert 'Free deterministic graph' not in text
    assert 'My own OpenAI API key' in text
