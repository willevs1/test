import streamlit as st
import pandas as pd

st.title("🏗 Retrofit Options Selection")

# Input building parameters if needed
floor_area_m2 = st.session_state.get("floor_area_m2", 1000)
years = st.session_state.get("years", 5)

# Retrofit options
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

# Flatten options to DataFrame
data = []
for cat, measures in retrofit_options.items():
    for name, props in measures.items():
        data.append({
            "Category": cat,
            "Measure": name,
            "Saving (kWh/m²)": props["saving"],
            "Cost (£/m²)": props["cost_per_m2"],
        })

df = pd.DataFrame(data)

st.subheader("Available Retrofit Options")
st.dataframe(df)

# Selection form
st.subheader("Select Measures and Investment Years")

selected_retrofits = {}

with st.form("retrofit_form"):
    for idx, row in df.iterrows():
        cols = st.columns([0.4, 0.2, 0.2, 0.2])
        with cols[0]:
            selected = st.checkbox(f"{row['Measure']} ({row['Category']})", key=f"check_{idx}")
        if selected:
            with cols[1]:
                year = st.number_input(
                    "Year",
                    min_value=1,
                    max_value=years,
                    value=1,
                    key=f"year_{idx}"
                )
            # Store selection
            selected_retrofits[row["Measure"]] = {
                "year": int(year),
                "saving": row["Saving (kWh/m²)"],
                "cost_per_m2": row["Cost (£/m²)"],
                "category": row["Category"],
            }
    submitted = st.form_submit_button("Save Selections")

# Store selections if submitted
if submitted:
    if selected_retrofits:
        st.session_state["selected_retrofit_data"] = selected_retrofits
        st.success("Selections saved!")
    else:
        st.warning("No measures selected.")

# Preview
if "selected_retrofit_data" in st.session_state:
    preview = pd.DataFrame([
        {
            "Measure": m,
            "Category": d["category"],
            "Year": d["year"],
            "Saving (kWh/m²)": d["saving"],
            "Cost (£/m²)": d["cost_per_m2"],
        }
        for m, d in st.session_state["selected_retrofit_data"].items()
    ])
    st.subheader("Selected Retrofits")
    st.table(preview)
