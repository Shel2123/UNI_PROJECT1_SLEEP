import pandas as pd
import logging
import uvicorn
import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import dotenv_values


class FormData(BaseModel):
        gender: str
        age: int
        occupation: str
        sleep_duration: float
        quality_of_sleep: int
        physical_activity_level: int
        stress_level: int


class SleepDataBackend:
    def __init__(self):
        self.setup_logging()
        self.app = FastAPI()
        self.setup_routes()
        self.PATH = dotenv_values('.env')['PATH']


    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)


    def setup_routes(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )

        @self.app.post("/api/submit/")
        async def submit_data(data: FormData):
            return await self.submit_data(data)


        @self.app.get('/api/clean_data')
        async def clean_data():
            return await self.clean_data()


        @self.app.get('/api/')
        async def main():
            return {'message': "Hello from FastAPI."}


    async def clean_data(self):
        try:
            df = pd.read_csv(self.PATH)
            self.logger.info('Origin data loaded')

            columns_to_delete = dotenv_values('.env')['COLUMNS_TO_DELETE']
            df.drop(columns=columns_to_delete, inplace=True, errors='ignore')
            self.logger.info('Useless columns removed')

            row_keep = []
            for index, row in df.iterrows():
                if not (row.isna().all() or (row == 0).all()):
                    row_keep.append(index)

            df = df.loc[row_keep]
            self.logger.info('Empty lines deleted.')

            df.to_csv(self.PATH, index=False)
            self.logger.info('Changes are saved')

            return {'message': 'Data successfully cleared.', 'data': df.head().to_dict()}
        except Exception as e:
            self.logger.error(f"Error while clearing data: {e}")
            return {'error': str(e)}


    async def submit_data(self, data: FormData):
        self.logger.info(f"Received data: {data}")

        if not os.path.exists(self.PATH):
            raise FileNotFoundError(f"File not found")

        df = pd.read_csv(self.PATH)

        last_person_id = df["Person ID"].max()
        new_person_id = last_person_id + 1 if not pd.isnull(last_person_id) else 1

        new_data = {
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
        ordered_columns = ["Person ID", "Gender","Age","Occupation","Sleep Duration","Quality of Sleep", "Physical Activity Level", "Stress Level"]
        print(df.columns.tolist())
        print(new_data)
        df = pd.concat([df, pd.DataFrame([new_data], columns=ordered_columns)], ignore_index=True)
        df.to_csv(self.PATH, index=False)

        return {"message": "Data taken successfully!", "data":new_data}


    def run(self):
        # start FastAPI
        uvicorn.run(self.app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    backend = SleepDataBackend()
    backend.run()
