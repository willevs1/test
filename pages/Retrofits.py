import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

years = int(st.session_state["years"])

retrofit_options = {
    "LED Lighting Upgrade": 20,   # kWh/m² saved
    "HVAC Optimization": 35,
    "Solar PV Installation": 25,
    "Insulation Improvement": 40,
    "Building Management System": 30,
}

selected_retrofits = st.multiselect("Select retrofits to apply:", list(retrofit_options.keys()))

retrofit_years = {}
for retrofit in selected_retrofits:
    year = st.number_input(
        f"Year of completion for {retrofit}:",
        min_value=1,
        max_value=years,
        value=1
    )
    retrofit_years[retrofit] = year

# Initialize arrays
remaining_intensity = np.full(years, current_intensity)

# Compute cumulative reductions over time
for retrofit, saving in retrofit_options.items():
    if retrofit in selected_retrofits:
        year_done = retrofit_years[retrofit]
        # From year_done onward, reduce intensity
        remaining_intensity[year_done-1:] -= saving

# Ensure no negative intensities
remaining_intensity = np.clip(remaining_intensity, 0, None)


# Chart
st.subheader("Energy Intensity Over Time")
fig, ax = plt.subplots()
ax.plot(results["Year"], results["Remaining Intensity (kWh/m²)"], label="Remaining Intensity")
ax.axhline(target_intensity, color="red", linestyle="--", label="Target Intensity")
ax.set_xlabel("Year")
ax.set_ylabel("Energy Intensity (kWh/m²)")
ax.set_title("Energy Intensity Reduction Path")
ax.legend()
st.pyplot(fig)
