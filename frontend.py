import analyse
import utils
import requests
import logging
import pandas as pd
import streamlit as st 
from dotenv import dotenv_values
import data.cfg as cfg
from typing import Any, Dict


class SleepDataFrontend:
    def __init__(self) -> None:
        self.logger: logging.Logger = None
        self.setup_logging()
        self.run()


    def setup_logging(self) -> None:
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)


    @st.cache_data
    def load_data(_self) -> pd.DataFrame:
        data: pd.DataFrame = pd.read_csv(dotenv_values('.env')['PATH'])
        return data

    def clean_data(self) -> None: 
        try: 
            response: requests.Response = requests.get(cfg.CLEAN_DATA_URL) 
            if response.status_code == 200: 
                self.logger.info("Data succsessfully cleared.")
                st.success("Data succsessfully cleared.")
            else: 
                self.logger.error("An error occured while cleaning data.")
                st.error("An error occured while cleaning data.")
        except requests.exceptions.RequestException as e: 
            self.logger.error(f"An error occured while connecting to the server: {e}")


    def dispaly_graphs(self, graph_generator: analyse.GenerateGraph) -> None:
        st.title("Sleep Statistics")
        
        self.clean_data()
        
        file_to_parse_PATH: str = dotenv_values('.env')['PATH_TO_PARSE']
        utils_obj: utils.Utils = utils.Utils(file_to_parse_PATH)
        content: list[tuple[str, str]] = utils_obj.parse_file()
        
        for block_type, block_content in content:
            if block_type == 'text':
                with st.container():
                    st.markdown(block_content)
            elif block_type == 'method':
                method_name: str = block_content.strip()
                if hasattr(graph_generator, method_name):
                    method = getattr(graph_generator, method_name)
                    if callable(method):
                        try:
                            fig = method()
                            if fig:
                                st.plotly_chart(fig, use_container_width=True, key=utils_obj.generate_key())
                            else:
                                st.error(f"Method '{method_name}' returned None.")
                        except Exception as e:
                            st.error(f"Error while calling method '{method_name}'")
                    else:
                        st.error(f"'{method_name}' is not a method.")
                else:
                    st.error(f"There is no '{method_name}' method.")
            elif block_type == "code":
                with st.expander("Show/Close code"):
                    st.code(block_content)


    def display_form(self):
        st.header("Add your own data to analyse it.")
        with st.form("sleep_form"):
            gender: str = st.selectbox("Gender", ["Male", "Female"])
            age: int = st.number_input("Age (18-60)", min_value=18, max_value=60, step=1)
            occupation: str = st.text_input("Occupation:")
            sleep_duration: float = st.slider("Sleep duration (in hours)", min_value=2.0, max_value=12.0, step=0.1)
            quality_of_sleep: int = st.slider("Quality of sleep", min_value=0, max_value=10, step=1)
            stress_level: int = st.slider("Stress level", min_value=0, max_value=10, step=1)
            physical_activity_level: int = st.slider("Physical activity level", min_value=0, max_value=100, step=5)

            submitted: bool = st.form_submit_button("Submit")

        if submitted:
            if occupation.strip() == '':
                occupation = 'Unemployed'

            n_data: Dict[str, Any] = {
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
            response: requests.Response = requests.post(cfg.SUBMIT_URL, json=n_data)

            if response.status_code == 200:
                st.success("Data sent successfully.")
                with st.expander("Show/Close sent data"):
                    st.json(response.json())
                st.cache_data.clear()
                data: pd.DataFrame = self.load_data()
                graph_generator: analyse.GenerateGraph = analyse.GenerateGraph(data)
                self.dispaly_graphs(graph_generator)
            else:
                st.error("An error occured while sending the data.")
                self.logger.info(n_data)
                self.logger.info(f"Error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error("Could not connect to the server.")
            self.logger.error(f"Connection error: {e}")


    def run(self):
        data: pd.DataFrame = self.load_data()
        graph_generator: analyse.GenerateGraph = analyse.GenerateGraph(data)
        self.dispaly_graphs(graph_generator)
        self.display_form()


if __name__ == "__main__":
    SleepDataFrontend()
