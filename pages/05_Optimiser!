import streamlit as st
import pandas as pd

def optimize_retrofits(current_intensity, target_intensity, retrofit_options, floor_area_m2):
    """
    Greedy optimizer: selects the most cost-effective retrofits to meet target intensity.
    """
    # Sort by cost-effectiveness (£ per kWh saved)
    sorted_retrofits = sorted(
        retrofit_options.items(),
        key=lambda x: x[1]["cost_per_m2"] / x[1]["saving"]
    )

    selected = []
    cumulative_saving = 0.0
    total_cost = 0.0

    for name, data in sorted_retrofits:
        if current_intensity - cumulative_saving <= target_intensity:
            break

        cumulative_saving += data["saving"]
        retrofit_cost = data["cost_per_m2"] * floor_area_m2
        total_cost += retrofit_cost

        selected.append({
            "Retrofit": name,
            "Saving (kWh/m²)": data["saving"],
            "Cost per m² (£)": data["cost_per_m2"],
            "Total Cost (£)": retrofit_cost
        })

    final_intensity = max(current_intensity - cumulative_saving, 0)

    return pd.DataFrame(selected), final_intensity, total_cost


st.title("🔧 Retrofit Optimizer (Auto-Select Best Combo)")

floor_area_m2 = st.number_input("Floor area (m²)", value=5000)
current_intensity = st.number_input("Current intensity (kWh/m²/year)", value=250.0)
target_intensity = st.number_input("Target intensity (kWh/m²/year)", value=75.0)

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

if st.button("Optimize Retrofit Plan"):
    results_df, achieved_intensity, total_cost = optimize_retrofits(
        current_intensity,
        target_intensity,
        retrofit_options,
        floor_area_m2
    )

    if results_df.empty:
        st.warning("❗️ No retrofits needed or possible to reach target.")
    else:
        st.subheader("✅ Selected Retrofits")
        st.dataframe(results_df)

        st.markdown(f"""
        ### 📊 Summary:
        - **Final Intensity:** {achieved_intensity:.2f} kWh/m²/year
        - **Total Estimated Cost:** £{total_cost:,.2f}
        """)
