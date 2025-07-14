import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Retrieve stored variables from Analysis page
floor_area_m2 = st.session_state["floor_area_m2"]
current_energy_consumption = st.session_state["current_energy_consumption"]
target_intensity = st.session_state["target_intensity"]
years = st.session_state["years"]
current_intensity = st.session_state["current_intensity"]

# Define retrofits with savings and costs
retrofit_options = {
    "LED Lighting Upgrade": {"saving": 130, "cost": 50_000},
    "HVAC Optimization": {"saving": 121.6, "cost": 100_000},
    "Solar PV Installation": {"saving": 90, "cost": 200_000},
    "Insulation Improvement": {"saving": 70, "cost": 75_000},
    "Building Management System": {"saving": 60, "cost": 40_000},
}

st.title("💡 Retrofit Selection")

selected_retrofits = st.multiselect(
    "Select retrofits to apply:",
    list(retrofit_options.keys())
)

# Collect selected retrofit years
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

# Compute remaining intensity over time
remaining_intensity = np.full(years, current_intensity)

# Track selected retrofits with metadata
selected_retrofit_data = {}

for retrofit in selected_retrofits:
    year_done = retrofit_years[retrofit]
    saving = retrofit_options[retrofit]["saving"]
    cost = retrofit_options[retrofit]["cost"]
    
    # Store metadata
    selected_retrofit_data[retrofit] = {
        "year": year_done,
        "saving": saving,
        "cost": cost
    }
    
    # Subtract energy intensity from year_done onward
    remaining_intensity[year_done - 1:] -= saving

remaining_intensity = np.clip(remaining_intensity, 0, None)

# Chart
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

# Table
retrofit_results = pd.DataFrame({
    "Year": year_range,
    "Remaining Intensity (kWh/m²)": remaining_intensity
})
st.dataframe(retrofit_results)

# Store for use on other pages
st.session_state["selected_retrofit_data"] = selected_retrofit_data
st.session_state["remaining_intensity_after_retrofits"] = remaining_intensity
