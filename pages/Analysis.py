import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="ESG Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("📊 ESG Retrofit and Stranding Risk Analysis")

st.write("Enter your building and financial parameters below:")

# Inputs in the MAIN BODY (not sidebar)
floor_area_m2 = st.number_input("Floor Area (m²)", min_value=1, value=5000)

current_energy_consumption = st.number_input(
    "Current Energy Consumption (kWh/year)",
    min_value=0.0,
    value=100000.0
)

target_intensity = st.number_input(
    "Target Intensity (kWh/m²/year)",
    min_value=0.0,
    value=75.0
)

years = st.slider(
    "Years to Reach Target",
    min_value=1,
    max_value=30,
    value=10
)

st.session_state["years"] = years

)

# Calculations
current_intensity = current_energy_consumption / floor_area_m2

st.session_state["current_intensity"] = current_intensity

annual_reduction = (current_intensity - target_intensity) / years
kwh_saved_per_m2 = np.linspace(0, current_intensity - target_intensity, years)
total_kwh_saved = kwh_saved_per_m2 * floor_area_m2
remaining_intensity = current_intensity - kwh_saved_per_m2


# Results
results = pd.DataFrame({
    "Year": np.arange(1, years + 1),
    "kWh Saved per m²": kwh_saved_per_m2,
    "Remaining Intensity (kWh/m²)": remaining_intensity
})

st.subheader("Simulation Results")
st.dataframe(results)

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
