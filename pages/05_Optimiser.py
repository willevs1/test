import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="🔍 Retrofit Optimiser",
    layout="wide",
)

st.title("🔍 Retrofit Optimiser")

# Retrieve session state
floor_area_m2 = st.session_state.get("floor_area_m2", 1000)
current_intensity = st.session_state.get("current_intensity", 100.0)
target_intensity = st.session_state.get("target_intensity", 40.0)
years = st.session_state.get("years", 5)
annual_reduction = st.session_state.get("annual_reduction", 0)
selected_retrofits = st.session_state.get("selected_retrofit_data", {})

if not selected_retrofits:
    st.warning("⚠️ No retrofits have been selected. Please select retrofits on the Retrofit page first.")
    st.stop()

# Create DataFrame of selected retrofits
retrofit_df = pd.DataFrame([
    {
        "name": retrofit,
        "saving": data["saving"],
        "cost_per_m2": data["cost_per_m2"]
    }
    for retrofit, data in selected_retrofits.items()
])

# Sort by cost efficiency (£/kWh saved)
retrofit_df["cost_per_kwh_saved"] = retrofit_df["cost_per_m2"] / retrofit_df["saving"]
retrofit_df = retrofit_df.sort_values("cost_per_kwh_saved")

# Optimise: Select retrofits until target achieved
remaining = current_intensity
chosen_retrofits = []
cumulative_saving = 0

for _, row in retrofit_df.iterrows():
    if remaining <= target_intensity:
        break
    chosen_retrofits.append(row)
    remaining -= row["saving"]
    cumulative_saving += row["saving"]

# Build output DataFrame
result_df = pd.DataFrame(chosen_retrofits)
result_df["total_cost"] = result_df["cost_per_m2"] * floor_area_m2

# Show results
st.subheader("📊 Optimised Retrofit Selection")
st.dataframe(result_df[["name", "saving", "cost_per_m2", "cost_per_kwh_saved", "total_cost"]])

final_intensity = max(target_intensity, remaining)
total_spend = result_df["total_cost"].sum()

st.success(
    f"✅ Achieved Intensity after Optimisation: {final_intensity:.1f} kWh/m²"
)
st.info(
    f"💰 Total Estimated Spend: £{total_spend:,.0f}"
)

# Prepare data for graph
years_array = np.arange(1, years + 1)

# Baseline: Only annual reductions
baseline_intensity = np.maximum(
    current_intensity - annual_reduction * (years_array - 1),
    target_intensity
)

# Optimised: Annual reductions plus cumulative retrofit savings
optimised_intensity = np.maximum(
    current_intensity - cumulative_saving - annual_reduction * (years_array - 1),
    target_intensity
)

# Plot comparison
st.subheader("📈 Energy Intensity Over Time (Baseline vs. Optimised)")

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(years_array, baseline_intensity, label="Baseline (No Retrofits)", marker="o")
ax.plot(years_array, optimised_intensity, label="Optimised Scenario", marker="o")
ax.axhline(target_intensity, color="red", linestyle="--", label="Target Intensity")
ax.set_xlabel("Year")
ax.set_ylabel("Energy Intensity (kWh/m²)")
ax.set_title("Energy Intensity Reduction Path")
ax.legend()
ax.grid(True)

st.pyplot(fig)
