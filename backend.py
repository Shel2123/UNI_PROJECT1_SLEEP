import pandas as pd
import logging
import uvicorn
import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

PATH = 'data/Sleep_health_and_lifestyle_dataset.csv'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FormData(BaseModel):
    gender: str
    age: int
    occupation: str
    sleep_duration: float
    quality_of_sleep: int
    stress_level: int
    physical_activity_level: int
    

@app.post("/submit/")
async def submit_data(data: FormData):
    logger.info(f"Received data: {data}")
    
    if not os.path.exists(PATH):
        raise FileNotFoundError(f"File not found")
    
    df = pd.read_csv(PATH)
    
    last_person_id = df["Person ID"].max()
    new_person_id = last_person_id + 1
    
    new_data = {
        "Person ID": int(new_person_id),
        "Gender": data.gender,
        "Age": data.age,
        "Occupation": data.occupation,
        "Sleep Duration": data.sleep_duration,
        "Quality of Sleep": data.quality_of_sleep,
        "Physical Activity Level": data.physical_activity_level,
        "Stress Level": data.stress_level,
    }
    
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_csv(PATH, index=False)
    
    return {"message": "Data taken successfully!", "data":new_data}


@app.get('/')
async def main():
    return {'message': 'Hello from FastAPI'}


if __name__ == "__main__":
    # start FastAPI
    uvicorn.run(app, host='0.0.0.0', port=8000)
