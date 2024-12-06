from typing import Any
from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from data.base_model import FormData


class Routes:
    """
    Routes class sets up the API routes and CORS configuration for the FastAPI application.
    """

    def __init__(self, app: FastAPI, backend_instance: Any) -> None:
        """
        Initialize routes and middleware.

        Args:
            app (FastAPI): The FastAPI instance.
            backend_instance (Any): The backend instance providing clean_data and submit_data methods.
        """
        self.app: FastAPI = app
        self.backend = backend_instance
        self.router: APIRouter = APIRouter()
        self.setup_cors()
        self.setup_routes()

    def setup_cors(self) -> None:
        """
        Set up CORS middleware to allow access from all origins.
        """
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )

    def setup_routes(self) -> None:
        """
        Define and include the API routes.
        """
        @self.router.post('/api/submit/')
        async def submit_data(request: Request, data: FormData) -> Any:
            return await self.backend.submit_data(request, data)

        @self.router.get('/api/clean_data/')
        async def clean_data() -> Any:
            return await self.backend.clean_data()

        @self.router.get('/api/')
        async def main() -> dict[str, str]:
            return {'message': "Hello from FastAPI."}

        self.app.include_router(self.router)
