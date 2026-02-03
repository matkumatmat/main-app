from __future__ import annotations
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from shared.backend.config.settings import settings

def addCorsMiddleware(app: FastAPI) -> None:
    """
    Apply CORS configuration using validated list from settings.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.corsOriginsList,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )