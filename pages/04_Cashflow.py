import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("💰 Retrofit Cash Flow Analysis")

# Retrieve stored data
retrofits = st.session_state["selected_retrofit_data"]
years = st.session_state["years"]
floor_area_m2 = st.session_state["floor_area_m2"]
remaining_intensity = st.session_state["remaining_intensity_after_retrofits"]

# Energy cost assumption
energy_cost_per_kwh = st.number_input(
    "Energy Cost per kWh (£)",
    min_value=0.0,
    value=0.15
)



   
