import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Building Decarbonization Model", layout="wide")

st.title("🏢 Decarbonization Pathway and Stranding Risk Calculator")

# Sidebar Inputs
st.sidebar.header("Building Parameters")

building_area = st.sidebar.number_input(
    "Building Area (m²)",
    min_value=100.0,
    value=10_000.0
)

baseline_intensity = st.sidebar.number_input(
    "Baseline Energy Intensity (kWh/m²/year)",
    min_value=50.0,
    value=200.0
)

energy_price = st.sidebar.number_input(
    "Energy Price (€/kWh)",
    min_value=0.01,
    value=0.15
)

carbon_price = st.sidebar.number_input(
    "Carbon Price (€/ton CO₂)",
    min_value=0.0,
    value=50.0
)

emissions_factor = st.sidebar.number_input(
    "CO₂ Factor (tons CO₂ per kWh)",
    min_value=0.0,
    value=0.0002
)

discount_rate = st.sidebar.slider(
    "Discount Rate",
    min_value=0.0,
    max_value=0.2,
    value=0.05,
    step=0.005
)

# Retrofit measures
st.sidebar.header("Retrofit Measures (per m²)")
retrofits = pd.DataFrame({
    "Measure": ["LED Upgrade", "HVAC Replacement", "Heat Pump", "Solar PV"],
    "Capex €/m²": [5, 30, 40, 20],
    "kWh saved/m²/year": [5, 12, 18, 8]
}).set_index("Measure")

selected_measures = st.sidebar.multiselect(
    "Select Retrofit Measures:",
    options=retrofits.index
)

# Trajectory: target kWh/m²/year
target_trajectory = {
    1: 180,
    5: 160,
    10: 130,
    15: 100,
    20: 70
}
years = np.arange(1, 21)
target_values = np.interp(
    years,
    list(target_trajectory.keys()),
    list(target_trajectory.values())
)

# Only compute if measures selected
if selected_measures:
    selected = retrofits.loc[selected_measures]
    
    total_capex_per_m2 = selected["Capex €/m²"].sum()
    capex_total = total_capex_per_m2 * building_area

    total_kwh_savings_per_m2 = selected["kWh saved/m²/year"].sum()
    post_intensity = baseline_intensity - total_kwh_savings_per_m2

    # Stranding Year
    stranding_year = None
    for y, target in zip(years, target_values):
        if post_intensity > target:
            stranding_year = y
            break

    # Annual kWh savings
    annual_kwh_saved = total_kwh_savings_per_m2 * building_area
    annual_energy_savings = annual_kwh_saved * energy_price

    # Fines
    fines = []
    for target in target_values:
        if post_intensity > target:
            excess_kwh = (post_intensity - target) * building_area
            excess_co2 = excess_kwh * emissions_factor
            fine = excess_co2 * carbon_price
        else:
            fine = 0
        fines.append(fine)

    net_cash_flows = annual_energy_savings - fines
    discounted = net_cash_flows / (1 + discount_rate) ** years
    npv = discounted.sum() - capex_total

    df = pd.DataFrame({
        "Year": years,
        "Target kWh/m²": target_values,
        "Post Intensity": post_intensity,
        "Fines (€)": fines,
        "Net Cash Flow (€)": net_cash_flows
    })

    # Show KPIs
    st.subheader("📊 Results Summary")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Capex (€)", f"{capex_total:,.0f}")
    kpi2.metric("NPV (€)", f"{npv:,.0f}")
    if stranding_year:
        kpi3.metric("⚠️ Stranding Year", str(stranding_year))
    else:
        kpi3.metric("✅ No Stranding", "Compliant 20 Years")

    # Intensity Chart
    st.subheader("📈 Energy Intensity vs. Target")
    fig1, ax1 = plt.subplots(figsize=(10,5))
    ax1.plot(df["Year"], df["Target kWh/m²"], label="Target Intensity")
    ax1.plot(df["Year"], [post_intensity]*len(df), label="Post-Retrofit Intensity")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("kWh/m²/year")
    ax1.set_title("Energy Intensity Trajectory")
    ax1.legend()
    ax1.grid(True)
    st.pyplot(fig1)

    # Cash Flow Chart
    st.subheader("💶 Net Cash Flows Over Time")
    fig2, ax2 = plt.subplots(figsize=(10,5))
    ax2.bar(df["Year"], df["Net Cash Flow (€)"])
    ax2.set_xlabel("Year")
    ax2.set_ylabel("€")
    ax2.set_title("Annual Net Cash Flows")
    ax2.grid(True)
    st.pyplot(fig2)

    # Show Table
    st.subheader("📋 Detailed Yearly Data")
    st.dataframe(df)

else:
    st.info("👈 Please select at least one retrofit measure to compute results.")
