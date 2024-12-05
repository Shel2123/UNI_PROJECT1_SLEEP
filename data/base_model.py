from pydantic import BaseModel


class FormData(BaseModel):
        gender: str
        age: int
        occupation: str
        sleep_duration: float
        quality_of_sleep: int
        physical_activity_level: int
        stress_level: int
