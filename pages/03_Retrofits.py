import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.title("🏗️ Retrofit Planning")

# Load previously stored session variables
floor_area_m2 = st.session_state["floor_area_m2"]
current_intensity = st.session_state["current_intensity"]
target_intensity = st.session_state["target_intensity"]
years = st.session_state["years"]

# Define retrofit measures and phases
retrofit_options = {
    "Optimization": {
        "Reduce Tenant Loads": {"saving": 23.1, "cost_per_m2": 3},
        "BMS Upgrade": {"saving": 4.0, "cost_per_m2": 5},
    },
    "Light Retrofit": {
        "Low Energy Lighting": {"saving": 8.5, "cost_per_m2": 15},
        "Lighting Controls": {"saving": 5.7, "cost_per_m2": 5},
    },
    "Deep Retrofit": {
        "Wall Insulation": {"saving": 4.1, "cost_per_m2": 60},
        "Roof Insulation": {"saving": 1.5, "cost_per_m2": 20},
        "Window Replacement": {"saving": 7.4, "cost_per_m2": 60},
        "Air Source Heat Pump": {"saving": 17.6, "cost_per_m2": 50},
    },
    "Renewables": {
        "Solar PV": {"saving": 5.3, "cost_per_m2": 3},
    },
}

# Phase selection
st.subheader("Select Retrofit Measures and Timing")

selected_retrofits = {}

# Let the user pick measures and years
for phase, measures in retrofit_options.items():
    st.markdown(f"**{phase} Measures**")
    for measure, data in measures.items():
        col1, col2 = st.columns([3, 2])
        with col1:
            selected = st.checkbox(f"{measure} (Save {data['saving']} kWh/m²/yr, Cost £{data['cost_per_m2']}/m²)", key=measure)
        if selected:
            with col2:
                year = st.number_input(
                    f"Year of completion",
                    min_value=1,
                    max_value=years,
                    value=1,
                    key=f"{measure}_year"
                )
            selected_retrofits[measure] = {
                "saving": data["saving"],
                "cost_per_m2": data["cost_per_m2"],
                "year": year,
            }

# Calculate annual intensity
remaining_intensity = np.full(years, current_intensity)

# Apply reductions per selected measure
for measure, data in selected_retrofits.items():
    year_idx = data["year"] - 1
    remaining_intensity[year_idx:] -= data["saving"]

remaining_intensity = np.clip(remaining_intensity, 0, None)

# Store for cashflow page
st.session_state["selected_retrofit_data"] = selected_retrofits
st.session_state["remaining_intensity_after_retrofits"] = remaining_intensity

# Show graph
st.subheader("📊 Projected Energy Intensity Over Time")
years_range = np.arange(1, years + 1)

fig, ax = plt.subplots()
ax.plot(years_range, remaining_intensity, marker="o", label="Projected Intensity")
ax.axhline(target_intensity, color="red", linestyle="--", label="Target Intensity")
ax.set_xlabel("Year")
ax.set_ylabel("kWh/m²/year")
ax.set_title("Energy Intensity Trajectory")
ax.legend()
ax.grid(True)
st.pyplot(fig)
