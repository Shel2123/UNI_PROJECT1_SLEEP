from fastapi import APIRouter, Query
from typing import List, Optional
from models import DataEntry
from database import dataset

router = APIRouter()

@router.get('/data')
def get_data(
    age_min: Optional[int] = Query(None),
    age_max: Optional[int] = Query(None),
    limit: int = 10,
    offset: int = 0
) -> List[dict]:
    filtered_data = [
        entry for entry in dataset
        if (age_min is None or entry['age'] >= age_min) and (age_max is None or entry['age'] <= age_max)
    ]
    return filtered_data[offset:offset + limit]

@router.post('/data')
def add_data(entry: DataEntry):
    dataset.append(entry.dict())
    return {'message': 'Data entry added successfully', 
            'entry': entry}

