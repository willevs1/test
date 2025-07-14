import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("💰 Retrofit Cash Flow Analysis")

# Retrieve stored data
retrofits = st.session_state["selected_retrofit_data"]
years = st.session_state["years"]
floor_area_m2 = st.session_state["floor_area_m2"]
remaining_intensity = st.session_state["remaining_intensity_after_retrofits"]

# Energy cost assumption
energy_cost_per_kwh = st.number_input(
    "Energy Cost per kWh (£)",
    min_value=0.0,
    value=0.15
)

# Initialize arrays
annual_capex = np.zeros(years)
annual_savings_kwh = np.zeros(years)
annual_savings_£ = np.zeros(years)

# Build CAPEX and energy savings
cumulative_saving_per_m2 = np.zeros(years)

for retrofit, data in retrofits.items():
    year_index = data["year"] - 1
    saving_per_m2 = data["saving"]
    cost = data["cost"]

    # CAPEX occurs in the completion year
    annual_capex[year_index] += cost

    # From year of completion onwards, the savings accumulate
    cumulative_saving_per_m2[year_index:] += saving_per_m2

# Compute annual kWh savings and monetary savings
annual_savings_kwh = cumulative_saving_per_m2 * floor_area_m2
annual_savings_£ = annual_savings_kwh * energy_cost_per_kwh
