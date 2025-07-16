import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("🛠 Retrofit Optimiser")

# Check data is available
required_keys = ["floor_area_m2", "current_intensity", "target_intensity"]
if not all(k in st.session_state for k in required_keys):
    st.warning("Missing required session data. Please complete previous steps first.")
    st.stop()

# Input values
floor_area_m2 = st.session_state["floor_area_m2"]
current_intensity = st.session_state["current_intensity"]
target_intensity = st.session_state["target_intensity"]
years = st.session_state["years"]

# Available retrofits
retrofit_options = {
    "LED Lighting Upgrade": {"saving": 30, "cost_per_m2": 25},
    "HVAC Optimization": {"saving": 40, "cost_per_m2": 35},
    "Solar PV Installation": {"saving": 45, "cost_per_m2": 50},
    "Insulation Improvement": {"saving": 35, "cost_per_m2": 30},
    "Building Management System": {"saving": 25, "cost_per_m2": 20},
}

# Display options
st.subheader("Available Retrofit Options")
retrofit_df = pd.DataFrame([
    {"Retrofit": name, **vals,
     "efficiency": vals["cost_per_m2"] / vals["saving"]}
    for name, vals in retrofit_options.items()
]).sort_values("efficiency")

st.dataframe(retrofit_df)

# Compute required savings
total_required_saving = current_intensity - target_intensity
st.info(f"🔍 Total required reduction: **{total_required_saving:.1f} kWh/m²**")

# Greedy optimisation: cheapest per unit saving first
selected_upgrades = []
cumulative_saving = 0

for name, row in retrofit_df.iterrows():
    if cumulative_saving >= total_required_saving:
        break
    selected_upgrades.append({
        "name": row["Retrofit"],
        "saving": row["saving"],
        "cost_per_m2": row["cost_per_m2"],
        "efficiency": row["efficiency"]
    })
    cumulative_saving += row["saving"]

# Schedule upgrades across years
savings_schedule = np.full(years, current_intensity)
year_plan = {}
current_year = 1

for upgrade in selected_upgrades:
    savings_schedule[current_year - 1:] -= upgrade["saving"]
    year_plan[upgrade["name"]] = current_year
    current_year += 1

# Ensure no negatives
savings_schedule = np.clip(savings_schedule, 0, None)

# Store for use in other pages
retrofit_output = {
    item["name"]: {
        "year": year_plan[item["name"]],
        "saving": item["saving"],
        "cost_per_m2": item["cost_per_m2"]
    }
    for item in selected_upgrades
}
st.session_state["selected_retrofit_data"] = retrofit_output
st.session_state["remaining_intensity_after_retrofits"] = savings_schedule

# Show result
st.subheader("📋 Optimised Retrofit Plan")
plan_df = pd.DataFrame([
    {
        "Retrofit": name,
        "Saving (kWh/m²)": data["saving"],
        "Cost (£/m²)": data["cost_per_m2"],
        "Year": data["year"]
    }
    for name, data in retrofit_output.items()
])
st.dataframe(plan_df)

# Chart
st.subheader("📉 Emissions Trajectory with Optimised Retrofits")
fig, ax = plt.subplots()
ax.plot(np.arange(1, years + 1), savings_schedule, marker="o", label="Remaining Intensity")
ax.axhline(target_intensity, color="red", linestyle="--", label="Target Intensity")
ax.set_xlabel("Year")
ax.set_ylabel("Energy Intensity (kWh/m²)")
ax.set_title("Projected Intensity Reduction Path")
ax.grid(True)
ax.legend()
st.pyplot(fig)
