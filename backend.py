import os
import logging

from typing import Dict, Any
from dotenv import dotenv_values
import uvicorn
import pandas as pd
import numpy as np

from fastapi import FastAPI
from data.base_model import FormData
from routes import Routes
import data.cfg as cfg


class SleepDataBackend:
    """
    SleepDataBackend is responsible for providing an API that:
    - Cleans and processes sleep data from a CSV file.
    - Submits new data entries into the CSV file.
    - Provides routes for data cleaning and data submission.
    """

    def __init__(self) -> None:
        """
        Initialize the backend by setting up logging, creating a FastAPI application,
        and adding routes.
        """
        self.setup_logging()
        self.app = FastAPI()
        self.PATH: str = dotenv_values('.env')['PATH']
        Routes(self.app, self)

    def setup_logging(self) -> None:
        """
        Set up basic logging configuration and logger instance.
        """
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def clean_data(self) -> Dict[str, Any]:
        """
        Clean the CSV data by:
        - Removing rows with all NaN values.
        - Removing rows where all numeric values are zero.
        - Replacing infinite values with NaN.
        - Dropping specified columns from configuration.
        - Saving the cleaned data back to CSV.

        Returns:
            Dict[str, Any]: Status message and a preview of the cleaned data.
        """
        try:
            df: pd.DataFrame = pd.read_csv(self.PATH)
            self.logger.info('Original data loaded.')

            # Drop rows with all NaN values
            df.dropna(how='all', inplace=True)
            self.logger.info('Rows with all NaN values removed.')

            numeric_cols = df.select_dtypes(include=[np.number]).columns

            # Keep rows that have at least one non-zero numeric value
            # First, drop rows where all numeric values are NaN
            df.dropna(subset=numeric_cols, how='all', inplace=True)
            # Keep rows where at least one numeric column is not zero
            df = df[(df[numeric_cols] != 0).any(axis=1)]
            self.logger.info('Rows with all zeros in numeric columns removed.')

            # Replace infinite values with NaN
            df.replace([np.inf, -np.inf], np.nan, inplace=True)
            self.logger.info('Infinite values replaced with NaN.')

            # Drop specified columns
            columns_to_delete = [col.strip().strip('"').strip("'") for col in cfg.COLUMNS_TO_DELETE]
            df.drop(columns=columns_to_delete, errors='ignore', inplace=True)
            self.logger.info('Specified columns removed.')

            df.to_csv(self.PATH, index=False)
            self.logger.info('Changes saved to CSV.')

            return {'message': 'Data successfully cleared.', 'data': df.head().to_dict()}

        except Exception as e:
            self.logger.error(f"Error while clearing data: {e}")
            return {'error': str(e)}

    async def submit_data(self, data: FormData) -> Dict[str, Any]:
        """
        Submit a new data entry to the CSV file.

        Args:
            data (FormData): The form data submitted by the user.

        Returns:
            Dict[str, Any]: Status message and the submitted data.
        """
        self.logger.info(f"Received data to submit: {data}")

        if not os.path.exists(self.PATH):
            error_msg = "File not found."
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        df: pd.DataFrame = pd.read_csv(self.PATH)

        last_person_id = df["Person ID"].max()
        new_person_id = int(last_person_id + 1 if pd.notnull(last_person_id) else 1)

        new_data: Dict[str, Any] = {
            "Person ID": new_person_id,
            "Gender": data.gender,
            "Age": data.age,
            "Occupation": data.occupation,
            "Sleep Duration": data.sleep_duration,
            "Quality of Sleep": data.quality_of_sleep,
            "Physical Activity Level": data.physical_activity_level,
            "Stress Level": data.stress_level
        }
        self.logger.info(f"Prepared new data entry: {new_data}")

        ordered_columns = [
            "Person ID", "Gender", "Age", "Occupation", 
            "Sleep Duration", "Quality of Sleep", 
            "Physical Activity Level", "Stress Level"
        ]

        df = pd.concat([df, pd.DataFrame([new_data], columns=ordered_columns)], ignore_index=True)
        df.to_csv(self.PATH, index=False)
        self.logger.info("New data appended and CSV updated.")

        return {"message": "Data taken successfully!", "data": new_data}

    def run(self) -> None:
        """
        Run the FastAPI application using uvicorn.
        """
        uvicorn.run(self.app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    backend = SleepDataBackend()
    backend.run()