import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# URL для подключения к FastAPI
backend_url = "http://localhost:8000"

# Заголовок
st.title("Sleep and Stress Analysis")

# Форма для фильтрации данных
st.header("Retrieve Data")
age_min = st.number_input("Minimum Age", value=0)
age_max = st.number_input("Maximum Age", value=100)
limit = st.number_input("Limit", value=10)
offset = st.number_input("Offset", value=0)

if st.button("Get Data"):
    response = requests.get(f"{backend_url}/data", params={"age_min": age_min, "age_max": age_max, "limit": limit, "offset": offset})
    if response.status_code == 200:
        data = response.json()
        st.write(pd.DataFrame(data))
    else:
        st.error("Failed to retrieve data")

# Форма для добавления новых данных
st.header("Add Data")
with st.form("data_entry_form"):
    age = st.number_input("Age", value=30)
    sleep_duration = st.number_input("Sleep Duration", value=7.0)
    quality_of_sleep = st.number_input("Quality of Sleep", value=8.0)
    stress_level = st.number_input("Stress Level", value=5.0)
    physical_activity = st.number_input("Physical Activity Level", value=6.0)
    submitted = st.form_submit_button("Add Data")
    if submitted:
        response = requests.post(f"{backend_url}/data", json={
            "age": age,
            "sleep_duration": sleep_duration,
            "quality_of_sleep": quality_of_sleep,
            "stress_level": stress_level,
            "physical_activity": physical_activity
        })
        if response.status_code == 200:
            st.success("Data added successfully")
        else:
            st.error("Failed to add data")

# Визуализации
st.header("Visualizations")
if st.button("Generate Plots"):
    response = requests.get(f"{backend_url}/data")
    if response.status_code == 200:
        data = pd.DataFrame(response.json())
        fig = px.scatter(data, x="age", y="stress_level", color="quality_of_sleep", title="Stress Level vs Age")
        st.plotly_chart(fig)
    else:
        st.error("Failed to retrieve data for visualization")