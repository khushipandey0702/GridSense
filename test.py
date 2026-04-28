import pytest
import pandas as pd
import numpy as np
from app import process_dataframe, optimize_energy_distribution, prepare_forecasting_data, forecast_with_prophet

# 1. Test: CO2 Calculation Accuracy
def test_co2_functionality():
    data = {
        'Date': ['2025-01-01'],
        'Variable': ['Coal'],
        'Value': [50], 
        'Category': ['Electricity generation'],
        'Unit': ['GWh']
    }
    df = pd.DataFrame(data)
    processed_df = process_dataframe(df)
    assert processed_df.loc[0, 'CO2_Emissions_Tonnes'] == 50000.0

# 2. Test: AI Prophet Forecasting
def test_forecasting_functionality():
    dates = pd.date_range(start='2024-01-01', periods=24, freq='MS')
    df = pd.DataFrame({
        'Date': dates,
        'Variable': ['Solar']*24,
        'Value': np.random.randint(100, 200, size=24)
    })
    f_data = prepare_forecasting_data(df, 'Solar')
    assert f_data is not None
    model, forecast = forecast_with_prophet(f_data, periods=6)
    assert forecast is not None
    assert len(forecast) == 30

# 3. Test: Smart Grid Optimizer
def test_optimizer_normal():
    r_used, f_used, waste, cost = optimize_energy_distribution(1500, 1000, 1000)
    assert r_used == 1000 
    assert f_used == 500  

# 4. Test: Data Validation
def test_data_validation():
    empty_df = pd.DataFrame()
    assert process_dataframe(empty_df) is None
    
    missing_cols_df = pd.DataFrame({'Date': ['2025-01-01'], 'Value': [10]})
    assert process_dataframe(missing_cols_df) is None