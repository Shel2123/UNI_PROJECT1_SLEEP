import pandas as pd
import logging
import uvicorn
import os
import numpy as np
import data.cfg as cfg
from fastapi import FastAPI
from dotenv import dotenv_values
from routes import Routes
from data.base_model import FormData
from typing import Dict, Any


class SleepDataBackend:
    def __init__(self) -> None:
        self.setup_logging()
        self.app = FastAPI()
        self.PATH: str = dotenv_values('.env')['PATH']
        Routes(self.app, self)


    def setup_logging(self) -> None:
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)


    async def clean_data(self) -> Dict[str, Any]:
        try:
            df: pd.DataFrame = pd.read_csv(self.PATH)
            self.logger.info('Original data loaded.')

            df = df.dropna(how='all')
            self.logger.info('Rows with all NaN values removed.')

            numeric_cols = df.select_dtypes(include=[np.number]).columns
            row_keep: list[int] = []
            for index, row in df.iterrows():
                if not row[numeric_cols].isna().all():
                    if any(value != 0 for value in row[numeric_cols] if isinstance(value, (int, float))):
                        row_keep.append(index)
            df = df.loc[row_keep]
            self.logger.info('Rows with all zeros in numeric columns removed.')

            for col in df.columns:
                df[col] = df[col].replace([np.inf, -np.inf], np.nan)
            self.logger.info('Inf values replaced with None.')

            columns_to_delete: list[str] = cfg.COLUMNS_TO_DELETE
            columns_to_delete = [col.strip().strip('"').strip("'") for col in columns_to_delete]

            df.drop(columns=columns_to_delete, errors='ignore', inplace=True)
            self.logger.info('Specified columns removed.')

            df.to_csv(self.PATH, index=False)
            self.logger.info('Changes saved to CSV.')

            return {'message': 'Data successfully cleared.', 'data': df.head().to_dict()}
        except Exception as e:
            self.logger.error(f"Error while clearing data: {e}")
            return {'error': str(e)}


    async def submit_data(self, data: FormData) -> Dict[str, Any]:
        self.logger.info(f"Received data: {data}")

        if not os.path.exists(self.PATH):
            raise FileNotFoundError(f"File not found")

        df: pd.DataFrame = pd.read_csv(self.PATH)

        last_person_id = df["Person ID"].max()
        new_person_id = last_person_id + 1 if not pd.isnull(last_person_id) else 1

        new_data: Dict[str, Any] = {
            "Person ID": int(new_person_id),
            "Gender": data.gender,
            "Age": data.age,
            "Occupation": data.occupation,
            "Sleep Duration": data.sleep_duration,
            "Quality of Sleep": data.quality_of_sleep,
            "Physical Activity Level": data.physical_activity_level,
            "Stress Level": data.stress_level
        }
        self.logger.info(f"Received data: {new_data}")
        ordered_columns: list[str] = ["Person ID", "Gender","Age","Occupation","Sleep Duration","Quality of Sleep", "Physical Activity Level", "Stress Level"]
        print(df.columns.tolist())
        print(new_data)
        df = pd.concat([df, pd.DataFrame([new_data], columns=ordered_columns)], ignore_index=True)
        df.to_csv(self.PATH, index=False)

        return {"message": "Data taken successfully!", "data":new_data}


    def run(self) -> None:
        # start FastAPI
        uvicorn.run(self.app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    backend = SleepDataBackend()
    backend.run()
