import streamlit as st 
from utils import generate_gender_chart

st.title("Sleep Statistics")

st.plotly_chart(generate_gender_chart(), use_container_width=True)
