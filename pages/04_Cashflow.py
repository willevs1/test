import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.title("💰 Retrofit Cash Flow Analysis")

# Check that retrofits were selected
if "selected_retrofit_data" not in st.session_state:
    st.warning("No retrofit data found. Please configure retrofits first.")
    st.stop()

# Retrieve stored data
retrofits = st.session_state["selected_retrofit_data"]
years = st.session_state["years"]
floor_area_m2 = st.session_state["floor_area_m2"]
remaining_intensity = st.session_state["remaining_intensity_after_retrofits"]

# Energy cost assumption
energy_cost_per_kwh = st.number_input(
    "Energy Cost per kWh (£)",
    min_value=0.0,
    value=0.15,
    step=0.01
)

# Initialize arrays
annual_capex = np.zeros(years)
cumulative_saving_per_m2 = np.zeros(years)

# Build CAPEX and energy savings
for retrofit, data in retrofits.items():
    year_index = data["year"] - 1
    saving_per_m2 = data["saving"]
    cost_per_m2 = data["cost_per_m2"]
    total_cost = cost_per_m2 * floor_area_m2

    # CAPEX occurs in the completion year
    annual_capex[year_index] += total_cost

    # From year of completion onwards, the savings accumulate
    cumulative_saving_per_m2[year_index:] += saving_per_m2

# Compute annual kWh savings and monetary savings
annual_savings_kwh = cumulative_saving_per_m2 * floor_area_m2
annual_savings_gbp = annual_savings_kwh * energy_cost_per_kwh

# Build the DataFrame
cashflow = pd.DataFrame({
    "Year": np.arange(1, years + 1),
    "CAPEX_GBP": annual_capex,
    "AnnualKwhSaved": annual_savings_kwh,
    "AnnualSavings_GBP": annual_savings_gbp,
    "RemainingIntensity": remaining_intensity
})

# Cumulative cashflow
cashflow["CumulativeSavings_GBP"] = cashflow["AnnualSavings_GBP"].cumsum()
cashflow["NetCashflow_GBP"] = cashflow["AnnualSavings_GBP"] - cashflow["CAPEX_GBP"]
cashflow["CumulativeNetCashflow_GBP"] = cashflow["NetCashflow_GBP"].cumsum()

# Display table
st.subheader("📊 Cash Flow Table")
st.dataframe(cashflow.style.format({
    "CAPEX_GBP": "£{:.0f}",
    "AnnualKwhSaved": "{:.0f} kWh",
    "AnnualSavings_GBP": "£{:.0f}",
    "CumulativeSavings_GBP": "£{:.0f}",
    "NetCashflow_GBP": "£{:.0f}",
    "CumulativeNetCashflow_GBP": "£{:.0f}"
}))

# Plot cumulative net cashflow
st.subheader("📈 Cumulative Net Cashflow Over Time")
chart = alt.Chart(cashflow).mark_line(point=True).encode(
    x=alt.X("Year:O", title="Year"),
    y=alt.Y("CumulativeNetCashflow_GBP", title="Cumulative Net Cashflow (£)"),
    tooltip=[
        alt.Tooltip("Year:O"),
        alt.Tooltip("CumulativeNetCashflow_GBP", format=",.0f", title="Cumulative Net £")
    ]
).properties(
    width="container",
    height=400,
    title="Cumulative Net Cashflow"
).configure_axis(
    grid=True
).configure_view(
    stroke=None
)

st.altair_chart(chart, use_container_width=True)
