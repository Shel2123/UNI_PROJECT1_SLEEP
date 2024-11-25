import pandas as pd
import logging
import uvicorn
import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


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
        self.PATH = 'data/Sleep_health_and_lifestyle_dataset.csv'


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
        
        @self.app.get('/api/')
        async def main():
            return {'message': "Hello from FastAPI."}
       

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
