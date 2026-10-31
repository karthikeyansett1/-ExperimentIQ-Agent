from engine import simulate, analyze, benchmark, power_approx

def test_conversion_analysis():
    result=analyze(simulate(n=1000,metric="conversion",effect=0.04),metric="conversion")
    assert 0<=result["p_value"]<=1

def test_sample_ratio_mismatch():
    result=analyze(simulate(n=1000,metric="conversion",srm=True),metric="conversion")
    assert any("ratio" in str(s).lower() or "SRM" in str(s) for s in result["warnings"])

def test_benchmark():
    assert benchmark()["total"]==20

def test_power():
    assert power_approx(0.2)>0
