import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(
    page_title="💰 Retrofit Cash Flow",
    layout="wide",
)

st.title("💰 Retrofit Cash Flow Analysis")

# Safely load inputs, with defaults if missing
if "years" not in st.session_state:
    st.warning(
        "⚠️ You haven't completed the Analysis and Retrofit selection yet. "
        "Default values will be used."
    )

years = st.session_state.get("years", 5)
floor_area_m2 = st.session_state.get("floor_area_m2", 1000)
remaining_intensity = st.session_state.get(
    "remaining_intensity_after_retrofits",
    np.full(years, 100.0)
)
retrofits = st.session_state.get("selected_retrofit_data", {})

# Input: Energy cost per kWh
energy_cost_per_kwh = st.number_input(
    "Energy Cost per kWh (£):",
    min_value=0.0,
    value=0.15
)

# Initialize arrays
annual_capex = np.zeros(years)
cumulative_saving_per_m2 = np.zeros(years)

# Calculate CAPEX and cumulative savings per m²
for retrofit, data in retrofits.items():
    year_index = data["year"] - 1
    saving_per_m2 = data["saving"]
    cost_per_m2 = data["cost_per_m2"]
    total_cost = cost_per_m2 * floor_area_m2

    annual_capex[year_index] += total_cost
    cumulative_saving_per_m2[year_index:] += saving_per_m2

# Compute kWh savings and £ savings
annual_savings_kwh = cumulative_saving_per_m2 * floor_area_m2
annual_savings_gbp = annual_savings_kwh * energy_cost_per_kwh

# Assemble cashflow table
cashflow = pd.DataFrame({
    "Year": np.arange(1, years + 1),
    "Capex": annual_capex,
    "Annual_kWh_Saved": annual_savings_kwh,
    "Annual_GBP_Savings": annual_savings_gbp,
    "Remaining_Intensity_kWh_per_m2": remaining_intensity
})

cashflow["Cumulative_GBP_Savings"] = cashflow["Annual_GBP_Savings"].cumsum()
cashflow["Net_Cashflow"] = cashflow["Annual_GBP_Savings"] - cashflow["Capex"]
cashflow["Cumulative_Net_Cashflow"] = cashflow["Net_Cashflow"].cumsum()

# Display DataFrame
st.subheader("📊 Cash Flow Table")
st.dataframe(cashflow.style.format({
    "Capex": "£{:.0f}",
    "Annual_kWh_Saved": "{:.0f}",
    "Annual_GBP_Savings": "£{:.0f}",
    "Cumulative_GBP_Savings": "£{:.0f}",
    "Net_Cashflow": "£{:.0f}",
    "Cumulative_Net_Cashflow": "£{:.0f}",
    "Remaining_Intensity_kWh_per_m2": "{:.1f}"
}))

# Chart: Cumulative Net Cashflow
st.subheader("📈 Cumulative Net Cashflow Over Time")
chart = (
    alt.Chart(cashflow)
    .mark_line(point=True)
    .encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Cumulative_Net_Cashflow", title="Cumulative Net Cashflow (£)"),
        tooltip=[
            alt.Tooltip("Year:O"),
            alt.Tooltip("Cumulative_Net_Cashflow", title="Cumulative Net Cashflow (£)", format=",.0f")
        ]
    )
    .properties(
        width="container",
        height=400
    )
    .interactive()
)

st.altair_chart(chart, use_container_width=True)
