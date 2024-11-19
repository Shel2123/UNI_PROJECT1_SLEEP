from pydantic import BaseModel

class DataEntry(BaseModel):
    age: int
    sleep_duration: float
    quality_of_sleep: float
    stress_level: float
    physical_activity: float