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

# Cash flow DataFrame
cashflow = pd.DataFrame({
    "Year": np.arange(1, years + 1),
    "CAPEX (£)": annual_capex,
    "Annual kWh Saved": annual_savings_kwh,
    "Annual £ Savings": annual_savings_£,
    "Remaining Intensity (kWh/m²)": remaining_intensity
})

# Cumulative cashflow
cashflow["Cumulative £ Savings"] = cashflow["Annual £ Savings"].cumsum()
cashflow["Net Cashflow (£)"] = cashflow["Annual £ Savings"] - cashflow["CAPEX (£)"]
cashflow["Cumulative Net Cashflow (£)"] = cashflow["Net Cashflow (£)"].cumsum()

# Display results
st.subheader("📈 Cash Flow Table")
st.dataframe(cashflow)

# Plot cumulative cashflow
st.subheader("📊 Cumulative Net Cashflow Over Time")
fig, ax = plt.subplots()
ax.plot(cashflow["Year"], cashflow["Cumulative Net Cashflow (£)"], marker="o")
ax.set_xlabel("Year")
ax.set_ylabel("£")
ax.set_title("Cumulative Net Cashflow")
ax.grid(True)
st.pyplot(fig)
