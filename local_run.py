from fastapi import FastAPI
from threading import Thread
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


star = FastAPI()

star.add_middleware(
    CORSMiddleware,
    allow_oriigns=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@star.get('/')
async def main():
    return {'message': 'Streamlit app is running at localhost'}

def run_stre():
    os.system('python -m streamlit run frontend.py --server.port 8501 --server.headless true')

if __name__ == "__main__":
    thread = Thread(target=run_stre, daemon=True)
    thread.start()
    
    uvicorn.run(star, host='0.0.0.0', port=8000)