import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("💰 Retrofit Cash Flow Analysis")

# Check for saved retrofit plan
if "retrofit_plan" not in st.session_state:
    st.warning("No retrofit plan found. Please go to the Retrofit Selection page first.")
    st.stop()

retrofits = st.session_state["retrofit_plan"]
floor_area_m2 = st.session_state["floor_area_m2"]
current_intensity = st.session_state["current_intensity"]
years = st.session_state["years"]

energy_cost_per_kwh = st.number_input(
    "Energy Cost per kWh (£)",
    min_value=0.0,
    value=0.15
)

# Initialize arrays
annual_capex = np.zeros(years)
cumulative_saving_per_m2 = np.zeros(years)

# Loop through retrofits
for measure, data in retrofits.items():
    year_index = data["year"] - 1
    saving_per_m2 = current_intensity * (data["saving_percent"] / 100)
    cost = data["cost_per_m2"] * floor_area_m2

    # CAPEX in implementation year
    annual_capex[year_index] += cost

    # Savings from that year onwards
    cumulative_saving_per_m2[year_index:] += saving_per_m2

# Calculate energy and monetary savings
annual_savings_kwh = cumulative_saving_per_m2 * floor_area_m2
annual_savings_pounds = annual_savings_kwh * energy_cost_per_kwh

# Create dataframe
cashflow = pd.DataFrame({
    "Year": np.arange(1, years + 1),
    "CAPEX": annual_capex,
    "Annual kWh Saved": annual_savings_kwh,
    "Annual Savings (£)": annual_savings_pounds,
})

cashflow["Cumulative Savings (£)"] = cashflow["Annual Savings (£)"].cumsum()
cashflow["Net Cashflow (£)"] = cashflow["Annual Savings (£)"] - cashflow["CAPEX"]
cashflow["Cumulative Net Cashflow (£)"] = cashflow["Net Cashflow (£)"].cumsum()

# Display table
st.subheader("📈 Cash Flow Table")
st.dataframe(cashflow)

# Plot
st.subheader("📊 Cumulative Net Cashflow Over Time")
fig, ax = plt.subplots()
ax.plot(cashflow["Year"], cashflow["Cumulative Net Cashflow (£)"], marker="o")
ax.set_xlabel("Year")
ax.set_ylabel("£")
ax.set_title("Cumulative Net Cashflow")
ax.grid(True)
st.pyplot(fig)
