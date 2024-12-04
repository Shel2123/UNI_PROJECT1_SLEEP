from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from data.base_model import FormData
from typing import Any


class Routes:
    def __init__(self, app: FastAPI, backend_instance) -> None:
        self.app: FastAPI = app
        self.backend = backend_instance
        self.router: APIRouter = APIRouter()
        self.setup_cors()
        self.setup_routes()


    def setup_cors(self) -> None:
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )


    def setup_routes(self) -> None:
        @self.router.post('/api/submit/')
        async def submit_data(data: FormData) -> Any:
            return await self.backend.submit_data(data)


        @self.router.get('/api/clean_data/')
        async def clean_data() -> Any:
            return await self.backend.clean_data()


        @self.router.get('/api/')
        async def main() -> dict[str, str]:
            return {'message': "Hello from FastAPI."}


        self.app.include_router(self.router)
