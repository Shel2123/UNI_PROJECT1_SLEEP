import os
import logging
from datetime import datetime, timezone, timedelta

from typing import Dict, Any
from dotenv import dotenv_values
import uvicorn
import pandas as pd
import numpy as np

from fastapi import FastAPI, Request
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
            
            if 'last_submission' not in df.columns:
                df['last_submissions'] = np.nan

            df.to_csv(self.PATH, index=False)
            self.logger.info('Changes saved to CSV.')

            return {'message': 'Data successfully cleared.', 'data': df.head().to_dict()}

        except Exception as e:
            self.logger.error(f"Error while clearing data: {e}")
            return {'error': str(e)}

    async def submit_data(self, request: Request, data: FormData) -> Dict[str, Any]:
        """
        Submit a new data entry to the CSV file. And check for spam.

        Args:
            data (FormData): The form data submitted by the user and request IP.

        Returns:
            Dict[str, Any]: Status message and the submitted data.
        """
        try:
            
            self.logger.info(f"Received data to submit: {data}")

            if not os.path.exists(self.PATH):
                error_msg = "File not found."
                self.logger.error(error_msg)
                return {'error': error_msg}

            df: pd.DataFrame = pd.read_csv(self.PATH)

            client_ip = request.client.host

            if 'ip_address' not in df.columns:
                df['ip_address'] = ''
                self.logger.info("'ip address' columns has been added")
            else:
                df['ip_address'] = df['ip_address'].astype(str)

            if 'last_submission' not in df.columns:
                df['last_submission'] = np.nan_to_num
                self.logger.info("'last submision' columns has been added")
            else:
                df['last_submission'] = pd.to_datetime(df['last_submission'], errors='coerce')

            ip_submissions = df[df['ip_address'] == client_ip]

            if not ip_submissions.empty:
                last_submission_time = ip_submissions['last_submission'].max()
                if pd.notnull(last_submission_time):
                    current_time = datetime.now(timezone.utc)
                    time_diff = current_time - last_submission_time

                    if time_diff < timedelta(minutes=5):
                        remaining_time = timedelta(minutes=5) - time_diff
                        minutes, seconds = divmod(remaining_time.seconds, 60)
                        error_msg = f"You can submit the form again in {minutes} minutes and {seconds} seconds."
                        self.logger.warning(f"Submission from IP {client_ip} blocked. Time remaining: {remaining_time}")
                        return {'error': error_msg}

            last_person_id = df["Person ID"].max()
            new_person_id = int(last_person_id + 1 if pd.notnull(last_person_id) else 1)

            current_time_iso = datetime.now(timezone.utc).isoformat()

            new_data: Dict[str, Any] = {
                "Person ID": new_person_id,
                "Gender": data.gender,
                "Age": data.age,
                "Occupation": data.occupation,
                "Sleep Duration": data.sleep_duration,
                "Quality of Sleep": data.quality_of_sleep,
                "Physical Activity Level": data.physical_activity_level,
                "Stress Level": data.stress_level,
                "ip_address": client_ip,
                'last_submission': current_time_iso
            }
            self.logger.info(f"Prepared new data entry: {new_data}")

            ordered_columns = [
                "Person ID", "Gender", "Age", "Occupation", 
                "Sleep Duration", "Quality of Sleep", 
                "Physical Activity Level", "Stress Level", 'ip_address', 'last_submission'
            ]

            new_data['last_submission'] = pd.to_datetime(new_data['last_submission'])

            df = pd.concat([df, pd.DataFrame([new_data], columns=ordered_columns)], ignore_index=True)
            df.to_csv(self.PATH, index=False)
            self.logger.info("New data appended and CSV updated.")

            return {"message": "Data taken successfully!", "data": new_data}
        except Exception as e:
            self.logger.error(f"Error while submitting data: {e}")
            return {'error': str(e)}

    def run(self) -> None:
        """
        Run the FastAPI application using uvicorn.
        """
        uvicorn.run(self.app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    backend = SleepDataBackend()
    backend.run()