import pandas as pd
from app.routers.turbine import calculate_analytics
from app import models

def test_calculate_analytics_logic():
    data = {
        'timestamp': ['2025-09-23T10:00:00'], 't1': [15.0], 't2': [310.0],
        'p1': [1.0], 'p2': [12.0], 't48': [550.0], 'p48': [1.1],
        'gtt': [1000.0], 'gtn': [3600.0], 'ggn': [3400.0], 'ts': [45.0],
        'tp': [46.0], 'mf': [0.25], 'decay_coeff_comp': [0.98], 'decay_coeff_turbine': [0.97],
        'lp': [0], 'v': [0], 'pexh': [0], 'tic': [0]
    }
    sample_df = pd.DataFrame(data)
    report = calculate_analytics(sample_df)
    
    assert abs(report.turbine_stats.power_proxy_kw.avg - 376991.11) < 1.0