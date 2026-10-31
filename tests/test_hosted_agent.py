"""Offline test of hosted tool calling with a mocked OpenAI client.
No API key, network requests, or LangGraph installation required for this test.
"""
from types import SimpleNamespace
import json
from graph_agent import hosted, retrieve, validate, report, MODEL
from engine import simulate

class ToolCall:
    type='function_call'
    name='get_experiment_results'
    call_id='call_test'
    arguments='{}'
    def model_dump(self, exclude_none=True):
        return {"type":"function_call","name":self.name,"call_id":self.call_id,"arguments":self.arguments}

class FakeResult:
    def __init__(self, tools):
        self.output=[ToolCall()] if tools else []
        self.output_text='' if tools else '## Decision\nThe evidence requires review.'
        self.usage=SimpleNamespace(input_tokens=99,output_tokens=55)

class FakeResponses:
    def __init__(self): self.count=0
    def create(self,**kwargs):
        self.count+=1
        assert kwargs['model']==MODEL
        assert kwargs['store'] is False
        assert kwargs['max_output_tokens']<=550
        if self.count==1: assert kwargs['tool_choice']=='required'
        return FakeResult(self.count==1)

class FakeClient:
    def __init__(self,**kwargs): self.responses=FakeResponses()

def test_mocked_hosted_tool_call(monkeypatch):
    import sys
    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=FakeClient))
    base={'data':simulate(n=400,seed=13),'metric':'conversion','question':'check validity'}
    s={**base,**validate(base)}
    s.update(retrieve(s))
    result=hosted(s,api_key='secret-key-should-never-appear')
    assert result['model_status']=='completed'
    assert result['trace'][0]['tool']=='get_experiment_results'
    assert result['tokens']['input_tokens']==198
    assert 'secret-key' not in json.dumps(result)
    s.update(result)
    final=report(s)['report']
    assert 'Deterministic gate' in final

def test_uploaded_variant_validation():
    df=simulate(n=400)
    df.loc[0,'variant']='unknown'
    from engine import analyze
    import pytest
    with pytest.raises(ValueError,match='variant'):
        analyze(df)

def test_bool_peeking_string_false_not_true():
    df=simulate(n=400)
    df['peeked']='False'
    from engine import analyze
    assert not any('peeking' in w.lower() for w in analyze(df)['warnings'])
