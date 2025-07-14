import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Retrieve stored variables
floor_area_m2 = st.session_state["floor_area_m2"]
current_energy_consumption = st.session_state["current_energy_consumption"]
target_intensity = st.session_state["target_intensity"]
years = st.session_state["years"]
current_intensity = st.session_state["current_intensity"]

# Retrofit options (in kWh/m²/year)
retrofit_options = {
    "LED Lighting Upgrade": 130,
    "HVAC Optimization": 121.6,
    "Solar PV Installation": 121.6,
    "Insulation Improvement": 121.6,
    "Building Management System": 121.6,
}

st.subheader("Retrofit Scenario")

selected_retrofits = st.multiselect("Select retrofits to apply:", list(retrofit_options.keys()))

retrofit_years = {}
for retrofit in selected_retrofits:
    year = st.number_input(
        f"Year of completion for {retrofit}:",
        min_value=1,
        max_value=years,
        value=1,
        key=f"year_{retrofit}"
    )
    retrofit_years[retrofit] = year

# Initialize
remaining_intensity = np.full(years, current_intensity)

# Apply retrofits
for retrofit, saving in retrofit_options.items():
    if retrofit in selected_retrofits:
        year_done = retrofit_years[retrofit]
        remaining_intensity[year_done-1:] -= saving

# Clip to avoid negatives
remaining_intensity = np.clip(remaining_intensity, 0, None)

# Display chart
st.subheader("Energy Intensity Over Time (with Retrofits)")
fig, ax = plt.subplots()
year_range = np.arange(1, years + 1)

ax.plot(year_range, remaining_intensity, label="Remaining Intensity After Retrofits", color="green")
ax.axhline(target_intensity, color="red", linestyle="--", label="Target Intensity")
ax.set_xlabel("Year")
ax.set_ylabel("Energy Intensity (kWh/m²)")
ax.set_title("Energy Intensity Reduction Path with Retrofits")
ax.legend()

st.pyplot(fig)

# Also show as a table
retrofit_results = pd.DataFrame({
    "Year": year_range,
    "Remaining Intensity (kWh/m²)": remaining_intensity
})
st.dataframe(retrofit_results)
