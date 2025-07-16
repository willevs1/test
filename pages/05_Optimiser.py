import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("🛠 Retrofit Optimiser (Minimal Annual Spend Strategy)")

# Check that prior data is available
required_keys = ["floor_area_m2", "current_intensity", "target_intensity", "years"]
if not all(k in st.session_state for k in required_keys):
    st.warning("Missing required session data. Please complete previous steps first.")
    st.stop()

# Retrieve inputs
floor_area_m2 = st.session_state["floor_area_m2"]
current_intensity = st.session_state["current_intensity"]
target_intensity = st.session_state["target_intensity"]
years = st.session_state["years"]

# Define your retrofit options exactly as given
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

# Flatten retrofit options to a DataFrame
retrofit_list = []
for category, measures in retrofit_options.items():
    for name, props in measures.items():
        retrofit_list.append({
            "Category": category,
            "Measure": name,
            "Saving": props["saving"],
            "Cost_per_m2": props["cost_per_m2"],
            "Efficiency": props["cost_per_m2"] / props["saving"] if props["saving"] else np.inf,
        })

df_retrofits = pd.DataFrame(retrofit_list)
df_retrofits = df_retrofits.sort_values("Efficiency")

# Determine required reduction
required_reduction = current_intensity - target_intensity
st.info(f"Required reduction: **{required_reduction:.2f} kWh/m²** over {years} years.")

# Select measures cumulatively until target is reached
selected = []
cumulative_saving = 0.0
for _, row in df_retrofits.iterrows():
    if cumulative_saving >= required_reduction:
        break
    selected.append(row)
    cumulative_saving += row["Saving"]

if not selected:
    st.error("No retrofits selected. Target may already be met.")
    st.stop()

# Schedule retrofits: spread them as evenly as possible over years
schedule = {}
step = max(1, years // len(selected))
current_year = 1
for i, row in enumerate(selected):
    schedule[row["Measure"]] = current_year
    current_year += step
    if current_year > years:
        current_year = years  # Keep any extra in the final year

# Build emissions trajectory
remaining_intensity = np.full(years, current_intensity)
for measure, year in schedule.items():
    saving = df_retrofits.loc[df_retrofits["Measure"] == measure, "Saving"].values[0]
    remaining_intensity[year-1:] -= saving

remaining_intensity = np.clip(remaining_intensity, 0, None)

# Store selected retrofits in session_state
st.session_state["selected_retrofit_data"] = {
    measure: {
        "year": year,
        "saving": df_retrofits.loc[df_retrofits["Measure"] == measure, "Saving"].values[0],
        "cost_per_m2": df_retrofits.loc[df_retrofits["Measure"] == measure, "Cost_per_m2"].values[0],
    }
    for measure, year in schedule.items()
}
st.session_state["remaining_intensity_after_retrofits"] = remaining_intensity

# Display selected measures and schedule
st.subheader("Selected Retrofit Measures")
plan_df = pd.DataFrame([
    {
        "Measure": measure,
        "Year of Install": data["year"],
        "Saving (kWh/m²)": data["saving"],
        "Cost (£/m²)": data["cost_per_m2"],
        "Category": df_retrofits.loc[df_retrofits["Measure"] == measure, "Category"].values[0]
    }
    for measure, data in st.session_state["selected_retrofit_data"].items()
])
st.dataframe(plan_df)

# Show emissions trajectory
st.subheader("Projected Energy Intensity Over Time")
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(np.arange(1, years + 1), remaining_intensity, marker="o", label="Remaining Intensity")
ax.axhline(target_intensity, color="red", linestyle="--", label="Target")
ax.set_xlabel("Year")
ax.set_ylabel("kWh/m²")
ax.set_title("Trajectory of Energy Intensity")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# Show estimated annual CAPEX
annual_capex = np.zeros(years)
for measure, data in st.session_state["selected_retrofit_data"].items():
    year_idx = data["year"] - 1
    annual_capex[year_idx] += data["cost_per_m2"] * floor_area_m2

capex_df = pd.DataFrame({
    "Year": np.arange(1, years + 1),
    "Estimated CAPEX (£)": annual_capex
})
st.subheader("Estimated Annual Spend")
st.bar_chart(capex_df.set_index("Year"))
