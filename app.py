from fastapi import FastAPI
import uvicorn
from threading import Thread
import os


app = FastAPI()

@app.get('/')
async def main():
    return {'message': 'Streamlit app is running at localhost'}

def run_stre():
    os.system('python -m streamlit run streamlit_app.py --server.port 8501 --server.headless true')

if __name__ == "__main__":
    thread = Thread(target=run_stre, daemon=True)
    thread.start()
    
    uvicorn.run(app, host='0.0.0.0', port=8000)