# main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from .modules.database import Base, engine
from .modules.entity import router as EntityRouter
from .modules.comparison import router as ComparisonRouter
from .modules.rating import router as RatingRouter
from .modules.similarity import router as SimilarityRouter
from .modules.mab import router as MABRouter

load_dotenv()

app = FastAPI(
    title="Compere",
    description="An advanced comparative rating system that leverages Multi-Armed Bandit (MAB) algorithms and Elo ratings to provide fair and efficient entity comparisons.",
    version="0.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(EntityRouter)
app.include_router(ComparisonRouter)
app.include_router(RatingRouter)
app.include_router(SimilarityRouter)
app.include_router(MABRouter)

@app.on_event("startup")
async def startup_event():
    # Any startup logic can go here
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # Any shutdown logic can go here
    pass