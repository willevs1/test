import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.title("💰 Retrofit Cash Flow Analysis")

# Retrieve stored data from session state
selected_retrofits = st.session_state.get("selected_retrofit_data", {})
floor_area_m2 = st.session_state.get("floor_area_m2", 1000)
years = st.session_state.get("years", 10)
remaining_intensity = st.session_state.get("remaining_intensity_after_retrofits", np.full(years, np.nan))

# If no retrofits were selected, show warning
if not selected_retrofits:
    st.warning("⚠️ No retrofits selected on the Retrofit page.")
    st.stop()

# User input: energy price
energy_cost_per_kwh = st.number_input(
    "Energy Cost per kWh (£)",
    min_value=0.0,
    value=0.15,
    step=0.01
)

# Initialize arrays
annual_capex = np.zeros(years)
annual_savings_kwh = np.zeros(years)
annual_savings_pounds = np.zeros(years)

# Cumulative savings applied over time
cumulative_saving_per_m2 = np.zeros(years)

# Compute cashflows
for measure, data in selected_retrofits.items():
    year_idx = data["year"] - 1
    saving_per_m2 = data["saving"]
    cost_per_m2 = data["cost_per_m2"]
    total_cost = cost_per_m2 * floor_area_m2

    # CAPEX in year of completion
    annual_capex[year_idx] += total_cost

    # From year of completion onward, accumulate savings
    cumulative_saving_per_m2[year_idx:] += saving_per_m2

# Annual savings in kWh and £
annual_savings_kwh = cumulative_saving_per_m2 * floor_area_m2
annual_savings_pounds = annual_savings_kwh * energy_cost_per_kwh

# Build DataFrame
cashflow = pd.DataFrame({
    "Year": np.arange(1, years + 1),
    "Capex": annual_capex,
    "Annual kWh Saved": annual_savings_kwh,
    "Annual Energy Savings (£)": annual_savings_pounds,
    "Remaining Intensity (kWh/m²)": remaining_intensity
})

# Cumulative columns
cashflow["Cumulative Energy Savings (£)"] = cashflow["Annual Energy Savings (£)"].cumsum()
cashflow["Net Cashflow (£)"] = cashflow["Annual Energy Savings (£)"] - cashflow["Capex"]
cashflow["Cumulative Net Cashflow (£)"] = cashflow["Net Cashflow (£)"].cumsum()

# Display Table
st.subheader("📊 Cash Flow Table")
st.dataframe(cashflow.style.format({
    "Capex": "£{:.0f}",
    "Annual Energy Savings (£)": "£{:.0f}",
    "Cumulative Energy Savings (£)": "£{:.0f}",
    "Net Cashflow (£)": "£{:.0f}",
    "Cumulative Net Cashflow (£)": "£{:.0f}",
    "Annual kWh Saved": "{:.0f}",
    "Remaining Intensity (kWh/m²)": "{:.1f}"
}))

# Cumulative Net Cashflow Chart
import altair as alt

chart = alt.Chart(cashflow).mark_line(point=True).encode(
    x=alt.X("Year:O", title="Year"),
    y=alt.Y("Cumulative Net Cashflow", title="£"),
    tooltip=["Year", "Cumulative Net Cashflow", "Net Cashflow"]
).properties(
    width="container",
    height=400,
    title="Cumulative Net Cashflow Over Time"
).configure_axis(
    grid=True
)

st.altair_chart(chart, use_container_width=True)
