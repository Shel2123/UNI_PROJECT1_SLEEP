import streamlit as st 
import utils
import data.source_code
import requests
import logging
import subprocess
import time

subprocess.run(
    ["python", 'delete_columns.py']
)

st.title("Sleep Statistics")

with st.container():
    st.markdown("### Firtly, Lets draw our gender statistic pie chart")
st.plotly_chart(utils.graph_generator.generate_gender_chart())
with st.expander("Show/Close code"):
    st.code(data.source_code.source_code_data_list[0], language='python')

with st.container():
    st.markdown("### Then, occupation pie chart")
st.plotly_chart(utils.graph_generator.generate_occupation_chart(), use_container_width=True)
with st.expander("Show/Close code"):
    st.code(data.source_code.source_code_data_list[1], language='python')

with st.container():
    st.markdown("### May be stress level is occured by occupation")
st.plotly_chart(utils.graph_generator.generate_stress_occupation_chart(), use_container_width=True)
with st.expander("Show/Close code"):
    st.code(data.source_code.source_code_data_list[2], language='python')

with st.container():
    st.markdown("### Draw histogram to compare sleep duration and stress level")
st.plotly_chart(utils.graph_generator.generate_spray_graph(), use_container_width=True)
with st.expander("Show/Close code"):
    st.code(data.source_code.source_code_data_list[3], language='python')

with st.container():
    st.markdown("### Lets look at the main tendense more carefully.")
    st.markdown("### Firstly, we need to find the average values at each age and find changes and draw the graph.")
st.plotly_chart(utils.graph_generator.generate_graph(), use_container_width=True)
with st.expander("Show/Close code"):
    st.code(data.source_code.source_code_data_list[4], language='python')

with st.container():
    st.markdown("### We can see that Sleep Duration and Stress level have inverse dependence. Lets draw some more graphs if wee can find some patterns.")
st.plotly_chart(utils.graph_generator.generate_phyz(), use_container_width=True)
with st.expander("Show/Close code"):
    st.code(data.source_code.source_code_data_list[5], language='python')

with st.container():
    st.markdown("### We obtain, that after 35 yo there a bit linear dependence between physical activity and stress level. I am going to look at the patterns between sleep duration, quality of sleep and physical activity.")
st.plotly_chart(utils.graph_generator.generate_duration_vs_quality_vs_phyz(), use_container_width=True)
with st.expander("Show/Close code"):
    st.code(data.source_code.source_code_data_list[6], language='python')

with st.container():
    st.markdown("### We can see that there is such a big dependence, but from 45 till 54 there is exception. After previous analise I can mention, that level of stress affects the physical activity. But lets look at numeratic statistics. I am going to use numpy to do it.")
    st.markdown("### I am using Pirson's corelation formula.")
st.plotly_chart(utils.graph_generator.generate_pirsons_mtx(), use_container_width=True)
with st.expander("Show/Close code"):
    st.code(data.source_code.source_code_data_list[7], language='python')
with st.container():
    st.markdown("### We can see that sleep duration and sleep quality extremly decreases stress level, physical activity increases a bit sleep duration and quality of sleep, but physical activity has almost no effect on stress level.")

st.header("Add your data")
with st.form("sleep_form"):
    gender = st.selectbox("Gender", ["Male", "Female"])
    age = st.number_input("Age (18-60)", min_value=18, max_value=60, step=1)
    occupation = st.text_input("Occupation:")
    sleep_duration = st.slider("Sleep duration (in hours)", min_value=0.0, max_value=12.0, step=0.1)
    quality_of_sleep = st.slider("Quality of sleep", min_value=0, max_value=10, step=1)
    stress_level = st.slider("Stress level", min_value=0, max_value=100, step=5)
    physical_activity_level = st.slider("Physical activity level", min_value=0, max_value=10, step=1)
    
    submitted = st.form_submit_button("Submit")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if submitted:
    run_api = subprocess.Popen(
        ["python", 'backend.py']
    )
    time.sleep(2)
    
    n_data = {
        "gender": gender,
        "age": age,
        "occupation": occupation,
        "sleep_duration": sleep_duration,
        "quality_of_sleep": quality_of_sleep,
        "stress_level": stress_level,
        "physical_activity_level": physical_activity_level
    }
    try:
        response = requests.post("https://projectsleepac.streamlit.app/submit/", json=n_data)

        if response.status_code == 200:
            st.success("Data submitted successfully!")
            st.json(response.json())
        else:
            st.error("An error occured while submitting the data.")
            logger.info(n_data)
            logger.info(f"Error {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error("Could not connect to the server.")
        logger.error(f"Connection error: {e}")
