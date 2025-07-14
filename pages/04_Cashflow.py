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
annual_savings_pounds = np.zeros(years)

# Build CAPEX and energy savings
cumulative_saving_per_m2 = np.zeros(years)

for retrofit, data in retrofits.items():
    year_index = data["year"] - 1
    saving_per_m2 = data["saving"]
    cost_per_m2 = data["cost_per_m2"]
    total_cost = cost_per_m2 * floor_area_m2

    # CAPEX occurs in the completion year
    annual_capex[year_index] += total_cost

    # From year of completion onward, savings accumulate
    cumulative_saving_per_m2[year_index:] += saving_per_m2

# Compute annual kWh and £ savings
annual_savings_kwh = cumulative_saving_per_m2 * floor_area_m2
annual_savings_pounds = annual_savings_kwh * energy_cost_per_kwh

# Cash flow DataFrame
cashflow = pd.DataFrame({
    "Year": np.arange(1, years + 1),
    "CAPEX (GBP)": annual_capex,
    "Annual kWh Saved": annual_savings_kwh,
    "Annual Savings (GBP)": annual_savings_pounds,
    "Remaining Intensity (kWh/m²)": remaining_intensity
})

# Cumulative cashflow
cashflow["Cumulative Savings (GBP)"] = cashflow["Annual Savings (GBP)"].cumsum()
cashflow["Net Cashflow (GBP)"] = cashflow["Annual Savings (GBP)"] - cashflow["CAPEX (GBP)"]
cashflow["Cumulative Net Cashflow (GBP)"] = cashflow["Net Cashflow (GBP)"].cumsum()

# Display results
st.subheader("📈 Cash Flow Table")
st.dataframe(cashflow)

# Plot cumulative net cashflow
st.subheader("📊 Cumulative Net Cashflow Over Time")
fig, ax = plt.subplots()
ax.plot(cashflow["Year"], cashflow["Cumulative Net Cashflow (GBP)"], marker="o")
ax.set_xlabel("Year")
ax.set_ylabel("£")
ax.set_title("Cumulative Net Cashflow")
ax.grid(True)
st.pyplot(fig)
