import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="ESG Analysis",
    page_icon="📊",
    layout="wide"
)


# Retrofit measures
st.sidebar.header("Retrofit Measures (per m²)")
retrofits = pd.DataFrame({
    "Measure": ["BMS Replacement", "Reduced Tennant Load", "Low Energy Light", "Night Purging"],
    "Capex €/m²": [40, 142, 142, 142],
    "kWh saved/m²/year": [130, 121.6, 121.6, 121.6]
}).set_index("Measure")

selected_measures = st.sidebar.multiselect(
    "Select Retrofit Measures:",
    options=retrofits.index
)
