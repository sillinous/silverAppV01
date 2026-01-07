from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database imports
from arbitrage_os.db import models
from arbitrage_os.db.database import engine

# API Router imports
from arbitrage_os.api import admin, auth, discovery, logistics, valuation, verification

def create_db_and_tables():
    models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Arbitrage OS",
    description="An OS to dominate local markets for silver arbitrage.",
    version="0.1.0"
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Arbitrage OS"}

# Include routers from the api modules
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(discovery.router, prefix="/discover", tags=["Discovery"])
app.include_router(logistics.router, prefix="/logistics", tags=["Logistics"])
app.include_router(valuation.router, prefix="/valuation", tags=["Valuation"])
app.include_router(verification.router, prefix="/verification", tags=["Verification"])
