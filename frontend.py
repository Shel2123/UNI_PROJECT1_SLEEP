import utils
import data.source_code
import requests
import logging
import pandas as pd
import streamlit as st 
from dotenv import dotenv_values
import data.cfg as cfg


class SleepDataFrontend:
    def __init__(self):
        self.setup_logging()
        self.run()


    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)


    @st.cache_data
    def load_data(_self):
        data = pd.read_csv(dotenv_values('.env')['PATH'])
        return data

    def clean_data(self): 
        try: 
            response = requests.get(cfg.CLEAN_DATA_URL) 
            if response.status_code == 200: 
                self.logger.info("Data succsessfully cleared.")
                st.success("Data succsessfully cleared.")
            else: 
                self.logger.error("An error occured while cleaning data.")
                st.error("An error occured while cleaning data.")
        except requests.exceptions.RequestException as e: 
            self.logger.error(f"An error occured while connecting to the server: {e}")


    def dispaly_graphs(self, graph_generator):
        st.title("Sleep Statistics")
        
        self.clean_data()
        
        with st.container():
            st.markdown("### Firtly, lets draw some graphs to see general information. There is our gender statistic pie chart:")
        st.plotly_chart(graph_generator.generate_gender_chart(), key=graph_generator.generate_key())
        with st.expander("Show/Close code"):
            st.code(data.source_code.source_code_data_list['first_table'], language='python')

        with st.container():
            st.markdown("### Then, occupation pie chart:")
        st.plotly_chart(graph_generator.generate_occupation_chart(), use_container_width=True, key=graph_generator.generate_key())
        with st.expander("Show/Close code"):
            st.code(data.source_code.source_code_data_list['second_table'], language='python')

        with st.container():
            st.markdown("### May be stress level is occured by occupation")
        st.plotly_chart(graph_generator.generate_stress_occupation_chart(), use_container_width=True, key=graph_generator.generate_key())
        with st.expander("Show/Close code"):
            st.code(data.source_code.source_code_data_list['third_table'], language='python')

        with st.container():
            st.markdown("### Draw 2D histogram to compare sleep duration and stress level")
        st.plotly_chart(graph_generator.generate_spray_graph(), use_container_width=True, key=graph_generator.generate_key())
        with st.expander("Show/Close code"):
            st.code(data.source_code.source_code_data_list['fourth_table'], language='python')

        with st.container():
            st.markdown("### Lets look at the main tendense more carefully.")
            st.markdown("### We need to find the average values at each age and find changes and draw the graph.")
        st.plotly_chart(graph_generator.generate_graph(), use_container_width=True, key=graph_generator.generate_key())
        with st.expander("Show/Close code"):
            st.code(data.source_code.source_code_data_list['fifth_table'], language='python')

        with st.container():
            st.markdown("### We can see that Sleep Duration and Stress level have strong inverse dependence. Lets draw some more graphs to find some more patterns.")
        st.plotly_chart(graph_generator.generate_phyz(), use_container_width=True, key=graph_generator.generate_key())
        with st.expander("Show/Close code"):
            st.code(data.source_code.source_code_data_list['sixth_table'], language='python')

        with st.container():
            st.markdown("### We obtain, that after 35 yo there a bit linear dependence between physical activity and stress level. I am going to look at the patterns between sleep duration, quality of sleep and physical activity.")
        st.plotly_chart(graph_generator.generate_duration_vs_quality_vs_phyz(), use_container_width=True, key=graph_generator.generate_key())
        with st.expander("Show/Close code"):
            st.code(data.source_code.source_code_data_list['seventh_table'], language='python')

        with st.container():
            st.markdown("### We can see that there is such a big dependence, but from 45 till 54 there is exception. After previous analise I can mention, that level of stress affects the physical activity. But lets look at numeratic statistics. I am going to use numpy to do it.")
            st.markdown("### I am using Pearson's correlation formula.")
        st.plotly_chart(graph_generator.generate_pirsons_mtx(), use_container_width=True, key=graph_generator.generate_key())
        with st.expander("Show/Close code"):
            st.code(data.source_code.source_code_data_list['eight_table'], language='python')
        with st.container():
            st.markdown("### So, sleep duration and sleep quality extremly decrease stress level, physical activity increases a bit sleep duration and quality of sleep, but physical activity has almost no effect on stress level.")


    def display_form(self):
        st.header("Add your data")
        with st.form("sleep_form"):
            gender = st.selectbox("Gender", ["Male", "Female"])
            age = st.number_input("Age (18-60)", min_value=18, max_value=60, step=1)
            occupation = st.text_input("Occupation:")
            sleep_duration = st.slider("Sleep duration (in hours)", min_value=2.0, max_value=12.0, step=0.1)
            quality_of_sleep = st.slider("Quality of sleep", min_value=0, max_value=10, step=1)
            stress_level = st.slider("Stress level", min_value=0, max_value=10, step=1)
            physical_activity_level = st.slider("Physical activity level", min_value=0, max_value=100, step=5)

            submitted = st.form_submit_button("Submit")

        if submitted:
            if occupation.strip() == '':
                occupation = 'Unemployed'

            n_data = {
                "gender": gender,
                "age": age,
                "occupation": occupation,
                "sleep_duration": sleep_duration,
                "quality_of_sleep": quality_of_sleep,
                "physical_activity_level": physical_activity_level,
                "stress_level": stress_level,
            }
            self.handle_submission(n_data)


    def handle_submission(self, n_data):
        try:
            response = requests.post(cfg.SUBMIT_URL, json=n_data)

            if response.status_code == 200:
                st.success("Data sent successfully.")
                with st.expander("Show/Close sent data"):
                    st.json(response.json())
                st.cache_data.clear()
                data = self.load_data()
                graph_generator = utils.GenerateGraph(data)
                self.dispaly_graphs(graph_generator)
            else:
                st.error("An error occured while sending the data.")
                self.logger.info(n_data)
                self.logger.info(f"Error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error("Could not connect to the server.")
            self.logger.error(f"Connection error: {e}")


    def run(self):
        data = self.load_data()
        graph_generator = utils.GenerateGraph(data)
        self.dispaly_graphs(graph_generator)
        self.display_form()


if __name__ == "__main__":
    SleepDataFrontend()
