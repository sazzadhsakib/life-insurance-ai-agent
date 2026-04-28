import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import chat_router

# 1. Configure Global Logging Standard
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def create_app() -> FastAPI:
    app = FastAPI(
        title="Life Insurance AI Agent API",
        description="Backend API for the Life Insurance Support Assistant assessment.",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat_router, prefix="/api/v1")

    # Add a startup log
    @app.on_event("startup")
    async def startup_event():
        logger = logging.getLogger("server")
        logger.info("Life Insurance Agent API successfully started and ready for requests.")

    return app

app = create_app()