import pandas as pd
import numpy as np
from prophet import Prophet
from pulp import LpProblem, LpVariable, LpMinimize, LpStatus, value
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import warnings

warnings.filterwarnings('ignore')

# --- CONFIGURATION ---
st.set_page_config(page_title="GridSense: AI-powered Smart Grid Energy Management", layout="wide")

# --- DATA PROCESSING FUNCTIONS ---

def process_dataframe(df):
    """
    Cleans and prepares a dataframe once it is loaded into memory.
    """
    try:
        df.columns = df.columns.str.strip()
        
        # Validation: Ensure required columns exist
        required = ['Date', 'Value', 'Variable', 'Category', 'Unit']
        missing = [c for c in required if c not in df.columns]
        if missing:
            st.error(f"Missing required columns: {missing}")
            return None

        # Clean Date and Value
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date', 'Value'])
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        df = df.dropna(subset=['Value'])

        # CO₂ Emission Calculation logic (FIXED MATH)
        # Factor is Tonnes of CO2 per MWh
        emission_factors = {
            'Coal': 1.00, 'Gas': 0.45, 'Gas and Other Fossil': 0.60,
            'Other Fossil': 0.78, 'Fossil': 0.85, 'Solar': 0, 'Wind': 0,
            'Hydro': 0, 'Bioenergy': 0, 'Other Renewables': 0, 'Nuclear': 0
        }
        
        df['CO2_Emissions_Tonnes'] = 0.0
        for energy_source, factor in emission_factors.items():
            # If Unit is GWh, we multiply by 1000 to get MWh, then by factor
            mask = (df['Variable'] == energy_source) & (df['Unit'] == 'GWh')
            df.loc[mask, 'CO2_Emissions_Tonnes'] = df.loc[mask, 'Value'] * 1000 * factor
        
        return df
    except Exception as e:
        st.error(f"Preprocessing error: {e}")
        return None

def prepare_forecasting_data(df, variable_name):
    variable_data = df[df['Variable'] == variable_name].copy()
    if len(variable_data) < 2: return None
    forecast_df = variable_data[['Date', 'Value']].rename(columns={'Date': 'ds', 'Value': 'y'})
    return forecast_df

def forecast_with_prophet(data, periods=12):
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=periods, freq='MS')
    forecast = model.predict(future)
    return model, forecast

def optimize_energy_distribution(demand, renewable_capacity, fossil_capacity):
    costs = {'Renewable': 20, 'Fossil': 50}
    co2_emissions = {'Renewable': 0.05, 'Fossil': 0.8}
    co2_weight = 100

    prob = LpProblem("Energy_Optimization", LpMinimize)
    renewable_used = LpVariable("Renewable_Used", 0, renewable_capacity)
    fossil_used = LpVariable("Fossil_Used", 0, fossil_capacity)
    energy_waste = LpVariable("Energy_Waste", 0, None)

    prob += (costs['Renewable'] * renewable_used + costs['Fossil'] * fossil_used) + \
            co2_weight * (co2_emissions['Renewable'] * renewable_used + co2_emissions['Fossil'] * fossil_used)

    prob += renewable_used + fossil_used - energy_waste == demand
    prob.solve()

    if LpStatus[prob.status] != 'Optimal':
        return None, None, None, None

    total_monetary_cost = value(costs['Renewable'] * renewable_used + costs['Fossil'] * fossil_used)
    return value(renewable_used), value(fossil_used), value(energy_waste), total_monetary_cost

# --- VISUALIZATION FUNCTIONS ---

def plot_forecast(forecast, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast', line=dict(color='#00CC96')))
    fig.update_layout(title=title, xaxis_title='Date', yaxis_title='Value (GWh)', height=450, template="plotly_dark")
    return fig

def plot_energy_mix(df):
    var_counts = df.groupby('Variable')['Value'].sum().reset_index()
    fig = px.pie(var_counts, values='Value', names='Variable', 
                 title="Total Generation Mix (by Source)")
    fig.update_layout(height=450, template="plotly_dark")
    return fig

# --- MAIN APP ---

def main():
    st.title("GridSense: AI-powered Smart Grid Energy Management")
    st.markdown("---")

    st.sidebar.header("📥 Data Management")
    uploaded_file = st.sidebar.file_uploader("Upload Energy Dataset", type=["xlsx", "csv"])
    
    st.sidebar.header("⚙️ Configuration")
    forecast_periods = st.sidebar.slider("Forecast Periods (Months)", 6, 36, 12)
    renewable_capacity = st.sidebar.number_input("Max Renewable Capacity (MWh)", min_value=0, value=2000)
    fossil_capacity = st.sidebar.number_input("Max Fossil Capacity (MWh)", min_value=0, value=5000)
    demand = st.sidebar.number_input("Target Energy Demand (MWh)", min_value=0, value=6000)

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_raw = pd.read_csv(uploaded_file)
            else:
                df_raw = pd.read_excel(uploaded_file, engine="openpyxl")
            
            df = process_dataframe(df_raw)
            if df is not None:
                st.sidebar.success("✅ Data Loaded")
            else:
                st.stop()
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()
    else:
        st.info("Please upload a dataset to begin.")
        st.stop()

    st.header("📊 Real-Time Data Overview")
    st.dataframe(df, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Summary Statistics")
        st.dataframe(df.describe(), use_container_width=True)
    with col2:
        st.plotly_chart(plot_energy_mix(df), use_container_width=True)

    st.markdown("---")
    st.header("📈 AI Forecasting")
    target_var = st.selectbox("Select Source to Forecast:", df['Variable'].unique())

    if st.button("Generate Forecast"):
        f_data = prepare_forecasting_data(df, target_var)
        if f_data is not None:
            model, forecast = forecast_with_prophet(f_data, periods=forecast_periods)
            st.plotly_chart(plot_forecast(forecast, f"{target_var} Forecast"), use_container_width=True)
        else:
            st.warning("Insufficient data.")

    st.markdown("---")
    st.header("⚖️ Optimization")
    if st.button("Run Optimization"):
        r_used, f_used, waste, cost = optimize_energy_distribution(demand, renewable_capacity, fossil_capacity)
        if r_used is not None:
            st.metric("Total Cost", f"${cost:,.2f}")
            fig_opt = px.bar(x=['Renewable', 'Fossil'], y=[r_used, f_used], title="Grid Distribution")
            st.plotly_chart(fig_opt, use_container_width=True)

if __name__ == "__main__":
    main()